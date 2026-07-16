#!/usr/bin/env python3
"""
Intentionally weak file-upload lab.

Weaknesses (deliberate):
  - Trusts client Content-Type (image/* allowed through)
  - Extension check uses only the *last* suffix (foo.php.jpg → .jpg)
  - Case-sensitive denylist for '.php' only (misses .pHp / .phtml)
  - Serves uploads; php/phtml/php5 executed via PHP CLI (marker-safe lab)

Local training only — do not expose.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

from flask import Flask, Response, request, send_from_directory

app = Flask(__name__)

UPLOAD_DIR = Path(__file__).resolve().parent / "vuln_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

_EXEC_EXT = {".php", ".phtml", ".php5", ".php7", ".phar"}


def _last_ext(name: str) -> str:
    base = name.replace("\x00", "").rstrip(". ").split("/")[-1].split("\\")[-1]
    if "." not in base:
        return ""
    return "." + base.rsplit(".", 1)[-1].lower()


def _weak_allow(filename: str, content_type: str) -> tuple[bool, str]:
    """
    Weak filter:
      - allow if Content-Type starts with image/
      - allow if last extension is a common image type
      - deny only exact last-ext .php when Content-Type is not image/*
    """
    ctype = (content_type or "").lower().split(";")[0].strip()
    ext = _last_ext(filename)
    if ctype.startswith("image/"):
        return True, "ctype-image"
    if ext in (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"):
        return True, "image-ext"
    # case-sensitive check on original last segment — classic mistake
    raw = filename.replace("\x00", "").rstrip(" ")
    if raw.lower().endswith(".php") and raw.endswith(".php"):
        return False, "denied-php"
    # .pHp / .phtml etc. slip through
    return True, "weak-default-allow"


def _safe_store_name(filename: str) -> str:
    # Intentionally naive: keep basename, allow weird suffixes (the bug)
    name = filename.replace("\\", "/").split("/")[-1]
    name = name.replace("\x00", "")  # OS paths cannot embed NUL; still "trimmed"
    name = name.strip() or "upload.bin"
    # Prevent absolute escape outside upload dir for the lab process
    name = name.lstrip(".")
    if name.startswith("/"):
        name = name.lstrip("/")
    # collapse path traversal attempts into basename-ish
    name = name.replace("..", "_")
    return name[:180]


@app.route("/")
def index():
    return (
        "vuln upload lab\n"
        "POST /upload field=file\n"
        "GET  /uploads/<name>\n",
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if f is None:
        return "error=missing file field\n", 400, {"Content-Type": "text/plain"}
    filename = f.filename or "upload.bin"
    ctype = f.content_type or request.content_type or ""
    ok, reason = _weak_allow(filename, ctype)
    if not ok:
        return (
            "rejected=%s\n" % reason,
            403,
            {"Content-Type": "text/plain; charset=utf-8"},
        )
    stored = _safe_store_name(filename)
    # unique prefix to avoid collisions across techniques
    stored = "%s_%s" % (uuid.uuid4().hex[:8], stored)
    path = UPLOAD_DIR / stored
    data = f.read()
    path.write_bytes(data)
    url_path = "/uploads/%s" % stored
    return (
        "stored=%s\nurl=%s\nreason=%s\n" % (stored, url_path, reason),
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@app.route("/uploads/<path:name>")
def serve(name: str):
    # block path escape
    target = (UPLOAD_DIR / name).resolve()
    if not str(target).startswith(str(UPLOAD_DIR.resolve())):
        return "forbidden\n", 403
    if not target.is_file():
        return "not found\n", 404

    ext = _last_ext(name)
    # Also treat .php.jpg polyglots: if content looks like PHP, try execute
    raw = target.read_bytes()
    looks_php = b"<?php" in raw[:500] or b"<?=" in raw[:500]
    exec_like = ext in _EXEC_EXT or (
        looks_php and ext in (".jpg", ".jpeg", ".png", ".gif", "")
    )

    if exec_like:
        # Real PHP CLI execution (benign marker only in lab payloads)
        try:
            proc = subprocess.run(
                ["php", str(target)],
                capture_output=True,
                timeout=5,
                check=False,
            )
            out = proc.stdout or b""
            # If PHP ignored leading garbage (GIF89a), stdout may still hold marker
            if not out and proc.stderr:
                # fallback: strip non-php prefix and retry once
                m = re.search(br"<\?php", raw)
                if m:
                    tmp = target.with_suffix(target.suffix + ".clean.php")
                    tmp.write_bytes(raw[m.start() :])
                    proc = subprocess.run(
                        ["php", str(tmp)],
                        capture_output=True,
                        timeout=5,
                        check=False,
                    )
                    out = proc.stdout or b""
                    try:
                        tmp.unlink()
                    except Exception:
                        pass
            return Response(out, status=200, mimetype="text/plain")
        except FileNotFoundError:
            return "php-cli missing\n", 500
        except Exception as e:
            return "exec-error=%s\n" % e, 500

    return send_from_directory(str(UPLOAD_DIR), name)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Vulnerable upload lab")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=18965)
    args = p.parse_args(argv)
    # clean slate for reproducible proofs
    for old in UPLOAD_DIR.glob("*"):
        try:
            old.unlink()
        except Exception:
            pass
    sys.stderr.write(
        "vuln_app on http://%s:%d/upload  (weak filter, PHP exec)\n"
        % (args.host, args.port)
    )
    app.run(host=args.host, port=args.port, threaded=True, use_reloader=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
