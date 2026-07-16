#!/usr/bin/env python3
"""
Intentionally vulnerable deserialization lab.

User-controlled base64 is passed to pickle.loads(). Local lab only.
"""
from __future__ import annotations

import argparse
import base64
import pickle
import sys

from flask import Flask, request

app = Flask(__name__)


def _decode_blob(raw: str) -> bytes:
    t = (raw or "").strip()
    pad = (-len(t)) % 4
    try:
        return base64.b64decode(t + ("=" * pad))
    except Exception:
        return base64.urlsafe_b64decode(t + ("=" * pad))


@app.route("/")
def index():
    data = request.args.get("data", "")
    if not data:
        return (
            "vuln pickle lab — pass ?data=<base64-pickle>\n",
            200,
            {"Content-Type": "text/plain; charset=utf-8"},
        )
    try:
        obj = pickle.loads(_decode_blob(data))
        # Reflect the result so marker payloads can prove execution
        return "result=%s\n" % (obj,), 200, {"Content-Type": "text/plain; charset=utf-8"}
    except Exception as e:
        return "error=%s\n" % e, 400, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/load", methods=["GET", "POST"])
def load():
    if request.method == "POST":
        data = request.form.get("data", "")
    else:
        data = request.args.get("data", "")
    if not data:
        return "missing data\n", 400, {"Content-Type": "text/plain; charset=utf-8"}
    try:
        obj = pickle.loads(_decode_blob(data))
        return "result=%s\n" % (obj,), 200, {"Content-Type": "text/plain; charset=utf-8"}
    except Exception as e:
        return "error=%s\n" % e, 400, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/cookie")
def cookie_path():
    raw = request.cookies.get("session", "")
    if not raw:
        return "missing session cookie\n", 400, {"Content-Type": "text/plain; charset=utf-8"}
    try:
        obj = pickle.loads(_decode_blob(raw))
        return "result=%s\n" % (obj,), 200, {"Content-Type": "text/plain; charset=utf-8"}
    except Exception as e:
        return "error=%s\n" % e, 400, {"Content-Type": "text/plain; charset=utf-8"}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Vulnerable pickle.loads lab")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=18865)
    args = p.parse_args(argv)
    sys.stderr.write(
        "vuln_app listening on http://%s:%d/  (pickle.loads via ?data=)\n"
        % (args.host, args.port)
    )
    app.run(host=args.host, port=args.port, threaded=True, use_reloader=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
