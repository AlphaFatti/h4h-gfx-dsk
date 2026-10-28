#!/usr/bin/env python3
"""
Hoops for Hope local graphics server.

Serves the HTML graphics package and provides:
    /api/playforapurpose

That endpoint fetches https://playforapurpose.org/ server-side so the OBS
browser source never has to fight browser CORS.

Bind is localhost-only: this server is not exposed to the venue LAN.
"""

from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

HOST = "127.0.0.1"
PORT = 8765
UPSTREAM = "https://playforapurpose.org/"


VERSIONED_HTML_RE = re.compile(r"_v(\d+)\.html$", re.IGNORECASE)


def find_latest_graphics_file(folder: str) -> str | None:
    """
    Find the highest-numbered HTML master in this folder.

    Examples accepted:
        hoops_for_hope_graphics_master_v13.html
        hoops_for_hope_graphics_master_v14.html
        anything_else_v27.html

    Files with extra text after the version number are intentionally ignored,
    so the clean *_v#.html naming convention always wins.
    """
    candidates = []

    for path in Path(folder).glob("*.html"):
        match = VERSIONED_HTML_RE.search(path.name)
        if match:
            candidates.append((int(match.group(1)), path.name))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


class H4HHandler(SimpleHTTPRequestHandler):
    server_version = "H4HGFX/1.0"

    def end_headers(self):
        # Do not cache the local GFX package during show development.
        if not self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            latest = find_latest_graphics_file(os.getcwd())
            if latest:
                self.send_response(302)
                self.send_header("Location", f"/{latest}")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return

        if parsed.path == "/api/playforapurpose":
            self.proxy_play_for_a_purpose()
            return

        if parsed.path == "/api/health":
            payload = b'{"ok":true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)
            return

        super().do_GET()

    def proxy_play_for_a_purpose(self):
        # Unique query string helps defeat intermediary/upstream caching.
        target = f"{UPSTREAM}?overlay_refresh={int(time.time() * 1000)}"

        req = Request(
            target,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/153.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            },
        )

        try:
            with urlopen(req, timeout=10) as response:
                body = response.read()

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.send_header("X-H4H-Data-Source", "playforapurpose.org")
            self.end_headers()
            self.wfile.write(body)

        except HTTPError as exc:
            self.send_error(502, f"Play For A Purpose returned HTTP {exc.code}")
        except URLError as exc:
            self.send_error(502, f"Could not reach Play For A Purpose: {exc.reason}")
        except Exception as exc:
            self.send_error(502, f"Live fundraiser fetch failed: {exc}")

    def log_message(self, fmt, *args):
        # Keep useful request logging without being too noisy.
        sys.stdout.write(
            f"[H4H] {self.address_string()} - {fmt % args}\n"
        )
        sys.stdout.flush()


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    httpd = ThreadingHTTPServer((HOST, PORT), H4HHandler)

    latest = find_latest_graphics_file(script_dir)

    print("")
    print("Hoops for Hope GFX server")
    print("=========================")
    print(f"Serving: {script_dir}")

    if latest:
        print(f"Latest:  {latest}")
        print(f"Program: http://{HOST}:{PORT}/{latest}")
        print(f"Dock:    http://{HOST}:{PORT}/{latest}#panel")
    else:
        print("Latest:  No *_v#.html graphics master found.")
        print(f"Program: http://{HOST}:{PORT}/")

    print(f"Root:    http://{HOST}:{PORT}/  (redirects to newest v#.html)")
    print(f"Health:  http://{HOST}:{PORT}/api/health")
    print("")
    print("Live fundraiser data is proxied directly from playforapurpose.org.")
    print("The newest clean *_v#.html file is selected automatically at startup.")
    print("Leave this window open while OBS is running.")
    print("Press Control-C to stop.")
    print("")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping H4H GFX server...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
