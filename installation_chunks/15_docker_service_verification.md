# Installation Chunk 15: Docker Service Verification

## Overview
This installation chunk verifies that all Docker services for the CRE Intelligence Platform are running correctly.

## Prerequisites
- Docker installation and verification completed (Chunk 02)
- Docker environment configuration completed (Chunk 08)
- Docker service deployment completed (Chunk 10)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Check Service Status
Verify that all Docker services are running:
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

### 3. Verify Service Logs
Check the logs for any errors or warnings:
```bash
# View logs for all services
docker-compose logs

# View logs for a specific service
docker-compose logs app
docker-compose logs postgres
docker-compose logs redis
docker-compose logs celery
docker-compose logs celery-beat
docker-compose logs nginx
```

### 4. Test Service Health
Test that the main application is responding:
```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response: {"status":"healthy"}
```

### 5. Access API Documentation
Verify that the API documentation is accessible:
```bash
# Open in browser or test with curl
curl http://localhost:8000/docs
```

Expected response: HTML content for the API documentation

### 6. Test API Endpoints
Test a few key API endpoints:
```bash
# Test basic API endpoint
curl http://localhost:8000/

# Test version endpoint
curl http://localhost:8000/version
```

### 7. Check Resource Usage
Monitor resource usage of the services:
```bash
docker stats
```

### 8. Verify Network Connections
Check that services can communicate with each other:
```bash
# Test database connection from application container
docker-compose exec app ping postgres

# Test Redis connection from application container
docker-compose exec app ping redis
```

### 9. Check Volume Mounts
Verify that data volumes are properly mounted:
```bash
# List volumes
docker volume ls

# Check specific volume usage
docker volume inspect reddit08_postgres_data
docker volume inspect reddit08_redis_data
```

### 10. Test Service Restart
Test restarting services:
```bash
# Restart all services
docker-compose restart

# Check status after restart
docker-compose ps
```

## Verification
After completing the above steps, you should have:
- [ ] All Docker services showing as "Up"
- [ ] No critical errors in service logs
- [ ] Health endpoint returning healthy status
- [ ] API documentation accessible
- [ ] Key API endpoints responding correctly
- [ ] Services communicating properly
- [ ] Data volumes properly mounted
- [ ] Services restartable without issues

## Troubleshooting
If Docker services fail verification:

1. **Service not running**:
   - Check service logs: `docker-compose logs service_name`
   - Restart the service: `docker-compose restart service_name`
   - Check if ports are in use: `netstat -an | grep :80`

2. **Health check failed**:
   - Check application logs: `docker-compose logs app`
   - Verify API keys are correctly configured
   - Check database connection settings

3. **API documentation not accessible**:
   - Verify Nginx is running: `docker-compose ps nginx`
   - Check Nginx logs: `docker-compose logs nginx`
   - Verify port mapping in docker-compose.yml

4. **Database connection issues**:
   - Check PostgreSQL logs: `docker-compose logs postgres`
   - Verify database credentials in .env
   - Ensure database service is running

5. **Redis connection issues**:
   - Check Redis logs: `docker-compose logs redis`
   - Verify Redis service is running
   - Check Redis configuration

6. **Port conflicts**:
   - Check if ports 80, 443, 5432, 6379 are in use
   - Modify docker-compose.yml to use different ports if needed

## Next Steps
Proceed to Chunk 17: Service Health Checks to perform more comprehensive health verification.