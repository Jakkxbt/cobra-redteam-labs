#!/usr/bin/env python3
"""
JWT authentication bypass lab.

A small API that hands you a signed token when you log in, and gates an admin
page behind that token. The VULNERABLE version trusts the token too much: it
honours the "none" algorithm (a token with no signature at all) and it signs
with a laughably weak secret. Either mistake lets you mint your own admin token.
Run with --safe to see the fixed verifier that closes both holes.

No third-party libraries — JWT is built by hand from stdlib so you can see every
byte. Local lab only — do not deploy publicly.

  python3 lab.py            # vulnerable, http://127.0.0.1:18208/
  python3 lab.py --safe     # fixed
"""
import argparse
import base64
import hashlib
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

SAFE = False

# The vulnerable server signs with this. It is a common dictionary word on
# purpose — a real attacker cracks it offline in seconds (hashcat -m 16500).
WEAK_SECRET = b"secret"
# The safe server uses a long random secret generated fresh at startup.
STRONG_SECRET = os.urandom(32)


def b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def sign(header_b64: str, payload_b64: str, secret: bytes) -> str:
    msg = f"{header_b64}.{payload_b64}".encode()
    return b64url(hmac.new(secret, msg, hashlib.sha256).digest())


def make_token(payload: dict, secret: bytes, alg: str = "HS256") -> str:
    h = b64url(json.dumps({"alg": alg, "typ": "JWT"}).encode())
    p = b64url(json.dumps(payload).encode())
    if alg == "none":
        return f"{h}.{p}."
    return f"{h}.{p}.{sign(h, p, secret)}"


def verify_vulnerable(token: str):
    """Trusts the header's alg field and uses the weak secret. Broken on purpose."""
    try:
        h_b64, p_b64, sig = token.split(".")
        header = json.loads(b64url_decode(h_b64))
        payload = json.loads(b64url_decode(p_b64))
    except Exception:
        return None
    alg = header.get("alg", "")
    if alg == "none":
        # BUG #1: "none" means "no signature", and we happily accept it.
        return payload
    if alg == "HS256":
        expected = sign(h_b64, p_b64, WEAK_SECRET)  # BUG #2: guessable secret
        if hmac.compare_digest(expected, sig):
            return payload
    return None


def verify_safe(token: str):
    """Pins the algorithm to HS256, rejects 'none', uses a strong secret."""
    try:
        h_b64, p_b64, sig = token.split(".")
        header = json.loads(b64url_decode(h_b64))
        payload = json.loads(b64url_decode(p_b64))
    except Exception:
        return None
    if header.get("alg") != "HS256":          # FIX: allowlist the algorithm
        return None
    expected = sign(h_b64, p_b64, STRONG_SECRET)  # FIX: strong, secret secret
    if hmac.compare_digest(expected, sig):
        return payload
    return None


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _token(self):
        auth = self.headers.get("Authorization", "")
        return auth[7:] if auth.startswith("Bearer ") else ""

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._send(200, {
                "hint": "POST /login to get a token for 'alice' (role: user). "
                        "GET /admin with 'Authorization: Bearer <token>' — needs role: admin.",
            })
            return
        if path == "/admin":
            secret = STRONG_SECRET if SAFE else WEAK_SECRET
            payload = verify_safe(self._token()) if SAFE else verify_vulnerable(self._token())
            if not payload:
                self._send(401, {"error": "invalid or missing token"})
                return
            if payload.get("role") != "admin":
                self._send(403, {"error": f"forbidden — you are '{payload.get('role')}', not admin"})
                return
            self._send(200, {"secret": "FLAG{jwt_forged_admin}", "welcome": payload.get("user")})
            return
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if urlparse(self.path).path == "/login":
            secret = STRONG_SECRET if SAFE else WEAK_SECRET
            token = make_token({"user": "alice", "role": "user"}, secret)
            self._send(200, {"token": token, "note": "you are a normal user; /admin needs role admin"})
            return
        self._send(404, {"error": "not found"})

    def log_message(self, *a):
        return


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=18208)
    p.add_argument("--safe", action="store_true")
    args = p.parse_args()
    SAFE = args.safe
    mode = "SAFE (alg pinned, strong secret)" if SAFE else "VULNERABLE (accepts alg:none + weak secret)"
    print(f"JWT lab [{mode}] on http://127.0.0.1:{args.port}/")
    print("  POST /login -> token   |   GET /admin (Bearer token, role must be admin)")
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
