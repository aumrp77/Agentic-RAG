.PHONY: help install install-dev test lint format clean build run-backend run-frontend docker-build docker-up docker-down

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  clean        - Clean cache and build artifacts"
	@echo "  build        - Build the project"
	@echo "  run-backend  - Run the backend server"
	@echo "  run-frontend - Run the frontend development server"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-up    - Start Docker services"
	@echo "  docker-down  - Stop Docker services"

# Installation
install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"
	cd frontend && npm install

# Testing
test:
	pytest tests/ -v --cov=backend --cov-report=html --cov-report=term-missing

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

# Code quality
lint:
	black --check backend tests
	isort --check-only backend tests
	flake8 backend tests
	mypy backend
	cd frontend && npm run lint

format:
	black backend tests
	isort backend tests
	cd frontend && npm run format

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	cd frontend && rm -rf node_modules/.cache dist build

# Build
build:
	python -m build
	cd frontend && npm run build

# Development servers
run-backend:
	python -m backend.main

run-frontend:
	cd frontend && npm run dev

# Docker operations
docker-build:
	docker-compose -f .devcontainer/docker-compose.yml build

docker-up:
	docker-compose -f .devcontainer/docker-compose.yml up -d

docker-down:
	docker-compose -f .devcontainer/docker-compose.yml down

# Development workflow
dev: install-dev
	@echo "Starting development environment..."
	@echo "Backend will be available at http://localhost:8000"
	@echo "Frontend will be available at http://localhost:3000"
	@echo ""
	@echo "Run 'make run-backend' in one terminal"
	@echo "Run 'make run-frontend' in another terminal"
