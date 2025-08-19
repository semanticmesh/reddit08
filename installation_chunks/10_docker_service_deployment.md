# Installation Chunk 10: Docker Service Deployment

## Overview
This installation chunk deploys the CRE Intelligence Platform services using Docker Compose.

## Prerequisites
- Docker installation and verification completed (Chunk 02)
- Docker environment configuration completed (Chunk 08)
- Repository cloned (Chunk 07)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Verify Docker Environment Configuration
Ensure your `.env` file is properly configured:
```bash
# Check that the environment file exists
ls -la .env

# Verify required variables are set
grep -E "(OPENAI_API_KEY|REDDIT_CLIENT_ID|REDDIT_CLIENT_SECRET)" .env
```

### 3. Build Docker Images
Build the Docker images for the application:
```bash
docker-compose build
```

This command will build all services defined in the `docker-compose.yml` file.

### 4. Start Docker Services
Start all services in detached mode:
```bash
docker-compose up -d
```

This command will:
- Start the FastAPI application
- Start PostgreSQL database
- Start Redis cache
- Start Celery worker
- Start Celery beat
- Start Nginx proxy

### 5. Monitor Service Startup
Check the status of all services:
```bash
docker-compose ps
```

Expected output should show all services as "Up":
- reddit08-cre-platform
- reddit08-postgres
- reddit08-redis
- reddit08-celery
- reddit08-celery-beat
- reddit08-nginx

### 6. View Service Logs
Monitor the logs of a specific service:
```bash
# View logs for the main application
docker-compose logs -f app

# View logs for all services
docker-compose logs -f
```

### 7. Check Service Health
Verify that services are running correctly:
```bash
# Check service status
docker-compose ps

# View resource usage
docker stats
```

### 8. Verify Service Access
Test that services are accessible:
```bash
# Check if the application is responding
curl http://localhost:8000/health

# Access API documentation
# Open http://localhost:8000/docs in your browser
```

## Verification
After completing the above steps, you should have:
- [ ] Docker images built successfully
- [ ] All Docker services started in detached mode
- [ ] All services showing as "Up" in `docker-compose ps`
- [ ] Services accessible via curl test
- [ ] API documentation accessible at http://localhost:8000/docs

## Troubleshooting
If Docker services fail to start:

1. **Service fails to start**:
   - Check service logs: `docker-compose logs service_name`
   - Verify environment variables are correct
   - Check for port conflicts

2. **Database connection issues**:
   - Verify PostgreSQL service is running
   - Check database credentials in `.env`
   - Ensure database is accessible

3. **Application crashes**:
   - Check application logs: `docker-compose logs app`
   - Verify all required API keys are set
   - Check for missing dependencies

4. **Port conflicts**:
   - Check if ports 80, 443, 5432, 6379 are in use
   - Modify `docker-compose.yml` to use different ports if needed

5. **Permission issues**:
   - Ensure Docker has proper permissions
   - Check volume mount permissions

## Next Steps
Proceed to Chunk 15: Docker Service Verification to confirm all services are running correctly.