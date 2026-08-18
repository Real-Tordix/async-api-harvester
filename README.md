# async-api-harvester

High-performance async API data collector with concurrency control,
retries, timeouts, and structured logging.

## Features

- Async HTTP requests with `httpx`
- Concurrent request handling
- Configurable concurrency limits
- Automatic retries with exponential backoff
- Request timeouts
- Structured logging
- Typed Python code
- Immutable result objects

## Requirements

- Python 3.11+
- `httpx`

## Installation

```bash
git clone https://github.com/yourusername/async-api-harvester.git
cd async-api-harvester

python -m venv .venv
source .venv/bin/activate
```

Windows:

```
.venv\Scripts\activate
```

Install dependencies:

```
pip install httpx
```

Usage
```
python main.py
```

Example output:

```
200 | https://jsonplaceholder.typicode.com/posts/1 | sunt aut facere...
200 | https://jsonplaceholder.typicode.com/posts/2 | qui est esse...
200 | https://jsonplaceholder.typicode.com/posts/3 | ea molestias...
```

Configuration

The harvester can be configured with:

```
APIHarvester(
    concurrency=10,
    timeout=10.0,
    retries=3,
)
```

Project Goals

This project demonstrates practical Python concepts including:

asyncio

async HTTP clients

concurrency control

error handling

retry strategies

type hints

dataclasses

logging


##

License

MIT
