# Makefile for CRE Intelligence Platform

.PHONY: help install install-dev test lint format clean build run serve docs deploy

# Default target
help:
	@echo "Available targets:"
	@echo "  install       - Install the package and dependencies"
	@echo "  install-dev   - Install package with development dependencies"
	@echo "  test          - Run the test suite"
	@echo "  test-unit     - Run unit tests only"
	@echo "  test-integration  - Run integration tests only"
	@echo "  test-cov      - Run tests with coverage report"
	@echo "  lint          - Run all code quality checks"
	@echo "  format        - Format code with black and isort"
	@echo "  format-check  - Check if code is formatted"
	@echo "  clean         - Clean build artifacts"
	@echo "  build         - Build the package"
	@echo "  run           - Run the application"
	@echo "  serve         - Start the FastAPI server"
	@echo "  docs          - Generate documentation"
	@echo "  pre-commit    - Install pre-commit hooks"
	@echo "  check-deps    - Check for security vulnerabilities"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

# Testing
test:
	pytest src/tests/ -v

test-unit:
	pytest src/tests/unit/ -v

test-integration:
	pytest src/tests/integration/ -v

test-cov:
	pytest src/tests/ --cov=src --cov-report=html --cov-report=term-missing

# Code quality
lint:
	@echo "Running code quality checks..."
	black --check src/
	isort --check-only src/
	flake8 src/
	mypy src/
	bandit -r src/

format:
	@echo "Formatting code..."
	black src/
	isort src/

format-check:
	@echo "Checking code formatting..."
	black --check src/
	isort --check-only src/

# Build and deployment
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

build: clean
	@echo "Building package..."
	python setup.py sdist bdist_wheel

run:
	@echo "Running application..."
	python -m mcp.fastapi_app.main

serve:
	@echo "Starting FastAPI server..."
	uvicorn mcp.fastapi_app.main:app --reload --host 0.0.0.0 --port 8000

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "Documentation is in docs/README.md"
	@echo "API docs available at: http://localhost:8000/docs"

# Development helpers
pre-commit:
	pre-commit install
	pre-commit run --all-files

check-deps:
	@echo "Checking for security vulnerabilities..."
	pip-audit
	safety check

# Docker commands (if Docker is available)
docker-build:
	@echo "Building Docker image..."
	docker build -t cre-intelligence:latest .

docker-run:
	@echo "Running Docker container..."
	docker run -p 8000:8000 cre-intelligence:latest

# Data management
data-clean:
	@echo "Cleaning data directories..."
	rm -rf data/raw/*
	rm -rf data/processed/*
	rm -rf data/lexicon/*
	rm -rf data/cache/*

data-init:
	@echo "Initializing data directories..."
	mkdir -p data/raw data/processed data/lexicon data/cache
	mkdir -p config

# Database
db-init:
	@echo "Initializing database..."
	alembic upgrade head

db-migrate:
	@echo "Creating new migration..."
	alembic revision --autogenerate -m "New migration"

db-rollback:
	@echo "Rolling back last migration..."
	alembic downgrade -1

# Performance monitoring
perf-profile:
	@echo "Running performance profiling..."
	python -m cProfile -o profile_output.prof src/scripts/run_pipeline.py
	python -m pstats profile_output.prof

# Monitoring
monitor-start:
	@echo "Starting monitoring services..."
	prometheus --config.file=monitoring/prometheus.yml &
	grafana-server --config=monitoring/grafana.ini --homepath=monitoring

# Utility commands
status:
	@echo "Project status:"
	@echo "Python version: $(shell python --version)"
	@echo "Virtual env: $(shell which python)"
	@echo "Git branch: $(shell git rev-parse --abbrev-ref HEAD)"
	@echo "Git status: $(shell git status --porcelain)"

deps-tree:
	@echo "Dependency tree:"
	pipdeptree --graphviz | dot -Tpng -o deps.png

# Quick development setup
setup-dev: install-dev pre-commit data-init db-init
	@echo "Development environment setup complete!"
	@echo "Run 'make serve' to start the server"

# Production deployment prep
prod-check: lint test check-deps
	@echo "Production checks passed!"

prod-build: prod-check build
	@echo "Production build complete!"
