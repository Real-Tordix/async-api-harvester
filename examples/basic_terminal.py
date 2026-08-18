import asyncio

from async_api_harvester.config import HarvesterConfig
from async_api_harvester.harvester import APIHarvester


async def main() -> None:
    config = HarvesterConfig(concurrency=4, timeout=8.0, retries=2)
    harvester = APIHarvester(config=config)

    urls = [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
    ]

    results = await harvester.collect(urls)
    for result in results:
        print(result.summary())


if __name__ == "__main__":
    asyncio.run(main())
