.PHONY: help setup dev-up dev-down test clean format

help:
	@echo "Document Intelligence Platform - Commands:"
	@echo "  make setup      - Initial setup (venv, deps)"
	@echo "  make dev-up     - Start all services"
	@echo "  make dev-down   - Stop all services"
	@echo "  make api        - Run API server"
	@echo "  make worker     - Run Celery worker"
	@echo "  make test       - Run tests"
	@echo "  make format     - Format code (black)"
	@echo "  make clean      - Clean up"

setup:
	python -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r app/requirements.txt
	cp .env.example .env
	@echo "✅ Setup complete! Edit .env with your Azure credentials"

dev-up:
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "   PostgreSQL: localhost:5432"
	@echo "   Redis: localhost:6379"
	@echo "   Azurite: localhost:10000"

dev-down:
	docker-compose down -v

api:
	cd app && uvicorn main:app --reload --host 0.0.0.0 --port 8000

worker:
	cd app && celery -A workers.celery_app worker --loglevel=info --concurrency=2

test:
	cd app && pytest -v --cov=. tests/

test-quick:
	cd app && pytest -v tests/

format:
	cd app && black . --line-length 100

lint:
	cd app && flake8 . --max-line-length=100 --exclude=venv,__pycache__

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf venv

logs-api:
	docker-compose logs -f api

logs-worker:
	docker-compose logs -f celery-worker

logs-db:
	docker-compose logs -f postgres
