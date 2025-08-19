# Installation Chunk 34: Container Relationship Verification

## Overview
This installation chunk covers how to verify and manage container relationships in the Docker deployment of the CRE Intelligence Platform, including network connectivity, service communication, and dependency management.

## Prerequisites
- Docker service deployment completed (Chunk 10)
- Docker service verification completed (Chunk 15)
- Service startup order verification completed (Chunk 33)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Understand Container Architecture

#### Review Docker Compose Network Configuration
```bash
# Examine docker-compose.yml for network configuration
cat docker-compose.yml | grep -A 20 -B 5 "networks"

# Expected network configuration:
# networks:
#   reddit08-network:
#     driver: bridge
```

#### Analyze Container Relationships
```bash
# Review service relationships in documentation
cat DEPLOYMENT_ARCHITECTURE.md | grep -A 30 "Container/Process Relationships"

# Expected relationships:
# - nginx --> app
# - app --> postgres
# - app --> redis
# - celery-worker --> postgres
# - celery-worker --> redis
# - celery-beat --> redis
```

### 3. Verify Current Container Relationships

#### Check Running Containers
```bash
# List all running containers
docker-compose ps

# Expected containers:
# reddit08-nginx
# reddit08-cre-platform
# reddit08-postgres
# reddit08-redis
# reddit08-celery
# reddit08-celery-beat

# Check container status
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

#### Examine Container Networks
```bash
# List Docker networks
docker network ls | grep reddit08

# Inspect the main network
docker network inspect reddit08-network

# Check which containers are connected to the network
docker network inspect reddit08-network | grep -A 10 "Containers"
```

### 4. Test Container Connectivity

#### Test Service-to-Service Communication
```bash
# Test app to postgres connectivity
docker-compose exec app pg_isready -h postgres -p 5432 -U user

# Test app to redis connectivity
docker-compose exec app redis-cli -h redis -p 6379 ping

# Test celery-worker to postgres connectivity
docker-compose exec celery-worker pg_isready -h postgres -p 5432 -U user

# Test celery-worker to redis connectivity
docker-compose exec celery-worker redis-cli -h redis -p 6379 ping

# Test celery-beat to redis connectivity
docker-compose exec celery-beat redis-cli -h redis -p 6379 ping
```

#### Test Network Isolation
```bash
# Test external network access from app container
docker-compose exec app ping -c 3 google.com

# Test external network access from other containers
docker-compose exec postgres ping -c 3 google.com
docker-compose exec redis ping -c 3 google.com

# Test container-to-container communication
docker-compose exec app ping -c 3 postgres
docker-compose exec app ping -c 3 redis
docker-compose exec celery-worker ping -c 3 postgres
docker-compose exec celery-worker ping -c 3 redis
```

### 5. Verify Service Dependencies

#### Check Database Dependencies
```bash
# Verify app can access database
docker-compose exec app psql -h postgres -U user -d reddit08_db -c "SELECT version();"

# Verify celery-worker can access database
docker-compose exec celery-worker psql -h postgres -U user -d reddit08_db -c "SELECT 1;"

# Check database schema
docker-compose exec app psql -h postgres -U user -d reddit08_db -c "\dt"
```

#### Check Redis Dependencies
```bash
# Verify app can access Redis
docker-compose exec app redis-cli -h redis -p 6379 info

# Verify celery-worker can access Redis
docker-compose exec celery-worker redis-cli -h redis -p 6379 info

# Verify celery-beat can access Redis
docker-compose exec celery-beat redis-cli -h redis -p 6379 info

# Test Redis operations
docker-compose exec app redis-cli -h redis -p 6379 set test_key "test_value"
docker-compose exec app redis-cli -h redis -p 6379 get test_key
```

#### Check Application Dependencies
```bash
# Verify nginx can access app
docker-compose exec nginx curl -f http://app:8000/health

# Test application endpoints
docker-compose exec app curl -f http://localhost:8000/health
docker-compose exec app curl -f http://localhost:8000/docs

# Check application logs for connection errors
docker-compose logs app | grep -E "(database|redis|connection.*failed)"
```

### 6. Implement Container Relationship Monitoring

#### Create Relationship Monitoring Script
```bash
# Create container relationship monitoring script
nano scripts/monitor_container_relationships.py
```

Example relationship monitoring script:
```python
#!/usr/bin/env python3
import subprocess
import json
import time
from datetime import datetime

