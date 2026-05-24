"""Create a tiny SVG image with a random color, base64-encode it, and insert into Supabase public.images.

Usage (PowerShell):
  $env:SUPABASE_PROJECT_URL='https://...'; $env:SUPABASE_PUBLISHABLE_KEY='sb_publishable_...'; \
  .\.venv\Scripts\python.exe scripts\send_random_image_to_supabase.py
"""
from __future__ import annotations

import base64
import json
import os
import random
import sys
from datetime import datetime

import requests


def make_random_svg() -> bytes:
    # Create a 64x64 SVG with a random background color
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    svg = f"""
<svg xmlns='http://www.w3.org/2000/svg' width='64' height='64'>
  <rect width='100%' height='100%' fill='rgb({r},{g},{b})' />
  <text x='50%' y='50%' font-size='12' text-anchor='middle' fill='white' dy='.35em'>R</text>
</svg>
"""
    return svg.strip().encode("utf-8")


def encode_to_base64_no_prefix(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def insert_image(project_url: str, api_key: str, image_name: str, image_b64: str) -> dict:
    url = f"{project_url.rstrip('/')}/rest/v1/images"
    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    payload = {"image_name": image_name, "image_url": image_b64}
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main() -> int:
    project_url = os.getenv("SUPABASE_PROJECT_URL")
    api_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")
    if not project_url or not api_key:
        print("Error: SUPABASE_PROJECT_URL and SUPABASE_PUBLISHABLE_KEY must be set in the environment.")
        return 2

    svg = make_random_svg()
    b64 = encode_to_base64_no_prefix(svg)
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    image_name = f"rand-svg-{stamp}"

    try:
        rows = insert_image(project_url, api_key, image_name, b64)
        print("Inserted image rows:")
        print(json.dumps(rows, indent=2))
        return 0
    except requests.RequestException as exc:
        print("Supabase request failed:", exc)
        if exc.response is not None:
            try:
                print(exc.response.status_code, exc.response.text)
            except Exception:
                pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
