from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

import requests


DEFAULT_TABLE_NAME = "known_faces"
DEFAULT_SELECT = "id,person_name,label,embedding,photo_url,created_at,last_seen_at"
DEFAULT_IMAGES_TABLE_NAME = "images"


def build_headers(api_key: str) -> dict[str, str]:
    return {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
    }


def build_write_headers(api_key: str) -> dict[str, str]:
    headers = build_headers(api_key)
    headers["Content-Type"] = "application/json"
    headers["Prefer"] = "return=representation"
    return headers


def display_name_for_face(face: dict[str, Any]) -> str:
    return (
        str(face.get("person_name") or "").strip()
        or str(face.get("label") or "").strip()
        or str(face.get("id") or "unknown")
    )


def normalize_embedding(raw: Any) -> list[float] | None:
    if isinstance(raw, list):
        try:
            values = [float(item) for item in raw]
        except (TypeError, ValueError):
            return None
        return values if values else None

    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return None
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return None
        if not isinstance(parsed, list):
            return None
        try:
            values = [float(item) for item in parsed]
        except (TypeError, ValueError):
            return None
        return values if values else None

    return None


@dataclass
class SupabaseKnownFacesCache:
    project_url: str
    api_key: str
    table_name: str = DEFAULT_TABLE_NAME
    refresh_seconds: int = 60
    timeout_seconds: int = 20
    _faces: list[dict[str, Any]] = field(default_factory=list)
    _last_refresh_ts: float = 0.0

    @property
    def rest_url(self) -> str:
        return f"{self.project_url.rstrip('/')}/rest/v1/{self.table_name}"

    def get_faces(self, *, force: bool = False) -> list[dict[str, Any]]:
        now = time.time()
        if force or not self._faces or (now - self._last_refresh_ts) >= self.refresh_seconds:
            self.refresh()
        return list(self._faces)

    def refresh(self) -> list[dict[str, Any]]:
        response = requests.get(
            self.rest_url,
            headers=build_headers(self.api_key),
            params={
                "select": DEFAULT_SELECT,
                "order": "id.asc",
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()

        raw_faces = response.json()
        normalized: list[dict[str, Any]] = []
        for item in raw_faces:
            embedding = normalize_embedding(item.get("embedding"))
            if not embedding:
                continue
            item = dict(item)
            item["embedding"] = embedding
            item["display_name"] = display_name_for_face(item)
            normalized.append(item)

        self._faces = normalized
        self._last_refresh_ts = time.time()
        return list(self._faces)

    def insert_known_face(
        self,
        *,
        embedding: list[float],
        person_name: str,
        label: str,
        photo_url: str = "",
        last_seen_at: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "embedding": embedding,
            "person_name": person_name,
            "label": label,
        }
        if photo_url:
            payload["photo_url"] = photo_url
        if last_seen_at:
            payload["last_seen_at"] = last_seen_at

        response = requests.post(
            self.rest_url,
            headers=build_write_headers(self.api_key),
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()

        rows = response.json()
        if not isinstance(rows, list) or not rows:
            raise RuntimeError("Supabase insert returned no row")

        row = dict(rows[0])
        row["display_name"] = display_name_for_face(row)
        self._faces.append(row)
        self._last_refresh_ts = time.time()
        return row

    def insert_image_record(
        self,
        *,
        image_name: str,
        image_url: str,
        table_name: str = DEFAULT_IMAGES_TABLE_NAME,
    ) -> dict[str, Any]:
        response = requests.post(
            f"{self.project_url.rstrip('/')}/rest/v1/{table_name}",
            headers=build_write_headers(self.api_key),
            json={
                "image_name": image_name,
                "image_url": image_url,
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list) or not rows:
            raise RuntimeError("Supabase image insert returned no row")
        return dict(rows[0])
