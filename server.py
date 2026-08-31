"""
Duty roster backend.

Run this, then open http://localhost:8000 in a browser.

What it does:
  GET  /              -> sends the frontend (duty-roster.html)
  GET  /api/roster     -> reads roster-data.json and sends it back as the current data
  POST /api/roster     -> takes whatever JSON the frontend sends and overwrites
                          roster-data.json with it

That's the whole "backend": a file on disk (roster-data.json) plus two routes
for reading it and writing it. No database needed for something this size.
"""

import json
import http.server
import socketserver
from pathlib import Path

PORT = 8000
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "roster-data.json"
FRONTEND_FILE = BASE_DIR / "duty-roster.html"


class RosterHandler(http.server.BaseHTTPRequestHandler):

    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            html = FRONTEND_FILE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)

        elif self.path == "/api/roster":
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            self._send_json(data)

        else:
            self.send_error(404, "Not found")

    def do_POST(self):
        if self.path == "/api/roster":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                self._send_json({"error": "invalid JSON"}, status=400)
                return

            DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            self._send_json({"status": "saved"})
        else:
            self.send_error(404, "Not found")

    # Quieter server log lines
    def log_message(self, fmt, *args):
        print("[server]", fmt % args)


if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), RosterHandler) as httpd:
        print(f"Duty roster running at http://localhost:{PORT}")
        print(f"Reading and saving data at {DATA_FILE}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
