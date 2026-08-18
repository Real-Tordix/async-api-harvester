# async-api-harvester

A lightweight async Python client for harvesting API data with concurrency limits, retries, rate limiting, and structured output.

## Project status

This project is focused on being a clean, testable async API fetcher with:

- a terminal-first CLI
- a PyQt5 desktop UI
- a reusable Python API
- a small, maintainable CI flow

## Features

- Async HTTP requests using `httpx`
- Configurable concurrency control with `asyncio.Semaphore`
- Retry support with exponential backoff
- Optional request-rate limit (`--max-rps`)
- Request timeout handling
- Immutable result objects
- CLI and Python API usage
- PyQt5 GUI mode
- Rich terminal output
- JSON or table-style result output

## Requirements

- Python 3.11+
- `httpx`
- `PyQt5` for GUI mode
- `rich` for the terminal UI

## Installation

```bash
git clone https://github.com/shayanghad0/async-api-harvester.git
cd async-api-harvester
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -e .
```

## Quick start

Terminal mode:

```bash
python main.py https://jsonplaceholder.typicode.com/posts/1 https://jsonplaceholder.typicode.com/posts/2
```

GUI mode:

```bash
python Gui.py
```

Read URLs from a file:

```bash
python main.py --input-file urls.txt
```

Example `urls.txt`:

```text
https://jsonplaceholder.typicode.com/posts/1
https://jsonplaceholder.typicode.com/posts/2
https://jsonplaceholder.typicode.com/posts/3
```

## Configuration

You can override runtime values with CLI arguments or environment variables.

Environment variables:

```bash
export API_HARVESTER_CONCURRENCY=10
export API_HARVESTER_TIMEOUT=5.0
export API_HARVESTER_RETRIES=3
export API_HARVESTER_BACKOFF_BASE=1.0
export API_HARVESTER_MAX_RPS=5
export API_HARVESTER_USER_AGENT="my-client/1.0"
```

CLI arguments:

```bash
python main.py \
  --concurrency 10 \
  --timeout 5.0 \
  --retries 3 \
  --backoff-base 1.0 \
  --max-rps 5 \
  https://jsonplaceholder.typicode.com/posts/1
```

## Python usage

```python
import asyncio

from async_api_harvester.config import HarvesterConfig
from async_api_harvester.harvester import APIHarvester


async def main() -> None:
    config = HarvesterConfig(concurrency=5, timeout=5.0, retries=3)
    harvester = APIHarvester(config=config)
    results = await harvester.collect([
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
    ])

    for result in results:
        print(result.summary())


asyncio.run(main())
```

## JSON output

```bash
python main.py --json https://jsonplaceholder.typicode.com/posts/1
```

## Examples

See the [examples folder](examples/README.md) for:

- terminal usage
- GUI launch
- file-based harvesting

## Roadmap

Planned improvements for the project:

- export to JSON, CSV, and NDJSON
- domain-aware throttling
- better retry-by-status logic
- per-host rate limits
- progress bar and summary reporting
- optional task queue and persistence layer

## Documentation

- [How to use](HOW_TO_USE.md)
- [Examples](examples/README.md)

## License

MIT
