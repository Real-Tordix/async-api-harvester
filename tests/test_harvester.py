from __future__ import annotations

import httpx
import pytest

from async_api_harvester.config import HarvesterConfig
from async_api_harvester.harvester import APIHarvester


@pytest.mark.asyncio
async def test_fetch_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://example.com/items/1"
        return httpx.Response(200, json={"title": "hello"})

    transport = httpx.MockTransport(handler)
    config = HarvesterConfig(concurrency=2, timeout=3.0, retries=2, backoff_base=0.01)
    harvester = APIHarvester(config=config)

    async with httpx.AsyncClient(transport=transport) as client:
        result = await harvester.fetch(client, "https://example.com/items/1")

    assert result is not None
    assert result.status_code == 200
    assert result.data == {"title": "hello"}
    assert result.latency_ms is not None


@pytest.mark.asyncio
async def test_fetch_retries_failed_request() -> None:
    attempts = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        if attempts["count"] < 2:
            raise httpx.HTTPError("temporary failure")
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    config = HarvesterConfig(concurrency=1, timeout=3.0, retries=3, backoff_base=0.01)
    harvester = APIHarvester(config=config)

    async with httpx.AsyncClient(transport=transport) as client:
        result = await harvester.fetch(client, "https://example.com/items/2")

    assert result is not None
    assert result.status_code == 200
    assert attempts["count"] == 2


@pytest.mark.asyncio
async def test_collect_filters_invalid_urls() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"id": 1})

    transport = httpx.MockTransport(handler)
    config = HarvesterConfig(concurrency=2, timeout=3.0, retries=1, backoff_base=0.01)
    harvester = APIHarvester(config=config)

    async with httpx.AsyncClient(transport=transport) as client:
        results = await harvester.collect(
            ["https://example.com/a", "https://example.com/b", "not-a-url"],
            client=client,
        )

    assert len(results) == 2
    assert {item.url for item in results} == {
        "https://example.com/a",
        "https://example.com/b",
    }
