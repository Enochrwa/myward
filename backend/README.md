# MyWard Backend — v2.0

AI-powered digital wardrobe & outfit recommendation system.

## Tech Stack
- **FastAPI 0.115** + Uvicorn
- **PostgreSQL 16** via SQLAlchemy 2.x + psycopg2
- **Alembic** — database migrations
- **Celery + Redis** — async task queue (ML inference)
- **JWT** auth (python-jose + bcrypt)
- **Ruff** lint/format, **Mypy** strict types, **Pytest** + coverage

## Quick Start
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,lint]"
cp .env.example .env   # fill in values
createdb myward
alembic upgrade head
uvicorn myward.main:app --reload
# Docs: http://localhost:8000/docs
```

## Docker Compose
```bash
cp backend/.env.example backend/.env
docker compose up --build
```

## Commands
```bash
ruff check src/ tests/          # lint
ruff format src/ tests/          # format
mypy src/myward                  # type check
pytest                           # tests + coverage
alembic revision --autogenerate -m "msg"   # new migration
alembic upgrade head             # apply migrations
```