def test_container_connectivity():
    """Test connectivity between containers"""
    relationships = {
        "app_to_postgres": {
            "container": "app",
            "command": "pg_isready -h postgres -p 5432 -U user",
            "expected": "accepting connections"
        },
        "app_to_redis": {
            "container": "app",
            "command": "redis-cli -h redis -p 6379 ping",
            "expected": "PONG"
        },
        "celery_to_postgres": {
            "container": "celery-worker",
            "command": "pg_isready -h postgres -p 5432 -U user",
            "expected": "accepting connections"
        },
        "celery_to_redis": {
            "container": "celery-worker",
            "command": "redis-cli -h redis -p 6379 ping",
            "expected": "PONG"
        },
        "beat_to_redis": {
            "container": "celery-beat",
            "command": "redis-cli -h redis -p 6379 ping",
            "expected": "PONG"
        },
        "nginx_to_app": {
            "container": "nginx",
            "command": "curl -f http://app:8000/health",
            "expected": "healthy"
        }
    }
    
    results = {}
    
    for relationship, config in relationships.items():
        try:
            print(f"Testing {relationship}...")
            result = subprocess.run(
                ["docker-compose", "exec", config["container"], "bash", "-c", config["command"]],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = config["expected"] in result.stdout or result.returncode == 0
            results[relationship] = {
                "success": success,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "return_code": result.returncode
            }
            
            if success:
                print(f"✓ {relationship} - OK")
            else:
                print(f"✗ {relationship} - FAILED")
                print(f"  stdout: {result.stdout}")
                print(f"  stderr: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            results[relationship] = {
                "success": False,
                "error": "Timeout"
            }
            print(f"✗ {relationship} - TIMEOUT")
        except Exception as e:
            results[relationship] = {
                "success": False,
                "error": str(e)
            }
            print(f"✗ {relationship} - ERROR: {e}")
    
    return results

def monitor_container_relationships():
    """Monitor container relationships continuously"""
    print("Starting container relationship monitoring...")
    
    while True:
        timestamp = datetime.now().isoformat()
        results = test_container_connectivity()
        
        # Save results
        monitoring_data = {
            "timestamp": timestamp,
            "relationships": results
        }
        
        with open("logs/container_relationships.json", "a") as f:
            f.write(json.dumps(monitoring_data) + "\n")
        
        # Check for failures
        failures = [rel for rel, result in results.items() if not result.get("success", False)]
        if failures:
            print(f"WARNING: Failed relationships: {', '.join(failures)}")
        
        # Wait before next check
        time.sleep(60)

if __name__ == "__main__":
    test_container_connectivity()
```

### 7. Troubleshoot Relationship Issues

#### Diagnose Network Problems
```bash
# Check container IP addresses
docker-compose exec app hostname -i
docker-compose exec postgres hostname -i
docker-compose exec redis hostname -i

# Test direct IP connectivity
APP_IP=$(docker-compose exec app hostname -i | tr -d ' ')
docker-compose exec app ping -c 3 $APP_IP

# Check DNS resolution within containers
docker-compose exec app nslookup postgres
docker-compose exec app nslookup redis

# Verify network configuration
docker-compose exec app cat /etc/hosts
```

#### Resolve Connectivity Issues
```bash
# Check if containers are on the same network
docker inspect reddit08-cre-platform | grep -A 5 "Networks"
docker inspect reddit08-postgres | grep -A 5 "Networks"

# Restart containers to refresh network connections
docker-compose restart app postgres redis

# Check for network conflicts
docker network ls | grep -E "(reddit08|bridge)"

# Recreate network if needed
docker-compose down
docker network prune -f
docker-compose up -d
```

### 8. Optimize Container Relationships

#### Implement Connection Pooling
```bash
# Check current connection pooling configuration
docker-compose exec app python -c "
from src.mcp.fastapi_app.database.connection import get_pool_status
print(get_pool_status())
"

# Monitor database connections
docker-compose exec postgres psql -U user -d reddit08_db -c "
SELECT count(*) as active_connections FROM pg_stat_activity;
"
```

#### Configure Service Discovery
```bash
# Use Docker's built-in service discovery
# In application code, use service names instead of IPs:
# DATABASE_URL=postgresql://user:password@postgres:5432/reddit08_db
# REDIS_URL=redis://redis:6379/0

# Test service discovery
docker-compose exec app python -c "
import socket
print('postgres IP:', socket.gethostbyname('postgres'))
print('redis IP:', socket.gethostbyname('redis'))
"
```

### 9. Verify Container Relationship Resolution
```bash
# Test final container relationships
python scripts/monitor_container_relationships.py

# Run comprehensive connectivity tests
docker-compose exec app bash -c "
set -e
echo 'Testing database connectivity...'
pg_isready -h postgres -p 5432 -U user
echo 'Testing Redis connectivity...'
redis-cli -h redis -p 6379 ping
echo 'Testing application health...'
curl -f http://localhost:8000/health
echo 'All connectivity tests passed!'
"

# Verify all services can communicate
docker-compose exec nginx curl -f http://app:8000/docs
docker-compose exec celery-worker python -c "import redis; print('Redis connection OK')"
docker-compose exec celery-beat python -c "import redis; print('Redis connection OK')"
```

## Verification
After completing the above steps, you should be able to:
- [ ] Understand container architecture and relationships
- [ ] Verify current container relationships and status
- [ ] Test service-to-service communication
- [ ] Verify service dependencies and connectivity
- [ ] Implement container relationship monitoring
- [ ] Troubleshoot relationship and network issues
- [ ] Optimize container relationships and performance
- [ ] Verify container relationship resolution

## Common Container Relationship Issues and Solutions

### Network Issues
- **"Could not resolve host"**: Check container names and network configuration
- **"Connection refused"**: Verify service is running and listening on correct port
- **"Network unreachable"**: Check if containers are on the same network
- **"Timeout"**: Increase connection timeouts or check firewall settings

### Service Discovery Issues
- **"Name or service not known"**: Verify service names in docker-compose.yml
- **"DNS resolution failed"**: Check container DNS configuration
- **"Host not found"**: Ensure containers are properly linked

### Dependency Issues
- **"Database not ready"**: Add proper health checks and dependencies
- **"Redis connection failed"**: Verify Redis service is running and accessible
- **"Service unavailable"**: Check service startup order and health status

## Troubleshooting Checklist

### Quick Fixes
- [ ] Verify containers are running: `docker-compose ps`
- [ ] Check network connectivity: `docker network inspect`
- [ ] Test service communication: `docker-compose exec`
- [ ] Restart containers: `docker-compose restart`
- [ ] Recreate network: `docker-compose down && up`

### Advanced Diagnostics
- [ ] Monitor container relationships continuously
- [ ] Analyze network traffic between containers
- [ ] Check connection pooling and resource usage
- [ ] Implement service discovery monitoring
- [ ] Test failover scenarios
- [ ] Optimize network configuration

## Next Steps
Proceed to Chunk 35: Network Architecture Verification to learn how to verify and optimize the network architecture of the CRE Intelligence Platform.