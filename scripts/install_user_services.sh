#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIT_DIR="${HOME}/.config/systemd/user"
ENV_FILE="${HOME}/.config/aegis-preview.env"

mkdir -p "$UNIT_DIR"
install -m 0644 "$REPO_DIR/deploy/systemd/aegis-preview.service" "$UNIT_DIR/aegis-preview.service"
install -m 0644 "$REPO_DIR/deploy/systemd/aegis-localtunnel.service" "$UNIT_DIR/aegis-localtunnel.service"

SOURCE_URL=""

if [ -f "$ENV_FILE" ]; then
  SOURCE_URL="$(sed -n 's/^LIMELIGHT_SOURCE_URL=//p' "$ENV_FILE" | tail -n 1)"
fi

if [ -z "$SOURCE_URL" ]; then
  SOURCE_URL="$(curl -fsS http://127.0.0.1:8080/healthz 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("source_url",""))' 2>/dev/null || true)"
fi

if [ -z "$SOURCE_URL" ]; then
  SOURCE_URL="$(
    cd "$REPO_DIR"
    . .venv/bin/activate
    python - <<'PY'
import sys

sys.path.insert(0, "pi")
from limelight_video_viewer import candidate_stream_from_host

print(candidate_stream_from_host("limelight.local") or "")
PY
  )"
fi

if [ -z "$SOURCE_URL" ]; then
  printf 'Could not determine a Limelight source URL for the preview service.\n' >&2
  exit 1
fi

printf 'LIMELIGHT_SOURCE_URL=%s\n' "$SOURCE_URL" > "$ENV_FILE"

systemctl --user daemon-reload
systemctl --user enable --now aegis-preview.service aegis-localtunnel.service
