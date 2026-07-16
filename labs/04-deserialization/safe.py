#!/usr/bin/env python3
"""
Safe lab target — never calls pickle.loads / deserialize.

Accepts the same ?data= shape but only echoes length / stores as opaque text.
"""
from __future__ import annotations

import argparse
import sys

from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def index():
    data = request.args.get("data", "")
    if not data:
        return (
            "safe lab — pass ?data=… (never deserialized)\n",
            200,
            {"Content-Type": "text/plain; charset=utf-8"},
        )
    # Opaque handling only — no pickle, no eval, no marshal
    return (
        "stored_len=%d\npreview=%s\n" % (len(data), data[:40]),
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@app.route("/load", methods=["GET", "POST"])
def load():
    if request.method == "POST":
        data = request.form.get("data", "")
    else:
        data = request.args.get("data", "")
    return (
        "stored_len=%d\n" % len(data or ""),
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Safe non-deserializing lab")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=18866)
    args = p.parse_args(argv)
    sys.stderr.write(
        "safe_app listening on http://%s:%d/  (no deserialization)\n"
        % (args.host, args.port)
    )
    app.run(host=args.host, port=args.port, threaded=True, use_reloader=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
