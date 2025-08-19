# Installation Chunk 31: Database Connection Troubleshooting

## Overview
This installation chunk covers how to diagnose and resolve database connection issues for the CRE Intelligence Platform, including connectivity problems, authentication failures, and performance issues.

## Prerequisites
- PostgreSQL installation and setup completed (Chunk 04)
- Database initialization completed (Chunk 12)
- API key configuration completed (Chunk 14)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Verify Database Service Status

#### For Local Development
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# On macOS with Homebrew
brew services list | grep postgresql

# Check if PostgreSQL process is running
ps aux | grep postgres

# Start PostgreSQL if not running
sudo systemctl start postgresql
# or on macOS
brew services start postgresql
```

#### For Docker Deployment
```bash
# Check Docker service status
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Check if container is healthy
docker inspect reddit08-postgres
```

### 3. Test Basic Database Connectivity

#### Test Connection with psql
```bash
# Test connection with default settings
psql -h localhost -p 5432 -U postgres -d postgres

# Test connection with application settings
psql -h localhost -p 5432 -U reddit08_user -d reddit08_db

# For Docker deployment
docker-compose exec postgres psql -U user -d reddit08_db

# Test connection with environment variables
source .env
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB
```

#### Test Connection with Python
```bash
# Test connection with Python script
python -c "
import psycopg2
import os

try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'reddit08'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'password')
    )
    print('Database connection successful')
    conn.close()
except Exception as e:
    print(f'Database connection failed: {e}')
"
```

### 4. Check Environment Configuration

#### Verify Environment Variables
```bash
# Check database environment variables
cat .env | grep POSTGRES

# Expected variables:
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DB=reddit08
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=your_password

# For Docker deployment
cat .env | grep DATABASE_URL

# Expected format:
# DATABASE_URL=postgresql://user:password@postgres:5432/reddit08_db
```

#### Test Environment Variable Loading
```bash
# Test if environment variables are loaded
python -c "
import os
from dotenv import load_dotenv

load_dotenv()
print('POSTGRES_HOST:', os.getenv('POSTGRES_HOST'))
print('POSTGRES_PORT:', os.getenv('POSTGRES_PORT'))
print('POSTGRES_DB:', os.getenv('POSTGRES_DB'))
print('POSTGRES_USER:', os.getenv('POSTGRES_USER'))
print('POSTGRES_PASSWORD:', '***' if os.getenv('POSTGRES_PASSWORD') else 'Not set')
"
```

### 5. Common Connection Error Diagnostics

#### "Connection Refused" Errors
```bash
# Check if PostgreSQL is listening on the correct port
netstat -an | grep 5432
# or
ss -tuln | grep 5432

