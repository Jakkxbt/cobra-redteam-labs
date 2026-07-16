#!/usr/bin/env python3
"""Self-contained local SSRF training lab."""

import argparse
import json
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def retrieve(url: str) -> tuple[int, bytes]:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "ssrf-lab/1.0"})
        with urllib.request.urlopen(request, timeout=2) as response:
            return response.status, response.read(256_000)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(256_000)
    except Exception as exc:
        return 502, str(exc).encode()


class InternalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if urllib.parse.urlsplit(self.path).path == "/internal":
            body = b"LAB_INTERNAL_ONLY_SECRET: loopback administration service"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, _format, *_args):
        return


class AppHandler(BaseHTTPRequestHandler):
    def send_body(self, status: int, body: bytes):
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            # A scanner timeout can close the client side before retrieval ends.
            pass

    def do_GET(self):
        parts = urllib.parse.urlsplit(self.path)
        params = urllib.parse.parse_qs(parts.query)
        target = params.get("url", [""])[0]
        if parts.path == "/vulnerable":
            status, body = retrieve(target)
            self.send_body(status, body)
        elif parts.path == "/blind":
            retrieve(target)
            self.send_body(202, b"job accepted")
        elif parts.path == "/safe":
            parsed = urllib.parse.urlsplit(target)
            if parsed.scheme != "http" or parsed.hostname != "public.test":
                self.send_body(403, b"destination rejected by allow-list")
            else:
                self.send_body(200, b"allow-listed destination")
        elif parts.path == "/health":
            self.send_body(200, b"ok")
        else:
            self.send_body(404, b"not found")

    def log_message(self, _format, *_args):
        return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app-port", type=int, default=18080)
    parser.add_argument("--internal-port", type=int, default=18081)
    args = parser.parse_args()
    internal = ThreadingHTTPServer(("127.0.0.1", args.internal_port), InternalHandler)
    app = ThreadingHTTPServer(("127.0.0.1", args.app_port), AppHandler)
    threading.Thread(target=internal.serve_forever, daemon=True).start()
    print(json.dumps({"app": f"http://127.0.0.1:{args.app_port}",
                      "internal": f"http://127.0.0.1:{args.internal_port}/internal"}),
          flush=True)
    try:
        app.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        app.server_close()
        internal.shutdown()
        internal.server_close()


if __name__ == "__main__":
    main()
