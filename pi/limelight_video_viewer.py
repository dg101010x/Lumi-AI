import argparse
import ipaddress
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable

import cv2
import requests


DEFAULT_HOST_CANDIDATES = [
    "limelight.local",
    "limelight",
]

DEFAULT_PORTS = [5800, 5801]
DEFAULT_STREAM_PATHS = [
    "/stream.mjpg",
    "/mjpg/video.mjpg",
    "/video_feed",
]


def candidate_base_urls() -> list[str]:
    urls: list[str] = []

    for host in DEFAULT_HOST_CANDIDATES:
        for port in DEFAULT_PORTS:
            urls.append(f"http://{host}:{port}")

    for subnet in local_subnets():
        for host in subnet.hosts():
            host_str = str(host)
            for port in DEFAULT_PORTS:
                urls.append(f"http://{host_str}:{port}")

    return urls


def local_subnets() -> list[ipaddress.IPv4Network]:
    subnets: list[ipaddress.IPv4Network] = []
    hostname = socket.gethostname()

    try:
        _, _, addresses = socket.gethostbyname_ex(hostname)
    except socket.gaierror:
        return subnets

    for address in addresses:
        if address.startswith("127."):
            continue
        try:
            network = ipaddress.ip_network(f"{address}/24", strict=False)
        except ValueError:
            continue
        if network not in subnets:
            subnets.append(network)

    return subnets


def stream_candidates(base_urls: Iterable[str]) -> list[str]:
    urls: list[str] = []
    for base_url in base_urls:
        for path in DEFAULT_STREAM_PATHS:
            urls.append(f"{base_url}{path}")
    return urls


def check_stream(url: str) -> str | None:
    try:
        response = requests.get(url, stream=True, timeout=0.6)
        content_type = response.headers.get("Content-Type", "").lower()
        if response.ok and ("multipart" in content_type or "mjpeg" in content_type):
            response.close()
            return url
        response.close()
    except requests.RequestException:
        return None
    return None


def autodiscover_stream() -> str | None:
    candidates = stream_candidates(candidate_base_urls())
    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = {executor.submit(check_stream, url): url for url in candidates}
        for future in as_completed(futures):
            found = future.result()
            if found:
                return found
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Display the live Limelight video feed."
    )
    parser.add_argument(
        "--url",
        help="Full Limelight stream URL, for example http://<ip>:5800/...",
    )
    parser.add_argument(
        "--host",
        help="Optional Limelight host or IP. Uses common stream paths automatically.",
    )
    args = parser.parse_args()

    stream_url = args.url
    if not stream_url and args.host:
        stream_url = f"http://{args.host}:5800{DEFAULT_STREAM_PATHS[0]}"

    if not stream_url:
        print("Trying to auto-discover Limelight stream...", flush=True)
        stream_url = autodiscover_stream()

    if not stream_url:
        print(
            "Could not auto-discover a Limelight stream. Pass --url or --host.",
            file=sys.stderr,
        )
        return 1

    print(f"Opening stream: {stream_url}", flush=True)
    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        print(f"Could not open stream: {stream_url}", file=sys.stderr)
        return 1

    print("Showing live feed. Press q to quit.", flush=True)

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Stream read failed.", file=sys.stderr)
            break

        cv2.imshow("Limelight Live Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
