import argparse
import json
import os
import time
from pathlib import Path

import cv2
import face_recognition
import requests


def parse_capture_device(value: str) -> str | int:
    return int(value) if value.isdigit() else value


def load_known_faces(known_dir: str | None) -> tuple[list[str], list]:
    if not known_dir:
        return [], []

    names: list[str] = []
    encodings: list = []
    for image_path in sorted(Path(known_dir).glob("*")):
        if not image_path.is_file():
            continue

        image = face_recognition.load_image_file(str(image_path))
        found = face_recognition.face_encodings(image)
        if not found:
            continue

        names.append(image_path.stem)
        encodings.append(found[0])

    return names, encodings


def annotate_frame(frame, boxes: list[tuple[int, int, int, int]], labels: list[str]):
    for (top, right, bottom, left), label in zip(boxes, labels):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 200, 0), 2)
        cv2.rectangle(frame, (left, bottom - 24), (right, bottom), (0, 200, 0), cv2.FILLED)
        cv2.putText(
            frame,
            label,
            (left + 6, bottom - 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )


def detect_faces(frame, known_names: list[str], known_encodings: list, tolerance: float):
    rgb_small = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb_small = cv2.resize(rgb_small, (0, 0), fx=0.25, fy=0.25)

    small_boxes = face_recognition.face_locations(rgb_small, model="hog")
    small_encodings = face_recognition.face_encodings(rgb_small, small_boxes)

    boxes: list[tuple[int, int, int, int]] = []
    labels: list[str] = []
    faces_payload: list[dict] = []

    for box, face_encoding in zip(small_boxes, small_encodings):
        top, right, bottom, left = box
        scaled_box = (top * 4, right * 4, bottom * 4, left * 4)
        label = "face"
        distance = None

        if known_encodings:
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_index = int(distances.argmin())
            distance = float(distances[best_index])
            matches = face_recognition.compare_faces(
                known_encodings,
                face_encoding,
                tolerance=tolerance,
            )
            if matches[best_index]:
                label = known_names[best_index]
            else:
                label = "unknown"

        boxes.append(scaled_box)
        labels.append(label)
        faces_payload.append(
            {
                "label": label,
                "top": scaled_box[0],
                "right": scaled_box[1],
                "bottom": scaled_box[2],
                "left": scaled_box[3],
                "distance": distance,
            }
        )

    return boxes, labels, faces_payload


def upload_frame(
    upload_url: str,
    frame,
    faces_payload: list[dict],
    jpeg_quality: int,
    source_device: str,
) -> None:
    ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
    if not ok:
        raise RuntimeError("Could not JPEG-encode frame")

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    files = {
        "image": (f"capture-{timestamp}.jpg", encoded.tobytes(), "image/jpeg"),
    }
    data = {
        "timestamp": timestamp,
        "device": source_device,
        "faces": json.dumps(faces_payload),
    }

    response = requests.post(upload_url, files=files, data=data, timeout=10)
    response.raise_for_status()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect faces from a local webcam and send matching frames to a Windows PC."
    )
    parser.add_argument("--upload-url", required=True, help="Receiver URL, e.g. http://<pc-ip>:5000/upload")
    parser.add_argument("--device", default=os.getenv("WEBCAM_DEVICE", "/dev/video1"))
    parser.add_argument("--known-dir", help="Optional folder of known face images named by person")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--fps", type=int, default=10)
    parser.add_argument("--sample-every", type=int, default=3)
    parser.add_argument("--jpeg-quality", type=int, default=70)
    parser.add_argument("--min-upload-interval", type=float, default=2.0)
    parser.add_argument("--tolerance", type=float, default=0.5)
    parser.add_argument("--show", action="store_true", help="Show a local preview window")
    args = parser.parse_args()

    known_names, known_encodings = load_known_faces(args.known_dir)
    capture_target = parse_capture_device(str(args.device))
    cap = cv2.VideoCapture(capture_target)
    if not cap.isOpened():
        raise SystemExit(f"Could not open webcam device {args.device}")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    cap.set(cv2.CAP_PROP_FPS, args.fps)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    last_upload = 0.0
    frame_index = 0

    print(f"Watching webcam {args.device} and uploading to {args.upload_url}", flush=True)
    if known_names:
        print(f"Loaded known faces: {', '.join(known_names)}", flush=True)

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Webcam read failed", flush=True)
                break

            frame_index += 1
            faces_payload: list[dict] = []
            boxes: list[tuple[int, int, int, int]] = []
            labels: list[str] = []

            if frame_index % max(1, args.sample_every) == 0:
                boxes, labels, faces_payload = detect_faces(
                    frame,
                    known_names,
                    known_encodings,
                    args.tolerance,
                )

                if faces_payload and time.time() - last_upload >= args.min_upload_interval:
                    annotate_frame(frame, boxes, labels)
                    upload_frame(
                        args.upload_url,
                        frame,
                        faces_payload,
                        args.jpeg_quality,
                        str(args.device),
                    )
                    print(f"Uploaded frame with {len(faces_payload)} face(s)", flush=True)
                    last_upload = time.time()

            if args.show:
                preview = frame.copy()
                if boxes:
                    annotate_frame(preview, boxes, labels)
                cv2.imshow("Face Capture Sender", preview)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        cap.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
