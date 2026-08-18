from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class HarvesterConfig:
    """Runtime configuration for the async harvester."""

    concurrency: int = field(default_factory=lambda: int(os.getenv("API_HARVESTER_CONCURRENCY", "10")))
    timeout: float = field(default_factory=lambda: float(os.getenv("API_HARVESTER_TIMEOUT", "10.0")))
    retries: int = field(default_factory=lambda: int(os.getenv("API_HARVESTER_RETRIES", "3")))
    backoff_base: float = field(default_factory=lambda: float(os.getenv("API_HARVESTER_BACKOFF_BASE", "1.0")))
    max_requests_per_second: float | None = field(
        default_factory=lambda: _coerce_optional_float("API_HARVESTER_MAX_RPS")
    )
    user_agent: str = field(default_factory=lambda: os.getenv("API_HARVESTER_USER_AGENT", "async-api-harvester/1.0"))

    def __post_init__(self) -> None:
        if self.concurrency <= 0:
            raise ValueError("concurrency must be greater than 0")
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        if self.retries < 0:
            raise ValueError("retries must be zero or greater")
        if self.backoff_base <= 0:
            raise ValueError("backoff_base must be greater than 0")
        if self.max_requests_per_second is not None and self.max_requests_per_second <= 0:
            raise ValueError("max_requests_per_second must be greater than 0")


def _coerce_optional_float(name: str) -> float | None:
    value = os.getenv(name)
    if value is None or value == "":
        return None
    return float(value)


def load_config(overrides: dict[str, Any] | None = None) -> HarvesterConfig:
    """Create a config object from environment and explicit overrides."""

    data = {
        "concurrency": int(os.getenv("API_HARVESTER_CONCURRENCY", "10")),
        "timeout": float(os.getenv("API_HARVESTER_TIMEOUT", "10.0")),
        "retries": int(os.getenv("API_HARVESTER_RETRIES", "3")),
        "backoff_base": float(os.getenv("API_HARVESTER_BACKOFF_BASE", "1.0")),
        "max_requests_per_second": _coerce_optional_float("API_HARVESTER_MAX_RPS"),
        "user_agent": os.getenv("API_HARVESTER_USER_AGENT", "async-api-harvester/1.0"),
    }

    if overrides:
        data.update(overrides)

    return HarvesterConfig(**data)
