from __future__ import annotations

import argparse
import base64
import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import face_recognition
from flask import Flask, jsonify, request
import requests

from face_matching import choose_best_match, distance_for_metric
from supabase_known_faces import SupabaseKnownFacesCache


DEFAULT_PROJECT_URL = "https://gmmpltgvtonpnrfckrvy.supabase.co"
DEFAULT_API_KEY_ENV = "SUPABASE_PUBLISHABLE_KEY"
DEFAULT_MATCH_METRIC = "euclidean"
DEFAULT_MATCH_THRESHOLD = 0.6

app = Flask(__name__)
cache: SupabaseKnownFacesCache | None = None
match_metric = DEFAULT_MATCH_METRIC
match_threshold = DEFAULT_MATCH_THRESHOLD
output_dir = Path("received_faces")
recent_faces: list[dict[str, Any]] = []
recent_distance_threshold = 0.25
recent_seconds = 45.0
camera_thread: threading.Thread | None = None
camera_stop_event = threading.Event()
camera_state_lock = threading.Lock()
camera_state: dict[str, Any] = {
    "running": False,
    "device": "0",
    "uploads_sent": 0,
    "last_error": "",
    "last_message": "camera not started",
    "last_upload_at": "",
    "last_detection_at": "",
    "last_result": None,
}


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def safe_json_loads(raw: str) -> dict[str, Any]:
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("metadata must decode to a JSON object")
    return payload


def safe_base64_image_to_bytes(raw: str) -> bytes:
    payload = raw.strip()
    if payload.startswith("data:"):
        comma = payload.find(",")
        if comma == -1:
            raise ValueError("invalid data URL")
        payload = payload[comma + 1 :]
    return base64.b64decode(payload, validate=True)


def update_camera_state(**changes: Any) -> dict[str, Any]:
    with camera_state_lock:
        camera_state.update(changes)
        return dict(camera_state)


def get_camera_state() -> dict[str, Any]:
    with camera_state_lock:
        return dict(camera_state)


def ensure_cache() -> SupabaseKnownFacesCache:
    if cache is None:
        raise RuntimeError("Supabase cache not configured")
    return cache


def prune_recent_faces(now_ts: float) -> None:
    global recent_faces
    recent_faces = [item for item in recent_faces if (now_ts - float(item["seen_at"])) <= recent_seconds]


def check_recent_face(embedding: list[float], now_ts: float) -> dict[str, Any] | None:
    prune_recent_faces(now_ts)
    for item in recent_faces:
        try:
            distance = distance_for_metric(embedding, item["embedding"], match_metric)
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


