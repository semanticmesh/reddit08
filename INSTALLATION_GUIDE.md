# CRE Intelligence Platform Installation Guide

## Overview

This guide will walk you through the complete installation and setup process for the CRE Intelligence Platform. The platform is a sophisticated system for gathering and analyzing commercial real estate intelligence from Reddit and social media sources.

## Current Installation Status

Based on the inspection of your project directory, the following components are already in place:

### ✅ Project Structure
- ✅ Repository cloned to `C:\Users\pigna\yuandao\reddit08`
- ✅ All source code in `src/` directory
- ✅ Configuration files (`.env`, `docker-compose.yml`, `Dockerfile`)
- ✅ Dependencies defined in `requirements.txt`
- ✅ Database initialization script in `scripts/init-db.sql`

### ✅ Dependencies
- ✅ `requirements.txt` with all necessary Python packages
- ✅ `Makefile` with build, test, and deployment commands
- ✅ `setup.py` for package installation

### ✅ Container Setup
- ✅ Docker configuration with multi-stage builds
- ✅ Docker Compose for full stack deployment (PostgreSQL, Redis, Celery)
- ✅ Nginx configuration for reverse proxy

## Prerequisites

Before you begin, ensure you have the following installed:

### System Requirements
- Python 3.8 or higher
- PostgreSQL 12 or higher
- Redis 6.0 or higher
- Git

### Development Tools (Recommended)
- Virtual environment (venv, conda, etc.)
- Docker and Docker Compose (for containerized deployment)

## Installation Options

The CRE Intelligence Platform can be installed in two ways:
1. **Docker Deployment** (Recommended for production)
2. **Local Development Setup** (For development and testing)

## Option 1: Docker Deployment (Recommended)

### Prerequisites for Docker Deployment
- Docker Engine 20.10 or higher
- Docker Compose 1.29 or higher
- At least 8GB RAM and 20GB free disk space

### Step 1: Configure Environment Variables

Create a `.env` file for Docker deployment:

```bash
# Copy the Docker environment template
cp .env.docker .env

# Edit the .env file with your configuration
# For production:
# 1. Set secure API keys
# 2. Configure database credentials
# 3. Adjust application settings
```

Edit `.env` file with your specific settings:

```env
# Docker-specific environment variables for Reddit08 CRE Intelligence Platform

# Database configuration
DATABASE_URL=postgresql://user:password@postgres:5432/reddit08_db

# Redis configuration
REDIS_URL=redis://redis:6379/0

# API Keys - IMPORTANT: Set these with real values
OPENAI_API_KEY=your_openai_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
NEWS_API_KEY=your_news_api_key_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here

# Application settings
DEBUG=false
LOG_LEVEL=INFO
MAX_WORKERS=4

# Data directories
DATA_DIR=/app/data
LOGS_DIR=/app/logs
CONFIG_DIR=/app/config

# Security
SECRET_KEY=your_secret_key_here_change_this_in_production

# CORS settings
CORS_ORIGINS=["http://localhost:8000", "http://localhost:3000", "http://127.0.0.1:8000"]

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Celery configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
CELERY_ACCEPT_CONTENT=['json']

# File upload settings
MAX_UPLOAD_SIZE=10485760  # 10MB
UPLOAD_EXTENSIONS=['.csv', '.xlsx', '.json']

# Intelligence service settings
INTELLIGENCE_ENABLED=true
INTELLIGENCE_CACHE_TTL=3600  # 1 hour in seconds
INTELLIGENCE_MAX_CONCURRENT_REQUESTS=10

# Monitoring and logging
SENTRY_DSN=your_sentry_dsn_here
LOG_FILE_LEVEL=INFO
LOG_CONSOLE_LEVEL=DEBUG
```

### Step 2: Build and Start Services

```bash
# Build and start all services in detached mode
docker-compose up -d

# View logs for a specific service
docker-compose logs -f app

# View logs for all services
docker-compose logs -f
```

### Step 3: Verify Docker Deployment

```bash
# Check if all services are running
docker-compose ps

# Expected output should show all services as "Up"
# - reddit08-cre-platform
# - reddit08-postgres
# - reddit08-redis
# - reddit08-celery
# - reddit08-celery-beat
# - reddit08-nginx

# Test the API
curl http://localhost:8000/health

# Access API documentation
# Open http://localhost:8000/docs in your browser
```

### Step 4: Access Services

Once deployed, the following services will be available:

- **FastAPI Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL Database**: localhost:5432
- **Redis Cache**: localhost:6379
- **Nginx Proxy**: http://localhost (port 80)

### Docker Deployment Management

```bash
# Stop all services
docker-compose down

# Stop services but keep volumes (data preserved)
docker-compose down --volumes

# Restart services
docker-compose restart

# Rebuild services after making changes
docker-compose up -d --build

# View resource usage
docker stats

# Execute commands in running containers
docker-compose exec app bash
docker-compose exec postgres psql -U user -d reddit08_db
```

## Option 2: Local Development Setup

### Step 1: Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

### Step 2: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install package in development mode with extras
pip install -e ".[dev]"

# Install pre-commit hooks for code quality
pre-commit install
```

### Step 3: Configure Environment Variables

```bash
# Copy the environment template
cp .env.example .env

# Edit the .env file with your configuration
# For development:
# 1. Set PostgreSQL connection details
# 2. Add your API keys
# 3. Configure application settings
```

Edit `.env` file with your specific settings:

```env
# PostgreSQL Configuration
# Environment variables take precedence over these values

# Database connection settings
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=reddit08
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# Connection pool settings
POSTGRES_POOL_SIZE=10
POSTGRES_MAX_OVERFLOW=20
POSTGRES_POOL_TIMEOUT=30

