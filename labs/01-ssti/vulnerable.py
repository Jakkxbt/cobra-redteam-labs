#!/usr/bin/env python3
"""
Intentionally vulnerable Jinja2 SSTI lab target.

User input is concatenated into a template and rendered with
jinja2.Environment.from_string / Flask render_template_string.
Local lab only — do not expose.
"""
from __future__ import annotations

import argparse
import os
import sys

from flask import Flask, request
from jinja2 import Environment

app = Flask(__name__)

# Explicit env so lipsum/cycler defaults exist for RCE-proof demos
_env = Environment(autoescape=False)


@app.route("/")
def index():
    name = request.args.get("name", "world")
    # Classic vulnerability: user input is the template source
    try:
        tmpl = _env.from_string("Hello " + name)
        return tmpl.render(), 200, {"Content-Type": "text/html; charset=utf-8"}
    except Exception as e:
        return "template error: %s" % e, 500


@app.route("/greet", methods=["GET", "POST"])
def greet():
    if request.method == "POST":
        name = request.form.get("name", "world")
    else:
        name = request.args.get("name", "world")
    try:
        tmpl = _env.from_string("Greetings, " + name + "!")
        return tmpl.render(), 200, {"Content-Type": "text/html; charset=utf-8"}
    except Exception as e:
        return "template error: %s" % e, 500


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Vulnerable SSTI lab (Jinja2)")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=18765)
    args = p.parse_args(argv)
    # Advertise marker path for optional file-read proofs
    marker = os.path.join(os.path.dirname(os.path.abspath(__file__)), "marker.txt")
    sys.stderr.write(
        "vuln_app listening on http://%s:%d/  (SSTI via ?name=)\n" % (args.host, args.port)
    )
    sys.stderr.write("marker file: %s\n" % marker)
    app.run(host=args.host, port=args.port, threaded=True, use_reloader=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
