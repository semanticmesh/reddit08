# Installation Chunk 30: Local Service Logs Inspection

## Overview
This installation chunk covers how to effectively inspect, monitor, and analyze logs for local development services of the CRE Intelligence Platform to diagnose issues and maintain system health.

## Prerequisites
- Local development server startup completed (Chunk 16)
- Local development management completed (Chunk 23)
- System requirements verification completed (Chunk 01)

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

### 3. View Application Logs
```bash
# View main application logs
tail -f logs/app.log

# View all log files
tail -f logs/*.log

# View last 100 lines of logs
tail -n 100 logs/app.log

# View logs with line numbers
cat -n logs/app.log

# View logs with timestamps
grep -E "\[(DEBUG|INFO|WARNING|ERROR|CRITICAL)\]" logs/app.log
```

### 4. Filter and Search Logs
```bash
# Search for error messages
grep "ERROR" logs/app.log

# Search for warning messages
grep "WARNING" logs/app.log

# Search for specific terms
grep -i "database" logs/app.log
grep -i "redis" logs/app.log
grep -i "api" logs/app.log

# Search for multiple terms
grep -E "(ERROR|CRITICAL|FATAL)" logs/app.log

# Case-insensitive search
grep -i "exception" logs/app.log

# Search with context (show 3 lines before and after)
grep -C 3 "ERROR" logs/app.log
```

### 5. Real-time Log Monitoring
```bash
# Monitor logs in real-time
tail -f logs/app.log

# Monitor multiple log files
tail -f logs/*.log

# Monitor logs with grep filtering
tail -f logs/app.log | grep -E "(ERROR|WARNING)"

# Monitor logs with color highlighting
tail -f logs/app.log | grep --color=always -E "(ERROR|WARNING|INFO)"

# Monitor logs with timestamp filtering
tail -f logs/app.log | grep "$(date +%Y-%m-%d)"
```

### 6. Advanced Log Analysis
```bash
# Count error occurrences
grep -c "ERROR" logs/app.log

# View unique error messages
grep "ERROR" logs/app.log | sort | uniq

# Show log statistics by level
grep -o -E "(DEBUG|INFO|WARNING|ERROR|CRITICAL)" logs/app.log | sort | uniq -c

# Analyze log volume over time
awk '{print $1, $2}' logs/app.log | sort | uniq -c

# Find most frequent log messages
grep "INFO" logs/app.log | sort | uniq -c | sort -nr | head -10
```

### 7. Service-Specific Log Analysis

#### PostgreSQL Logs
```bash
# View PostgreSQL logs (if configured)
tail -f /var/log/postgresql/postgresql-*.log

# On macOS with Homebrew
tail -f /usr/local/var/log/postgres.log

# View PostgreSQL logs via Docker (if using Docker for DB)
docker-compose logs postgres

# Search for PostgreSQL errors
grep -i "error\|fatal\|panic" /var/log/postgresql/postgresql-*.log
```

#### Redis Logs
```bash
# View Redis logs (if configured)
tail -f /var/log/redis/redis-server.log

# On macOS with Homebrew
tail -f /usr/local/var/log/redis.log

# View Redis logs via Docker (if using Docker for Redis)
docker-compose logs redis

# Search for Redis errors
grep -i "error\|critical" /var/log/redis/redis-server.log
```

#### System Service Logs
```bash
# View system service logs (Linux)
sudo journalctl -u postgresql
sudo journalctl -u redis
sudo journalctl -f -u postgresql
sudo journalctl -f -u redis

# View system logs (macOS)
tail -f /var/log/system.log

# View system logs (Windows - PowerShell)
Get-EventLog -LogName Application -Newest 100
```

### 8. Log File Management
```bash
# Check log file sizes
du -sh logs/*.log

# Check available disk space
df -h

# Rotate logs manually
logrotate -f /etc/logrotate.d/reddit08

# Compress old logs
gzip logs/app.log.1

# Remove old compressed logs
find logs/ -name "*.log.*.gz" -mtime +30 -delete

# Archive logs to backup directory
mkdir -p logs/archive
mv logs/app.log.1 logs/archive/
```

### 9. Configure Log Rotation
```bash
# Create or edit logrotate configuration
sudo nano /etc/logrotate.d/reddit08
```

Example logrotate configuration:
```bash
/path/to/reddit08/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 reddit08 reddit08
    postrotate
        systemctl reload reddit08-app.service > /dev/null 2>&1 || true
    endscript
}
```

### 10. Centralized Log Management
```bash
# Create log aggregation script
nano scripts/aggregate_local_logs.py
```

Example log aggregation script:
```python
#!/usr/bin/env python3
import os
import glob
import shutil
from datetime import datetime

def aggregate_local_logs():
    log_dir = "logs"
    backup_dir = "logs/archive"
    
    # Create backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Aggregate all log files
    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    
    for log_file in log_files:
        if os.path.isfile(log_file):
            # Create backup
            backup_file = os.path.join(backup_dir, f"{os.path.basename(log_file)}.{timestamp}")
            shutil.copy2(log_file, backup_file)
            print(f"Backed up {log_file} to {backup_file}")
    
    print("Log aggregation completed")

if __name__ == "__main__":
    aggregate_local_logs()
```

