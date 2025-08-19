# CRE Intelligence Platform Installation Checklist

## Pre-Installation Requirements

### System Requirements
- [ ] Python 3.8 or higher installed
- [ ] PostgreSQL 12 or higher installed (for local setup)
- [ ] Redis 6.0 or higher installed (for local setup)
- [ ] Docker and Docker Compose installed (for Docker deployment)
- [ ] Git installed
- [ ] At least 8GB RAM and 20GB free disk space

### API Keys Required
- [ ] OpenAI API Key obtained
- [ ] Reddit API Client ID obtained
- [ ] Reddit API Client Secret obtained
- [ ] News API Key (optional)
- [ ] Twitter Bearer Token (optional)

## Installation Method Selection

### Docker Deployment (Recommended for Production)
- [ ] Chosen if deploying to production
- [ ] Chosen if wanting isolated environment
- [ ] Chosen if preferring simplified management

### Local Development Setup (For Development)
- [ ] Chosen if actively developing new features
- [ ] Chosen if needing detailed debugging
- [ ] Chosen if working offline

## Docker Deployment Checklist

### Environment Configuration
- [ ] Copied `.env.docker` to `.env`
- [ ] Configured API keys in `.env`
- [ ] Set secure database credentials
- [ ] Configured application settings

### Service Deployment
- [ ] Built and started services with `docker-compose up -d`
- [ ] Verified all services are running with `docker-compose ps`
- [ ] Confirmed services show as "Up":
  - [ ] reddit08-cre-platform
  - [ ] reddit08-postgres
  - [ ] reddit08-redis
  - [ ] reddit08-celery
  - [ ] reddit08-celery-beat
  - [ ] reddit08-nginx

### Verification
- [ ] Accessed http://localhost:8000/health successfully
- [ ] Accessed http://localhost:8000/docs successfully
- [ ] Verified API endpoints are accessible
- [ ] Checked service logs with `docker-compose logs`

## Local Development Setup Checklist

### Environment Setup
- [ ] Created virtual environment with `python -m venv venv`
- [ ] Activated virtual environment
- [ ] Upgraded pip with `python -m pip install --upgrade pip`

### Dependency Installation
- [ ] Installed dependencies with `pip install -r requirements.txt`
- [ ] Installed development dependencies with `pip install -e ".[dev]"`
- [ ] Installed pre-commit hooks with `pre-commit install`

### Environment Configuration
- [ ] Copied `.env.example` to `.env`
- [ ] Configured API keys in `.env`
- [ ] Set database connection details
- [ ] Configured application settings

### Database Setup
- [ ] Created data directories with `make data-init`
- [ ] Created database with `createdb reddit08` or equivalent
- [ ] Ran database migrations with `make db-init`

### Service Startup
- [ ] Started development server with `make serve`
- [ ] Verified server is running on http://localhost:8000
- [ ] Accessed API documentation at http://localhost:8000/docs

## Post-Installation Setup

### Data Source Configuration
- [ ] Configured target cities in `config/cities.yml`
- [ ] Configured market verticals
- [ ] Set up subreddit lists
- [ ] Defined keyword filters

### Lexicon Initialization
- [ ] Initialized vocabulary with `python src/scripts/refresh_tfidf_via_mcp.py`
- [ ] Verified lexicon files created in `data/lexicon/`

### Testing and Verification
- [ ] Ran tests with `make test`
- [ ] Checked code quality with `make lint`
- [ ] Verified all services are responsive
- [ ] Tested API endpoints with sample requests

## Common Issues Checklist

### If Services Won't Start
- [ ] Verified Docker daemon is running (for Docker deployment)
- [ ] Verified PostgreSQL is running (for local setup)
- [ ] Verified Redis is running (for local setup)
- [ ] Checked service logs for error messages
- [ ] Verified sufficient system resources

### If API is Not Accessible
- [ ] Verified service is running on correct port
- [ ] Checked firewall settings
- [ ] Verified network connectivity
- [ ] Confirmed API keys are correctly configured

### If Database Connection Fails
- [ ] Verified database service is running
- [ ] Checked database credentials in `.env`
- [ ] Confirmed database exists and is accessible
- [ ] Verified network connectivity to database

## Success Criteria

### Minimum Viable Installation
- [ ] Platform accessible at http://localhost:8000
- [ ] API documentation accessible at http://localhost:8000/docs
- [ ] Health check endpoint returns success at http://localhost:8000/health
- [ ] All required services are running without errors

### Full Installation
- [ ] All minimum viable criteria met
- [ ] Data directories properly configured
- [ ] Database accessible and populated
- [ ] API keys properly configured and functional
- [ ] Sample data processing workflows executable

## Next Steps After Successful Installation

### For Development
- [ ] Explore API endpoints in documentation
- [ ] Run sample intelligence workflows
- [ ] Configure monitoring and logging
- [ ] Set up development environment preferences

### For Production
- [ ] Configure monitoring and alerting
- [ ] Set up backup and recovery procedures
- [ ] Implement security hardening
- [ ] Configure performance optimization
- [ ] Set up automated deployment procedures

## Support Resources

If you encounter issues:
- [ ] Check [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) for detailed instructions
- [ ] Review [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md) for deployment options
- [ ] Examine [DEPLOYMENT_ARCHITECTURE.md](./DEPLOYMENT_ARCHITECTURE.md) for architecture details
- [ ] Use [QUICK_START.md](./QUICK_START.md) for rapid deployment
- [ ] Refer to [docs/README.md](./docs/README.md) for comprehensive documentation

## Completion Date: ________________
## Installer: ________________
## Notes: ________________