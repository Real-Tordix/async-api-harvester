from __future__ import annotations

import asyncio
from pathlib import Path

from async_api_harvester.config import HarvesterConfig
from async_api_harvester.harvester import APIHarvester


async def main(path: str) -> None:
    urls = [
        line.strip()
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    config = HarvesterConfig(concurrency=5, timeout=10.0, retries=3)
    harvester = APIHarvester(config=config)

    results = await harvester.collect(urls)
    for result in results:
        print(result.summary())


if __name__ == "__main__":
    if len(__import__("sys").argv) < 2:
        raise SystemExit("Usage: python examples/url_file_input.py <urls.txt>")
    asyncio.run(main(__import__("sys").argv[1]))
