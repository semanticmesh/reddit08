# Installation Chunk 28: Troubleshooting Common Issues

## Overview
This installation chunk covers troubleshooting common issues that may arise during the operation of the CRE Intelligence Platform, including service failures, connectivity problems, and performance issues.

## Prerequisites
- System requirements verification completed (Chunk 01)
- Service health checks completed (Chunk 17)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Service Startup Issues

#### Docker Services Won't Start
```bash
# Check Docker service status
docker-compose ps

# View service logs
docker-compose logs --tail=100

# Check specific service logs
docker-compose logs app
docker-compose logs postgres
docker-compose logs redis

# Restart specific services
docker-compose restart app
docker-compose restart postgres
docker-compose restart redis

# Rebuild services
docker-compose up -d --build

# Check Docker daemon status
sudo systemctl status docker
```

#### Local Services Won't Start
```bash
# Check if required services are running
ps aux | grep postgres
ps aux | grep redis

# Start services
sudo systemctl start postgresql
sudo systemctl start redis

# Check service status
sudo systemctl status postgresql
sudo systemctl status redis

# Check service logs
sudo journalctl -u postgresql
sudo journalctl -u redis
```

### 3. Database Connection Issues

#### PostgreSQL Connection Problems
```bash
# Test database connection
psql -h localhost -p 5432 -U postgres -d reddit08

# For Docker deployment
docker-compose exec postgres psql -U user -d reddit08_db

# Check database configuration
cat .env | grep POSTGRES

# Verify database service is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Test connection with Python
python -c "import psycopg2; print('PostgreSQL connection successful')"
```

#### Common Database Error Solutions
```bash
# Fix "database does not exist" error
createdb reddit08

# Fix "role does not exist" error
createuser -s postgres

# Fix "password authentication failed" error
# Update .env file with correct credentials
nano .env

# Fix "connection refused" error
# Check if PostgreSQL is running
sudo systemctl status postgresql
```

### 4. Redis Connection Issues

#### Redis Connection Problems
```bash
# Test Redis connection
redis-cli ping

# For Docker deployment
docker-compose exec redis redis-cli ping

# Check Redis configuration
cat .env | grep REDIS

# Verify Redis service is running
docker-compose ps redis

# Check Redis logs
docker-compose logs redis

# Test connection with Python
python -c "import redis; r = redis.Redis(); print(r.ping())"
```

#### Common Redis Error Solutions
```bash
# Fix "connection refused" error
# Check if Redis is running
sudo systemctl status redis

# Fix "NOAUTH" error
# Add password to Redis configuration
echo "requirepass your_password" >> redis.conf

# Fix "MISCONF" error
# Check Redis memory configuration
redis-cli config get maxmemory
```

### 5. API and Application Issues

#### Application Won't Start
```bash
# Check application logs
tail -f logs/app.log

# For Docker deployment
docker-compose logs app

# Check if port is in use
netstat -an | grep :8000

# Kill process using port
lsof -i :8000
kill -9 <PID>

# Check Python dependencies
pip list | grep fastapi
pip list | grep uvicorn
```

#### API Endpoints Not Responding
```bash
# Test API health endpoint
curl http://localhost:8000/health

# Test API documentation
curl http://localhost:8000/docs

# Check network connectivity
ping localhost

# Check firewall settings
sudo ufw status

# Test with different tools
wget http://localhost:8000/health
```

### 6. Data Collection Issues

#### Reddit Data Collection Fails
```bash
# Check Reddit API credentials
cat .env | grep REDDIT

# Test Reddit API access
curl -H "User-Agent: CRE Intelligence Platform" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     https://oauth.reddit.com/api/v1/me

# Check rate limits
curl -H "User-Agent: CRE Intelligence Platform" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -I https://oauth.reddit.com/api/v1/me

# Verify subreddit access
curl -H "User-Agent: CRE Intelligence Platform" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     https://oauth.reddit.com/r/realestate/about
```

#### News Data Collection Fails
```bash
# Check News API credentials
cat .env | grep NEWS_API

# Test News API access
curl "https://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=YOUR_API_KEY"

# Verify API quota
curl "https://newsapi.org/v2/sources?apiKey=YOUR_API_KEY"
```

### 7. Performance Issues

#### High CPU Usage
```bash
# Monitor CPU usage
top
htop

# For Docker deployment
docker stats

# Check specific processes
ps aux --sort=-%cpu | head -20

# Monitor application performance
python src/scripts/monitor_performance.py
```

#### High Memory Usage
```bash
# Monitor memory usage
free -h
htop

# For Docker deployment
docker stats

# Check specific processes
ps aux --sort=-%mem | head -20

# Monitor application memory
python -m memory_profiler src/scripts/profile_memory.py
```

