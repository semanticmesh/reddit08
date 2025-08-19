# Installation Chunk 33: Service Startup Order Verification

## Overview
This installation chunk covers how to verify and ensure the proper startup order of services for the CRE Intelligence Platform, including dependency management, health checks, and initialization sequences.

## Prerequisites
- Docker service deployment completed (Chunk 10)
- Service health checks completed (Chunk 17)
- Container relationship verification completed (Chunk 34)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Understand Service Dependencies

#### Review Docker Compose Dependencies
```bash
# Examine docker-compose.yml for service dependencies
cat docker-compose.yml | grep -A 10 -B 2 "depends_on"

# Expected dependencies:
# app depends on: postgres, redis
# celery-worker depends on: postgres, redis
# celery-beat depends on: redis
# nginx depends on: app
```

#### Analyze Service Startup Requirements
```bash
# Review service requirements in documentation
cat DEPLOYMENT_ARCHITECTURE.md | grep -A 20 "Service Startup Procedures"

# Expected startup order:
# 1. PostgreSQL Database
# 2. Redis Cache
# 3. FastAPI Application
# 4. Celery Worker
# 5. Celery Beat
# 6. Nginx Proxy
```

### 3. Verify Current Startup Order

#### Check Service Status
```bash
# Start all services and monitor startup
docker-compose up -d

# Check service startup order in logs
docker-compose logs --since="1h" | grep -E "(reddit08-|Starting|Started)"

# Monitor service initialization
docker-compose logs -f --since="1m" | grep -E "(database system is ready|Ready to accept connections|Application startup complete|Connected to|Starting worker)"

# Check service health status
docker-compose ps
```

#### Analyze Startup Timeline
```bash
# Get detailed startup timeline
docker-compose logs --since="1h" --timestamps | grep -E "(Starting|Started|ready|accept|startup|Connected)" | sort

# Check for startup errors
docker-compose logs --since="1h" | grep -E "(ERROR|FATAL|Failed|Cannot connect)"

# Monitor service dependencies
docker-compose logs --since="1h" | grep -E "(depends_on|waiting for|dependency)"
```

### 4. Test Service Dependencies

#### Verify Database Availability
```bash
# Test database connectivity during startup
docker-compose exec app bash -c "pg_isready -h postgres -p 5432 -U user"

# Check database initialization
docker-compose exec postgres psql -U user -d reddit08_db -c "SELECT 1;"

# Monitor database readiness
docker-compose logs postgres | grep "database system is ready"
```

#### Verify Redis Availability
```bash
# Test Redis connectivity during startup
docker-compose exec app bash -c "redis-cli -h redis -p 6379 ping"

# Check Redis initialization
docker-compose exec redis redis-cli ping

# Monitor Redis readiness
docker-compose logs redis | grep "Ready to accept connections"
```

#### Verify Application Readiness
```bash
# Test application health endpoint
curl -f http://localhost:8000/health || echo "Application not ready"

# Check application startup logs
docker-compose logs app | grep "Application startup complete"

# Monitor application dependencies
docker-compose logs app | grep -E "(database|redis|connection)"
```

### 5. Implement Proper Startup Dependencies

#### Update Docker Compose Configuration
```bash
# Edit docker-compose.yml to ensure proper dependencies
nano docker-compose.yml
```

Example updated docker-compose.yml service dependencies:
```yaml
services:
  app:
    # ... other configuration
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    # ... other configuration
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d reddit08_db"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s

  redis:
    # ... other configuration
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  celery-worker:
    # ... other configuration
    depends_on:
      app:
        condition: service_healthy
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery-beat:
    # ... other configuration
    depends_on:
      redis:
        condition: service_healthy

  nginx:
    # ... other configuration
    depends_on:
      app:
        condition: service_started
```

### 6. Add Startup Health Checks

#### Implement Application Health Checks
```bash
# Check existing health check endpoint
curl http://localhost:8000/health

# Test detailed health check
curl http://localhost:8000/health/detail

# Monitor health check logs
docker-compose logs app | grep -i health
```

#### Add Custom Health Checks
```python
# Edit src/mcp/fastapi_app/health/extended_health.py
from fastapi import APIRouter, HTTPException
import psycopg2
import redis
import os

router = APIRouter()

@router.get("/health/extended")
async def extended_health_check():
    health_status = {
        "application": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "dependencies": []
    }
    
    # Check database connectivity
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'postgres'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'reddit08_db'),
            user=os.getenv('POSTGRES_USER', 'user'),
            password=os.getenv('POSTGRES_PASSWORD', 'password')
        )
        conn.close()
        health_status["database"] = "healthy"
    except Exception as e:
        health_status["database"] = f"unhealthy: {str(e)}"
        health_status["application"] = "degraded"
    
    # Check Redis connectivity
    try:
        r = redis.Redis(
            host=os.getenv('REDIS_HOST', 'redis'),
            port=os.getenv('REDIS_PORT', '6379'),
            db=0,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        r.ping()
        health_status["redis"] = "healthy"
    except Exception as e:
        health_status["redis"] = f"unhealthy: {str(e)}"
        health_status["application"] = "degraded"
    
    return health_status
```

### 7. Monitor Startup Sequence

#### Create Startup Monitoring Script
```bash
# Create startup monitoring script
nano scripts/monitor_startup.py
```