def process_incoming_image_bytes(
    image_bytes: bytes,
    metadata: dict[str, Any],
    *,
    transport: str,
    source: str,
) -> dict[str, Any]:
    known_faces = ensure_cache().get_faces()
    results = classify_embeddings(metadata, known_faces)

    stamp = utc_stamp()
    base_name = metadata.get("frame_id") or stamp
    if not isinstance(base_name, str):
        base_name = str(base_name)
    base_name = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in base_name)

    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = output_dir / f"{base_name}.jpg"
    json_path = output_dir / f"{base_name}.json"
    image_path.write_bytes(image_bytes)
    image_url = image_path.resolve().as_uri()

    created = create_new_faces_for_unknowns(
        metadata,
        results,
        ensure_cache(),
        image_url=image_url,
        image_name=base_name,
    )

    json_payload = {
        "received_at": stamp,
        "metadata": metadata,
        "matches": results,
        "transport": transport,
        "source": source,
        "created": created,
    }
    json_path.write_text(json.dumps(json_payload, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "saved_image": str(image_path),
        "saved_json": str(json_path),
        "matches": results,
        "created": created,
        "known_faces_count": len(known_faces),
        "transport": transport,
        "source": source,
    }


def process_base64_upload_payload(
    image_base64: str,
    metadata: dict[str, Any],
    *,
    source: str,
) -> dict[str, Any]:
    image_bytes = safe_base64_image_to_bytes(image_base64)
    return process_incoming_image_bytes(image_bytes, metadata, transport="base64", source=source)


def camera_loop(
    *,
    device: str,
    jpeg_quality: int,
    repeat_distance: float,
    repeat_seconds: float,
    poll_seconds: float,
) -> None:
    update_camera_state(
        running=True,
        device=device,
        last_error="",
        last_message="starting camera",
        last_result=None,
    )

    cap = cv2.VideoCapture(int(device) if str(device).isdigit() else device)
    if not cap.isOpened():
        update_camera_state(running=False, last_error=f"Could not open camera device: {device}", last_message="camera open failed")
        return

    last_uploaded_embedding = None
    last_uploaded_ts = 0.0

    try:
        update_camera_state(last_message="camera watching for faces")
        while not camera_stop_event.is_set():
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.1)
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model="hog")
            encodings = face_recognition.face_encodings(rgb, boxes)

            if not boxes or not encodings:
                time.sleep(poll_seconds)
                continue

            now = time.time()
            encoding = encodings[0]
            update_camera_state(last_detection_at=datetime.now(timezone.utc).isoformat(), last_message="face detected")

            if last_uploaded_embedding is not None:
                distance = float(face_recognition.face_distance([last_uploaded_embedding], encoding)[0])
                if distance <= repeat_distance and (now - last_uploaded_ts) <= repeat_seconds:
                    time.sleep(poll_seconds)
                    continue

            top, right, bottom, left = boxes[0]
            face_crop = frame[top:bottom, left:right]
            if face_crop.size == 0:
                time.sleep(poll_seconds)
                continue

            ok, encoded = cv2.imencode(".jpg", face_crop, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
            if not ok:
                update_camera_state(last_error="Failed to encode face crop", last_message="encode failed")
                time.sleep(poll_seconds)
                continue

            image_base64 = "data:image/jpeg;base64," + base64.b64encode(encoded.tobytes()).decode("ascii")
            metadata = {
                "frame_id": f"live-face-{utc_stamp()}",
                "captured_at": utc_stamp(),
                "boxes": [{"top": top, "right": right, "bottom": bottom, "left": left}],
                "embeddings": [encoding.tolist()],
            }

            try:
                result = process_base64_upload_payload(image_base64, metadata, source="local_camera")
                last_uploaded_embedding = encoding
                last_uploaded_ts = now
                state = get_camera_state()
                update_camera_state(
                    uploads_sent=int(state.get("uploads_sent", 0)) + 1,
                    last_upload_at=datetime.now(timezone.utc).isoformat(),
                    last_result=result,
                    last_message="face uploaded",
                    last_error="",
                )
            except Exception as exc:
                update_camera_state(last_error=str(exc), last_message="upload failed")

            time.sleep(poll_seconds)
    finally:
        cap.release()
        update_camera_state(running=False, last_message="camera stopped")


def start_camera_worker(
    *,
    device: str = "0",
    jpeg_quality: int = 85,
    repeat_distance: float = 0.45,
    repeat_seconds: float = 15.0,
    poll_seconds: float = 0.25,
) -> dict[str, Any]:
    global camera_thread

    if camera_thread is not None and camera_thread.is_alive():
        return get_camera_state()

    camera_stop_event.clear()
    camera_thread = threading.Thread(
        target=camera_loop,
        kwargs={
            "device": device,
            "jpeg_quality": jpeg_quality,
            "repeat_distance": repeat_distance,
            "repeat_seconds": repeat_seconds,
            "poll_seconds": poll_seconds,
        },
        daemon=True,
    )
    camera_thread.start()
    return update_camera_state(device=device, last_message="camera worker started")


def stop_camera_worker() -> dict[str, Any]:
    camera_stop_event.set()
    return update_camera_state(last_message="camera stop requested")


def classify_embeddings(metadata: dict[str, Any], known_faces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    embeddings = metadata.get("embeddings", [])
    boxes = metadata.get("boxes", [])
    results: list[dict[str, Any]] = []

    if not isinstance(embeddings, list):
        return results

    for index, embedding in enumerate(embeddings):
        if not isinstance(embedding, list) or not embedding:
            continue

        now_ts = datetime.now(timezone.utc).timestamp()
        recent = check_recent_face(embedding, now_ts)
        if recent is not None:
            results.append(
                {
                    "index": index,
                    "box": boxes[index] if isinstance(boxes, list) and index < len(boxes) else None,
                    "matched": False,
                    "metric": match_metric,
                    "threshold": match_threshold,
                    "status": "recently_seen",
                    "distance": recent["distance"],
                    "display_name": recent.get("display_name"),
                }
            )
            continue

        best = choose_best_match(
            embedding,
            known_faces,
            threshold=match_threshold,
            metric=match_metric,
        )

        result: dict[str, Any] = {
            "index": index,
            "box": boxes[index] if isinstance(boxes, list) and index < len(boxes) else None,
            "matched": False,
            "metric": match_metric,
            "threshold": match_threshold,
        }

        if best is None:
            result["status"] = "no_known_embeddings"
        else:
            result["distance"] = best["distance"]
            result["matched"] = best["matched"]
            if best["matched"]:
                person = best["person"]
                mark_recent_face(embedding, person.get("display_name") or "matched", now_ts)
                result["status"] = "matched"
                result["person"] = {
                    "id": person.get("id"),
                    "display_name": person.get("display_name"),
                    "person_name": person.get("person_name"),
                    "label": person.get("label"),
                    "photo_url": person.get("photo_url"),
                }
            else:
                result["status"] = "unknown"

        results.append(result)

    return results


def create_new_faces_for_unknowns(
    metadata: dict[str, Any],
    results: list[dict[str, Any]],
    known_faces_cache: SupabaseKnownFacesCache,
    image_url: str,
    image_name: str,
) -> list[dict[str, Any]]:
    embeddings = metadata.get("embeddings", [])
    created: list[dict[str, Any]] = []

    for result in results:
        if result.get("status") != "unknown":
            continue

        index = result.get("index")
        if not isinstance(index, int) or index >= len(embeddings):
            continue

        embedding = embeddings[index]
        if not isinstance(embedding, list) or not embedding:
            continue

        stamp = utc_stamp()
        try:
            image_row = known_faces_cache.insert_image_record(
                image_name=f"{image_name}-{index}",
                image_url=image_url,
            )
            row = known_faces_cache.insert_known_face(
                embedding=embedding,
                person_name=f"Unknown {stamp}",
                label="auto-created",
                photo_url=image_row.get("image_url", image_url),
                last_seen_at=datetime.now(timezone.utc).isoformat(),
            )
            mark_recent_face(embedding, row.get("person_name") or "created", datetime.now(timezone.utc).timestamp())
            result["status"] = "created"
            result["created_row"] = {
                "id": row.get("id"),
                "display_name": row.get("display_name"),
                "person_name": row.get("person_name"),
                "label": row.get("label"),
                "photo_url": row.get("photo_url"),
                "image_id": image_row.get("id"),
            }
            created.append(result["created_row"])
        except requests.RequestException as exc:
            response = exc.response
            body = response.text if response is not None else ""
            result["create_error"] = {
                "type": "supabase_insert_failed",
                "message": str(exc),
                "response_text": body[:500],
            }
        except Exception as exc:
            result["create_error"] = {
                "type": "unexpected_insert_failure",
                "message": str(exc),
            }

    return created


@app.get("/healthz")
def healthz():
    known_faces = ensure_cache().get_faces()
    return jsonify(
        {
            "ok": True,
            "known_faces_count": len(known_faces),
            "metric": match_metric,
            "threshold": match_threshold,
            "output_dir": str(output_dir.resolve()),
        }
    )


@app.get("/")
def index():
    known_faces = ensure_cache().get_faces()
    return (
        "<html><body style='font-family:Segoe UI,Arial,sans-serif;padding:24px'>"
        "<h1>Face Receiver Running</h1>"
        f"<p><strong>Known faces:</strong> {len(known_faces)}</p>"
        f"<p><strong>Metric:</strong> {match_metric}</p>"
        f"<p><strong>Threshold:</strong> {match_threshold}</p>"
        "<p><a href='/healthz'>/healthz</a></p>"
        "</body></html>"
    )


@app.post("/refresh")
def refresh():
    known_faces = ensure_cache().get_faces(force=True)
    return jsonify({"ok": True, "known_faces_count": len(known_faces)})


@app.post("/upload")
def upload():
    if "image" not in request.files:
        return jsonify({"ok": False, "error": "missing multipart file field 'image'"}), 400
    if "metadata" not in request.form:
        return jsonify({"ok": False, "error": "missing form field 'metadata'"}), 400

    try:
        metadata = safe_json_loads(request.form["metadata"])
    except (ValueError, json.JSONDecodeError) as exc:
        return jsonify({"ok": False, "error": f"invalid metadata: {exc}"}), 400

    image = request.files["image"]
    known_faces = ensure_cache().get_faces()
    results = classify_embeddings(metadata, known_faces)

    stamp = utc_stamp()
    base_name = metadata.get("frame_id") or stamp
    if not isinstance(base_name, str):
        base_name = str(base_name)
    base_name = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in base_name)

    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = output_dir / f"{base_name}.jpg"
    json_path = output_dir / f"{base_name}.json"

    image.save(image_path)
    image_url = image_path.resolve().as_uri()
    json_payload = {
        "received_at": stamp,
        "metadata": metadata,
        "matches": results,
    }
    json_path.write_text(json.dumps(json_payload, indent=2), encoding="utf-8")

    created = create_new_faces_for_unknowns(
        metadata,
        results,
        ensure_cache(),
        image_url=image_url,
        image_name=base_name,
    )

    return jsonify(
        {
            "ok": True,
            "saved_image": str(image_path),
            "saved_json": str(json_path),
            "matches": results,
            "created": created,
            "known_faces_count": len(known_faces),
        }
    )


@app.post("/upload-base64")
def upload_base64():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"ok": False, "error": "expected JSON body"}), 400

    image_base64 = body.get("image_base64")
    metadata = body.get("metadata")
    if not isinstance(image_base64, str) or not image_base64.strip():
        return jsonify({"ok": False, "error": "missing image_base64"}), 400
    if not isinstance(metadata, dict):
        return jsonify({"ok": False, "error": "missing metadata object"}), 400

    try:
        image_bytes = safe_base64_image_to_bytes(image_base64)
    except (ValueError, base64.binascii.Error) as exc:
        return jsonify({"ok": False, "error": f"invalid image_base64: {exc}"}), 400

    known_faces = ensure_cache().get_faces()
    results = classify_embeddings(metadata, known_faces)

    stamp = utc_stamp()
    base_name = metadata.get("frame_id") or stamp
    if not isinstance(base_name, str):
        base_name = str(base_name)
    base_name = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in base_name)

    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = output_dir / f"{base_name}.jpg"
    json_path = output_dir / f"{base_name}.json"
    image_path.write_bytes(image_bytes)
    image_url = image_path.resolve().as_uri()

    json_payload = {
        "received_at": stamp,
        "metadata": metadata,
        "matches": results,
        "transport": "base64",
    }
    json_path.write_text(json.dumps(json_payload, indent=2), encoding="utf-8")

    created = create_new_faces_for_unknowns(
        metadata,
        results,
        ensure_cache(),
        image_url=image_url,
        image_name=base_name,
    )

    return jsonify(
        {
            "ok": True,
            "saved_image": str(image_path),
            "saved_json": str(json_path),
            "matches": results,
            "created": created,
            "known_faces_count": len(known_faces),
        }
    )


