from __future__ import annotations

import argparse
import asyncio
import json
import logging
from dataclasses import asdict
from pathlib import Path

from .config import HarvesterConfig, load_config
from .harvester import APIHarvester

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Async API harvester")
    parser.add_argument("urls", nargs="*", help="URLs to fetch")
    parser.add_argument("--input-file", type=Path, help="Path to a file containing one URL per line")
    parser.add_argument("--concurrency", type=int, help="Maximum concurrent requests")
    parser.add_argument("--timeout", type=float, help="Per-request timeout in seconds")
    parser.add_argument("--retries", type=int, help="Number of retry attempts")
    parser.add_argument("--backoff-base", type=float, help="Backoff base delay in seconds")
    parser.add_argument("--max-rps", type=float, help="Optional global requests per second limit")
    parser.add_argument("--user-agent", help="Custom User-Agent header")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    return parser


def read_urls_from_file(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

    urls = list(args.urls)
    if args.input_file:
        urls.extend(read_urls_from_file(args.input_file))

    if not urls:
        parser.print_help()
        return 1

    overrides: dict[str, object] = {}
    if args.concurrency is not None:
        overrides["concurrency"] = args.concurrency
    if args.timeout is not None:
        overrides["timeout"] = args.timeout
    if args.retries is not None:
        overrides["retries"] = args.retries
    if args.backoff_base is not None:
        overrides["backoff_base"] = args.backoff_base
    if args.max_rps is not None:
        overrides["max_requests_per_second"] = args.max_rps
    if args.user_agent is not None:
        overrides["user_agent"] = args.user_agent

    config = load_config(overrides)
    harvester = APIHarvester(config=config)

    results = asyncio.run(harvester.collect(urls))

    if args.json:
        print(json.dumps([asdict(result) for result in results], indent=2, default=str))
        return 0

    for result in results:
        print(result.summary())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
