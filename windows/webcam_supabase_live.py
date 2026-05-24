from __future__ import annotations

import argparse
import base64
import json
import socket
import subprocess
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


def discover_local_ipv4() -> str:
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, family=socket.AF_INET):
            address = info[4][0]
            if not address.startswith("127."):
                return address
    except OSError:
        pass
    return "127.0.0.1"


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


def jpg_bytes_for_frame(frame, quality: int = 85) -> bytes | None:
    ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        return None
    return encoded.tobytes()


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


def describe_face_with_gemini(face_crop_bgr, api_key: str) -> str | None:
    image_bytes = jpg_bytes_for_frame(face_crop_bgr, quality=80)
    if not image_bytes:
        return None

    prompt = (
        "Describe this person briefly for a naming prompt. "
        "Use one short sentence with visible features only, such as hair, glasses, clothing color, or position. "
        "Do not guess race, ethnicity, age, gender identity, health, or emotions."
    )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-1.5-flash:generateContent"
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": base64.b64encode(image_bytes).decode("ascii"),
                        }
                    },
                ]
            }
        ]
    }

    response = requests.post(url, params={"key": api_key}, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    body = response.json()
    candidates = body.get("candidates", [])
    if not candidates:
        return None
    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        text = part.get("text")
        if text:
            return text.strip()
    return None


def speak_windows_message(message: str) -> None:
    escaped = message.replace("'", "''")
    script = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.Speak('{escaped}')"
    )
    subprocess.Popen(
        ["powershell", "-NoProfile", "-Command", script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def try_create_unknown_face(
    cache: SupabaseKnownFacesCache,
    *,
    encoding: list[float],
    image_base64: str,
    image_name: str,
    description: str | None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    stamp = utc_stamp()
    try:
        image_row = cache.insert_image_base64(
            image_name=image_name,
            image_base64=image_base64,
        )
        label = "auto-created"
        if description:
            label = f"auto-created: {description[:120]}"
        row = cache.insert_known_face(
            embedding=encoding,
            person_name="unidentified",
            label=label,
            photo_url=image_row.get("image_url", image_base64),
            last_seen_at=datetime.now(timezone.utc).isoformat(),
        )
        row["image_id"] = image_row.get("id")
        row["description"] = description
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
    frame_index = 0
    latest_processed_detections: list[dict[str, Any]] = []

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

            frame_index += 1
            annotated = frame.copy()
            detections = latest_processed_detections

            if frame_index % args.process_every_n == 0:
                known_faces = cache.get_faces()
                small = cv2.resize(frame, (0, 0), fx=args.detect_scale, fy=args.detect_scale)
                rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
                boxes_small = face_recognition.face_locations(rgb_small, model="hog")
                encodings = face_recognition.face_encodings(rgb_small, boxes_small)
                detections = []

                for (top_s, right_s, bottom_s, left_s), encoding in zip(boxes_small, encodings):
                    scale = 1.0 / args.detect_scale
                    top = int(top_s * scale)
                    right = int(right_s * scale)
                    bottom = int(bottom_s * scale)
                    left = int(left_s * scale)
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
                        detections.append(
                            {
                                "box": {"top": top, "right": right, "bottom": bottom, "left": left},
                                "status": "recently_seen",
                                "distance": recent["distance"],
                                "metric": args.metric,
                                "threshold": args.threshold,
                                "embedding": encoding_list,
                                "match": {"display_name": recent.get("display_name")},
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
                        match_payload = {
                            "id": person.get("id"),
                            "display_name": person.get("display_name"),
                            "person_name": person.get("person_name"),
                            "label": person.get("label"),
                            "photo_url": person.get("photo_url"),
                        }
                        detections.append(
                            {
                                "box": {"top": top, "right": right, "bottom": bottom, "left": left},
                                "status": "matched",
                                "distance": best["distance"],
                                "metric": args.metric,
                                "threshold": args.threshold,
                                "embedding": encoding_list,
                                "match": match_payload,
                            }
                        )
                    else:
                        detections.append(
                            {
                                "box": {"top": top, "right": right, "bottom": bottom, "left": left},
                                "status": "unknown",
                                "distance": best["distance"] if best else None,
                                "metric": args.metric,
                                "threshold": args.threshold,
                                "embedding": encoding_list,
                                "match": None,
                            }
                        )

                latest_processed_detections = detections

            for detection in detections:
                box = detection["box"]
                top = int(box["top"])
                right = int(box["right"])
                bottom = int(box["bottom"])
                left = int(box["left"])
                status = detection["status"]
                distance = detection.get("distance")
                if status == "matched":
                    text = f"{detection['match'].get('display_name') or 'matched'} {distance:.3f}"
                    color = (0, 255, 0)
                elif status == "recently_seen":
                    text = f"recent {distance:.3f}"
                    color = (255, 165, 0)
                elif status == "created":
                    text = f"created {detection['match'].get('display_name') or 'new'}"
                    color = (255, 255, 0)
                else:
                    text = f"unknown {distance:.3f}" if distance is not None else "unknown"
                    color = (0, 0, 255)
                cv2.rectangle(annotated, (left, top), (right, bottom), color, 2)
                draw_label(annotated, text, left, top, color)

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
                for detection in detections:
                    status = detection.get("status")
                    detection_embedding = detection.get("embedding")
                    if not isinstance(detection_embedding, list) or not detection_embedding:
                        continue

                    # Prepare face crop base64 (clean, no prefix)
                    box = detection["box"]
                    face_crop = frame[
                        max(0, int(box["top"])):max(0, int(box["bottom"])),
                        max(0, int(box["left"])):max(0, int(box["right"])),
                    ]
                    if face_crop.size == 0:
                        continue
                    
                    crop_bytes = jpg_bytes_for_frame(face_crop, quality=85)
                    if not crop_bytes:
                        continue
                    face_base64 = base64.b64encode(crop_bytes).decode("ascii")

                    if status == "unknown":
                        created_row, create_error = try_create_unknown_face(
                            cache,
                            encoding=detection_embedding,
                            image_base64=face_base64,
                            image_name=image_path.stem,
                            description=None,
                        )
                        if created_row is not None:
                            description = None
                            if args.gemini_api_key:
                                try:
                                    description = describe_face_with_gemini(face_crop, args.gemini_api_key)
                                except requests.RequestException as exc:
                                    detection["gemini_error"] = str(exc)
                            if description:
                                speak_windows_message(
                                    f"After this message, say the name of the person who is {description}"
                                )
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
                                "description": description,
                            }
                        elif create_error is not None:
                            detection["match"] = {"create_error": create_error}
                    elif status == "matched":
                        # Replace the old image in public.images with the new face_base64
                        match_info = detection.get("match")
                        if match_info and match_info.get("photo_url"):
                            old_url = match_info["photo_url"]
                            img_rec = cache.find_image_by_url(image_url=old_url)
                            if img_rec:
                                try:
                                    cache.update_image_by_id(image_id=img_rec["id"], image_base64=face_base64)
                                except Exception as exc:
                                    detection["update_error"] = str(exc)

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
            time.sleep(0.03)

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.get("/images/<filename>")
def get_saved_image(filename: str):
    from flask import send_from_directory

    image_dir = Path(app.config["IMAGE_DIR"])
    return send_from_directory(image_dir, filename)


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
    parser.add_argument("--jpeg-quality", type=int, default=70)
    parser.add_argument("--recent-distance", type=float, default=0.25)
    parser.add_argument("--recent-seconds", type=float, default=45.0)
    parser.add_argument("--process-every-n", type=int, default=3)
    parser.add_argument("--detect-scale", type=float, default=0.25)
    parser.add_argument("--gemini-api-key", default="")
    parser.add_argument("--image-base-url", default="")
    args = parser.parse_args()

    app.config["IMAGE_DIR"] = str(Path(args.save_dir).resolve())
    if not args.image_base_url:
        args.image_base_url = f"http://{discover_local_ipv4()}:{args.port}"

    worker = threading.Thread(target=webcam_loop, args=(args,), daemon=True)
    worker.start()

    print(f"[INFO] Live view: http://127.0.0.1:{args.port}/")
    print(f"[INFO] Stream: http://127.0.0.1:{args.port}/stream.mjpg")
    print(f"[INFO] Health: http://127.0.0.1:{args.port}/healthz")
    app.run(host=args.host, port=args.port, debug=False, threaded=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
