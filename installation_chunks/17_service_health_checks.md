# Installation Chunk 17: Service Health Checks

## Overview
This installation chunk performs comprehensive health checks on all services of the CRE Intelligence Platform.

## Prerequisites
- Docker service verification completed (Chunk 15) OR
- Local development server startup completed (Chunk 16)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Check Overall System Health
Test the main health endpoint:
```bash
# For Docker deployment
curl http://localhost:8000/health

# For local development
curl http://localhost:8000/health
```

Expected response: `{"status":"healthy"}`

### 3. Check Database Health
Verify database connectivity and health:
```bash
# For Docker deployment
docker-compose exec postgres pg_isready -U user -d reddit08_db

# For local development
pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB
```

Expected response: `reddit08_db:5432 - accepting connections`

### 4. Check Redis Health
Verify Redis connectivity and health:
```bash
# For Docker deployment
docker-compose exec redis redis-cli ping

# For local development
redis-cli ping
```

Expected response: `PONG`

### 5. Check Celery Worker Health
Verify Celery worker status:
```bash
# For Docker deployment
docker-compose exec celery-worker celery -A src.mcp.fastapi_app.tasks inspect active

# For local development (if Celery is running separately)
celery -A src.mcp.fastapi_app.tasks inspect active
```

### 6. Check Celery Beat Health
Verify Celery beat status:
```bash
# For Docker deployment
docker-compose exec celery-beat ps aux | grep celery

# For local development (if Celery beat is running separately)
ps aux | grep celery
```

### 7. Check Nginx Health (Docker only)
Verify Nginx proxy health:
```bash
# For Docker deployment
docker-compose exec nginx nginx -t
```

Expected response: `nginx: configuration file /etc/nginx/nginx.conf test is successful`

### 8. Check Service Logs for Errors
Examine service logs for any errors or warnings:
```bash
# For Docker deployment
docker-compose logs --tail=100

# For local development
tail -n 100 logs/app.log
```

### 9. Check Resource Usage
Monitor system resource usage:
```bash
# For Docker deployment
docker stats --no-stream

# For local development
top -b -n 1 | head -20
```

### 10. Check Disk Space
Verify sufficient disk space:
```bash
df -h
```

Ensure at least 10GB free space available.

### 11. Check Memory Usage
Check memory usage and availability:
```bash
free -h
```

Ensure sufficient memory for all services.

### 12. Check Network Connectivity
Verify network connectivity between services:
```bash
# For Docker deployment
docker-compose exec app ping -c 4 postgres
docker-compose exec app ping -c 4 redis

# For local development
ping -c 4 localhost
```

### 13. Check External API Connectivity
Test connectivity to external APIs:
```bash
# Test OpenAI API
curl -X GET https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json"

# Test Reddit API
curl -X GET https://oauth.reddit.com/api/v1/me \
  -H "Authorization: Bearer YOUR_REDDIT_ACCESS_TOKEN" \
  -H "User-Agent: CRE Intelligence Platform"
```

### 14. Run Built-in Health Checks
Execute the platform's built-in health check scripts:
```bash
# Run health check script
python src/scripts/health_check.py

# Or use Makefile command if available
make health-check
```

### 15. Check Data Directory Health
Verify data directory accessibility and permissions:
```bash
# Check data directory access
ls -la data/
ls -la data/raw/
ls -la data/processed/
ls -la data/cache/
ls -la data/lexicon/
```

### 16. Check Configuration Files
Verify configuration files are accessible:
```bash
# Check environment file
ls -la .env

# Check configuration directory
ls -la config/
```

## Verification
After completing the above steps, you should have:
- [ ] Overall system health check passing
- [ ] Database health check passing
- [ ] Redis health check passing
- [ ] Celery worker health check passing
- [ ] Celery beat health check passing
- [ ] Nginx health check passing (Docker only)
- [ ] No critical errors in service logs
- [ ] Sufficient system resources available
- [ ] Network connectivity between services verified
- [ ] External API connectivity verified
- [ ] Data directories accessible
- [ ] Configuration files accessible

## Troubleshooting
If health checks fail:

1. **Database health check failed**:
   - Check PostgreSQL service status
   - Verify database credentials
   - Check database logs for errors
   - Restart database service if needed

2. **Redis health check failed**:
   - Check Redis service status
   - Verify Redis configuration
   - Check Redis logs for errors
   - Restart Redis service if needed

3. **Celery worker not responding**:
   - Check Celery worker logs
   - Verify Celery configuration
   - Restart Celery worker
   - Check Redis connectivity for Celery

4. **External API connectivity issues**:
   - Verify API keys are correct
   - Check network connectivity
   - Verify API service status
   - Check rate limits

5. **Insufficient resources**:
   - Check system resources
   - Stop unnecessary services
   - Increase system resources if possible
   - Optimize service configurations

6. **Network connectivity issues**:
   - Check firewall settings
   - Verify network configuration
   - Test connectivity manually
   - Restart network services

## Next Steps
Proceed to Chunk 18: API Endpoint Testing to verify all API endpoints are working correctly.