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
