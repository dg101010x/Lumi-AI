import argparse
import json
import os
import sys
import threading
import time
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
    webcam_stream = None

    def do_HEAD(self) -> None:
        if self.path in ("/", "/index.html"):
            body = HTML_PAGE.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return

        if self.path == "/healthz":
            body = json.dumps(self._health_payload()).encode("utf-8")
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
            self._send_json(self._health_payload())
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

    def _health_payload(self) -> dict:
        payload = {"ok": True}
        if self.webcam_stream is not None:
            payload["source_type"] = "webcam"
            payload["webcam_device"] = self.webcam_stream.device
            return payload

        payload["source_type"] = "url"
        payload["source_url"] = self.source_url
        return payload

    def _proxy_stream(self) -> None:
        if self.webcam_stream is not None:
            self._serve_webcam_stream()
            return

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

    def _serve_webcam_stream(self) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Pragma", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        try:
            while True:
                frame_bytes = self.webcam_stream.next_frame(timeout=5.0)
                if frame_bytes is None:
                    self.send_error(HTTPStatus.BAD_GATEWAY, "Webcam frame timeout")
                    return

                self.wfile.write(b"--frame\r\n")
                self.wfile.write(b"Content-Type: image/jpeg\r\n")
                self.wfile.write(f"Content-Length: {len(frame_bytes)}\r\n\r\n".encode("ascii"))
                self.wfile.write(frame_bytes)
                self.wfile.write(b"\r\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass


class WebcamStream:
    def __init__(
        self,
        device: str | int,
        width: int,
        height: int,
        fps: int,
        jpeg_quality: int,
    ) -> None:
        import cv2

        self.cv2 = cv2
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps
        self.jpeg_quality = jpeg_quality
        self._frame_lock = threading.Lock()
        self._latest_frame: bytes | None = None
        self._stopped = threading.Event()

        capture_target = int(device) if isinstance(device, str) and device.isdigit() else device
        cap = cv2.VideoCapture(capture_target)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open webcam device {device}")

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, fps)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap = cap

        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def _capture_loop(self) -> None:
        sleep_for = 1.0 / max(1, self.fps)
        encode_params = [self.cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality]

        while not self._stopped.is_set():
            ok, frame = self.cap.read()
            if not ok:
                time.sleep(0.05)
                continue

            ok, encoded = self.cv2.imencode(".jpg", frame, encode_params)
            if not ok:
                continue

            with self._frame_lock:
                self._latest_frame = encoded.tobytes()

            time.sleep(sleep_for)

    def next_frame(self, timeout: float) -> bytes | None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._frame_lock:
                if self._latest_frame is not None:
                    return self._latest_frame
            time.sleep(0.01)
        return None

    def close(self) -> None:
        self._stopped.set()
        self._thread.join(timeout=1.0)
        self.cap.release()


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
    parser.add_argument(
        "--webcam-device",
        default=os.getenv("WEBCAM_DEVICE", "-1"),
        help="Use a local webcam device index or /dev/video path instead of proxying a URL",
    )
    args = parser.parse_args()

    webcam_stream = None
    if args.webcam_device != "-1":
        webcam_stream = WebcamStream(
            device=args.webcam_device,
            width=int(os.getenv("WEBCAM_WIDTH", "640")),
            height=int(os.getenv("WEBCAM_HEIGHT", "480")),
            fps=int(os.getenv("WEBCAM_FPS", "15")),
            jpeg_quality=int(os.getenv("WEBCAM_JPEG_QUALITY", "70")),
        )
        PreviewServer.webcam_stream = webcam_stream
        print(f"Using webcam device: {args.webcam_device}")
    else:
        source_url = resolve_source_url(args)
        if not source_url:
            print("Could not find a Limelight stream. Pass --url/--host or set WEBCAM_DEVICE.")
            return 1
        PreviewServer.source_url = source_url

    server = ThreadingHTTPServer((args.bind, args.port), PreviewServer)

    print(f"Preview page: http://127.0.0.1:{args.port}/")
    print(f"Preview stream: http://127.0.0.1:{args.port}/stream.mjpg")
    if webcam_stream is not None:
        print("Upstream source: webcam")
    else:
        print(f"Upstream source: {PreviewServer.source_url}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if webcam_stream is not None:
            webcam_stream.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
