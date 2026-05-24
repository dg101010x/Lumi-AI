from __future__ import annotations

import argparse
import base64
import json
from datetime import datetime, timezone

import cv2
import face_recognition
import requests


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture the first detected webcam face, encode it as base64, and send it to the face receiver."
    )
    parser.add_argument("--upload-url", default="http://127.0.0.1:5000/upload-base64")
    parser.add_argument("--device", default="0")
    parser.add_argument("--jpeg-quality", type=int, default=85)
    parser.add_argument("--max-frames", type=int, default=120)
    args = parser.parse_args()

    device: int | str = int(args.device) if str(args.device).isdigit() else args.device
    cap = cv2.VideoCapture(device)
    if not cap.isOpened():
        print(f"[ERROR] Could not open camera device: {args.device}")
        return 1

    try:
        for frame_index in range(args.max_frames):
            ok, frame = cap.read()
            if not ok:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model="hog")
            encodings = face_recognition.face_encodings(rgb, boxes)
            if not boxes or not encodings:
                continue

            top, right, bottom, left = boxes[0]
            face_crop = frame[top:bottom, left:right]
            if face_crop.size == 0:
                continue

            ok, encoded = cv2.imencode(".jpg", face_crop, [int(cv2.IMWRITE_JPEG_QUALITY), args.jpeg_quality])
            if not ok:
                print("[ERROR] Failed to encode face crop")
                return 1

            image_base64 = base64.b64encode(encoded.tobytes()).decode("ascii")
            payload = {
                "image_base64": image_base64,
                "metadata": {
                    "frame_id": f"first-face-{utc_stamp()}",
                    "captured_at": utc_stamp(),
                    "boxes": [
                        {"top": top, "right": right, "bottom": bottom, "left": left}
                    ],
                    "embeddings": [encodings[0].tolist()],
                },
            }

            response = requests.post(args.upload_url, json=payload, timeout=30)
            print(f"[INFO] frame_index={frame_index} status={response.status_code}")
            print(response.text[:2000])
            response.raise_for_status()
            return 0

        print("[ERROR] No face detected before max-frames limit")
        return 1
    finally:
        cap.release()


if __name__ == "__main__":
    raise SystemExit(main())
