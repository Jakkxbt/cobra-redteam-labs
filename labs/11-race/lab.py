#!/usr/bin/env python3
"""
Race-condition lab — one-time voucher redemption.

A shop endpoint lets you redeem a single-use voucher for store credit. The
VULNERABLE version checks "already used?" and then (later) marks it used and
grants credit as two separate steps, with a small sleep between them that
widens the race window. Fire many concurrent redemptions of the same code and
the voucher can be cashed more than once. Run with --safe to take a lock around
the whole check-and-set so exactly one redemption wins.

No third-party libraries. Local lab only — do not deploy publicly.

  python3 lab.py            # vulnerable, http://127.0.0.1:18212/
  python3 lab.py --safe     # fixed
"""
import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

SAFE = False

# One voucher, one intended redemption.
VOUCHER_CODE = "ONE-SHOT-50"
CREDIT_PER_REDEEM = 50
FLAG = "FLAG{race_condition_over_redeem}"

_lock = threading.Lock()
_state_lock = threading.Lock()  # only protects shared counters for bookkeeping
_used = False
_balance = 0
_success_count = 0


def reset_state():
    global _used, _balance, _success_count
    with _state_lock:
        _used = False
        _balance = 0
        _success_count = 0


def redeem_vulnerable(code: str):
    """
    BUG: 'already used?' check and 'mark used + grant credit' are NOT atomic.
    A short sleep widens the window so concurrent requests can all pass the
    check before any of them marks the voucher used.
    """
    global _used, _balance, _success_count
    if code != VOUCHER_CODE:
        return 400, {"error": "unknown voucher"}

    # --- check (no lock) ---
    if _used:
        return 409, {"error": "voucher already used", "balance": _balance}

    # Artificial delay: stands in for slow I/O / multi-step DB work that makes
    # the race easy to win with a concurrent burst.
    time.sleep(0.08)

    # --- update (still no lock) ---
    _used = True
    _balance += CREDIT_PER_REDEEM
    _success_count += 1
    out = {
        "ok": True,
        "credited": CREDIT_PER_REDEEM,
        "balance": _balance,
        "redeems": _success_count,
    }
    # Flag appears once the single-use voucher has been cashed more than once.
    if _balance > CREDIT_PER_REDEEM:
        out["flag"] = FLAG
    return 200, out


def redeem_safe(code: str):
    """FIX: one lock wraps check-and-set so only one concurrent redeemer wins."""
    global _used, _balance, _success_count
    if code != VOUCHER_CODE:
        return 400, {"error": "unknown voucher"}

    with _lock:
        if _used:
            return 409, {"error": "voucher already used", "balance": _balance}
        # Same slow step as vuln — but still inside the lock, so no interleaving.
        time.sleep(0.08)
        _used = True
        _balance += CREDIT_PER_REDEEM
        _success_count += 1
        out = {
            "ok": True,
            "credited": CREDIT_PER_REDEEM,
            "balance": _balance,
            "redeems": _success_count,
        }
        if _balance > CREDIT_PER_REDEEM:
            out["flag"] = FLAG
        return 200, out


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b"{}"
        try:
            return json.loads(raw.decode() or "{}")
        except Exception:
            return {}

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._send(200, {
                "hint": (
                    "One-time voucher %r is worth %d credit. "
                    "POST /redeem with {\"code\": %r}. "
                    "GET /balance shows your store credit. "
                    "A single-use voucher that can be cashed more than once is the prize."
                ) % (VOUCHER_CODE, CREDIT_PER_REDEEM, VOUCHER_CODE),
                "mode": "SAFE" if SAFE else "VULNERABLE",
            })
            return
        if path == "/balance":
            with _state_lock:
                bal, used, n = _balance, _used, _success_count
            self._send(200, {
                "balance": bal,
                "voucher_used": used,
                "successful_redeems": n,
                "credit_per_redeem": CREDIT_PER_REDEEM,
            })
            return
        self._send(404, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/redeem":
            body = self._read_json()
            code = str(body.get("code") or "")
            if SAFE:
                status, obj = redeem_safe(code)
            else:
                status, obj = redeem_vulnerable(code)
            self._send(status, obj)
            return
        if path == "/reset":
            # Convenience for re-running the lab without restarting the process.
            reset_state()
            self._send(200, {"ok": True, "note": "voucher and balance reset"})
            return
        self._send(404, {"error": "not found"})

    def log_message(self, *a):
        return


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=18212)
    p.add_argument("--safe", action="store_true")
    args = p.parse_args()
    SAFE = args.safe
    reset_state()
    mode = (
        "SAFE (atomic check-and-set under lock)"
        if SAFE
        else "VULNERABLE (non-atomic check then update)"
    )
    print(f"Race lab [{mode}] on http://127.0.0.1:{args.port}/")
    print(
        f"  voucher {VOUCHER_CODE!r} = {CREDIT_PER_REDEEM} credit once  |  "
        "POST /redeem  |  GET /balance"
    )
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
