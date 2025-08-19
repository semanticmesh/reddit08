# CRE Intelligence Platform Installation Documentation

## Overview

This repository contains comprehensive documentation for installing and deploying the CRE Intelligence Platform. The platform can be deployed using either Docker (recommended for production) or local development setup (for development and testing).

## Documentation Structure

### 1. [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) - Complete Installation Guide
**Use this for:** Detailed step-by-step installation instructions
- Comprehensive guide for both Docker and local deployment
- Environment configuration details
- Troubleshooting common issues
- Post-installation setup steps

### 2. [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md) - Deployment Options Summary
**Use this for:** Quick comparison of deployment options
- Key differences between Docker and local setup
- Quick start commands for each option
- When to use each deployment method
- Management commands overview

### 3. [DEPLOYMENT_ARCHITECTURE.md](./DEPLOYMENT_ARCHITECTURE.md) - Architecture Diagrams
**Use this for:** Understanding system architecture
- Visual diagrams of Docker deployment
- Visual diagrams of local development setup
- Service dependencies and relationships
- Network architecture overview

### 4. [QUICK_START.md](./QUICK_START.md) - Rapid Deployment Guide
**Use this for:** Fastest path to running system
- Minimal steps to get platform running
- Quick configuration requirements
- Immediate verification steps
- Common next steps

### 5. [INSTALLATION_CHECKLIST.md](./INSTALLATION_CHECKLIST.md) - Verification Checklist
**Use this for:** Ensuring complete installation
- Step-by-step verification checklist
- Common issues troubleshooting guide
- Success criteria validation
- Post-installation setup verification

## Recommended Installation Path

### For Production Deployment
1. Start with [QUICK_START.md](./QUICK_START.md) for initial setup
2. Follow [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) for Docker deployment
3. Use [INSTALLATION_CHECKLIST.md](./INSTALLATION_CHECKLIST.md) to verify installation
4. Refer to [DEPLOYMENT_ARCHITECTURE.md](./DEPLOYMENT_ARCHITECTURE.md) for understanding system components

### For Development Setup
1. Start with [QUICK_START.md](./QUICK_START.md) for initial setup
2. Follow [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) for local development setup
3. Use [INSTALLATION_CHECKLIST.md](./INSTALLATION_CHECKLIST.md) to verify installation
4. Refer to [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md) for deployment options comparison

### For Architecture Understanding
1. Review [DEPLOYMENT_ARCHITECTURE.md](./DEPLOYMENT_ARCHITECTURE.md) for visual diagrams
2. Check [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md) for key differences
3. Refer to [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) for detailed component information

## Key Documents at a Glance

| Document | Purpose | Best For |
|----------|---------|----------|
| [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) | Complete installation instructions | Detailed setup |
| [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md) | Deployment options comparison | Decision making |
| [DEPLOYMENT_ARCHITECTURE.md](./DEPLOYMENT_ARCHITECTURE.md) | System architecture diagrams | Understanding components |
| [QUICK_START.md](./QUICK_START.md) | Fastest setup path | Rapid deployment |
| [INSTALLATION_CHECKLIST.md](./INSTALLATION_CHECKLIST.md) | Verification checklist | Quality assurance |

## Getting Started

### Fastest Path (5-10 minutes)
```bash
# For Docker deployment:
cp .env.docker .env
# Edit .env with your API keys
docker-compose up -d
curl http://localhost:8000/health
```

### Detailed Path (10-15 minutes)
1. Review [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md) to choose deployment option
2. Follow [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) for chosen option
3. Use [INSTALLATION_CHECKLIST.md](./INSTALLATION_CHECKLIST.md) to verify installation

## Support and Resources

### Documentation
- Full Platform Documentation: [docs/README.md](./docs/README.md)
- API Documentation: http://localhost:8000/docs (after installation)
- Configuration Guide: [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) - Configuration Details section

### Troubleshooting
- Common Issues: [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) - Troubleshooting section
- Quick Reference: [INSTALLATION_CHECKLIST.md](./INSTALLATION_CHECKLIST.md) - Common Issues Checklist
- Logs: Check `logs/` directory or Docker logs

### Community and Support
- Issue Tracker: https://github.com/your-org/reddit08/issues
- Documentation: [docs/README.md](./docs/README.md)
- Installation Support: This directory's documentation

## Next Steps After Installation

1. **Configure Data Sources** - Edit `config/cities.yml` with your target markets
2. **Initialize Lexicon** - Run `python src/scripts/refresh_tfidf_via_mcp.py`
3. **Test API Endpoints** - Visit http://localhost:8000/docs
4. **Run Sample Pipeline** - Execute `python src/scripts/run_full_pipeline.py`
5. **Set Up Monitoring** - Configure Prometheus and Grafana integration

## Contributing

If you're improving the installation process:
1. Update relevant documentation files
2. Ensure [INSTALLATION_CHECKLIST.md](./INSTALLATION_CHECKLIST.md) reflects changes
3. Update [QUICK_START.md](./QUICK_START.md) if needed for new fast paths
4. Modify diagrams in [DEPLOYMENT_ARCHITECTURE.md](./DEPLOYMENT_ARCHITECTURE.md) as needed

## License

This documentation is part of the CRE Intelligence Platform project and is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.