Example startup monitoring script:
```python
#!/usr/bin/env python3
import subprocess
import time
import json
from datetime import datetime

def monitor_service_startup():
    startup_sequence = []
    
    print("Monitoring service startup sequence...")
    
    # Start services
    subprocess.run(["docker-compose", "up", "-d"])
    
    services = ["postgres", "redis", "app", "celery-worker", "celery-beat", "nginx"]
    
    for service in services:
        start_time = datetime.now()
        print(f"Waiting for {service} to become healthy...")
        
        # Wait for service to be healthy
        while True:
            try:
                result = subprocess.run(
                    ["docker-compose", "ps", service],
                    capture_output=True,
                    text=True
                )
                
                if "Up" in result.stdout and "healthy" in result.stdout:
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    startup_sequence.append({
                        "service": service,
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "duration_seconds": duration,
                        "status": "healthy"
                    })
                    print(f"{service} is healthy (took {duration:.2f} seconds)")
                    break
                elif "Exit" in result.stdout:
                    startup_sequence.append({
                        "service": service,
                        "start_time": start_time.isoformat(),
                        "end_time": datetime.now().isoformat(),
                        "duration_seconds": 0,
                        "status": "failed"
                    })
                    print(f"{service} failed to start")
                    break
                    
                time.sleep(5)
            except Exception as e:
                print(f"Error monitoring {service}: {e}")
                break
    
    # Save startup sequence
    with open("logs/startup_sequence.json", "w") as f:
        json.dump(startup_sequence, f, indent=2)
    
    print("Startup sequence monitoring completed")
    return startup_sequence

if __name__ == "__main__":
    monitor_service_startup()
```

### 8. Troubleshoot Startup Issues

#### Diagnose Startup Delays
```bash
# Check for startup delays
docker-compose logs --since="1h" | grep -E "(timeout|slow|delay|waiting)"

# Monitor resource usage during startup
docker stats --no-stream

# Check system resources
free -h
df -h
```

#### Resolve Dependency Issues
```bash
# Check for circular dependencies
docker-compose config --services

# Verify service names match dependencies
docker-compose ps --services

# Test individual service startup
docker-compose up -d postgres
docker-compose up -d redis
docker-compose up -d app
# ... start services one by one
```

### 9. Optimize Startup Performance

#### Implement Startup Caching
```bash
# Add startup caching to application
# Edit src/mcp/fastapi_app/startup/cache_startup.py

import asyncio
import time

async def initialize_startup_cache():
    """Initialize cache during application startup"""
    print("Initializing startup cache...")
    start_time = time.time()
    
    # Perform cache warming operations
    # This could include loading frequently accessed data
    # or pre-computing common operations
    
    end_time = time.time()
    print(f"Startup cache initialized in {end_time - start_time:.2f} seconds")

# Call during application startup
# In main application file:
# await initialize_startup_cache()
```

#### Configure Startup Retries
```bash
# Add retry logic to docker-compose.yml
# Example for application service:
# app:
#   # ... other configuration
#   deploy:
#     restart_policy:
#       condition: on-failure
#       delay: 5s
#       max_attempts: 3
#       window: 120s
```

### 10. Verify Startup Order Resolution
```bash
# Test final startup sequence
docker-compose down
docker-compose up -d

# Monitor startup completion
timeout 300 docker-compose logs -f | grep -E "(All services started|Application ready|healthy)"

# Verify all services are running
docker-compose ps

# Check startup sequence timing
python scripts/monitor_startup.py
```

## Verification
After completing the above steps, you should be able to:
- [ ] Understand service dependencies and requirements
- [ ] Verify current startup order and timing
- [ ] Test service dependencies during startup
- [ ] Implement proper startup dependencies
- [ ] Add comprehensive health checks
- [ ] Monitor startup sequence and timing
- [ ] Troubleshoot startup issues and delays
- [ ] Optimize startup performance
- [ ] Verify startup order resolution

## Common Startup Order Issues and Solutions

### Dependency Issues
- **"Cannot connect to database"**: Ensure postgres service starts before app
- **"Redis connection failed"**: Ensure redis service starts before dependent services
- **"Service not healthy"**: Add proper health checks to dependent services

### Timing Issues
- **"Timeout during startup"**: Increase start_period in healthcheck configuration
- **"Race conditions"**: Use service_healthy condition instead of service_started
- **"Slow service initialization"**: Optimize service startup code or increase resources

### Health Check Issues
- **"Health check failed"**: Verify health check endpoint and connectivity
- **"Service marked unhealthy"**: Check service logs for errors
- **"Health check timeout"**: Increase timeout in healthcheck configuration

## Troubleshooting Checklist

### Quick Fixes
- [ ] Verify docker-compose.yml dependencies
- [ ] Check service health check configurations
- [ ] Monitor startup logs for errors
- [ ] Test services individually
- [ ] Increase health check timeouts
- [ ] Add startup retry policies

### Advanced Diagnostics
- [ ] Analyze startup timing and bottlenecks
- [ ] Implement detailed health checks
- [ ] Monitor resource usage during startup
- [ ] Test different startup sequences
- [ ] Optimize service initialization code
- [ ] Configure proper restart policies

## Next Steps
Proceed to Chunk 34: Container Relationship Verification to learn how to verify and manage container relationships in the Docker deployment.