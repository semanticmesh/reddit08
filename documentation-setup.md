# CRE Intelligence Platform - Complete Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Quick Start Guide](#quick-start-guide)
3. [Installation Guide](#installation-guide)
4. [Configuration Guide](#configuration-guide)
5. [Usage Guide](#usage-guide)
6. [API Documentation](#api-documentation)
7. [Goose Integration](#goose-integration)
8. [BMAD Workflow](#bmad-workflow)
9. [MCP Server Guide](#mcp-server-guide)
10. [Deployment Guide](#deployment-guide)
11. [Troubleshooting](#troubleshooting)
12. [Contributing](#contributing)

---

## System Overview

The CRE Intelligence Platform is a comprehensive system for gathering, processing, and analyzing commercial real estate intelligence from Reddit and other social media sources. It combines AI-powered orchestration (Goose), structured workflows (BMAD), and specialized processing tools (MCP servers) to deliver actionable insights.

### Key Components

- **Goose**: Primary orchestrator for interactive AI workflows
- **BMAD**: Structured story-based task management
- **FastAPI MCP**: RESTful API and MCP server for data processing
- **Native MCP**: WebSocket-based MCP server
- **Git MCP**: Version-controlled knowledge base
- **MCP Use**: Automation library for headless execution

### Six Core Intelligence Techniques

1. **Iterative JSON Refinement**: Optimizes Apify Actor payloads
2. **TF-IDF Phrase Mining**: Extracts domain-specific terminology
3. **Client-Side Filtering**: 6-stage quality control pipeline
4. **Local-Sub Targeting**: Geographic subreddit discovery
5. **Vertical Specialization**: Market segment analysis
6. **Dual-Sort Strategy**: Comprehensive coverage with backfill

---

## Quick Start Guide

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Git
- 8GB RAM minimum
- 50GB disk space

### 5-Minute Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/cre-intelligence.git
cd cre-intelligence

# 2. Copy environment configuration
cp .env.example .env
# Edit .env with your API keys

# 3. Start services with Docker
docker-compose up -d

# 4. Verify services are running
curl http://localhost:8000/  # FastAPI
curl http://localhost:3000/  # Grafana
curl http://localhost:9090/  # Prometheus

# 5. Run your first intelligence gathering
python scripts/run_full_pipeline.py --metros nyc sf --verticals office retail
```

---

## Installation Guide

### Option 1: Docker Installation (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f fastapi-mcp

# Stop services
docker-compose down

# Remove all data (careful!)
docker-compose down -v
```

### Option 2: Local Development Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .  # Install package in development mode

# Install additional development tools
pip install black flake8 mypy pytest

# Set up pre-commit hooks
pre-commit install

# Initialize database
alembic upgrade head

# Start services individually
uvicorn mcp.fastapi_app.main:app --reload --port 8000  # FastAPI
python -m mcp.native_server.server --port 8001  # Native MCP
celery -A mcp.tasks worker --loglevel=info  # Celery worker
celery -A mcp.tasks beat --loglevel=info  # Celery beat
```

### Option 3: Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace cre-intelligence

# Apply configurations
kubectl apply -f kubernetes/

# Check deployment status
kubectl get pods -n cre-intelligence

# Port forward for local access
kubectl port-forward -n cre-intelligence svc/fastapi-mcp 8000:8000
```

---

## Configuration Guide

### Environment Variables

Create a `.env` file with the following variables:

```bash
# API Keys (Required)
OPENAI_API_KEY=sk-...
APIFY_API_KEY=apify_api_...
REDDIT_CLIENT_ID=your_reddit_app_id
REDDIT_CLIENT_SECRET=your_reddit_secret

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/cre_intelligence
REDIS_URL=redis://localhost:6379

# MCP Server URLs
FASTAPI_MCP_URL=http://localhost:8000
BMAD_MCP_URL=ws://localhost:8001/mcp
REDDIT_MCP_URL=ws://localhost:8002/mcp

# Application Settings
ENVIRONMENT=development  # or production
DEBUG=true
LOG_LEVEL=INFO

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
```

### Configuration Files

#### `config/settings.yml`
```yaml
app:
  name: CRE Intelligence Platform
  version: 1.0.0

data:
  batch_size: 1000
  max_workers: 4

quality:
  min_text_length: 50
  max_text_length: 10000
  min_relevance_score: 0.3
```

#### `config/cities.yml`
```yaml
metros:
  tier_1:
    nyc:
      subreddits: [r/nyc, r/manhattan]
      keywords: [manhattan, brooklyn, queens]
    sf:
      subreddits: [r/sanfrancisco, r/bayarea]
      keywords: [soma, fidi, mission bay]
```

#### `config/filters.yml`
```yaml
keywords:
  must_any: [lease, rent, tenant, landlord]
  exclude: [residential only, apartment hunt]
```

---

## Usage Guide

### Running Individual Techniques

#### 1. Payload Optimization
```bash
python scripts/optimize_payload.py \
  --subreddits nyc sf chicago \
  --keywords "office lease" "retail space" \
  --start 2024-01-01 \
  --end 2024-01-31
```

#### 2. Phrase Mining
```bash
python scripts/refresh_tfidf_via_mcp.py \
  --corpus last_month \
  --top-k 100 \
  --categories financial legal operational
```

#### 3. Post Filtering
```bash
python scripts/run_filter_via_mcp.py \
  --start 2024-01-01 \
  --end 2024-01-31 \
  --keywords lease rent commercial \
  --city nyc \
  --output data/filtered/
```

#### 4. Geographic Targeting
```bash
python scripts/expand_cities_via_mcp.py \
  nyc sf chicago boston \
  --keywords "commercial real estate" "office space"
```

#### 5. Vertical Specialization
```bash
curl -X POST http://localhost:8000/specialize_verticals \
  -H "Content-Type: application/json" \
  -d '{
    "verticals": ["office", "retail", "industrial"],
    "custom_lexicons": {},
    "conflict_resolution": true
  }'
```

#### 6. Dual-Sort Strategy
```bash
curl -X POST http://localhost:8000/execute_dual_sort \
  -H "Content-Type: application/json" \
  -d '{
    "timeframe_days": 30,
    "sort_strategies": ["new", "relevance"],
    "deduplication": true,
    "backfill_months": 3
  }'
```

### Running the Complete Pipeline

```bash
# Basic pipeline execution
python scripts/run_full_pipeline.py

# With custom parameters
python scripts/run_full_pipeline.py \
  --metros nyc sf chicago la boston \
  --verticals office retail industrial multifamily \
  --start 2024-01-01 \
  --end 2024-01-31 \
  --output reports/

# Scheduled execution
python scripts/schedule_jobs.py  # Runs continuously
```

---

## API Documentation

### FastAPI Endpoints

The FastAPI server provides RESTful endpoints for all six techniques:

#### Base URL
```
http://localhost:8000
```

#### Authentication
```bash
# Add to request headers
Authorization: Bearer YOUR_API_KEY
```

#### Endpoints

##### Health Check
```http
GET /
```

##### Optimize Payload
```http
POST /optimize_payload
Content-Type: application/json

{
  "subreddits": ["r/nyc", "r/commercialrealestate"],
  "keywords": ["lease", "rent", "tenant"],
  "date_start": "2024-01-01",
  "date_end": "2024-01-31",
  "max_url_length": 512,
  "optimization_rounds": 3
}
```

##### Mine Phrases
```http
POST /mine_phrases
Content-Type: application/json

{
  "corpus_source": "last_month",
  "ngram_range": [1, 3],
  "top_k": 100,
  "domain_categories": ["financial", "legal", "operational"]
}
```

##### Filter Posts
```http
POST /filter_posts
Content-Type: application/json

{
  "date_start": "2024-01-01",
  "date_end": "2024-01-31",
  "keywords": ["office", "lease"],
  "exclude_keywords": ["residential"],
  "quality_thresholds": {
    "min_length": 50,
    "max_length": 10000,
    "min_score": 1
  },
  "semantic_similarity_threshold": 0.4,
  "city": "nyc"
}
```

##### Full Pipeline
```http
POST /execute_full_pipeline
Content-Type: application/json

{
  "metros": ["nyc", "sf", "chicago"],
  "verticals": ["office", "retail", "industrial"],
  "date_start": "2024-01-01",
  "date_end": "2024-01-31"
}
```

### Interactive API Documentation

Access Swagger UI at: `http://localhost:8000/docs`
Access ReDoc at: `http://localhost:8000/redoc`

---

## Goose Integration

### Configuring Goose

1. **Install Goose**
```bash
pip install goose-ai
```

2. **Configure Extensions**

Edit `~/.config/goose/config.yaml`:
```yaml
projects:
  cre-intelligence:
    base_path: "/path/to/cre-intelligence"
    default_extensions:
      - fastapi-mcp
      - git-mcp
      
extensions:
  fastapi-mcp:
    type: mcp_server
    server_url: "http://localhost:8000"
    
  git-mcp:
    type: git_repository
    repo_path: "/path/to/cre-intelligence"
```

3. **Start Goose Session**
```bash
goose session start --project cre-intelligence
```

### Using Goose Sessions

#### Market Assessment Session
```
goose> Load market assessment template for NYC office market
goose> Set assessment period to last 30 days
goose> Execute data collection phase
goose> Analyze trends and patterns
goose> Generate executive report
```

#### Competitive Intelligence Session
```
goose> Identify competitors in Chicago retail market
goose> Analyze competitor mentions in last quarter
goose> Compare market positioning
goose> Generate competitive landscape report
```

---

## BMAD Workflow

### Understanding BMAD Stories

BMAD (Business Model Agile Development) organizes work into stories with specific roles and acceptance criteria.

### Story Structure

```yaml
id: CRE-SI-01
name: Query Architect
role: QueryArchitect
tasks:
  - design_minimal_boolean_clauses
  - emit_reddit_actor_payloads
acceptance:
  - payloads saved to data/processed/payloads/
  - each clause < 256 chars
```

### Executing Stories

```bash
# Execute a specific story
python -m bmad.story_executor --story CRE-SI-01

# Execute all stories in a sprint
python -m bmad.sprint_planner --sprint current

# View story status
python -m bmad.story_status
```

### Sprint Planning

```bash
# Create new sprint
python -m bmad.sprint_planner create \
  --start 2024-02-01 \
  --duration 7 \
  --stories CRE-SI-01 CRE-SI-02 CRE-SI-03

# Review sprint progress
python -m bmad.sprint_review --sprint current
```

---

## MCP Server Guide

### Native MCP Server

The native MCP server provides WebSocket access to all intelligence tools.

#### Starting the Server
```bash
python -m mcp.native_server.server --host 0.0.0.0 --port 8001
```

#### Connecting with WebSocket
```python
import websockets
import json

async def call_mcp_tool():
    async with websockets.connect("ws://localhost:8001") as ws:
        # List available tools
        await ws.send(json.dumps({
            "id": "1",
            "method": "tools.list",
            "params": {}
        }))
        
        response = await ws.recv()
        print(f"Available tools: {response}")
        
        # Call a specific tool
        await ws.send(json.dumps({
            "id": "2",
            "method": "tools.call",
            "params": {
                "name": "filter_posts",
                "params": {
                    "date_start": "2024-01-01",
                    "date_end": "2024-01-31",
                    "keywords": ["lease"]
                }
            }
        }))
        
        result = await ws.recv()
        print(f"Result: {result}")
```

### FastAPI MCP Integration

The FastAPI server can be accessed as an MCP server through the MCP adapter.

```python
from mcp_use import MCPClient

client = MCPClient("http://localhost:8000")
await client.connect()

# Call any tool
result = await client.call_tool("mine_phrases", {
    "corpus_source": "last_month",
    "top_k": 100
})
```

---

## Deployment Guide

### Production Deployment Checklist

#### 1. Environment Preparation
- [ ] Set all production environment variables
- [ ] Configure SSL certificates
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategies
- [ ] Set up log aggregation

#### 2. Database Setup
- [ ] Create production database
- [ ] Run migrations
- [ ] Set up replication
- [ ] Configure backups
- [ ] Test restore procedures

#### 3. Security
- [ ] Enable firewall rules
- [ ] Configure API authentication
- [ ] Set up rate limiting
- [ ] Enable audit logging
- [ ] Scan for vulnerabilities

#### 4. Monitoring
- [ ] Configure Prometheus metrics
- [ ] Set up Grafana dashboards
- [ ] Configure alerting rules
- [ ] Set up error tracking
- [ ] Enable performance monitoring

#### 5. Deployment
- [ ] Build Docker images
- [ ] Push to registry
- [ ] Deploy to Kubernetes/ECS
- [ ] Verify health checks
- [ ] Run smoke tests

### AWS Deployment

```bash
# Build and push Docker image
docker build -t cre-intelligence:latest .
docker tag cre-intelligence:latest YOUR_ECR_REPO:latest
docker push YOUR_ECR_REPO:latest

# Deploy with Terraform
cd deployment/terraform
terraform init
terraform plan
terraform apply

# Update ECS service
aws ecs update-service \
  --cluster cre-intelligence \
  --service fastapi-mcp \
  --force-new-deployment
```

### Kubernetes Deployment

```bash
# Build and push image
docker build -t your-registry/cre-intelligence:v1.0.0 .
docker push your-registry/cre-intelligence:v1.0.0

# Deploy to Kubernetes
kubectl apply -f kubernetes/

# Check deployment
kubectl rollout status deployment/fastapi-mcp -n cre-intelligence

# Scale deployment
kubectl scale deployment/fastapi-mcp --replicas=5 -n cre-intelligence
```

---

## Troubleshooting

### Common Issues

#### 1. FastAPI Server Won't Start
```bash
# Check logs
docker-compose logs fastapi-mcp

# Common fixes:
# - Check DATABASE_URL is correct
# - Ensure Redis is running
# - Verify Python dependencies installed
```

#### 2. MCP Connection Failed
```bash
# Test MCP server
curl -X POST http://localhost:8000/

# Check WebSocket connection
wscat -c ws://localhost:8001

# Verify firewall rules
sudo ufw status
```

#### 3. Database Connection Issues
```bash
# Test PostgreSQL connection
psql -h localhost -U cre_user -d cre_intelligence

# Check PostgreSQL logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d
alembic upgrade head
```

#### 4. Memory Issues
```bash
# Check memory usage
docker stats

# Increase Docker memory limit
# Edit Docker Desktop settings or:
docker update --memory 4g container_name

# Optimize batch sizes in config/settings.yml
```

#### 5. Slow Performance
```bash
# Check Redis
redis-cli ping

# Monitor query performance
python -m monitoring.performance

# Enable query caching
# Set in .env: ENABLE_CACHE=true
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG

# Or via command line
DEBUG=true uvicorn mcp.fastapi_app.main:app --log-level debug
```

### Health Checks

```bash
# Check all services
./scripts/health_check.sh

# Manual checks
curl http://localhost:8000/health  # FastAPI
curl http://localhost:3000/api/health  # Grafana
curl http://localhost:9090/-/healthy  # Prometheus
```

---

## Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Set up development environment
4. Make changes with tests
5. Submit pull request

### Code Style

```bash
# Format code
black .
isort .

# Run linters
flake8 .
mypy .

# Run tests
pytest tests/ -v --cov=.
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_filtering.py

# Run with coverage
pytest --cov=mcp --cov-report=html

# Run integration tests
pytest tests/integration/ -v
```

### Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers

### Release Process

```bash
# Update version
bump2version minor  # or major, patch

# Create release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Build and publish
python setup.py sdist bdist_wheel
twine upload dist/*
```

---

## Support

### Getting Help

- **Documentation**: This guide and inline code documentation
- **Issues**: GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for questions and ideas
- **Email**: support@cre-intelligence.com
- **Slack**: Join our community workspace

### Reporting Issues

When reporting issues, please include:

1. System information (OS, Python version, Docker version)
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Relevant logs
6. Configuration files (sanitized)

### Feature Requests

Submit feature requests through GitHub Issues with:

1. Use case description
2. Proposed solution
3. Alternative solutions considered
4. Impact on existing functionality

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## Acknowledgments

- Anthropic for Claude and MCP protocol
- OpenAI for GPT models
- Reddit API for data access
- Open source community for contributions

---

## Appendix

### Glossary

- **BMAD**: Business Model Agile Development
- **CRE**: Commercial Real Estate
- **MCP**: Model Context Protocol
- **TF-IDF**: Term Frequency-Inverse Document Frequency
- **CAM**: Common Area Maintenance
- **NNN**: Triple Net Lease
- **NOI**: Net Operating Income

### Resources

- [MCP Documentation](https://github.com/anthropics/mcp)
- [Goose Documentation](https://github.com/goose-ai/goose)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Reddit API Documentation](https://www.reddit.com/dev/api)
- [Docker Documentation](https://docs.docker.com)
- [Kubernetes Documentation](https://kubernetes.io/docs)

### Performance Benchmarks

| Operation | Target | Actual |
|-----------|--------|--------|
| Payload Optimization | <30s | 15s |
| Phrase Mining (10k posts) | <60s | 45s |
| Filtering (100k posts) | <120s | 90s |
| Full Pipeline | <5min | 4min |

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Storage | 50 GB | 200 GB |
| Network | 10 Mbps | 100 Mbps |

---

*Last Updated: 2024*
*Version: 1.0.0*