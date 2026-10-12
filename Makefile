.PHONY: up down build test lint seed migrate local-backend local-frontend

up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build

test:
	.venv/Scripts/pytest tests/ -v

lint:
	.venv/Scripts/ruff check backend/

seed:
	.venv/Scripts/python scripts/seed_demo.py

local-backend:
	.venv/Scripts/uvicorn app.main:app --app-dir backend --reload --port 8000

local-frontend:
	cd frontend && npm run dev
