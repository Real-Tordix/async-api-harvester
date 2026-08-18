from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class HarvesterConfig:
    """Runtime configuration for the async harvester."""

    concurrency: int = 10
    timeout: float = 10.0
    retries: int = 3
    backoff_base: float = 1.0
    max_requests_per_second: float | None = None
    user_agent: str = "async-api-harvester/1.0"

    def __post_init__(self) -> None:
        if self.concurrency <= 0:
            raise ValueError("concurrency must be greater than 0")
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        if self.retries < 0:
            raise ValueError("retries must be zero or greater")
        if self.backoff_base <= 0:
            raise ValueError("backoff_base must be greater than 0")
        if (
            self.max_requests_per_second is not None
            and self.max_requests_per_second <= 0
        ):
            raise ValueError("max_requests_per_second must be greater than 0")


def _coerce_optional_float(name: str) -> float | None:
    value = os.getenv(name)
    if value is None or value == "":
        return None
    return float(value)


def load_config(overrides: dict[str, Any] | None = None) -> HarvesterConfig:
    """Create a config object from environment and explicit overrides."""

    config = HarvesterConfig(
        concurrency=int(os.getenv("API_HARVESTER_CONCURRENCY", "10")),
        timeout=float(os.getenv("API_HARVESTER_TIMEOUT", "10.0")),
        retries=int(os.getenv("API_HARVESTER_RETRIES", "3")),
        backoff_base=float(os.getenv("API_HARVESTER_BACKOFF_BASE", "1.0")),
        max_requests_per_second=_coerce_optional_float("API_HARVESTER_MAX_RPS"),
        user_agent=os.getenv("API_HARVESTER_USER_AGENT", "async-api-harvester/1.0"),
    )

    if not overrides:
        return config

    for key, value in overrides.items():
        if key == "concurrency":
            config = HarvesterConfig(
                concurrency=int(value),
                timeout=config.timeout,
                retries=config.retries,
                backoff_base=config.backoff_base,
                max_requests_per_second=config.max_requests_per_second,
                user_agent=config.user_agent,
            )
        elif key == "timeout":
            config = HarvesterConfig(
                concurrency=config.concurrency,
                timeout=float(value),
                retries=config.retries,
                backoff_base=config.backoff_base,
                max_requests_per_second=config.max_requests_per_second,
                user_agent=config.user_agent,
            )
        elif key == "retries":
            config = HarvesterConfig(
                concurrency=config.concurrency,
                timeout=config.timeout,
                retries=int(value),
                backoff_base=config.backoff_base,
                max_requests_per_second=config.max_requests_per_second,
                user_agent=config.user_agent,
            )
        elif key == "backoff_base":
            config = HarvesterConfig(
                concurrency=config.concurrency,
                timeout=config.timeout,
                retries=config.retries,
                backoff_base=float(value),
                max_requests_per_second=config.max_requests_per_second,
                user_agent=config.user_agent,
            )
        elif key == "max_requests_per_second":
            config = HarvesterConfig(
                concurrency=config.concurrency,
                timeout=config.timeout,
                retries=config.retries,
                backoff_base=config.backoff_base,
                max_requests_per_second=None if value in (None, "") else float(value),
                user_agent=config.user_agent,
            )
        elif key == "user_agent":
            config = HarvesterConfig(
                concurrency=config.concurrency,
                timeout=config.timeout,
                retries=config.retries,
                backoff_base=config.backoff_base,
                max_requests_per_second=config.max_requests_per_second,
                user_agent=str(value),
            )

    return config
