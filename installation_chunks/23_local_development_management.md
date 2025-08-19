# Installation Chunk 23: Local Development Management

## Overview
This installation chunk covers the management of the CRE Intelligence Platform in local development mode, including starting, stopping, and managing the development environment.

## Prerequisites
- Python virtual environment setup completed (Chunk 03)
- Local development server startup completed (Chunk 16)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Activate Virtual Environment
Activate your Python virtual environment:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Start Development Server
Start the development server with auto-reload:
```bash
# Using Makefile
make serve

# Or directly with uvicorn
uvicorn src.mcp.fastapi_app.main:app --reload --host 0.0.0.0 --port 8000

# Or with custom settings
uvicorn src.mcp.fastapi_app.main:app \
  --reload \
  --host 0.0.0.0 \
  --port 8000 \
  --log-level debug \
  --reload-dir src/
```

### 4. Stop Development Server
Stop the development server:
```bash
# Press Ctrl+C in the terminal where the server is running

# Or if running in background, find and kill the process
ps aux | grep uvicorn
kill -9 <process_id>
```

### 5. Manage Background Processes
Run the server in the background:
```bash
# Run in background
uvicorn src.mcp.fastapi_app.main:app --reload --host 0.0.0.0 --port 8000 &

# Or redirect output to log file
uvicorn src.mcp.fastapi_app.main:app --reload --host 0.0.0.0 --port 8000 > server.log 2>&1 &

# Find background process
ps aux | grep uvicorn

# Kill background process
pkill -f uvicorn
```

### 6. Monitor Development Server Logs
Monitor server logs:
```bash
# View log file if redirected
tail -f server.log

# View application logs
tail -f logs/app.log

# View all log files
tail -f logs/*.log
```

### 7. Manage Database Services
Manage local database services:
```bash
# Start PostgreSQL (Ubuntu/Debian)
sudo systemctl start postgresql

# Start PostgreSQL (macOS with Homebrew)
brew services start postgresql

# Start Redis (Ubuntu/Debian)
sudo systemctl start redis

# Start Redis (macOS with Homebrew)
brew services start redis

# Check service status
sudo systemctl status postgresql
sudo systemctl status redis
```

### 8. Run Development Tasks
Execute common development tasks:
```bash
# Run tests
make test

# Run unit tests
make test-unit

# Run integration tests
make test-integration

# Run tests with coverage
make test-cov

# Run linter
make lint

# Format code
make format

# Check code formatting
make format-check
```

### 9. Manage Dependencies
Manage Python dependencies:
```bash
# Install new dependencies
pip install package_name

# Install from requirements file
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"

# Upgrade dependencies
pip install --upgrade package_name

# Generate requirements file
pip freeze > requirements.txt

# Check for security vulnerabilities
make check-deps
```

### 10. Database Management
Manage the local database:
```bash
# Run database migrations
make db-init

# Create new migration
make db-migrate

# Rollback migration
make db-rollback

# Connect to database
psql -h localhost -p 5432 -U postgres -d reddit08

# Backup database
pg_dump -h localhost -p 5432 -U postgres reddit08 > backup.sql

# Restore database
psql -h localhost -p 5432 -U postgres reddit08 < backup.sql
```

### 11. Data Directory Management
Manage data directories:
```bash
# Initialize data directories
make data-init

# Clean data directories
make data-clean

# Check data directory status
ls -la data/
du -sh data/
```

### 12. Environment Management
Manage environment variables:
```bash
# View environment variables
env | grep POSTGRES
env | grep REDIS

# Set environment variables temporarily
export DEBUG=true
export LOG_LEVEL=DEBUG

# Unset environment variables
unset DEBUG
unset LOG_LEVEL
```

### 13. Performance Profiling
Run performance profiling:
```bash
# Run performance profiling
make perf-profile

# Profile specific script
python -m cProfile -o profile_output.prof src/scripts/specific_script.py

# Analyze profile results
python -m pstats profile_output.prof
```

### 14. Development Environment Cleanup
Clean up development environment:
```bash
# Clean build artifacts
make clean

# Remove Python cache files
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Reset database (development only)
make db-reset
```

### 15. Development Environment Status
Check development environment status:
```bash
# Check Python version
python --version

# Check virtual environment
which python

# Check installed packages
pip list

# Check service status
ps aux | grep postgres
ps aux | grep redis
```

## Verification
After completing the above steps, you should be able to:
- [ ] Start and stop the development server
- [ ] Manage background processes
- [ ] Monitor server logs
- [ ] Manage database services
- [ ] Run development tasks (tests, linting, formatting)
- [ ] Manage Python dependencies
- [ ] Manage the local database
- [ ] Manage data directories
- [ ] Manage environment variables
- [ ] Run performance profiling
- [ ] Clean up the development environment
- [ ] Check development environment status

## Troubleshooting
If local development management issues occur:

1. **Server won't start**:
   - Check port availability: `netstat -an | grep :8000`
   - Verify virtual environment is activated
   - Check environment variables
   - Review application logs

2. **Auto-reload not working**:
   - Verify `--reload` flag is used
   - Check file permissions
   - Review reload directory settings
   - Test with simple file changes

3. **Database connection issues**:
   - Check database service status
   - Verify connection settings in .env
   - Test manual database connection
   - Review firewall settings

4. **Dependency conflicts**:
   - Check requirements.txt for conflicts
   - Use virtual environment isolation
   - Upgrade or downgrade specific packages
   - Recreate virtual environment

5. **Test failures**:
   - Check test environment setup
   - Verify test database configuration
   - Review test dependencies
   - Run tests in isolation

6. **Performance issues**:
   - Run performance profiling
   - Check system resource usage
   - Optimize database queries
   - Review caching configuration

## Next Steps
Proceed to Chunk 24: Monitoring Setup to configure comprehensive monitoring for the CRE Intelligence Platform.