from __future__ import annotations

import argparse
import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import face_recognition
import requests
from flask import Flask, Response, jsonify

from face_matching import choose_best_match, distance_for_metric
from supabase_known_faces import SupabaseKnownFacesCache


DEFAULT_PROJECT_URL = "https://gmmpltgvtonpnrfckrvy.supabase.co"

app = Flask(__name__)
state_lock = threading.Lock()
latest_jpeg: bytes | None = None
latest_status: dict[str, Any] = {"ok": False, "message": "not started"}
recent_faces: list[dict[str, Any]] = []


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def draw_label(frame, text: str, left: int, top: int, color: tuple[int, int, int]) -> None:
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.6
    thickness = 2
    (tw, th), baseline = cv2.getTextSize(text, font, scale, thickness)
    box_top = max(0, top - th - baseline - 8)
    box_bottom = max(top, th + baseline + 8)
    box_right = left + tw + 14
    cv2.rectangle(frame, (left, box_top), (box_right, box_bottom), (0, 0, 0), -1)
    cv2.putText(frame, text, (left + 7, box_bottom - baseline - 3), font, scale, color, thickness)


def save_detection_with_paths(output_dir: Path, frame, payload: dict[str, Any]) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = utc_stamp()
    image_path = output_dir / f"{stamp}.jpg"
    json_path = output_dir / f"{stamp}.json"
    cv2.imwrite(str(image_path), frame)
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return image_path, json_path


def set_latest_jpeg(frame, quality: int = 80) -> None:
    global latest_jpeg
    ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        return
    with state_lock:
        latest_jpeg = encoded.tobytes()


def set_status(payload: dict[str, Any]) -> None:
    global latest_status
    with state_lock:
        latest_status = payload


def get_status() -> dict[str, Any]:
    with state_lock:
        return dict(latest_status)


def prune_recent_faces(now_ts: float, recent_seconds: float) -> None:
    global recent_faces
    recent_faces = [item for item in recent_faces if (now_ts - float(item["seen_at"])) <= recent_seconds]


def check_recent_face(
    embedding: list[float],
    *,
    metric: str,
    now_ts: float,
    recent_seconds: float,
    recent_distance_threshold: float,
) -> dict[str, Any] | None:
    prune_recent_faces(now_ts, recent_seconds)
    for item in recent_faces:
        try:
            distance = distance_for_metric(embedding, item["embedding"], metric)
        except ValueError:
            continue
        if distance <= recent_distance_threshold:
            return {
                "status": "recently_seen",
                "distance": float(distance),
                "display_name": item.get("display_name"),
            }
    return None


def mark_recent_face(embedding: list[float], display_name: str, now_ts: float) -> None:
    recent_faces.append(
        {
            "embedding": embedding,
            "display_name": display_name,
            "seen_at": now_ts,
        }
    )


