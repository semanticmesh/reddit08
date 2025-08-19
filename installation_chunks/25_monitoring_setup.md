# Installation Chunk 25: Monitoring Setup

## Overview
This installation chunk covers the setup of comprehensive monitoring for the CRE Intelligence Platform, including system metrics, application logs, and health checks.

## Prerequisites
- System requirements verification completed (Chunk 01)
- Docker service deployment completed (Chunk 10) OR
- Local development server startup completed (Chunk 16)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Set Up Application Logging

#### Configure Logging Levels
Edit the logging configuration:
```bash
# Edit logging configuration file
nano config/logging_config.json
# or
code config/logging_config.json
# or
vim config/logging_config.json
```

Example logging configuration:
```json
{
  "version": 1,
  "disable_existing_loggers": false,
  "formatters": {
    "standard": {
      "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    },
    "detailed": {
      "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
    }
  },
  "handlers": {
    "console": {
      "class": "logging.StreamHandler",
      "level": "INFO",
      "formatter": "standard",
      "stream": "ext://sys.stdout"
    },
    "file": {
      "class": "logging.handlers.RotatingFileHandler",
      "level": "DEBUG",
      "formatter": "detailed",
      "filename": "logs/app.log",
      "maxBytes": 10485760,
      "backupCount": 5
    }
  },
  "loggers": {
    "": {
      "handlers": ["console", "file"],
      "level": "DEBUG",
      "propagate": false
    }
  }
}
```

#### Test Logging Configuration
```bash
# Test logging
python src/scripts/test_logging.py

# Or use Makefile command
make test-logging
```

### 3. Set Up System Monitoring

#### For Docker Deployment - Add Monitoring Services
Edit `docker-compose.yml` to include monitoring services:
```yaml
# Add to services section
prometheus:
  image: prom/prometheus:latest
  container_name: reddit08-prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  networks:
    - reddit08-network
  restart: unless-stopped

grafana:
  image: grafana/grafana:latest
  container_name: reddit08-grafana
  ports:
    - "3000:3000"
  volumes:
    - grafana_data:/var/lib/grafana
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin123
  networks:
    - reddit08-network
  restart: unless-stopped
  depends_on:
    - prometheus

# Add to volumes section
volumes:
  prometheus_data:
    driver: local
  grafana_data:
    driver: local
```

#### Create Prometheus Configuration
```bash
# Create monitoring directory
mkdir -p monitoring

# Create Prometheus configuration
nano monitoring/prometheus.yml
```

Example Prometheus configuration:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'reddit08-app'
    static_configs:
      - targets: ['app:8000']

  - job_name: 'reddit08-postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'reddit08-redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'reddit08-celery'
    static_configs:
      - targets: ['celery-worker:5555']
```

### 4. Set Up Log Monitoring

#### For Local Development - Install Log Analysis Tools
```bash
# Install log analysis tools
pip install loguru
pip install elasticsearch

# Or using system package manager (Ubuntu/Debian)
sudo apt install logrotate multitail
```

#### Configure Log Rotation
```bash
# Create logrotate configuration
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

### 5. Set Up Health Check Monitoring

#### Create Health Check Script
```bash
# Create health check script
nano scripts/health_monitor.py
# or
code scripts/health_monitor.py
# or
vim scripts/health_monitor.py
```

Example health check script:
```python
#!/usr/bin/env python3
import requests
import time
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/health_monitor.log'),
        logging.StreamHandler()
    ]
)

def check_service_health(service_name, url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            logging.info(f"{service_name} is healthy")
            return True
        else:
            logging.warning(f"{service_name} returned status {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"{service_name} health check failed: {str(e)}")
        return False

def main():
    services = {
        "API Service": "http://localhost:8000/health",
        "Database": "http://localhost:8000/health/database",
        "Redis": "http://localhost:8000/health/redis"
    }
    
    for service_name, url in services.items():
        check_service_health(service_name, url)
    
    logging.info("Health check completed")

if __name__ == "__main__":
    main()
```

