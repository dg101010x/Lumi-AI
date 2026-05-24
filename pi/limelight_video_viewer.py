import argparse
import ipaddress
import os
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable

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


def dedupe(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def build_base_urls(hosts: Iterable[str], ports: Iterable[int] = DEFAULT_PORTS) -> list[str]:
    urls: list[str] = []
    for host in hosts:
        for port in ports:
            urls.append(f"http://{host}:{port}")
    return dedupe(urls)


def candidate_base_urls() -> list[str]:
    urls: list[str] = []

    urls.extend(build_base_urls(DEFAULT_HOST_CANDIDATES))
    urls.extend(build_base_urls(resolved_ipv4_hosts(DEFAULT_HOST_CANDIDATES)))
    urls.extend(build_base_urls(neighbor_ipv4_hosts()))

    for subnet in local_subnets():
        for host in subnet.hosts():
            host_str = str(host)
            for port in DEFAULT_PORTS:
                urls.append(f"http://{host_str}:{port}")

    return dedupe(urls)


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


def resolved_ipv4_hosts(hosts: Iterable[str]) -> list[str]:
    resolved: list[str] = []

    for host in hosts:
        try:
            infos = socket.getaddrinfo(host, None, family=socket.AF_INET, type=socket.SOCK_STREAM)
        except socket.gaierror:
            continue

        for info in infos:
            address = info[4][0]
            resolved.append(address)

    return dedupe(resolved)


def neighbor_ipv4_hosts() -> list[str]:
    path = "/proc/net/arp"
    if not os.path.exists(path):
        return []

    hosts: list[str] = []
    with open(path, "r", encoding="ascii") as arp_table:
        next(arp_table, None)
        for line in arp_table:
            columns = line.split()
            if len(columns) < 6:
                continue
            ip_address, _, flags, _, _, device = columns[:6]
            if flags != "0x2":
                continue
            if device == "lo":
                continue
            hosts.append(ip_address)

    return dedupe(hosts)


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


def first_working_stream(base_urls: Iterable[str]) -> str | None:
    candidates = stream_candidates(base_urls)
    with ThreadPoolExecutor(max_workers=min(32, max(1, len(candidates)))) as executor:
        futures = {executor.submit(check_stream, url): url for url in candidates}
        for future in as_completed(futures):
            found = future.result()
            if found:
                return found
    return None


def autodiscover_stream() -> str | None:
    return first_working_stream(candidate_base_urls())


def candidate_stream_from_host(host: str) -> str | None:
    host = host.strip().rstrip("/")
    if host.startswith(("http://", "https://")):
        return first_working_stream([host])

    hosts = [host]
    hosts.extend(resolved_ipv4_hosts([host]))
    hosts.extend(neighbor_ipv4_hosts())
    return first_working_stream(build_base_urls(hosts))


def main() -> int:
    import cv2

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
        stream_url = candidate_stream_from_host(args.host)

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
