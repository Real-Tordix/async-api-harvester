from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class FetchResult:
    """Immutable result returned from a single URL fetch."""

    url: str
    status_code: int
    data: dict[str, Any] | list[Any] | None
    attempts: int = 1
    latency_ms: float | None = None
    error: str | None = None
    timestamp: str = field(default_factory=lambda: "")

    def summary(self) -> str:
        title = "N/A"
        if isinstance(self.data, dict):
            title = str(self.data.get("title") or self.data.get("name") or "N/A")
        elif isinstance(self.data, list) and self.data and isinstance(self.data[0], dict):
            title = str(self.data[0].get("title") or self.data[0].get("name") or "N/A")

        return f"{self.status_code} | {self.url} | {title}"
