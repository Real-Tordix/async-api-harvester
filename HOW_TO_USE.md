# How to Use async-api-harvester

This project is an async API harvester built with Python and `httpx`.
It can fetch multiple URLs concurrently, retry failed requests, limit concurrency, and return structured results.

## 1) Install Python

Make sure you have Python 3.11 or newer installed.

Check:

```bash
python --version
```

## 2) Create a virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

## 3) Install dependencies

```bash
pip install -e .
```

If you want the minimal install:

```bash
pip install httpx
```

## 4) Run the project

### Simple example

```bash
python main.py
```

This uses the default demo URLs in `main.py`.

### With your own URLs

```bash
python main.py https://jsonplaceholder.typicode.com/posts/1 https://jsonplaceholder.typicode.com/posts/2
```

### Read URLs from a file

Create a file named `urls.txt`:

```text
https://jsonplaceholder.typicode.com/posts/1
https://jsonplaceholder.typicode.com/posts/2
https://jsonplaceholder.typicode.com/posts/3
```

Then run:

```bash
python main.py --input-file urls.txt
```

### JSON output

```bash
python main.py --json https://jsonplaceholder.typicode.com/posts/1
```

## 5) Advanced options

You can control concurrency and retries:

```bash
python main.py \
  --concurrency 10 \
  --timeout 5.0 \
  --retries 3 \
  --backoff-base 1.0 \
  --max-rps 5 \
  https://jsonplaceholder.typicode.com/posts/1
```

## 6) Python API usage

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

## 7) Notes

- The harvester skips invalid URLs.
- Failed requests retry with exponential backoff.
- The project supports structured JSON output.
- You can also set environment variables like:

```bash
export API_HARVESTER_CONCURRENCY=10
export API_HARVESTER_TIMEOUT=5.0
export API_HARVESTER_RETRIES=3
export API_HARVESTER_MAX_RPS=5
```

## 8) Troubleshooting

### Module not found

If you get an import error, reinstall the package:

```bash
pip install -e .
```

### Script fails on a bad URL

The harvester skips invalid URLs automatically. Make sure the URL starts with `http://` or `https://`.

### Timeout issues

Increase the timeout when calling slow APIs:

```bash
python main.py --timeout 30 https://example.com
```

## 9) Example result

```text
200 | https://jsonplaceholder.typicode.com/posts/1 | sunt aut facere repellat provident occaecati excepturi optio reprehenderit
```