Make script executable:
```bash
chmod +x scripts/health_monitor.py
```

#### Schedule Health Checks
```bash
# Add to crontab for regular health checks
crontab -e

# Add health check every 5 minutes
*/5 * * * * cd /path/to/reddit08 && python scripts/health_monitor.py
```

### 6. Set Up Performance Monitoring

#### Configure Application Performance Monitoring
```bash
# Install performance monitoring tools
pip install prometheus-client
pip install psutil
```

#### Add Performance Metrics to Application
Edit the main application file to include metrics:
```python
# Add to src/mcp/fastapi_app/main.py
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

# Define metrics
REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration', ['method', 'endpoint'])

# Add metrics endpoint
@app.get('/metrics')
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

### 7. Set Up Alerting

#### Create Alert Configuration
```bash
# Create alert configuration
nano monitoring/alerts.yml
```

Example alert configuration:
```yaml
groups:
  - name: reddit08-alerts
    rules:
      - alert: HighCPUUsage
        expr: rate(process_cpu_seconds_total[5m]) > 0.8
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 2 minutes"

      - alert: HighMemoryUsage
        expr: rate(process_resident_memory_bytes[5m]) > 1073741824  # 1GB
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 1GB for more than 2 minutes"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "Service has been down for more than 1 minute"
```

### 8. Start Monitoring Services

#### For Docker Deployment
```bash
# Start monitoring services
docker-compose up -d prometheus grafana

# Check service status
docker-compose ps prometheus grafana
```

#### For Local Development
```bash
# Start monitoring services
make monitor-start

# Or manually start services
prometheus --config.file=monitoring/prometheus.yml &
grafana-server --config=monitoring/grafana.ini --homepath=monitoring &
```

### 9. Configure Grafana Dashboards

#### Access Grafana
1. Open browser to http://localhost:3000
2. Login with username: admin, password: admin123
3. Change password when prompted

#### Create Dashboards
1. Go to "Create" → "Dashboard"
2. Add panels for:
   - CPU Usage
   - Memory Usage
   - Disk I/O
   - Network Traffic
   - Application Response Time
   - Error Rates
   - Database Performance

### 10. Verify Monitoring Setup
```bash
# Check if monitoring services are running
docker-compose ps prometheus grafana

# Check if metrics endpoint is accessible
curl http://localhost:8000/metrics

# Check if Prometheus is scraping metrics
curl http://localhost:9090/metrics

# Check if Grafana is accessible
curl http://localhost:3000
```

## Verification
After completing the above steps, you should have:
- [ ] Application logging configured and tested
- [ ] System monitoring services (Prometheus, Grafana) deployed
- [ ] Log monitoring and rotation configured
- [ ] Health check monitoring implemented
- [ ] Performance monitoring metrics added
- [ ] Alerting configuration set up
- [ ] Monitoring services started and accessible
- [ ] Grafana dashboards created
- [ ] Monitoring setup verified

## Troubleshooting
If monitoring setup issues occur:

1. **Services won't start**:
   - Check service logs: `docker-compose logs service_name`
   - Verify configuration files
   - Check port availability
   - Review environment variables

2. **Metrics not appearing**:
   - Verify metrics endpoint is accessible
   - Check Prometheus configuration
   - Review scraping intervals
   - Test metrics endpoint manually

3. **Grafana connection issues**:
   - Check Grafana service status
   - Verify Prometheus data source configuration
   - Review network connectivity
   - Check firewall settings

4. **Alerts not firing**:
   - Verify alert rules configuration
   - Check alert manager setup
   - Review alert thresholds
   - Test alert conditions manually

5. **Performance issues**:
   - Monitor resource usage of monitoring services
   - Optimize scraping intervals
   - Review retention policies
   - Scale monitoring infrastructure

## Next Steps
Proceed to Chunk 26: Security Hardening to implement security measures for the CRE Intelligence Platform.