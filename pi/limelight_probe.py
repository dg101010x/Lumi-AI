import argparse
import json
import sys
import time
from typing import Any

import requests


def build_url(host: str, path: str) -> str:
    host = host.strip().rstrip("/")
    if not host.startswith(("http://", "https://")):
        host = f"http://{host}"
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{host}{path}"


def fetch_json(session: requests.Session, url: str, timeout: float) -> Any:
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Continuously poll a Limelight JSON endpoint and print the payload."
    )
    parser.add_argument("--host", required=True, help="Limelight host or IP")
    parser.add_argument(
        "--path",
        default="/results",
        help="HTTP JSON path to poll. Default: /results",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.25,
        help="Polling interval in seconds. Default: 0.25",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=2.0,
        help="Per-request timeout in seconds. Default: 2.0",
    )
    args = parser.parse_args()

    url = build_url(args.host, args.path)
    session = requests.Session()

    print(f"Polling {url} every {args.interval:.2f}s", flush=True)

    while True:
        started = time.time()
        try:
            payload = fetch_json(session, url, args.timeout)
            print(json.dumps(payload, indent=2), flush=True)
        except requests.RequestException as exc:
            print(f"[http-error] {exc}", file=sys.stderr, flush=True)
        except ValueError as exc:
            print(f"[json-error] {exc}", file=sys.stderr, flush=True)

        elapsed = time.time() - started
        sleep_for = max(0.0, args.interval - elapsed)
        time.sleep(sleep_for)


if __name__ == "__main__":
    raise SystemExit(main())
