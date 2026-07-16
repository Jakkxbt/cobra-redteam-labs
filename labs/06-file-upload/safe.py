#!/usr/bin/env python3
"""
Safe upload lab — extension allowlist + content re-encode + no execution.

- Only .jpg / .jpeg / .png / .gif (last extension, lowercased)
- Ignores client Content-Type for authorisation
- Stores under a random name with forced .img.bin extension
- Replaces body with a fixed placeholder (original bytes discarded)
- Serves as application/octet-stream only — never executed
"""
from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path

from flask import Flask, request, send_from_directory

app = Flask(__name__)

UPLOAD_DIR = Path(__file__).resolve().parent / "safe_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

_ALLOW = {".jpg", ".jpeg", ".png", ".gif"}
_PLACEHOLDER = (
    b"SAFE-UPLOAD-PLACEHOLDER\n"
    b"original content discarded; not executable\n"
)


def _last_ext(name: str) -> str:
    base = (name or "").replace("\x00", "").rstrip(". ").split("/")[-1]
    if "." not in base:
        return ""
    return "." + base.rsplit(".", 1)[-1].lower()


@app.route("/")
def index():
    return (
        "safe upload lab\nPOST /upload field=file\nGET /uploads/<name>\n",
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if f is None:
        return "error=missing file\n", 400, {"Content-Type": "text/plain"}
    filename = f.filename or ""
    ext = _last_ext(filename)
    if ext not in _ALLOW:
        return (
            "rejected=extension-allowlist\n",
            403,
            {"Content-Type": "text/plain; charset=utf-8"},
        )
    # Force neutral name + extension — no user-controlled suffix kept
    stored = "%s.img.bin" % uuid.uuid4().hex
    # Discard attacker body; re-encode to placeholder
    _ = f.read()
    (UPLOAD_DIR / stored).write_bytes(_PLACEHOLDER)
    url_path = "/uploads/%s" % stored
    return (
        "stored=%s\nurl=%s\n" % (stored, url_path),
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@app.route("/uploads/<path:name>")
def serve(name: str):
    target = (UPLOAD_DIR / name).resolve()
    if not str(target).startswith(str(UPLOAD_DIR.resolve())):
        return "forbidden\n", 403
    if not target.is_file():
        return "not found\n", 404
    # Never execute — static bytes only
    return send_from_directory(
        str(UPLOAD_DIR),
        name,
        mimetype="application/octet-stream",
    )


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Safe upload lab")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=18966)
    args = p.parse_args(argv)
    for old in UPLOAD_DIR.glob("*"):
        try:
            old.unlink()
        except Exception:
            pass
    sys.stderr.write(
        "safe_app on http://%s:%d/upload  (allowlist + re-encode, no exec)\n"
        % (args.host, args.port)
    )
    app.run(host=args.host, port=args.port, threaded=True, use_reloader=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
