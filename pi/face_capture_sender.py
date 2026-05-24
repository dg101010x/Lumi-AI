from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone

import cv2
import face_recognition
import requests


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def jpg_bytes_for_frame(frame, quality: int) -> bytes:
    ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        raise RuntimeError("Failed to encode frame as JPEG")
    return encoded.tobytes()


def label_for_match(distance: float | None, threshold: float) -> str:
    if distance is None:
        return "unknown"
    if distance <= threshold:
        return f"match {distance:.3f}"
    return f"unknown {distance:.3f}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture webcam frames, compute face_recognition embeddings, and upload to a receiver."
    )
    parser.add_argument("--upload-url", required=True, help="Receiver upload URL, for example http://WINDOWS_IP:5000/upload")
    parser.add_argument("--device", default="0", help="OpenCV camera index or device path")
    parser.add_argument("--show", action="store_true", help="Show the local annotated preview")
    parser.add_argument("--fps", type=float, default=2.0, help="Upload rate limit. Default: 2 FPS")
    parser.add_argument("--jpeg-quality", type=int, default=80, help="JPEG quality for uploads")
    parser.add_argument(
        "--repeat-distance",
        type=float,
        default=0.45,
        help="Skip immediate repeats if face distance is below this value",
    )
    parser.add_argument(
        "--repeat-seconds",
        type=float,
        default=15.0,
        help="Skip immediate repeats if they happen within this many seconds",
    )
    args = parser.parse_args()

    device: int | str
    device = int(args.device) if str(args.device).isdigit() else args.device
    cap = cv2.VideoCapture(device)
    if not cap.isOpened():
        print(f"[ERROR] Could not open camera device: {args.device}")
        return 1

    last_embedding = None
    last_upload_ts = 0.0
    min_interval = 1.0 / max(args.fps, 0.1)

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("[WARN] Camera read failed")
                time.sleep(0.25)
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model="hog")
            encodings = face_recognition.face_encodings(rgb, boxes)

            annotated = frame.copy()
            best_distance = None

            for (top, right, bottom, left), encoding in zip(boxes, encodings):
                if last_embedding is not None:
                    best_distance = float(face_recognition.face_distance([last_embedding], encoding)[0])
                cv2.rectangle(annotated, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(
                    annotated,
                    label_for_match(best_distance, args.repeat_distance),
                    (left, max(20, top - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

            now = time.time()
            should_upload = bool(encodings) and (now - last_upload_ts) >= min_interval

            if should_upload and last_embedding is not None and best_distance is not None:
                if best_distance <= args.repeat_distance and (now - last_upload_ts) <= args.repeat_seconds:
                    should_upload = False

            if should_upload:
                payload = {
                    "frame_id": utc_stamp(),
                    "captured_at": utc_stamp(),
                    "boxes": [
                        {"top": top, "right": right, "bottom": bottom, "left": left}
                        for (top, right, bottom, left) in boxes
                    ],
                    "embeddings": [encoding.tolist() for encoding in encodings],
                }
                image_bytes = jpg_bytes_for_frame(annotated, args.jpeg_quality)
                try:
                    response = requests.post(
                        args.upload_url,
                        data={"metadata": json.dumps(payload)},
                        files={"image": ("frame.jpg", image_bytes, "image/jpeg")},
                        timeout=30,
                    )
                    print(f"[INFO] Upload status: {response.status_code} {response.text[:240]}")
                    response.raise_for_status()
                    last_upload_ts = now
                    last_embedding = encodings[0]
                except requests.RequestException as exc:
                    print(f"[ERROR] Upload failed: {exc}")

            if args.show:
                cv2.imshow("Face Capture Sender", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        cap.release()
        if args.show:
            cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
