#!/usr/bin/env python3
"""
Safe Jinja2 lab target — user input is data, not template source.

Uses autoescaped template with a named variable. Math payloads must not
evaluate; bare reflection of {{...}} may appear escaped or literal but
must never produce a computed product.
"""
from __future__ import annotations

import argparse
import sys

from flask import Flask, request
from jinja2 import Environment, select_autoescape
from markupsafe import escape

app = Flask(__name__)

_env = Environment(autoescape=select_autoescape(enabled_extensions=("html", "htm", "xml"), default_for_string=True))
_tmpl = _env.from_string("Hello {{ name }}")


@app.route("/")
def index():
    name = request.args.get("name", "world")
    # Safe: name is a variable binding, not template source
    return _tmpl.render(name=name), 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/escape")
def escape_path():
    name = request.args.get("name", "world")
    # Extra-safe path: no template engine at all
    body = "Hello %s" % escape(name)
    return body, 200, {"Content-Type": "text/html; charset=utf-8"}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Safe SSTI lab (autoescaped Jinja2)")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=18766)
    args = p.parse_args(argv)
    sys.stderr.write(
        "safe_app listening on http://%s:%d/  (safe ?name=)\n" % (args.host, args.port)
    )
    app.run(host=args.host, port=args.port, threaded=True, use_reloader=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
