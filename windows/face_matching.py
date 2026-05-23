from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np


def as_float_vector(values: Iterable[float]) -> np.ndarray:
    return np.asarray(list(values), dtype=np.float32)


def normalize_vector(values: Iterable[float]) -> np.ndarray:
    array = as_float_vector(values)
    norm = np.linalg.norm(array)
    if norm == 0:
        return array
    return array / norm


def cosine_distance(vector_a: Iterable[float], vector_b: Iterable[float]) -> float:
    a = normalize_vector(vector_a)
    b = normalize_vector(vector_b)
    if a.shape != b.shape:
        raise ValueError("Vector shape mismatch for cosine distance")
    return float(1.0 - np.dot(a, b))


def euclidean_distance(vector_a: Iterable[float], vector_b: Iterable[float]) -> float:
    a = as_float_vector(vector_a)
    b = as_float_vector(vector_b)
    if a.shape != b.shape:
        raise ValueError("Vector shape mismatch for euclidean distance")
    return float(np.linalg.norm(a - b))


def distance_for_metric(
    query_embedding: Iterable[float],
    stored_embedding: Iterable[float],
    metric: str,
) -> float:
    metric = metric.strip().lower()
    if metric == "cosine":
        return cosine_distance(query_embedding, stored_embedding)
    if metric == "euclidean":
        return euclidean_distance(query_embedding, stored_embedding)
    raise ValueError(f"Unsupported metric: {metric}")


def choose_best_match(
    query_embedding: Iterable[float],
    stored_people: list[dict[str, Any]],
    *,
    threshold: float,
    metric: str,
    embedding_key: str = "embedding",
) -> dict[str, Any] | None:
    best_person: dict[str, Any] | None = None
    best_distance: float | None = None

    for person in stored_people:
        candidate_embedding = person.get(embedding_key)
        if not isinstance(candidate_embedding, list) or not candidate_embedding:
            continue

        try:
            distance = distance_for_metric(query_embedding, candidate_embedding, metric)
        except ValueError:
            continue

        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_person = person

    if best_person is None or best_distance is None:
        return None

    return {
        "person": best_person,
        "distance": float(best_distance),
        "metric": metric,
        "threshold": float(threshold),
        "matched": bool(best_distance <= threshold),
    }
