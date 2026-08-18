from __future__ import annotations

import argparse
import asyncio

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from async_api_harvester.config import load_config
from async_api_harvester.harvester import APIHarvester

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="async-api-harvester terminal client")
    parser.add_argument("urls", nargs="*", help="URLs to fetch")
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--max-rps", type=float, default=None)
    return parser


async def harvest(
    urls: list[str],
    concurrency: int,
    timeout: float,
    retries: int,
    max_rps: float | None,
) -> list[object]:
    config = load_config(
        {
            "concurrency": concurrency,
            "timeout": timeout,
            "retries": retries,
            "max_requests_per_second": max_rps,
        }
    )
    harvester = APIHarvester(config=config)
    return await harvester.collect(urls)


def main() -> None:
    args = build_parser().parse_args()
    urls = args.urls or [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
        "https://jsonplaceholder.typicode.com/posts/3",
    ]

    console.print(
        Panel.fit("[bold cyan]Async API Harvester[/bold cyan]", border_style="cyan")
    )

    results = asyncio.run(
        harvest(
            urls,
            concurrency=args.concurrency,
            timeout=args.timeout,
            retries=args.retries,
            max_rps=args.max_rps,
        )
    )

    table = Table(title="Fetched results", show_lines=True)
    table.add_column("Status", style="green")
    table.add_column("URL", style="cyan")
    table.add_column("Title", style="magenta")

    for result in results:
        title = "N/A"
        if isinstance(result.data, dict):
            title = str(result.data.get("title") or result.data.get("name") or "N/A")
        table.add_row(str(result.status_code), result.url, title)

    console.print(table)


if __name__ == "__main__":
    main()
