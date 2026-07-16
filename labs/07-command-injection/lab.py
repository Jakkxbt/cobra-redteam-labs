#!/usr/bin/env python3
"""Local training target with vulnerable and safe command execution routes."""

import argparse
import subprocess
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def parameter(self) -> str:
        parts = urllib.parse.urlsplit(self.path)
        if self.command == "GET":
            values = urllib.parse.parse_qs(parts.query, keep_blank_values=True)
        else:
            length = int(self.headers.get("Content-Length", "0"))
            values = urllib.parse.parse_qs(
                self.rfile.read(length).decode("utf-8", "replace"),
                keep_blank_values=True)
        return values.get("input", [""])[0]

    def respond(self):
        path = urllib.parse.urlsplit(self.path).path
        value = self.parameter()
        if path == "/vulnerable":
            completed = subprocess.run(value, shell=True, capture_output=True,
                                       text=True, timeout=5)
            body = (completed.stdout + completed.stderr).encode()
            status = 200
        elif path == "/safe":
            completed = subprocess.run(["printf", "%s", value], shell=False,
                                       capture_output=True, text=True, timeout=5)
            body = completed.stdout.encode()
            status = 200
        else:
            body, status = b"not found", 404
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    do_GET = respond
    do_POST = respond

    def log_message(self, _format, *_args):
        return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=18180)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"command-injection lab: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
