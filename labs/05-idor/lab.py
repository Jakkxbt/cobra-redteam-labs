#!/usr/bin/env python3
"""
IDOR / broken access control lab.

An order API where each order belongs to a user. The VULNERABLE version returns
any order to anyone who asks (no ownership check). Run with --safe to see the
fixed version that enforces ownership.

Local lab only — do not deploy publicly.

  python3 lab.py            # vulnerable
  python3 lab.py --safe     # fixed
"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

SAFE = False

# order_id -> record. You are "alice" (orders 1 & 2). Order 3 is bob's.
ORDERS = {
    "1": {"owner": "alice", "item": "Laptop",        "card_last4": "4242"},
    "2": {"owner": "alice", "item": "Headphones",    "card_last4": "4242"},
    "3": {"owner": "bob",   "item": "Diamond Ring",  "card_last4": "1337"},
}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        # "who you are" — a real app reads this from your session/token
        user = q.get("user", ["alice"])[0]
        if u.path == "/":
            self._send(200, {"hint": "GET /api/order/<id>?user=alice — you are alice (orders 1,2); order 3 is bob's"})
            return
        if u.path.startswith("/api/order/"):
            oid = u.path.rsplit("/", 1)[-1]
            order = ORDERS.get(oid)
            if not order:
                self._send(404, {"error": "not found"})
                return
            if SAFE and order["owner"] != user:
                # FIX: enforce ownership
                self._send(403, {"error": "forbidden — not your order"})
                return
            # VULNERABLE path: no ownership check
            self._send(200, {"order_id": oid, **order})
            return
        self._send(404, {"error": "not found"})

    def log_message(self, *a):
        return


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=18190)
    p.add_argument("--safe", action="store_true")
    args = p.parse_args()
    SAFE = args.safe
    mode = "SAFE (ownership enforced)" if SAFE else "VULNERABLE (no ownership check)"
    print(f"IDOR lab [{mode}] on http://127.0.0.1:{args.port}/  — GET /api/order/<id>?user=alice")
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
