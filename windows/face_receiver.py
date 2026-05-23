import argparse
import json
import os
import time
from pathlib import Path

from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename


def create_app(output_dir: Path) -> Flask:
    app = Flask(__name__)
    output_dir.mkdir(parents=True, exist_ok=True)

    @app.get("/")
    def index():
        files = sorted(output_dir.glob("*.jpg"), reverse=True)[:20]
        return jsonify(
            {
                "ok": True,
                "output_dir": str(output_dir),
                "recent_files": [file.name for file in files],
            }
        )

    @app.post("/upload")
    def upload():
        image = request.files.get("image")
        if image is None:
            return jsonify({"ok": False, "error": "missing image file"}), 400

        timestamp = request.form.get("timestamp") or time.strftime("%Y%m%d-%H%M%S")
        safe_name = secure_filename(image.filename or f"{timestamp}.jpg")
        image_path = output_dir / safe_name
        image.save(image_path)

        metadata = {
            "timestamp": timestamp,
            "device": request.form.get("device"),
            "faces": json.loads(request.form.get("faces", "[]")),
            "image_file": image_path.name,
        }
        metadata_path = image_path.with_suffix(".json")
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        return jsonify({"ok": True, "image_file": image_path.name, "metadata_file": metadata_path.name})

    return app


def main() -> int:
    parser = argparse.ArgumentParser(description="Receive uploaded face images from the Pi.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--output-dir", default="received_faces")
    args = parser.parse_args()

    app = create_app(Path(args.output_dir))
    app.run(host=args.host, port=args.port, debug=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
