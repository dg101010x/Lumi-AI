from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2
import face_recognition
import requests

from face_matching import choose_best_match
from supabase_known_faces import SupabaseKnownFacesCache


DEFAULT_PROJECT_URL = "https://gmmpltgvtonpnrfckrvy.supabase.co"


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
    cv2.putText(
        frame,
        text,
        (left + 7, box_bottom - baseline - 3),
        font,
        scale,
        color,
        thickness,
    )


def save_detection(output_dir: Path, frame, payload: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = utc_stamp()
    image_path = output_dir / f"{stamp}.jpg"
    json_path = output_dir / f"{stamp}.json"
    cv2.imwrite(str(image_path), frame)
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def try_create_unknown_face(
    cache: SupabaseKnownFacesCache,
    *,
    encoding: list[float],
    photo_url: str,
) -> tuple[dict | None, dict | None]:
    stamp = utc_stamp()
    try:
        row = cache.insert_known_face(
            embedding=encoding,
            person_name=f"Unknown {stamp}",
            label="auto-created",
            photo_url=photo_url,
            last_seen_at=datetime.now(timezone.utc).isoformat(),
        )
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Use the local Windows webcam and match faces against Supabase known_faces."
    )
    parser.add_argument("--device", default="0", help="OpenCV camera index. Default: 0")
    parser.add_argument(
        "--project-url",
        default=DEFAULT_PROJECT_URL,
        help="Supabase project URL",
    )
    parser.add_argument(
        "--api-key",
        required=True,
        help="Supabase publishable key",
    )
    parser.add_argument(
        "--table-name",
        default="known_faces",
        help="Supabase table holding stored face embeddings",
    )
    parser.add_argument(
        "--metric",
        choices=("euclidean", "cosine"),
        default="euclidean",
        help="Distance metric for comparisons",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.6,
        help="Match threshold for the selected metric",
    )
    parser.add_argument(
        "--refresh-seconds",
        type=int,
        default=60,
        help="How often to refresh known faces from Supabase",
    )
    parser.add_argument(
        "--save-dir",
        default="received_faces_local",
        help="Directory to save annotated detections and JSON metadata",
    )
    parser.add_argument(
        "--save-cooldown",
        type=float,
        default=10.0,
        help="Minimum seconds between saved detections",
    )
    args = parser.parse_args()

    device = int(args.device) if str(args.device).isdigit() else args.device
    cap = cv2.VideoCapture(device)
    if not cap.isOpened():
        print(f"[ERROR] Could not open camera device: {args.device}")
        return 1

    cache = SupabaseKnownFacesCache(
        project_url=args.project_url,
        api_key=args.api_key,
        table_name=args.table_name,
        refresh_seconds=args.refresh_seconds,
    )
    known_faces = cache.get_faces(force=True)

    print(f"[INFO] Loaded {len(known_faces)} known faces from Supabase table {args.table_name}")
    print(f"[INFO] Metric: {args.metric}")
    print(f"[INFO] Threshold: {args.threshold}")
    print("[INFO] Press q to quit")

    output_dir = Path(args.save_dir)
    last_save_ts = 0.0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("[WARN] Camera read failed")
                time.sleep(0.25)
                continue

            known_faces = cache.get_faces()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model="hog")
            encodings = face_recognition.face_encodings(rgb, boxes)
            annotated = frame.copy()
            detections: list[dict] = []

            for (top, right, bottom, left), encoding in zip(boxes, encodings):
                best = choose_best_match(
                    encoding.tolist(),
                    known_faces,
                    threshold=args.threshold,
                    metric=args.metric,
                )

                if best and best["matched"]:
                    person = best["person"]
                    display_name = person.get("display_name") or "matched"
                    text = f"{display_name} {best['distance']:.3f}"
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

                    created_row, create_error = try_create_unknown_face(
                        cache,
                        encoding=encoding.tolist(),
                        photo_url="",
                    )
                    if created_row is not None:
                        text = f"created {created_row.get('display_name')}"
                        color = (255, 255, 0)
                        status = "created"
                        match_payload = {
                            "id": created_row.get("id"),
                            "display_name": created_row.get("display_name"),
                            "person_name": created_row.get("person_name"),
                            "label": created_row.get("label"),
                            "photo_url": created_row.get("photo_url"),
                        }
                        known_faces = cache.get_faces(force=True)
                    elif create_error is not None:
                        match_payload = {"create_error": create_error}

                cv2.rectangle(annotated, (left, top), (right, bottom), color, 2)
                draw_label(annotated, text, left, top, color)
                detections.append(
                    {
                        "box": {"top": top, "right": right, "bottom": bottom, "left": left},
                        "status": status,
                        "distance": best["distance"] if best else None,
                        "metric": args.metric,
                        "threshold": args.threshold,
                        "match": match_payload,
                    }
                )

            if detections and (time.time() - last_save_ts) >= args.save_cooldown:
                payload = {
                    "captured_at": utc_stamp(),
                    "known_faces_count": len(known_faces),
                    "detections": detections,
                }
                save_detection(output_dir, annotated, payload)
                last_save_ts = time.time()

            cv2.imshow("Aegis Windows Webcam Matcher", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
