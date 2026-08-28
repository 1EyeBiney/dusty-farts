#!/usr/bin/env python3
"""Local preview server for this static site: python tools/serve.py [port]

Plain `python -m http.server` is NOT enough here - it doesn't support HTTP
Range requests, which the <audio> element needs to seek inside an episode
file. Without Range support, play/pause and switching episodes look fine but
every seek-dependent control (10s/1min buttons, chapter jump, the chapter
list, the Jukebox) silently fails, because the browser can never fetch just
the bytes it needs. This server adds real Range support (206 Partial
Content, Accept-Ranges, Content-Range) plus no-cache headers, so a reload
always reflects whatever is currently on disk rather than a stale cached
copy of an earlier version of a script or page.

Default port 8000. Serves the directory this script's parent folder is in
(the site root), regardless of the working directory it's launched from.
"""
import http.server
import os
import re
import sys

RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")
SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RangeHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SITE_ROOT, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def send_head(self):
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().send_head()

        range_header = self.headers.get("Range")
        if not range_header:
            return super().send_head()

        file_size = os.path.getsize(path)
        m = RANGE_RE.match(range_header)
        if not m:
            self.send_error(416, "Invalid range")
            return None

        start_s, end_s = m.groups()
        if start_s == "":
            length = int(end_s)
            start = max(0, file_size - length)
            end = file_size - 1
        else:
            start = int(start_s)
            end = int(end_s) if end_s else file_size - 1
            end = min(end, file_size - 1)

        if start > end or start >= file_size:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{file_size}")
            self.end_headers()
            return None

        length = end - start + 1
        f = open(path, "rb")
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        f.seek(start)
        self._range_length = length
        return f

    def copyfile(self, source, outputfile):
        if hasattr(self, "_range_length"):
            remaining = self._range_length
            while remaining > 0:
                chunk = source.read(min(65536, remaining))
                if not chunk:
                    break
                outputfile.write(chunk)
                remaining -= len(chunk)
        else:
            super().copyfile(source, outputfile)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    http.server.test(HandlerClass=RangeHandler, port=port)
