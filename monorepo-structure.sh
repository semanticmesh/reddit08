#!/bin/bash
# Complete CRE Intelligence Platform Monorepo Structure
# This script creates the entire directory structure and essential files

# Create the monorepo
mkdir -p cre-intelligence && cd cre-intelligence

# Initialize git repository
git init

# Create root configuration files
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
*.egg-info/
dist/
build/

# Data
data/raw/*
data/processed/*
data/cache/*
!data/raw/.gitkeep
!data/processed/.gitkeep
!data/cache/.gitkeep

# Secrets
.env
*.key
*.pem
secrets/

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Logs
logs/
*.log

# Testing
.coverage
.pytest_cache/
htmlcov/

# Docker
.dockerignore
EOF

cat > .env.example << 'EOF'
# API Keys
OPENAI_API_KEY=your_openai_key_here
APIFY_API_KEY=your_apify_key_here
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/cre_intelligence
REDIS_URL=redis://localhost:6379

# MCP Servers
BMAD_MCP_URL=ws://localhost:8001/mcp
REDDIT_MCP_URL=ws://localhost:8002/mcp
PHRASE_MCP_URL=ws://localhost:8003/mcp
MARKET_MCP_URL=ws://localhost:8004/mcp
GEO_MCP_URL=ws://localhost:8005/mcp
APIFY_MCP_URL=ws://localhost:8006/mcp

# FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_WORKERS=4

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
EOF

cat > README.md << 'EOF'
# CRE Intelligence Platform

A comprehensive Commercial Real Estate intelligence gathering and analysis platform that combines Reddit social monitoring with advanced NLP and geographic analysis.

## 🏗️ Architecture

The platform implements a four-plane architecture:
- **Orchestration Plane**: Goose for interactive AI workflows
- **Structure Plane**: BMAD for organized story execution
- **Processing Plane**: FastAPI MCP for data processing tools
- **Knowledge Plane**: Git MCP for persistent context

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Redis
- PostgreSQL

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/cre-intelligence.git
cd cre-intelligence
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Start services:
```bash
docker-compose up -d
```

6. Run FastAPI MCP server:
```bash
uvicorn mcp.fastapi_app.main:app --reload --port 8000
```

## 📊 Six Intelligence Techniques

1. **Iterative JSON Refinement**: Optimize Apify Actor payloads
2. **TF-IDF Phrase Mining**: Extract domain-specific terminology
3. **Client-Side Filtering**: 6-stage quality control pipeline
4. **Local-Sub Targeting**: Geographic subreddit discovery
5. **Vertical Specialization**: Market segment analysis
6. **Dual-Sort Strategy**: Comprehensive coverage with backfill

## 🛠️ Development

### Running Tests
```bash
pytest tests/ -v --cov=.
```

### Code Quality
```bash
black .
flake8 .
mypy .
```

### Documentation
```bash
mkdocs serve
```

## 📈 Monitoring

Access dashboards:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- FastAPI Docs: http://localhost:8000/docs

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
EOF

cat > requirements.txt << 'EOF'
# Core Dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0

# Data Processing
pandas==2.1.3
numpy==1.24.3
scikit-learn==1.3.2

# Reddit & Scraping
praw==7.7.1
aiohttp==3.9.0
beautifulsoup4==4.12.2

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
redis==5.0.1

# MCP & Integration
websockets==12.0
httpx==0.25.2
mcp-python==0.1.0  # Replace with actual MCP library

# NLP & ML
nltk==3.8.1
spacy==3.7.2
transformers==4.35.2

# Task Queue
celery==5.3.4
flower==2.0.1

# Monitoring
prometheus-client==0.19.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
faker==20.1.0

# Code Quality
black==23.11.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.5.0

# Documentation
mkdocs==1.5.3
mkdocs-material==9.4.14

# Utilities
pyyaml==6.0.1
click==8.1.7
rich==13.7.0
python-multipart==0.0.6
EOF

cat > pyproject.toml << 'EOF'
[tool.poetry]
name = "cre-intelligence"
version = "1.0.0"
description = "Commercial Real Estate Intelligence Platform"
authors = ["Your Team <team@company.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.9"
fastapi = "^0.104.1"
pandas = "^2.1.3"
scikit-learn = "^1.3.2"
pydantic = "^2.5.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
black = "^23.11.0"
mypy = "^1.7.1"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ['py39']

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --cov=. --cov-report=html"
EOF

cat > Makefile << 'EOF'
.PHONY: help install test lint format run clean docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  install      Install dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run linters"
	@echo "  format       Format code"
	@echo "  run          Run FastAPI server"
	@echo "  clean        Clean generated files"
	@echo "  docker-up    Start Docker services"
	@echo "  docker-down  Stop Docker services"

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v --cov=.

lint:
	flake8 .
	mypy .

format:
	black .
	isort .

run:
	uvicorn mcp.fastapi_app.main:app --reload --port 8000

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Data pipeline commands
harvest:
	python scripts/harvest_reddit.py

filter:
	python scripts/run_filter_via_mcp.py

mine:
	python scripts/refresh_tfidf_via_mcp.py

analyze:
	python scripts/run_full_pipeline.py

# BMAD commands
sprint-plan:
	python -m bmad.sprint_planner

story-execute:
	python -m bmad.story_executor --story $(STORY)

# Monitoring
monitor:
	python -m monitoring.dashboard

logs:
	tail -f logs/cre-intelligence.log
EOF

# Create directory structure
mkdir -p {data/{raw,processed,lexicon,cache,archive},config,docs,bmad/{sprints,stories},mcp/{fastapi_app,native_server},scripts,n8n/workflows,tests/{unit,integration,e2e},monitoring,deployment,logs,.gitmcp}

# Create .gitkeep files for empty directories
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch data/cache/.gitkeep
touch data/archive/.gitkeep
touch logs/.gitkeep

# Create config files
cat > config/settings.yml << 'EOF'
# Global Settings Configuration
app:
  name: CRE Intelligence Platform
  version: 1.0.0
  environment: ${ENVIRONMENT}
  debug: ${DEBUG}

data:
  base_path: ./data
  raw_path: ./data/raw
  processed_path: ./data/processed
  lexicon_path: ./data/lexicon
  cache_path: ./data/cache

processing:
  batch_size: 1000
  max_workers: 4
  timeout_seconds: 300

quality:
  min_text_length: 50
  max_text_length: 10000
  min_relevance_score: 0.3
  dedup_threshold: 0.9

monitoring:
  metrics_port: 9090
  log_level: ${LOG_LEVEL}
  enable_tracing: true
EOF

cat > config/filters.yml << 'EOF'
# Filter Configuration
temporal:
  default_window: 30  # days
  max_lookback: 365  # days

keywords:
  must_any:
    - lease
    - rent
    - tenant
    - landlord
    - commercial
    - property
    - CAM
    - triple net
    - NNN

  should_have:
    - sublease
    - renewal
    - vacancy
    - absorption
    - cap rate
    - NOI

  exclude:
    - residential only
    - homeowner
    - apartment hunt
    - roommate

quality:
  min_score: 1
  min_comments: 0
  max_deleted_ratio: 0.2
EOF

cat > config/cities.yml << 'EOF'
# Geographic Configuration
metros:
  tier_1:
    nyc:
      subreddits:
        - r/nyc
        - r/CommercialRealEstate
        - r/manhattan
        - r/brooklyn
      keywords:
        - manhattan
        - brooklyn
        - queens
        - midtown
        - fidi
      heuristics:
        rent_unit: psf
        market_type: high_density

    sf:
      subreddits:
        - r/sanfrancisco
        - r/bayarea
        - r/oakland
      keywords:
        - soma
        - fidi
        - mission bay
        - silicon valley
      heuristics:
        rent_unit: psf
        market_type: tech_driven

    chicago:
      subreddits:
        - r/chicago
        - r/chicagosuburbs
      keywords:
        - loop
        - river north
        - west loop
      heuristics:
        rent_unit: psf
        market_type: mixed

  tier_2:
    - austin
    - boston
    - seattle
    - denver
    - miami

  tier_3:
    - portland
    - nashville
    - charlotte
    - phoenix
EOF

cat > config/verticals.yml << 'EOF'
# Vertical Market Configuration
verticals:
  office:
    keywords:
      primary:
        - office space
        - sublease
        - coworking
        - hybrid work
      secondary:
        - class a
        - class b
        - amenities
        - build-out
    metrics:
      - vacancy_rate
      - asking_rent
      - sublease_availability

  retail:
    keywords:
      primary:
        - retail space
        - storefront
        - shopping center
        - foot traffic
      secondary:
        - anchor tenant
        - inline space
        - pad site
        - qsr
    metrics:
      - sales_per_sqft
      - occupancy_cost
      - traffic_counts

  industrial:
    keywords:
      primary:
        - warehouse
        - distribution
        - logistics
        - last mile
      secondary:
        - clear height
        - dock doors
        - rail served
        - cold storage
    metrics:
      - availability_rate
      - net_absorption
      - lease_rates

  multifamily:
    keywords:
      primary:
        - apartment building
        - rental property
        - multifamily
        - occupancy
      secondary:
        - rent roll
        - cap rate
        - value-add
        - stabilized
    metrics:
      - occupancy_rate
      - rent_growth
      - concessions
EOF

# Create sprint templates
cat > bmad/sprints/sprint-template.yml << 'EOF'
# Sprint Template
sprint:
  number: ${SPRINT_NUMBER}
  start_date: ${START_DATE}
  end_date: ${END_DATE}
  
  goals:
    - ${GOAL_1}
    - ${GOAL_2}
    - ${GOAL_3}
  
  stories:
    - id: CRE-SI-01
      role: QueryArchitect
      priority: P0
      estimate: 3
      
    - id: CRE-SI-02
      role: PhraseMiner
      priority: P0
      estimate: 5
      
    - id: CRE-SI-03
      role: FilterEnforcer
      priority: P0
      estimate: 3
  
  acceptance_criteria:
    - All P0 stories completed
    - Test coverage > 80%
    - Documentation updated
    
  retrospective:
    what_went_well: []
    what_to_improve: []
    action_items: []
EOF

# Create test structure
cat > tests/__init__.py << 'EOF'
"""CRE Intelligence Platform Test Suite"""
EOF

cat > tests/conftest.py << 'EOF'
"""Pytest configuration and fixtures"""
import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    """Create test client for FastAPI app"""
    from mcp.fastapi_app.main import app
    return TestClient(app)

@pytest.fixture
def test_data():
    """Load test data fixtures"""
    return {
        "posts": [
            {
                "id": "test1",
                "title": "Office space for lease in Manhattan",
                "selftext": "Looking for tenant for Class A office space...",
                "subreddit": "nyc",
                "created_utc": 1700000000,
                "score": 42
            }
        ]
    }
EOF

# Create monitoring configuration
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['localhost:8000']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:6379']
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:5432']
EOF

# Create Docker configuration
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: cre_intelligence
      POSTGRES_USER: cre_user
      POSTGRES_PASSWORD: cre_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  fastapi:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://cre_user:cre_password@postgres:5432/cre_intelligence
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - postgres
    volumes:
      - ./:/app
    command: uvicorn mcp.fastapi_app.main:app --host 0.0.0.0 --port 8000 --reload

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/dashboards:/etc/grafana/provisioning/dashboards

volumes:
  redis_data:
  postgres_data:
  prometheus_data:
  grafana_data:
EOF

cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "mcp.fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Create GitHub Actions workflow
mkdir -p .github/workflows
cat > .github/workflows/ci.yml << 'EOF'
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run linting
      run: |
        flake8 .
        black --check .
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=.
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  docker:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t cre-intelligence:${{ github.sha }} .
    
    - name: Run Docker tests
      run: |
        docker run --rm cre-intelligence:${{ github.sha }} pytest tests/
EOF

echo "Monorepo structure created successfully!"
echo "Next steps:"
echo "1. cd cre-intelligence"
echo "2. python -m venv venv"
echo "3. source venv/bin/activate"
echo "4. pip install -r requirements.txt"
echo "5. cp .env.example .env and configure"
echo "6. docker-compose up -d"
echo "7. uvicorn mcp.fastapi_app.main:app --reload"