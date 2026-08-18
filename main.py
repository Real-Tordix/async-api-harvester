import asyncio
import logging
from dataclasses import dataclass
from typing import Any

import httpx


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class FetchResult:
    url: str
    status_code: int
    data: dict[str, Any]


class APIHarvester:
    def __init__(
        self,
        concurrency: int = 10,
        timeout: float = 10.0,
        retries: int = 3,
    ) -> None:
        self.semaphore = asyncio.Semaphore(concurrency)
        self.timeout = timeout
        self.retries = retries

    async def fetch(
        self,
        client: httpx.AsyncClient,
        url: str,
    ) -> FetchResult | None:
        async with self.semaphore:
            for attempt in range(1, self.retries + 1):
                try:
                    response = await client.get(url)
                    response.raise_for_status()

                    logger.info(
                        "Fetched %s [%s]",
                        url,
                        response.status_code,
                    )

                    return FetchResult(
                        url=url,
                        status_code=response.status_code,
                        data=response.json(),
                    )

                except (httpx.HTTPError, ValueError) as exc:
                    logger.warning(
                        "Request failed: %s | attempt=%d/%d",
                        exc,
                        attempt,
                        self.retries,
                    )

                    if attempt < self.retries:
                        await asyncio.sleep(2 ** (attempt - 1))

            logger.error("Giving up on %s", url)
            return None

    async def collect(self, urls: list[str]) -> list[FetchResult]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            tasks = [
                self.fetch(client, url)
                for url in urls
            ]

            results = await asyncio.gather(*tasks)

        return [result for result in results if result is not None]


async def main() -> None:
    urls = [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
        "https://jsonplaceholder.typicode.com/posts/3",
    ]

    harvester = APIHarvester(
        concurrency=5,
        timeout=5.0,
        retries=3,
    )

    results = await harvester.collect(urls)

    for result in results:
        print(
            f"{result.status_code} | "
            f"{result.url} | "
            f"{result.data.get('title', 'N/A')}"
        )


if __name__ == "__main__":
    asyncio.run(main())
