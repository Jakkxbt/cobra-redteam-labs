#!/usr/bin/env python3
"""
Blind SQL injection lab.

A simple API that checks if a username exists in the database and returns ONLY
"exists" or "does not exist". The VULNERABLE version builds the query by string
concatenation, so a crafted input can turn the boolean response into an oracle
and extract the admin's password one character at a time. The SAFE version uses
parameterised queries and the attack is impossible.

Run with --safe to see the fixed version.

No third-party libraries — sqlite3 (stdlib) + http.server. Local lab only —
do not deploy publicly.

  python3 lab.py            # vulnerable, http://127.0.0.1:18210/
  python3 lab.py --safe     # fixed
"""
import argparse
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

SAFE = False

# Admin password (the flag you're trying to extract)
ADMIN_PASSWORD = "FLAG{bl1nd_but_1_c4n_s33}"


def init_db():
    """Initialize a new in-memory SQLite database with test users."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    # Insert test users
    cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", ("alice", "password123"))
    cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", ("bob", "password456"))
    cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", ("admin", ADMIN_PASSWORD))

    conn.commit()
    return conn


def check_user_vulnerable(username: str, db_connection) -> bool:
    """
    VULNERABLE: String concatenation allows SQL injection.

    This query is the bug:
        SELECT 1 FROM users WHERE name='<username>'

    An attacker can inject:
        alice' AND SUBSTR((SELECT password FROM users WHERE name='admin'),1,1)='a

    This makes the whole query true only if the admin's password starts with 'a'.
    By testing characters a-z, A-Z, 0-9, and special chars, you can extract the entire
    password one character at a time.
    """
    cursor = db_connection.cursor()

    # VULNERABLE: String concatenation — SQL injection possible
    query = f"SELECT 1 FROM users WHERE name='{username}'"
    cursor.execute(query)

    # Return True if any row exists, False otherwise
    row = cursor.fetchone()
    return row is not None


def check_user_safe(username: str, db_connection) -> bool:
    """
    SAFE: Parameterised query prevents SQL injection.

    The username is passed as a parameter, not concatenated into the query string.
    This prevents SQL injection entirely.
    """
    cursor = db_connection.cursor()

    # SAFE: Parameterised query — SQL injection impossible
    cursor.execute("SELECT 1 FROM users WHERE name=?", (username,))

    # Return True if any row exists, False otherwise
    row = cursor.fetchone()
    return row is not None


class Handler(BaseHTTPRequestHandler):
    def _send_text(self, text: str, code=200):
        body = text.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._send_text("Blind SQL injection lab. GET /check?user=<username> returns 'exists' or 'does not exist'.")
            return
        if path == "/check":
            query = parse_qs(urlparse(self.path).query)
            username = query.get("user", [""])[0]

            if not username:
                self._send_text("missing username parameter", 400)
                return

            try:
                # Create a new database connection for each request (thread safety)
                db_connection = init_db()

                if SAFE:
                    exists = check_user_safe(username, db_connection)
                else:
                    exists = check_user_vulnerable(username, db_connection)
            except Exception:
                # Keep it BLIND: a malformed/erroring query must be
                # indistinguishable from "no match" — never leak the SQL error,
                # or this stops being a blind lab.
                self._send_text("does not exist")
                return

            if exists:
                self._send_text("exists")
            else:
                self._send_text("does not exist")
            return

        self._send_text("not found", 404)

    def log_message(self, *a):
        return


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=18210)
    p.add_argument("--safe", action="store_true")
    args = p.parse_args()
    SAFE = args.safe
    mode = "SAFE (parameterised query)" if SAFE else "VULNERABLE (string concatenation)"
    print(f"Blind SQL injection lab [{mode}] on http://127.0.0.1:{args.port}/")
    print("  GET /check?user=<username> -> returns 'exists' or 'does not exist'")
    print("  Tip: Blind SQLi can extract the admin's password one character at a time")
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
