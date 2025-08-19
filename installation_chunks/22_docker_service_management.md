# Installation Chunk 22: Docker Service Management

## Overview
This installation chunk covers the management of Docker services for the CRE Intelligence Platform, including starting, stopping, and monitoring services.

## Prerequisites
- Docker installation and verification completed (Chunk 02)
- Docker service deployment completed (Chunk 10)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. View Service Status
Check the status of all Docker services:
```bash
# View all services
docker-compose ps

# View specific service
docker-compose ps app
docker-compose ps postgres
docker-compose ps redis
```

### 3. Start Services
Start all services or specific services:
```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d app
docker-compose up -d postgres redis

# Start services with build
docker-compose up -d --build
```

### 4. Stop Services
Stop all services or specific services:
```bash
# Stop all services
docker-compose down

# Stop specific services
docker-compose stop app
docker-compose stop postgres

# Stop services and remove containers
docker-compose down --remove-orphans
```

### 5. Restart Services
Restart all services or specific services:
```bash
# Restart all services
docker-compose restart

# Restart specific services
docker-compose restart app
docker-compose restart postgres redis

# Restart with dependency services
docker-compose restart --no-deps app
```

### 6. Scale Services
Scale services up or down:
```bash
# Scale worker services
docker-compose up -d --scale celery-worker=3

# Scale API services
docker-compose up -d --scale app=2

# Reset to original scale
docker-compose up -d --scale celery-worker=1 --scale app=1
```

### 7. View Service Logs
Monitor service logs:
```bash
# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs app

# View logs with follow
docker-compose logs -f app

# View last N lines of logs
docker-compose logs --tail=100 app

# View logs since a specific time
docker-compose logs --since="2025-01-01" app
```

### 8. Execute Commands in Running Containers
Execute commands inside running containers:
```bash
# Execute shell in app container
docker-compose exec app /bin/bash

# Execute shell in postgres container
docker-compose exec postgres /bin/bash

# Execute specific command
docker-compose exec app python --version

# Execute command with environment
docker-compose exec -e ENV_VAR=value app python script.py
```

### 9. Manage Service Resources
Monitor and manage service resources:
```bash
# View resource usage
docker stats

# View resource usage for specific containers
docker stats reddit08-app reddit08-postgres

# View container information
docker-compose top

# View container details
docker-compose inspect app
```

### 10. Update Services
Update services with new configurations or images:
```bash
# Pull latest images
docker-compose pull

# Build services
docker-compose build

# Build specific service
docker-compose build app

# Update services
docker-compose up -d

# Force recreate containers
docker-compose up -d --force-recreate
```

### 11. Backup and Restore Service Data
Manage data volumes for services:
```bash
# List volumes
docker volume ls

# Inspect specific volume
docker volume inspect reddit08_postgres_data

# Backup volume data
docker run --rm -v reddit08_postgres_data:/source -v /backup/path:/backup alpine tar czf /backup/postgres_backup.tar.gz -C /source .

# Restore volume data
docker run --rm -v reddit08_postgres_data:/target -v /backup/path:/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /target
```

### 12. Service Health Monitoring
Set up health monitoring for services:
```bash
# Check service health
docker-compose ps

# View health status
docker inspect --format='{{json .State.Health}}' reddit08-app

# Configure health checks in docker-compose.yml
# Example:
# healthcheck:
#   test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
#   interval: 30s
#   timeout: 10s
#   retries: 3
```

### 13. Network Management
Manage service networking:
```bash
# List networks
docker network ls

# Inspect network
docker network inspect reddit08-network

# View container network connections
docker-compose exec app ip addr show
```

### 14. Environment Variable Management
Manage environment variables for services:
```bash
# View environment variables
docker-compose exec app env

# Set environment variables at runtime
docker-compose run -e NEW_VAR=value app

# Update environment variables
# Edit .env file and restart services
docker-compose down && docker-compose up -d
```

## Verification
After completing the above steps, you should be able to:
- [ ] View service status effectively
- [ ] Start, stop, and restart services
- [ ] Scale services as needed
- [ ] Monitor service logs
- [ ] Execute commands in containers
- [ ] Manage service resources
- [ ] Update services with new configurations
- [ ] Backup and restore service data
- [ ] Monitor service health
- [ ] Manage service networking
- [ ] Manage environment variables

## Troubleshooting
If Docker service management issues occur:

1. **Services won't start**:
   - Check service logs: `docker-compose logs service_name`
   - Verify dependencies are running
   - Check port conflicts
   - Review environment variables

2. **Services crash frequently**:
   - Check resource limits
   - Review application logs
   - Verify data directory permissions
   - Check health check configurations

3. **Logs not accessible**:
   - Verify logging driver configuration
   - Check disk space
   - Review log rotation settings

4. **Scaling issues**:
   - Check resource availability
   - Verify load balancing configuration
   - Review application state management

5. **Network connectivity issues**:
   - Check network configuration
   - Verify service discovery
   - Review firewall settings
   - Test container-to-container connectivity

6. **Volume mounting issues**:
   - Check directory permissions
   - Verify volume paths
   - Review SELinux/AppArmor settings
   - Test volume access inside containers

## Next Steps
Proceed to Chunk 24: Monitoring Setup to configure comprehensive monitoring for the CRE Intelligence Platform.