# Check PostgreSQL configuration
sudo nano /etc/postgresql/*/main/postgresql.conf

# Look for:
# listen_addresses = 'localhost' or '*'
# port = 5432

# Check PostgreSQL authentication configuration
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Ensure proper authentication entries exist
```

#### "Authentication Failed" Errors
```bash
# Check PostgreSQL user exists
psql -h localhost -p 5432 -U postgres -d postgres -c "\du"

# Create user if missing
psql -h localhost -p 5432 -U postgres -d postgres -c "CREATE USER reddit08_user WITH PASSWORD 'your_password';"

# Grant database privileges
psql -h localhost -p 5432 -U postgres -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE reddit08_db TO reddit08_user;"

# For Docker, check docker-compose.yml environment variables
docker-compose exec postgres psql -U user -d reddit08_db -c "\du"
```

#### "Database Does Not Exist" Errors
```bash
# Check if database exists
psql -h localhost -p 5432 -U postgres -d postgres -l

# Create database if missing
createdb -h localhost -p 5432 -U postgres reddit08

# For Docker
docker-compose exec postgres createdb -U user reddit08_db
```

### 6. Network and Firewall Issues

#### Check Network Connectivity
```bash
# Test network connectivity to database server
ping localhost
# or for remote database
ping database-server-ip

# Test port connectivity
telnet localhost 5432
# or
nc -zv localhost 5432

# For Docker networks
docker network ls
docker network inspect reddit08-network
```

#### Check Firewall Settings
```bash
# Check firewall status (Linux)
sudo ufw status

# Allow PostgreSQL port
sudo ufw allow 5432

# Check iptables rules
sudo iptables -L

# For Docker, check container connectivity
docker-compose exec app ping postgres
```

### 7. Database Performance Issues

#### Check Database Performance
```bash
# Check active connections
psql -h localhost -p 5432 -U postgres -d reddit08 -c "SELECT count(*) FROM pg_stat_activity;"

# Check for long-running queries
psql -h localhost -p 5432 -U postgres -d reddit08 -c "SELECT pid, query, state FROM pg_stat_activity WHERE state = 'active';"

# Check database size
psql -h localhost -p 5432 -U postgres -d reddit08 -c "SELECT pg_size_pretty(pg_database_size('reddit08'));"

# For Docker
docker-compose exec postgres psql -U user -d reddit08_db -c "SELECT count(*) FROM pg_stat_activity;"
```

#### Optimize Database Configuration
```bash
# Check current PostgreSQL settings
psql -h localhost -p 5432 -U postgres -d reddit08 -c "SHOW shared_buffers;"
psql -h localhost -p 5432 -U postgres -d reddit08 -c "SHOW work_mem;"

# For Docker, check postgres service configuration in docker-compose.yml
# Add performance parameters to command section:
# command: >
#   postgres
#   -c shared_buffers=256MB
#   -c work_mem=32MB
```

### 8. Connection Pool Issues

#### Check Connection Pool Configuration
```bash
# Check application connection pool settings
cat src/mcp/fastapi_app/database/connection.py

# Look for pool settings:
# pool_size=20
# max_overflow=30
# pool_pre_ping=True
# pool_recycle=3600

# Monitor connection pool usage
python -c "
from src.mcp.fastapi_app.database.connection import get_pool_status
print(get_pool_status())
"
```

#### Reset Connection Pool
```bash
# Restart application to reset connection pool
# For Docker
docker-compose restart app

# For local development
pkill -f uvicorn
make serve
```

### 9. SSL/TLS Connection Issues

#### Check SSL Configuration
```bash
# Check if SSL is required
psql -h localhost -p 5432 -U postgres -d reddit08 -c "SHOW ssl;"

# For Docker, check postgres service environment
docker-compose exec postgres psql -U user -d reddit08_db -c "SHOW ssl;"

# Update connection string for SSL
# DATABASE_URL=postgresql://user:password@postgres:5432/reddit08_db?sslmode=require
```

### 10. Advanced Troubleshooting

#### Enable Detailed Logging
```bash
# Enable PostgreSQL query logging
psql -h localhost -p 5432 -U postgres -d reddit08 -c "ALTER SYSTEM SET log_statement = 'all';"
psql -h localhost -p 5432 -U postgres -d reddit08 -c "SELECT pg_reload_conf();"

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# For Docker
docker-compose logs postgres
```

#### Use Connection Debugging Tools
```bash
# Install debugging tools
pip install pgcli

# Use pgcli for better connection debugging
pgcli -h localhost -p 5432 -U postgres -d reddit08

# Check connection details
\conninfo

# List databases
\l

# List tables
\dt
```

### 11. Verify Database Connection Resolution
```bash
# Test final database connection
python src/scripts/test_database_connection.py

# Run database health check
curl http://localhost:8000/health/database

# Check application logs for database errors
tail -f logs/app.log | grep -i database
```

## Verification
After completing the above steps, you should be able to:
- [ ] Verify database service status
- [ ] Test basic database connectivity
- [ ] Check environment configuration
- [ ] Diagnose common connection errors
- [ ] Resolve network and firewall issues
- [ ] Address database performance issues
- [ ] Manage connection pool problems
- [ ] Handle SSL/TLS connection issues
- [ ] Use advanced troubleshooting techniques
- [ ] Verify database connection resolution

## Common Database Error Messages and Solutions

### Connection Errors
- **"FATAL: password authentication failed"**: Verify credentials in .env file
- **"FATAL: database 'reddit08' does not exist"**: Create database with `createdb`
- **"could not connect to server: Connection refused"**: Ensure PostgreSQL is running
- **"FATAL: role 'reddit08_user' does not exist"**: Create user with `CREATE USER`

### Authentication Errors
- **"FATAL: no pg_hba.conf entry"**: Add authentication entry to pg_hba.conf
- **"FATAL: Ident authentication failed"**: Check authentication method in pg_hba.conf
- **"FATAL: Peer authentication failed"**: Use md5 authentication instead of peer

### Performance Errors
- **"FATAL: sorry, too many clients already"**: Increase max_connections in PostgreSQL
- **"connection timeout"**: Check network connectivity and firewall settings
- **"server closed the connection unexpectedly"**: Check database logs for errors

## Troubleshooting Checklist

### Quick Fixes
- [ ] Check if PostgreSQL service is running
- [ ] Verify environment variables in .env file
- [ ] Test connection with psql command
- [ ] Check firewall settings
- [ ] Verify database and user exist
- [ ] Check network connectivity
- [ ] Review application logs for errors

### Advanced Diagnostics
- [ ] Enable detailed PostgreSQL logging
- [ ] Monitor connection pool usage
- [ ] Check database performance metrics
- [ ] Analyze slow query logs
- [ ] Review system resource usage
- [ ] Test with different connection parameters

## Next Steps
Proceed to Chunk 32: API Key Troubleshooting to learn how to diagnose and resolve API key authentication issues.