def try_create_unknown_face(
    cache: SupabaseKnownFacesCache,
    *,
    encoding: list[float],
    photo_url: str,
    image_name: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    stamp = utc_stamp()
    try:
        image_row = cache.insert_image_record(
            image_name=image_name,
            image_url=photo_url,
        )
        row = cache.insert_known_face(
            embedding=encoding,
            person_name=f"Unknown {stamp}",
            label="auto-created",
            photo_url=image_row.get("image_url", photo_url),
            last_seen_at=datetime.now(timezone.utc).isoformat(),
        )
        row["image_id"] = image_row.get("id")
        return row, None
    except requests.RequestException as exc:
        response = exc.response
        body = response.text if response is not None else ""
        return None, {
            "type": "supabase_insert_failed",
            "message": str(exc),
            "response_text": body[:500],
        }
    except Exception as exc:
        return None, {
            "type": "unexpected_insert_failure",
            "message": str(exc),
        }


def webcam_loop(args: argparse.Namespace) -> None:
    device = int(args.device) if str(args.device).isdigit() else args.device
    cap = cv2.VideoCapture(device)
    if not cap.isOpened():
        set_status({"ok": False, "message": f"Could not open camera device: {args.device}"})
        return

    cache = SupabaseKnownFacesCache(
        project_url=args.project_url,
        api_key=args.api_key,
        table_name=args.table_name,
        refresh_seconds=args.refresh_seconds,
    )
    output_dir = Path(args.save_dir)
    last_save_ts = 0.0

    try:
        known_faces = cache.get_faces(force=True)
        set_status(
            {
                "ok": True,
                "message": "running",
                "known_faces_count": len(known_faces),
                "metric": args.metric,
                "threshold": args.threshold,
                "output_dir": str(output_dir.resolve()),
            }
        )

        while True:
            ok, frame = cap.read()
            if not ok:
                set_status({"ok": False, "message": "camera read failed"})
                time.sleep(0.25)
                continue

            known_faces = cache.get_faces()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model="hog")
            encodings = face_recognition.face_encodings(rgb, boxes)
            annotated = frame.copy()
            detections: list[dict[str, Any]] = []

            for (top, right, bottom, left), encoding in zip(boxes, encodings):
                encoding_list = encoding.tolist()
                now_ts = datetime.now(timezone.utc).timestamp()
                recent = check_recent_face(
                    encoding_list,
                    metric=args.metric,
                    now_ts=now_ts,
                    recent_seconds=args.recent_seconds,
                    recent_distance_threshold=args.recent_distance,
                )
                if recent is not None:
                    text = f"recent {recent['distance']:.3f}"
                    color = (255, 165, 0)
                    status = "recently_seen"
                    match_payload = {
                        "display_name": recent.get("display_name"),
                    }
                    cv2.rectangle(annotated, (left, top), (right, bottom), color, 2)
                    draw_label(annotated, text, left, top, color)
                    detections.append(
                        {
                            "box": {"top": top, "right": right, "bottom": bottom, "left": left},
                            "status": status,
                            "distance": recent["distance"],
                            "metric": args.metric,
                            "threshold": args.threshold,
                            "embedding": encoding_list,
                            "match": match_payload,
                        }
                    )
                    continue

                best = choose_best_match(
                    encoding_list,
                    known_faces,
                    threshold=args.threshold,
                    metric=args.metric,
                )

                if best and best["matched"]:
                    person = best["person"]
                    mark_recent_face(encoding_list, person.get("display_name") or "matched", now_ts)
                    text = f"{person.get('display_name') or 'matched'} {best['distance']:.3f}"
                    color = (0, 255, 0)
                    status = "matched"
                    match_payload = {
                        "id": person.get("id"),
                        "display_name": person.get("display_name"),
                        "person_name": person.get("person_name"),
                        "label": person.get("label"),
                        "photo_url": person.get("photo_url"),
                    }
                else:
                    distance = best["distance"] if best else None
                    text = f"unknown {distance:.3f}" if distance is not None else "unknown"
                    color = (0, 0, 255)
                    status = "unknown"
                    match_payload = None

                cv2.rectangle(annotated, (left, top), (right, bottom), color, 2)
                draw_label(annotated, text, left, top, color)
                detections.append(
                    {
                        "box": {"top": top, "right": right, "bottom": bottom, "left": left},
                        "status": status,
                        "distance": best["distance"] if best else None,
                        "metric": args.metric,
                        "threshold": args.threshold,
                        "embedding": encoding_list,
                        "match": match_payload,
                    }
                )

            payload = {
                "ok": True,
                "message": "running",
                "captured_at": utc_stamp(),
                "known_faces_count": len(known_faces),
                "detections": detections,
                "metric": args.metric,
                "threshold": args.threshold,
            }
            set_status(payload)

            if detections and (time.time() - last_save_ts) >= args.save_cooldown:
                image_path, json_path = save_detection_with_paths(output_dir, annotated, payload)
                image_url = image_path.resolve().as_uri()
                for detection in detections:
                    if detection.get("status") != "unknown":
                        continue
                    detection_embedding = detection.get("embedding")
                    if not isinstance(detection_embedding, list) or not detection_embedding:
                        continue
                    created_row, create_error = try_create_unknown_face(
                        cache,
                        encoding=detection_embedding,
                        photo_url=image_url,
                        image_name=image_path.stem,
                    )
                    if created_row is not None:
                        mark_recent_face(
                            detection_embedding,
                            created_row.get("display_name") or created_row.get("person_name") or "created",
                            datetime.now(timezone.utc).timestamp(),
                        )
                        detection["status"] = "created"
                        detection["match"] = {
                            "id": created_row.get("id"),
                            "display_name": created_row.get("display_name"),
                            "person_name": created_row.get("person_name"),
                            "label": created_row.get("label"),
                            "photo_url": created_row.get("photo_url"),
                            "image_id": created_row.get("image_id"),
                        }
                    elif create_error is not None:
                        detection["match"] = {"create_error": create_error}
                    detection.pop("embedding", None)

                for detection in detections:
                    detection.pop("embedding", None)
                json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
                last_save_ts = time.time()
            else:
                for detection in detections:
                    detection.pop("embedding", None)

            set_latest_jpeg(annotated, args.jpeg_quality)
            time.sleep(max(0.0, 1.0 / max(args.fps, 0.1)))
    finally:
        cap.release()