#### Slow Database Queries
```bash
# Enable query logging
docker-compose exec postgres psql -U user -d reddit08_db -c "SET log_statement = 'all';"

# Check slow queries
docker-compose exec postgres psql -U user -d reddit08_db -c "SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Analyze query performance
docker-compose exec postgres psql -U user -d reddit08_db -c "EXPLAIN ANALYZE SELECT * FROM posts WHERE platform = 'reddit';"
```

### 8. Authentication Issues

#### Login Failures
```bash
# Check user credentials
python src/scripts/list_users.py

# Reset user password
python src/scripts/reset_user_password.py

# Check JWT configuration
cat .env | grep SECRET_KEY

# Verify authentication logs
tail -f logs/auth.log
```

#### Permission Denied Errors
```bash
# Check user roles
python src/scripts/list_user_roles.py

# Update user permissions
python src/scripts/update_user_permissions.py

# Check API key permissions
cat .env | grep API_KEY
```

### 9. Configuration Issues

#### Environment Variable Problems
```bash
# Check environment variables
env | grep POSTGRES
env | grep REDIS
env | grep API

# Verify .env file
cat .env

# Check file permissions
ls -la .env

# Reload environment variables
source .env
```

#### Configuration File Errors
```bash
# Validate JSON configuration files
python -m json.tool config/reddit_sources.json
python -m json.tool config/news_sources.json

# Check YAML files
python -c "import yaml; yaml.safe_load(open('docker-compose.yml'))"

# Validate configuration syntax
make test-config
```

### 10. Backup and Recovery Issues

#### Backup Failures
```bash
# Check backup directory permissions
ls -la backups/

# Verify disk space
df -h

# Test backup script
bash -x scripts/backup.sh

# Check backup logs
tail -f logs/backup.log
```

#### Restore Failures
```bash
# Verify backup file integrity
ls -la backups/
file backups/*.sql

# Test restore in dry-run mode
pg_restore --list backups/reddit08_backup.dump

# Check database connectivity
psql -h localhost -p 5432 -U postgres -d reddit08 -c "SELECT 1;"
```

### 11. Monitoring and Logging Issues

#### Log File Problems
```bash
# Check log directory permissions
ls -la logs/

# Verify log file sizes
du -sh logs/

# Check disk space
df -h

# Rotate logs manually
logrotate -f /etc/logrotate.d/reddit08
```

#### Monitoring Service Issues
```bash
# Check monitoring services
docker-compose ps prometheus grafana

# Verify metrics endpoint
curl http://localhost:8000/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Grafana status
curl http://localhost:3000/api/health
```

### 12. Network and Connectivity Issues

#### Internal Service Communication
```bash
# Test service connectivity (Docker)
docker-compose exec app ping postgres
docker-compose exec app ping redis

# Test service connectivity (Local)
ping localhost
telnet localhost 5432
telnet localhost 6379
```

#### External API Connectivity
```bash
# Test internet connectivity
ping google.com

# Test API endpoints
curl -I https://api.openai.com
curl -I https://oauth.reddit.com
curl -I https://newsapi.org

# Check DNS resolution
nslookup api.openai.com
nslookup oauth.reddit.com
```

## Verification
After troubleshooting common issues, you should be able to:
- [ ] Resolve service startup problems
- [ ] Fix database connection issues
- [ ] Address Redis connectivity problems
- [ ] Resolve API and application issues
- [ ] Fix data collection failures
- [ ] Address performance issues
- [ ] Resolve authentication problems
- [ ] Fix configuration errors
- [ ] Address backup and recovery issues
- [ ] Resolve monitoring and logging problems
- [ ] Fix network and connectivity issues

## Common Error Messages and Solutions

### Docker Errors
- **"Cannot connect to the Docker daemon"**: Start Docker service with `sudo systemctl start docker`
- **"Port is already allocated"**: Kill process using port or change port configuration
- **"No such container"**: Check service names in docker-compose.yml

### Database Errors
- **"FATAL: database 'reddit08' does not exist"**: Create database with `createdb reddit08`
- **"FATAL: password authentication failed"**: Verify credentials in .env file
- **"could not connect to server"**: Ensure PostgreSQL service is running

### Application Errors
- **"ModuleNotFoundError"**: Install missing dependencies with `pip install -r requirements.txt`
- **"Address already in use"**: Kill process using port or change application port
- **"ImportError: No module named"**: Check Python path and virtual environment

## Next Steps
Proceed to Chunk 29: Docker Service Logs Inspection to learn how to effectively monitor and analyze Docker service logs.