### 11. Log Monitoring and Alerting
```bash
# Create log monitoring script
nano scripts/monitor_local_logs.sh
```

Example log monitoring script:
```bash
#!/bin/bash

LOG_FILE="logs/app.log"
ALERT_EMAIL="admin@example.com"
ERROR_THRESHOLD=5

# Function to send alert
send_alert() {
    local error_count=$1
    local errors=$2
    
    echo "CRITICAL: $error_count errors detected in $LOG_FILE
    
$errors" | mail -s "CRE Intelligence Platform - Log Alert" $ALERT_EMAIL
    
    echo "Alert sent for $error_count errors"
}

# Monitor logs for errors
monitor_logs() {
    echo "Starting log monitoring..."
    
    while true; do
        # Count errors in the last 5 minutes
        error_count=$(tail -n 1000 $LOG_FILE | grep -c "ERROR")
        
        if [ $error_count -gt $ERROR_THRESHOLD ]; then
            # Get the actual error lines
            errors=$(tail -n 1000 $LOG_FILE | grep "ERROR" | tail -n 10)
            send_alert $error_count "$errors"
        fi
        
        # Wait before next check
        sleep 300
    done
}

# Run monitoring
monitor_logs
```

Make script executable:
```bash
chmod +x scripts/monitor_local_logs.sh
```

### 12. Performance Log Analysis
```bash
# Monitor application performance logs
tail -f logs/performance.log

# Analyze response times
grep "response_time" logs/app.log | awk '{print $NF}' | sort -n | tail -10

# Monitor memory usage logs
grep "memory_usage" logs/app.log

# Analyze database query performance
grep "query_duration" logs/app.log | awk '{print $NF}' | sort -n | tail -10
```

### 13. Security Log Analysis
```bash
# Monitor security logs
tail -f logs/security.log

# Search for authentication failures
grep "authentication failed" logs/security.log

# Search for unauthorized access attempts
grep "unauthorized" logs/security.log

# Search for security violations
grep -i "security violation\|intrusion\|attack" logs/security.log
```

### 14. Verify Log Inspection Setup
```bash
# Test log viewing commands
tail -n 10 logs/app.log

# Test log filtering
grep "INFO" logs/app.log | head -5

# Test log monitoring
timeout 10s tail -f logs/app.log || true

# Test log aggregation script
python scripts/aggregate_local_logs.py --test
```

## Verification
After completing the above steps, you should be able to:
- [ ] View and monitor application logs effectively
- [ ] Filter and search logs for specific content
- [ ] Perform real-time log monitoring
- [ ] Conduct advanced log analysis
- [ ] Analyze service-specific logs
- [ ] Manage log files and rotation
- [ ] Implement centralized log management
- [ ] Set up log monitoring and alerting
- [ ] Analyze performance logs
- [ ] Monitor security logs
- [ ] Verify log inspection setup

## Common Log Patterns and Meanings

### Application Logs
- **"INFO:     Application startup complete"**: Application started successfully
- **"ERROR:    [Errno 98] Address already in use"**: Port conflict
- **"CRITICAL: Database connection failed"**: Database connectivity issue
- **"WARNING:  Retrying database connection"**: Temporary database issue

### Database Logs
- **"database system is ready to accept connections"**: PostgreSQL ready
- **"connection received"**: New database connection
- **"disconnection"**: Database connection closed
- **"statement: "**: SQL query executed

### Redis Logs
- **"Ready to accept connections"**: Redis ready
- **"Accepted"**: New Redis connection
- **"Client closed connection"**: Redis connection closed
- **"OOM"**: Out of memory condition

### System Logs
- **"systemd[1]: Started"**: Service started successfully
- **"systemd[1]: Failed"**: Service failed to start
- **"kernel: [error]"**: Kernel-level error
- **"oom-killer"**: Out of memory condition

## Troubleshooting
If local service log inspection issues occur:

1. **Cannot view logs**:
   - Check if log files exist: `ls -la logs/`
   - Verify file permissions: `ls -la logs/*.log`
   - Check if services are writing to logs

2. **Logs not showing**:
   - Verify logging configuration in application
   - Check log level settings
   - Ensure services are running and generating logs

3. **Performance issues with log viewing**:
   - Use `tail -n` to limit log output
   - Filter logs with `grep`
   - Consider log rotation for large files

4. **Log rotation issues**:
   - Check logrotate configuration
   - Verify log file permissions
   - Test logrotate manually

5. **Monitoring script issues**:
   - Check script permissions
   - Verify email configuration
   - Test script manually

## Next Steps
Proceed to Chunk 31: Database Connection Troubleshooting to learn how to diagnose and resolve database connectivity issues.