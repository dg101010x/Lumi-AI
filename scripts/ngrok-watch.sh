#!/usr/bin/env bash
set -euo pipefail

STATE_DIR="${XDG_RUNTIME_DIR:-/tmp}/aegisai"
LOG_FILE="$STATE_DIR/ngrok.log"
URL_FILE="$STATE_DIR/ngrok-url.txt"

mkdir -p "$STATE_DIR"
: > "$LOG_FILE"
rm -f "$URL_FILE"

~/.local/bin/ngrok http 8080 --inspect=false --log stdout 2>&1 | while IFS= read -r line; do
  printf '%s\n' "$line" | tee -a "$LOG_FILE"
done
