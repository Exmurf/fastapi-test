# FastAPI Product API

A backend API built with **FastAPI**, following a Clean Architecture-inspired structure.

The project includes authentication, authorization, product management, activity logging, error logging, Redis-backed rate limiting and caching, analytics, cron jobs, and Docker support.

## Tech Stack

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- Redis
- Pydantic
- JWT
- Argon2id
- Docker
- Docker Compose

## Environment Variables

Create a `.env` file in the project root. An example is available in the root.

## Run with Docker Compose

Build and start FastAPI and Redis:

```bash
docker compose up -d --build
```

Check running services:

```bash
docker compose ps
```

View FastAPI logs:

```bash
docker compose logs -f fastapi
```

Stop the services:

```bash
docker compose down
```

The API will be available at:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

## Product DB and Cache Performance Test

The performance script generates products under a unique `run_id`. Cleanup
physically removes only products carrying that marker, their related test
records, and their Redis product-cache keys. Existing application data is not
included in the cleanup condition.

Run the complete 10,000-product test. Dummy data is removed automatically even
if the benchmark fails:

```bash
DEBUG=false python scripts/product_performance.py run --count 10000
```

To inspect or test the data manually before removing it, use the separate
commands. The `seed` command prints the generated `run_id`:

```bash
DEBUG=false python scripts/product_performance.py seed --count 10000
DEBUG=false python scripts/product_performance.py benchmark --run-id RUN_ID
DEBUG=false python scripts/product_performance.py cleanup --run-id RUN_ID
```

You can also retain the data after a combined run:

```bash
DEBUG=false python scripts/product_performance.py run --count 10000 --keep-data
```

By default, the first active user owns the generated products. Select another
active user when needed:

```bash
DEBUG=false python scripts/product_performance.py run \
  --owner-email user@example.com
```

The report includes first/last-page database reads, server-side sorting by
name, price and stock, a single-product database read, and Redis hit, miss and
set timings. Redis measurements are skipped with an explicit message when
Redis is unavailable. Reported repository/cache timings do not include HTTP,
authentication, serialization or network latency.

## Run Locally

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start Redis separately, then run:

```bash
uvicorn app.main:app --reload
```

## API Documentation

Interactive API documentation is available at:

```text
http://localhost:8000/docs
```