def main() -> int:
    global cache
    global match_metric
    global match_threshold
    global output_dir

    parser = argparse.ArgumentParser(
        description="Receive face uploads from the Pi and match them against Supabase known_faces."
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind host. Default: 0.0.0.0")
    parser.add_argument("--port", type=int, default=5000, help="Bind port. Default: 5000")
    parser.add_argument(
        "--project-url",
        default=os.getenv("SUPABASE_PROJECT_URL", DEFAULT_PROJECT_URL),
        help="Supabase project URL",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv(DEFAULT_API_KEY_ENV, ""),
        help=f"Supabase publishable key. Defaults to ${DEFAULT_API_KEY_ENV}",
    )
    parser.add_argument(
        "--table-name",
        default=os.getenv("SUPABASE_KNOWN_FACES_TABLE", "known_faces"),
        help="Supabase table name for stored face embeddings",
    )
    parser.add_argument(
        "--refresh-seconds",
        type=int,
        default=int(os.getenv("SUPABASE_REFRESH_SECONDS", "60")),
        help="How often to refresh known faces from Supabase",
    )
    parser.add_argument(
        "--metric",
        choices=("euclidean", "cosine"),
        default=os.getenv("FACE_MATCH_METRIC", DEFAULT_MATCH_METRIC),
        help="Distance metric for embedding comparison",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=float(os.getenv("FACE_MATCH_THRESHOLD", str(DEFAULT_MATCH_THRESHOLD))),
        help="Match threshold for the selected metric",
    )
    parser.add_argument(
        "--output-dir",
        default=os.getenv("FACE_RECEIVER_OUTPUT_DIR", "received_faces"),
        help="Directory to store incoming images and JSON",
    )
    args = parser.parse_args()

    if not args.api_key:
        parser.error(f"--api-key is required or set {DEFAULT_API_KEY_ENV}")

    cache = SupabaseKnownFacesCache(
        project_url=args.project_url,
        api_key=args.api_key,
        table_name=args.table_name,
        refresh_seconds=args.refresh_seconds,
    )
    known_faces = cache.get_faces(force=True)

    match_metric = args.metric
    match_threshold = args.threshold
    output_dir = Path(args.output_dir)

    print(f"[INFO] Supabase table: {args.table_name}")
    print(f"[INFO] Known faces loaded: {len(known_faces)}")
    print(f"[INFO] Match metric: {match_metric}")
    print(f"[INFO] Match threshold: {match_threshold}")
    print(f"[INFO] Output dir: {output_dir.resolve()}")
    print(f"[INFO] Listening on http://{args.host}:{args.port}")

    app.run(host=args.host, port=args.port, debug=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
