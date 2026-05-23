#!/usr/bin/env bash
set -euo pipefail

PORT="${LOCALTUNNEL_PORT:-8080}"
STATE_DIR="${XDG_RUNTIME_DIR:-/tmp}/aegisai"
LOG_FILE="$STATE_DIR/localtunnel.log"
URL_FILE="$STATE_DIR/localtunnel-url.txt"

mkdir -p "$STATE_DIR"
: > "$LOG_FILE"
rm -f "$URL_FILE"

npx localtunnel --port "$PORT" 2>&1 | while IFS= read -r line; do
  printf '%s\n' "$line" | tee -a "$LOG_FILE"
  case "$line" in
    "your url is: "*)
      printf '%s\n' "${line#your url is: }" > "$URL_FILE"
      ;;
  esac
done
