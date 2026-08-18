from __future__ import annotations

import asyncio
import logging
import random
import time
from collections.abc import Iterable
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx

from .config import HarvesterConfig
from .models import FetchResult

logger = logging.getLogger(__name__)


class APIHarvester:
    """Async API fetcher with retries, concurrency limits, and rate limiting."""

    def __init__(
        self,
        config: HarvesterConfig | None = None,
        **kwargs: object,
    ) -> None:
        self.config = config or HarvesterConfig(**kwargs)
        self.semaphore = asyncio.Semaphore(self.config.concurrency)
        self._request_lock = asyncio.Lock()
        self._last_request_time = 0.0

    async def fetch(
        self,
        client: httpx.AsyncClient,
        url: str,
    ) -> FetchResult | None:
        normalized_url = self._normalize_url(url)
        async with self.semaphore:
            response: httpx.Response | None = None
            start = time.perf_counter()
            last_error: Exception | None = None

            for attempt in range(1, self.config.retries + 2):
                try:
                    await self._respect_rate_limit()
                    response = await client.get(
                        normalized_url,
                        headers={"User-Agent": self.config.user_agent},
                    )
                    response.raise_for_status()

                    payload = response.json()
                    elapsed_ms = (time.perf_counter() - start) * 1000
                    logger.info("Fetched %s [%s] in %.1f ms", normalized_url, response.status_code, elapsed_ms)
                    return FetchResult(
                        url=normalized_url,
                        status_code=response.status_code,
                        data=payload,
                        attempts=attempt,
                        latency_ms=elapsed_ms,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    )
                except (httpx.HTTPError, ValueError) as exc:
                    last_error = exc
                    logger.warning(
                        "Request failed for %s (attempt=%d/%d): %s",
                        normalized_url,
                        attempt,
                        self.config.retries + 1,
                        exc,
                    )
                    if attempt <= self.config.retries:
                        delay = self.config.backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.25)
                        await asyncio.sleep(delay)

            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.error("Giving up on %s after %d attempts", normalized_url, self.config.retries + 1)
            return FetchResult(
                url=normalized_url,
                status_code=response.status_code if response is not None else 0,
                data=None,
                attempts=self.config.retries + 1,
                latency_ms=elapsed_ms,
                error=str(last_error) if last_error else "unknown error",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

    async def collect(
        self,
        urls: Iterable[str],
        *,
        client: httpx.AsyncClient | None = None,
    ) -> list[FetchResult]:
        unique_urls = list(dict.fromkeys(str(url).strip() for url in urls if str(url).strip()))
        valid_urls: list[str] = []
        for url in unique_urls:
            try:
                valid_urls.append(self._normalize_url(url))
            except ValueError:
                logger.warning("Skipping invalid URL: %s", url)

        if client is not None:
            tasks = [self.fetch(client, url) for url in valid_urls]
            results = await asyncio.gather(*tasks)
            return [result for result in results if result is not None]

        async with httpx.AsyncClient(timeout=self.config.timeout) as managed_client:
            tasks = [self.fetch(managed_client, url) for url in valid_urls]
            results = await asyncio.gather(*tasks)

        return [result for result in results if result is not None]

    @staticmethod
    def _normalize_url(url: str) -> str:
        cleaned = url.strip()
        if not cleaned:
            raise ValueError("URL cannot be empty")

        parsed = urlparse(cleaned)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError(f"Unsupported URL scheme for: {cleaned}")
        if not parsed.netloc:
            raise ValueError(f"Invalid URL: {cleaned}")
        return cleaned

    async def _respect_rate_limit(self) -> None:
        if self.config.max_requests_per_second is None:
            return

        interval = 1.0 / self.config.max_requests_per_second
        async with self._request_lock:
            elapsed = time.monotonic() - self._last_request_time
            if elapsed < interval:
                await asyncio.sleep(interval - elapsed)
            self._last_request_time = time.monotonic()
