.PHONY: install lint format typecheck test test-unit test-integration migrate seed run docker-up docker-down clean

# ── Setup ──────────────────────────────────────────────────────────────────────
install:
	pip install -e ".[dev,lint]"
	pre-commit install

# ── Code quality ───────────────────────────────────────────────────────────────
lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

lint-fix:
	ruff check --fix src/ tests/
	ruff format src/ tests/

typecheck:
	mypy src/myward

check: lint typecheck
	@echo "✅ All checks passed"

# ── Tests ──────────────────────────────────────────────────────────────────────
test:
	pytest

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-cov:
	pytest --cov=src/myward --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

# ── Database ───────────────────────────────────────────────────────────────────
migrate:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

migrate-new:
	@read -p "Migration name: " name; alembic revision --autogenerate -m "$$name"

db-reset:
	alembic downgrade base
	alembic upgrade head

# ── Dev server ─────────────────────────────────────────────────────────────────
run:
	uvicorn myward.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	celery -A myward.workers.celery_app worker --loglevel=info

# ── Docker ─────────────────────────────────────────────────────────────────────
docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f api

# ── Clean ──────────────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf htmlcov/ coverage.xml .coverage
	@echo "✅ Clean complete"
