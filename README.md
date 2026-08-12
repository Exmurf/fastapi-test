# FastAPI Product API

A backend API built with **FastAPI**, following a Clean Architecture-inspired structure.

The project includes authentication, authorization, product management, activity logging, error logging, Redis-backed rate limiting and caching, analytics, cron jobs, and Docker support.

## Features

- JWT authentication with access and refresh tokens
- Argon2id password hashing
- User/Admin role-based authorization
- Product CRUD with soft delete
- Pagination, search, sorting, and filtering
- Product tags and product details
- User profiles
- Activity logging
- HTTP 4xx/5xx error logging
- Redis-backed sliding-window rate limiting
- Redis product caching with TTL and cache invalidation
- User/product analytics
- Cron-based product processing
- Docker and Docker Compose support

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

## Project Structure

```text
app/
├── application/
│   ├── schemas/
│   ├── security/
│   └── services/
├── domain/
│   ├── entities/
│   ├── repositories/
│   ├── read_models/
│   └── security/
├── infrastructure/
│   ├── logging/
│   ├── models/
│   └── repositories/
├── presentation/
│   ├── dependencies/
│   ├── middleware/
│   └── routers/
├── config.py
└── main.py

scripts/
└── product_name_cron.py
```

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
