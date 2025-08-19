# Installation Chunk 29: Docker Service Logs Inspection

## Overview
This installation chunk covers how to effectively inspect, monitor, and analyze Docker service logs for the CRE Intelligence Platform to diagnose issues and maintain system health.

## Prerequisites
- Docker installation and verification completed (Chunk 02)
- Docker service deployment completed (Chunk 10)
- Docker service management completed (Chunk 22)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. View Logs for All Services
```bash
# View logs for all services
docker-compose logs

# View last 100 lines of all logs
docker-compose logs --tail=100

# View logs with timestamps
docker-compose logs -t

# View logs in color (if supported)
docker-compose logs --color
```

### 3. View Logs for Specific Services
```bash
# View logs for the main application
docker-compose logs app

# View logs for PostgreSQL database
docker-compose logs postgres

# View logs for Redis
docker-compose logs redis

# View logs for Celery worker
docker-compose logs celery-worker

# View logs for Celery beat
docker-compose logs celery-beat

# View logs for Nginx (if configured)
docker-compose logs nginx
```

### 4. Real-time Log Monitoring
```bash
# Follow logs in real-time for all services
docker-compose logs -f

# Follow logs for specific service
docker-compose logs -f app

# Follow logs with timestamp
docker-compose logs -f -t

# Follow logs with color
docker-compose logs -f --color
```

### 5. Filter and Search Logs
```bash
# View logs since a specific time
docker-compose logs --since="2025-01-01"

# View logs until a specific time
docker-compose logs --until="2025-01-02"

# View logs from the last hour
docker-compose logs --since="1h"

# View logs from the last 30 minutes
docker-compose logs --since="30m"

# Search for specific terms in logs
docker-compose logs | grep "ERROR"
docker-compose logs | grep "WARNING"
docker-compose logs | grep "Exception"

# Case-insensitive search
docker-compose logs | grep -i "error"
```

### 6. Advanced Log Analysis
```bash
# Count error occurrences
docker-compose logs | grep -c "ERROR"

# View unique error messages
docker-compose logs | grep "ERROR" | sort | uniq

# Show log statistics
docker-compose logs | awk '{print $1}' | sort | uniq -c | sort -nr

# Extract specific fields from logs
docker-compose logs --since="1h" | grep "app" | awk '{print $3, $4, $5}'

# Monitor log volume
docker-compose logs --since="1h" | wc -l
```

### 7. Export Logs for Analysis
```bash
# Export all logs to a file
docker-compose logs > logs/docker_all_$(date +%Y%m%d_%H%M%S).log

# Export logs for specific service
docker-compose logs app > logs/docker_app_$(date +%Y%m%d_%H%M%S).log

# Export logs with timestamps
docker-compose logs -t > logs/docker_timestamped_$(date +%Y%m%d_%H%M%S).log

# Export logs since specific time
docker-compose logs --since="24h" > logs/docker_last24h_$(date +%Y%m%d_%H%M%S).log
```

### 8. Log Level Filtering
```bash
# View only error logs
docker-compose logs | grep -E "(ERROR|CRITICAL|FATAL)"

# View warning and error logs
docker-compose logs | grep -E "(WARNING|ERROR|CRITICAL)"

# View info level logs
docker-compose logs | grep "INFO"

# View debug level logs
docker-compose logs | grep "DEBUG"
```

### 9. Service-Specific Log Analysis

#### Application Service Logs
```bash
# View application startup logs
docker-compose logs app | grep "Startup"

# View API request logs
docker-compose logs app | grep "GET\|POST\|PUT\|DELETE"

# View database connection logs
docker-compose logs app | grep "database\|postgres"

# View authentication logs
docker-compose logs app | grep "auth\|login\|token"
```

#### Database Service Logs
```bash
# View PostgreSQL startup logs
docker-compose logs postgres | grep "database system is ready"

# View connection logs
docker-compose logs postgres | grep "connection"

# View query logs
docker-compose logs postgres | grep "statement\|duration"

# View error logs
docker-compose logs postgres | grep "ERROR\|FATAL"
```

#### Redis Service Logs
```bash
# View Redis startup logs
docker-compose logs redis | grep "Ready to accept connections"

# View connection logs
docker-compose logs redis | grep "Accepted\|Client"

# View memory usage logs
docker-compose logs redis | grep "MEMORY"

# View error logs
docker-compose logs redis | grep "ERROR"
```

#### Celery Service Logs
```bash
# View Celery worker startup logs
docker-compose logs celery-worker | grep "Connected to"

# View task execution logs
docker-compose logs celery-worker | grep "Task\|task"

# View task result logs
docker-compose logs celery-worker | grep "Result\|result"

# View error logs
docker-compose logs celery-worker | grep "ERROR\|Exception"
```

