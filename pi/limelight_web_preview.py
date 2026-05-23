import argparse
import json
import os
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

sys.path.insert(0, os.path.dirname(__file__))

from limelight_video_viewer import autodiscover_stream, candidate_stream_from_host


HTML_PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Limelight Preview</title>
    <style>
      :root {
        color-scheme: dark;
        --bg: #0d1117;
        --panel: #161b22;
        --text: #e6edf3;
        --accent: #2f81f7;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        background:
          radial-gradient(circle at top, rgba(47,129,247,0.22), transparent 30%),
          linear-gradient(180deg, #0d1117 0%, #05080d 100%);
        color: var(--text);
        font-family: ui-sans-serif, system-ui, sans-serif;
      }
      .shell {
        width: min(1100px, 94vw);
        padding: 24px;
      }
      .card {
        border: 1px solid rgba(255,255,255,0.08);
        background: var(--panel);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 18px 60px rgba(0,0,0,0.38);
      }
      .label {
        margin: 0 0 12px;
        font-size: 14px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #8b949e;
      }
      img {
        display: block;
        width: 100%;
        border-radius: 12px;
        background: #000;
      }
      code {
        color: #7ee787;
      }
    </style>
  </head>
  <body>
    <main class="shell">
      <section class="card">
        <p class="label">AegisAI Limelight Preview</p>
        <img src="/stream.mjpg" alt="Limelight live preview">
      </section>
      <p>Use <code>/stream.mjpg</code> from a webpage, React app, or WebView.</p>
    </main>
  </body>
</html>
"""


class PreviewServer(BaseHTTPRequestHandler):
    source_url = ""

    def do_HEAD(self) -> None:
        if self.path in ("/", "/index.html"):
            body = HTML_PAGE.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return

        if self.path == "/healthz":
            body = json.dumps({"ok": True, "source_url": self.source_url}).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            return

        if self.path == "/stream.mjpg":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Pragma", "no-cache")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            body = HTML_PAGE.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == "/healthz":
            self._send_json({"ok": True, "source_url": self.source_url})
            return

        if self.path == "/stream.mjpg":
            self._proxy_stream()
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _proxy_stream(self) -> None:
        try:
            upstream = requests.get(self.source_url, stream=True, timeout=(2, 10))
            upstream.raise_for_status()
        except requests.RequestException as exc:
            self.send_error(HTTPStatus.BAD_GATEWAY, f"Upstream stream error: {exc}")
            return

        self.send_response(HTTPStatus.OK)
        self.send_header(
            "Content-Type",
            upstream.headers.get(
                "Content-Type",
                "multipart/x-mixed-replace; boundary=frame",
            ),
        )
        self.send_header("Cache-Control", "no-store")
        self.send_header("Pragma", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        try:
            for chunk in upstream.iter_content(chunk_size=16 * 1024):
                if not chunk:
                    continue
                self.wfile.write(chunk)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            upstream.close()


def resolve_source_url(args: argparse.Namespace) -> str | None:
    source_url = args.source_url or os.getenv("LIMELIGHT_SOURCE_URL")
    if source_url:
        return source_url

    source_host = args.source_host or os.getenv("LIMELIGHT_SOURCE_HOST")
    if source_host:
        return candidate_stream_from_host(source_host)

    return autodiscover_stream()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Expose the Limelight feed on a local webpage and MJPEG endpoint."
    )
    parser.add_argument(
        "--bind",
        default=os.getenv("BIND", "0.0.0.0"),
        help="Bind address. Default: 0.0.0.0",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8080")),
        help="HTTP port. Default: $PORT or 8080",
    )
    parser.add_argument("--source-url", help="Full upstream Limelight stream URL")
    parser.add_argument("--source-host", help="Limelight host or IP to probe")
    args = parser.parse_args()

    source_url = resolve_source_url(args)
    if not source_url:
        print("Could not find a Limelight stream. Pass --source-url or --source-host.")
        return 1

    PreviewServer.source_url = source_url
    server = ThreadingHTTPServer((args.bind, args.port), PreviewServer)

    print(f"Preview page: http://127.0.0.1:{args.port}/")
    print(f"Preview stream: http://127.0.0.1:{args.port}/stream.mjpg")
    print(f"Upstream source: {source_url}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
