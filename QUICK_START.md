# CRE Intelligence Platform Quick Start Guide

## Overview

This guide provides the fastest path to getting the CRE Intelligence Platform up and running. Choose either Docker deployment (recommended) or local development setup.

## Option 1: Docker Deployment (Fastest)

### Prerequisites
- Docker and Docker Compose installed

### Steps
```bash
# 1. Configure environment
cp .env.docker .env
# Edit .env with your API keys

# 2. Start all services
docker-compose up -d

# 3. Verify installation
docker-compose ps
curl http://localhost:8000/health

# 4. Access the platform
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

**Time to run: ~5-10 minutes**

## Option 2: Local Development Setup

### Prerequisites
- Python 3.8+, PostgreSQL, Redis installed

### Steps
```bash
# 1. Set up virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Start development server
make serve

# 5. Access the platform
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

**Time to run: ~10-15 minutes**

## Required Configuration

### Essential API Keys
Add these to your `.env` file:

```env
# For Docker (.env.docker) or Local (.env.example)
OPENAI_API_KEY=your_openai_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
```

## Verification Steps

### Check Services
```bash
# For Docker:
docker-compose ps

# For Local:
ps aux | grep postgres
ps aux | grep redis
```

### Test API
```bash
# Health check
curl http://localhost:8000/health

# API documentation
# Open in browser: http://localhost:8000/docs
```

## Common Next Steps

1. **Configure Data Sources** in `config/cities.yml`
2. **Initialize Lexicon** with `python src/scripts/refresh_tfidf_via_mcp.py`
3. **Run Sample Pipeline** with `python src/scripts/run_full_pipeline.py`

## Troubleshooting

### If services don't start:
```bash
# Check logs
docker-compose logs  # For Docker
tail -f logs/app.log  # For Local
```

### If API is not accessible:
```bash
# Check if service is running
netstat -an | grep 8000
```

## Support

- Full Documentation: [docs/README.md](./docs/README.md)
- Installation Guide: [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md)
- API Documentation: http://localhost:8000/docs