### 10. Log Rotation and Management
```bash
# Check Docker log driver
docker info | grep "Logging Driver"

# Configure log rotation in docker-compose.yml
# Add to service configuration:
# logging:
#   driver: "json-file"
#   options:
#     max-size: "10m"
#     max-file: "3"

# View current log file sizes
docker inspect reddit08-app | grep LogPath
ls -lh $(docker inspect reddit08-app | grep LogPath | cut -d'"' -f4)
```

### 11. Centralized Log Management
```bash
# Create log aggregation script
nano scripts/aggregate_logs.py
```

Example log aggregation script:
```python
#!/usr/bin/env python3
import subprocess
import json
from datetime import datetime
import os

def aggregate_docker_logs():
    services = ['app', 'postgres', 'redis', 'celery-worker', 'celery-beat']
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for service in services:
        try:
            # Get logs from service
            result = subprocess.run(
                ['docker-compose', 'logs', service],
                capture_output=True,
                text=True,
                cwd='/path/to/reddit08'
            )
            
            # Save to file
            log_file = f"logs/{service}_logs_{timestamp}.log"
            with open(log_file, 'w') as f:
                f.write(result.stdout)
            
            print(f"Logs for {service} saved to {log_file}")
        except Exception as e:
            print(f"Error collecting logs for {service}: {e}")

if __name__ == "__main__":
    aggregate_docker_logs()
```

### 12. Log Monitoring and Alerting
```bash
# Create log monitoring script
nano scripts/monitor_logs.py
```

Example log monitoring script:
```python
#!/usr/bin/env python3
import subprocess
import re
import smtplib
from email.mime.text import MIMEText
import time

def monitor_critical_errors():
    while True:
        # Get recent logs
        result = subprocess.run(
            ['docker-compose', 'logs', '--since=5m'],
            capture_output=True,
            text=True
        )
        
        # Check for critical errors
        critical_patterns = [
            r'CRITICAL',
            r'FATAL',
            r'Unhandled exception',
            r'Database connection failed'
        ]
        
        errors_found = []
        for line in result.stdout.split('\n'):
            for pattern in critical_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    errors_found.append(line)
        
        # Send alert if errors found
        if errors_found:
            send_alert(errors_found)
        
        # Wait before next check
        time.sleep(300)  # Check every 5 minutes

def send_alert(errors):
    # Email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "admin@example.com"
    receiver_email = "alerts@example.com"
    password = "your_email_password"
    
    # Create message
    message = MIMEText(f"Critical errors detected:\n\n" + "\n".join(errors))
    message["Subject"] = "CRE Intelligence Platform - Critical Error Alert"
    message["From"] = sender_email
    message["To"] = receiver_email
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print("Alert sent successfully")
    except Exception as e:
        print(f"Failed to send alert: {e}")

if __name__ == "__main__":
    monitor_critical_errors()
```

### 13. Verify Log Inspection Setup
```bash
# Test log viewing commands
docker-compose logs --tail=10

# Test log filtering
docker-compose logs | grep "INFO" | head -5

# Test log export
docker-compose logs --tail=100 > test_logs.log && ls -la test_logs.log

# Test log monitoring script
python scripts/monitor_logs.py --test
```

## Verification
After completing the above steps, you should be able to:
- [ ] View logs for all Docker services
- [ ] View logs for specific services
- [ ] Monitor logs in real-time
- [ ] Filter and search logs effectively
- [ ] Perform advanced log analysis
- [ ] Export logs for further analysis
- [ ] Filter logs by level and content
- [ ] Analyze service-specific logs
- [ ] Manage log rotation and storage
- [ ] Implement centralized log management
- [ ] Set up log monitoring and alerting
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

### Celery Logs
- **"Connected to redis"**: Celery connected to broker
- **"Task [task_name] succeeded"**: Task completed successfully
- **"Task [task_name] failed"**: Task failed
- **"Received task"**: Task received for processing

## Troubleshooting
If log inspection issues occur:

1. **Cannot view logs**:
   - Check if services are running: `docker-compose ps`
   - Verify container names
   - Check Docker daemon status

2. **Logs not showing**:
   - Check log driver configuration
   - Verify service is generating logs
   - Check log level settings

3. **Performance issues with log viewing**:
   - Use `--tail` to limit log output
   - Filter logs with `grep`
   - Export large logs to files

4. **Log rotation issues**:
   - Check Docker log driver settings
   - Verify log file sizes
   - Review log rotation configuration

## Next Steps
Proceed to Chunk 30: Local Service Logs Inspection to learn how to monitor and analyze logs for local development services.