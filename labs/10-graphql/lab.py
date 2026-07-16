#!/usr/bin/env python3
"""
GraphQL schema discovery and broken resolver authorisation lab.

The public UI asks only for `me { name }`, but the VULNERABLE schema can be
introspected and exposes sensitive fields whose resolvers have no access check.
Run with --safe to disable introspection and enforce authorisation at each
sensitive resolver.

This is a deliberately tiny GraphQL-like implementation built with Python's
standard library. It recognises only the handful of queries used by the lab.
Local training only — do not deploy publicly.

  python3 lab.py            # vulnerable, http://127.0.0.1:18211/
  python3 lab.py --safe     # fixed
"""
import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

__author__ = "Jakkxbt"

SAFE = False

USERS = {
    "1": {"id": "1", "name": "alice", "email": "alice@example.test"},
    "2": {"id": "2", "name": "admin", "email": "admin@cobra.internal"},
}
ADMIN_TOKEN = "training-admin-token"
FLAG = "FLAG{graphql_hidden_resolver}"


def selections(query, field):
    """Return the simple selection set following a named field."""
    match = re.search(rf"\b{re.escape(field)}\b(?:\s*\([^)]*\))?\s*\{{([^{{}}]*)\}}",
                      query, re.S)
    return re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", match.group(1)) if match else []


def project(record, fields):
    return {field: record.get(field) for field in fields if field in record}


def schema_result():
    return {
        "__schema": {
            "queryType": {"name": "Query"},
            "types": [
                {
                    "kind": "OBJECT",
                    "name": "Query",
                    "fields": [
                        {"name": "me"},
                        {"name": "user"},
                        {"name": "adminSecret"},
                    ],
                },
                {
                    "kind": "OBJECT",
                    "name": "User",
                    "fields": [
                        {"name": "id"},
                        {"name": "name"},
                        {"name": "email"},
                    ],
                },
            ],
        }
    }


def execute(query, authorised):
    if not isinstance(query, str) or not query.strip():
        return 400, {"errors": [{"message": "query must be a non-empty string"}]}

    if "__schema" in query or "__type" in query:
        if SAFE:
            return 200, {"data": None, "errors": [
                {"message": "introspection is disabled"}
            ]}
        return 200, {"data": schema_result()}

    data = {}
    errors = []
    me_fields = selections(query, "me")
    if me_fields:
        data["me"] = project(USERS["1"], me_fields)

    user_match = re.search(r"\buser\s*\(\s*id\s*:\s*[\"']([^\"']+)[\"']\s*\)",
                           query)
    if user_match:
        if SAFE and not authorised:
            data["user"] = None
            errors.append({"message": "not authorised to query another user",
                           "path": ["user"]})
        else:
            record = USERS.get(user_match.group(1))
            data["user"] = project(record, selections(query, "user")) if record else None

    if re.search(r"\badminSecret\b", query):
        if SAFE and not authorised:
            data["adminSecret"] = None
            errors.append({"message": "not authorised to read adminSecret",
                           "path": ["adminSecret"]})
        else:
            data["adminSecret"] = FLAG

    if not data and not errors:
        errors.append({"message": "unsupported field or malformed query"})
    response = {"data": data}
    if errors:
        response["errors"] = errors
    return 200, response


class Handler(BaseHTTPRequestHandler):
    def send_json(self, code, obj):
        body = json.dumps(obj, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if urlparse(self.path).path == "/":
            self.send_json(200, {
                "product": "Cobra account portal",
                "ui_query": "{ me { name } }",
                "graphql": "POST /graphql with JSON: {\"query\":\"...\"}",
            })
            return
        self.send_json(404, {"error": "not found"})

    def do_POST(self):
        if urlparse(self.path).path != "/graphql":
            self.send_json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            request = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            self.send_json(400, {"errors": [{"message": "invalid JSON request"}]})
            return
        authorised = self.headers.get("Authorization") == f"Bearer {ADMIN_TOKEN}"
        code, response = execute(request.get("query"), authorised)
        self.send_json(code, response)

    def log_message(self, *a):
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=18211)
    parser.add_argument("--safe", action="store_true")
    args = parser.parse_args()
    SAFE = args.safe
    mode = ("SAFE (introspection disabled, sensitive resolvers authorised)"
            if SAFE else
            "VULNERABLE (introspection enabled, sensitive resolvers ungated)")
    print(f"GraphQL lab [{mode}] on http://127.0.0.1:{args.port}/")
    print("  UI uses { me { name } }   |   POST queries to /graphql")
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