@app.get("/")
def index() -> str:
    return """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Aegis Live View</title>
    <style>
      body { font-family: system-ui, sans-serif; background:#0d1117; color:#e6edf3; margin:0; padding:24px; }
      .wrap { max-width: 1100px; margin: 0 auto; }
      img { width:100%; border-radius:16px; background:#000; display:block; }
      .card { background:#161b22; padding:16px; border-radius:20px; border:1px solid rgba(255,255,255,0.08); }
      code { color:#7ee787; }
    </style>
  </head>
  <body>
    <main class="wrap">
      <div class="card">
        <h1>Aegis Live View</h1>
        <img src="/stream.mjpg" alt="Live webcam stream">
        <p>Health: <code>/healthz</code></p>
      </div>
    </main>
  </body>
</html>"""


@app.get("/healthz")
def healthz():
    return jsonify(get_status())


@app.get("/stream.mjpg")
def stream():
    def generate():
        boundary = b"--frame\r\n"
        while True:
            with state_lock:
                frame = latest_jpeg
            if frame is None:
                time.sleep(0.1)
                continue
            yield boundary
            yield b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            time.sleep(0.1)

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run local webcam matching against Supabase and expose a live MJPEG preview."
    )
    parser.add_argument("--device", default="0", help="OpenCV camera index. Default: 0")
    parser.add_argument("--project-url", default=DEFAULT_PROJECT_URL, help="Supabase project URL")
    parser.add_argument("--api-key", required=True, help="Supabase service or publishable key")
    parser.add_argument("--table-name", default="known_faces", help="Supabase known faces table")
    parser.add_argument("--metric", choices=("euclidean", "cosine"), default="euclidean")
    parser.add_argument("--threshold", type=float, default=0.6)
    parser.add_argument("--refresh-seconds", type=int, default=60)
    parser.add_argument("--save-dir", default="received_faces_local")
    parser.add_argument("--save-cooldown", type=float, default=10.0)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--fps", type=float, default=5.0)
    parser.add_argument("--jpeg-quality", type=int, default=75)
    parser.add_argument("--recent-distance", type=float, default=0.25)
    parser.add_argument("--recent-seconds", type=float, default=45.0)
    args = parser.parse_args()

    worker = threading.Thread(target=webcam_loop, args=(args,), daemon=True)
    worker.start()

    print(f"[INFO] Live view: http://127.0.0.1:{args.port}/")
    print(f"[INFO] Stream: http://127.0.0.1:{args.port}/stream.mjpg")
    print(f"[INFO] Health: http://127.0.0.1:{args.port}/healthz")
    app.run(host=args.host, port=args.port, debug=False, threaded=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
