"""Live race console, zero dependencies, zero keys.

  python -m pitcrew.serve            # then open http://localhost:842

Serves ui/live.html and streams the mock race over Server-Sent Events. Each page
load runs a fresh race. This is the real UI driven by the real engine, so it is
the closest thing to the Friday demo you can run today. Swap the provider/sandbox
in run_race() for the live ones and this same page shows the real thing.
"""
from __future__ import annotations

import json
import os
import queue
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import fixtures
from .providers import MockPatchProvider
from .race import run_race
from .telemetry import NullTelemetry

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.normpath(os.path.join(HERE, "..", "widget-api"))
UI = os.path.normpath(os.path.join(HERE, "..", "ui", "live.html"))
PORT = 8420


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.startswith("/events"):
            self._events()
        else:
            self._page()

    def _page(self):
        with open(UI, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _events(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        q: "queue.Queue" = queue.Queue()
        fixture = fixtures.write_mini(os.path.join(tempfile.gettempdir(), "pitcrew_live.json"))

        def race():
            run_race(
                target_repo=TARGET, fixture=fixture,
                provider=MockPatchProvider(), n_bays=10,
                telemetry=NullTelemetry(), emit=q.put, max_workers=8,
            )
            q.put({"type": "done"})

        threading.Thread(target=race, daemon=True).start()

        while True:
            e = q.get()
            try:
                self.wfile.write(f"data: {json.dumps(e)}\n\n".encode())
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                return
            if e.get("type") == "done":
                return


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Pit Crew live console: http://localhost:{PORT}")
    print("each page load runs a fresh mock race. Ctrl+C to stop.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()