# SSL settings
POSTGRES_SSL_MODE=prefer
POSTGRES_SSL_CERT_FILE=
POSTGRES_SSL_KEY_FILE=

# Connection settings
POSTGRES_ECHO=false
POSTgreSQL_POOL_RECYCLE=3600

# Database setup settings
POSTGRES_CREATE_DB=true
POSTGRES_CREATE_EXTENSION=true
```

### Step 4: Set Up Database

#### Option A: Using the Setup Script
```bash
# Run the setup script
python setup.py
```

#### Option B: Manual Setup
```bash
# Create database directory structure
mkdir -p data/raw data/processed data/cache data/lexicon logs

# Initialize PostgreSQL database
# Connect to PostgreSQL and create database:
createdb reddit08

# Run migrations (if using Alembic)
alembic upgrade head
```

### Step 5: Start Development Services

```bash
# Start FastAPI server with auto-reload
make serve

# Or directly:
uvicorn src.mcp.fastapi_app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 6: Verify Installation

```bash
# Run tests to verify everything is working
make test

# Check code quality
make lint

# Start the development server
make serve
```

## Configuration Details

### API Keys Required

1. **OpenAI API Key** - For AI-powered intelligence analysis
2. **Reddit API Credentials** - For accessing Reddit data
   - Client ID and Client Secret
   - OAuth setup for Reddit API access
3. **News API Key** - For news data integration
4. **Twitter Bearer Token** - For Twitter data integration

### Database Configuration

The platform uses PostgreSQL as the primary database:

```env
# Connection settings
DATABASE_URL=postgresql://user:password@localhost:5432/reddit08

# Connection pool settings
POSTGRES_POOL_SIZE=10
POSTGRES_MAX_OVERFLOW=20
```

### Redis Configuration

Redis is used for caching and task queue:

```env
# Redis configuration
REDIS_URL=redis://localhost:6379/0
```

## Running the Platform

### Development Mode

```bash
# Start FastAPI server with auto-reload
make serve

# Or directly:
uvicorn src.mcp.fastapi_app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Build and run with Docker
make docker-build
make docker-run

# Or using Docker Compose
docker-compose up -d
```

### Testing the API

Once the server is running, you can access:

- **API Documentation**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Data Directory Structure

The platform creates the following directory structure:

```
data/
├── raw/          # Raw collected data from Reddit and other sources
├── processed/    # Processed and analyzed data
├── cache/        # Redis cache and temporary files
├── lexicon/      # Vocabulary and classification data
└── logs/         # Application logs
```

## Common Commands

### Development
```bash
# Install dependencies
make install

# Run tests
make test

# Code formatting
make format

# Code quality checks
make lint

# Build package
make build
```

### Data Management
```bash
# Clean data directories
make data-clean

# Initialize data directories
make data-init

# Backup data
python src/scripts/utility_scripts.py --backup
```

### Database Operations
```bash
# Initialize database
make db-init

# Create migration
make db-migrate

# Rollback migration
make db-rollback
```

## Service Startup Procedures

### Docker Services Startup Order

1. **PostgreSQL Database** - Starts first as other services depend on it
2. **Redis Cache** - Starts second for caching and task queue
3. **FastAPI Application** - Main application service
4. **Celery Worker** - Background task processing
5. **Celery Beat** - Scheduled task scheduler
6. **Nginx Proxy** - Reverse proxy for external access

### Local Development Services

1. **PostgreSQL Database** - Ensure PostgreSQL is running locally
2. **Redis Cache** - Ensure Redis is running locally
3. **FastAPI Application** - Start with `make serve` or `uvicorn`

## Post-Installation Setup

### 1. Configure Data Sources

Add your data source configurations in `config/cities.yml`:

```yaml
metros:
  nyc:
    subreddits: 
      - r/nyc
      - r/nycrealestate
    keywords:
      - manhattan
      - brooklyn
      - nyc
    heuristics:
      rent_unit: psf
      market_type: high_density
      price_tier: premium
```

### 2. Initialize Lexicon

```bash
# Initialize vocabulary and classification data
python src/scripts/refresh_tfidf_via_mcp.py --corpus last_month --top-k 150
```

### 3. Set Up Scheduled Jobs

```bash
# Start the scheduler for automated data collection
python src/scripts/schedule_jobs.py
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check .env file settings
   - Ensure database exists

2. **Import Errors**
   - Verify Python path includes project root
   - Check virtual environment activation
   - Reinstall dependencies with `pip install -r requirements.txt`

3. **API Key Issues**
   - Verify API keys are correctly set in .env
   - Check API key validity and rate limits
   - Ensure proper authentication setup

4. **Docker Service Issues**
   - Check if Docker daemon is running
   - Verify sufficient system resources
   - Check Docker logs with `docker-compose logs`

### Getting Help

1. **Check Logs**
   ```bash
   # View application logs
   tail -f logs/app.log
   
   # View Docker service logs
   docker-compose logs -f app
   ```

2. **Debug Mode**
   ```bash
   # Run with debug logging
   DEBUG=true make serve
   
   # For Docker:
   # Set DEBUG=true in .env file
   ```

3. **Health Check**
   ```bash
   # Check system health
   curl http://localhost:8000/health
   ```

4. **Service Status**
   ```bash
   # Check Docker service status
   docker-compose ps
   
   # Check local service processes
   ps aux | grep python
   ```

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs to see available endpoints
2. **Run Intelligence Workflows**: Try the BMAD stories for automated analysis
3. **Configure Data Sources**: Add your target cities and market verticals
4. **Set Up Monitoring**: Configure Prometheus and Grafana for monitoring

## Support

For additional support, refer to:
- [Full Documentation](./docs/README.md)
- [API Documentation](http://localhost:8000/docs)
- [Issue Tracker](https://github.com/your-org/reddit08/issues)
