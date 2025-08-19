# Installation Chunk 21: Scheduled Jobs Setup

## Overview
This installation chunk configures automated scheduled jobs for data collection, processing, and analysis in the CRE Intelligence Platform.

## Prerequisites
- Repository cloned (Chunk 07)
- Data source configuration completed (Chunk 19)
- Lexicon initialization completed (Chunk 20)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Activate Virtual Environment (for local development)
If using local development setup:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Configure Celery Beat Schedule
Edit the Celery beat schedule configuration:
```bash
# Edit the Celery configuration file
nano src/mcp/fastapi_app/celery_config.py
# or
code src/mcp/fastapi_app/celery_config.py
# or
vim src/mcp/fastapi_app/celery_config.py
```

Update the beat schedule configuration:
```python
from celery.schedules import crontab

beat_schedule = {
    'collect-reddit-data': {
        'task': 'src.mcp.fastapi_app.tasks.collect_reddit_data',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'collect-news-data': {
        'task': 'src.mcp.fastapi_app.tasks.collect_news_data',
        'schedule': crontab(minute=0, hour=9),  # Daily at 9 AM
    },
    'process-collected-data': {
        'task': 'src.mcp.fastapi_app.tasks.process_collected_data',
        'schedule': crontab(minute=30, hour='*/6'),  # 30 minutes after data collection
    },
    'generate-market-reports': {
        'task': 'src.mcp.fastapi_app.tasks.generate_market_reports',
        'schedule': crontab(minute=0, hour=10, day_of_week=1),  # Weekly on Monday at 10 AM
    },
    'update-lexicon': {
        'task': 'src.mcp.fastapi_app.tasks.update_lexicon',
        'schedule': crontab(minute=0, hour=2, day_of_week=0),  # Weekly on Sunday at 2 AM
    },
    'cleanup-old-data': {
        'task': 'src.mcp.fastapi_app.tasks.cleanup_old_data',
        'schedule': crontab(minute=0, hour=1, day_of_month=1),  # Monthly on 1st at 1 AM
    },
}
```

### 4. For Docker Deployment - Verify Docker Compose Configuration
Check that Celery beat is configured in `docker-compose.yml`:
```yaml
# Ensure this section exists in docker-compose.yml
celery-beat:
  build:
    context: .
    dockerfile: Dockerfile
  container_name: reddit08-celery-beat
  command: python -m celery -A src.mcp.fastapi_app.tasks beat --loglevel=info
  environment:
    # ... environment variables ...
  depends_on:
    - postgres
    - redis
  networks:
    - reddit08-network
  restart: unless-stopped
```

### 5. For Local Development - Start Celery Beat
Start Celery beat for local development:
```bash
# Start Celery beat
celery -A src.mcp.fastapi_app.tasks beat --loglevel=info

# Or run in background
celery -A src.mcp.fastapi_app.tasks beat --loglevel=info --detach
```

### 6. Configure System Cron Jobs (Alternative Approach)
Set up system-level cron jobs as an alternative to Celery beat:
```bash
# Edit crontab
crontab -e

# Add scheduled jobs to crontab
0 */6 * * * cd /path/to/reddit08 && venv/bin/python src/scripts/collect_reddit_data.py
0 9 * * * cd /path/to/reddit08 && venv/bin/python src/scripts/collect_news_data.py
30 */6 * * * cd /path/to/reddit08 && venv/bin/python src/scripts/process_data.py
0 10 * * 1 cd /path/to/reddit08 && venv/bin/python src/scripts/generate_reports.py
0 2 * * 0 cd /path/to/reddit08 && venv/bin/python src/scripts/refresh_tfidf_via_mcp.py
0 1 1 * * cd /path/to/reddit08 && venv/bin/python src/scripts/cleanup_data.py
```

### 7. Test Scheduled Job Configuration
Test that scheduled jobs can be executed manually:
```bash
# Test Reddit data collection
python src/scripts/collect_reddit_data.py

# Test news data collection
python src/scripts/collect_news_data.py

# Test data processing
python src/scripts/process_data.py

# Test market report generation
python src/scripts/generate_reports.py
```

### 8. Monitor Scheduled Jobs
Monitor the execution of scheduled jobs:
```bash
# For Docker deployment
docker-compose logs celery-beat
docker-compose logs celery-worker

# For local development
tail -f logs/celery_beat.log
tail -f logs/celery_worker.log

# Check Redis for scheduled tasks
redis-cli keys "celery*"
```

### 9. Verify Job Scheduling
Verify that jobs are properly scheduled:
```bash
# For Celery beat
celery -A src.mcp.fastapi_app.tasks inspect scheduled

# List active tasks
celery -A src.mcp.fastapi_app.tasks inspect active
```

### 10. Configure Job Retry Policies
Set up retry policies for failed jobs:
```bash
# Edit task definitions to include retry configuration
nano src/mcp/fastapi_app/tasks.py
```

Example task with retry policy:
```python
@app.task(bind=True, max_retries=3, default_retry_delay=60)
def collect_reddit_data(self):
    try:
        # Task implementation
        pass
    except Exception as exc:
        raise self.retry(exc=exc)
```

### 11. Set Up Job Monitoring
Configure monitoring for scheduled jobs:
```bash
# Create monitoring script
nano src/scripts/monitor_jobs.py
# or
code src/scripts/monitor_jobs.py
# or
vim src/scripts/monitor_jobs.py
```

### 12. Test Job Failures and Recovery
Test job failure handling:
```bash
# Simulate job failure
python src/scripts/test_job_failure.py

# Check retry mechanism
celery -A src.mcp.fastapi_app.tasks inspect reserved
```

## Verification
After completing the above steps, you should have:
- [ ] Celery beat schedule configured
- [ ] Scheduled jobs properly defined
- [ ] Docker compose configuration verified (Docker deployment)
- [ ] Celery beat started (local development)
- [ ] System cron jobs configured (alternative approach)
- [ ] Scheduled jobs testable manually
- [ ] Job monitoring configured
- [ ] Retry policies implemented
- [ ] Job scheduling verified
- [ ] Job failure handling tested

## Troubleshooting
If scheduled jobs setup fails:

1. **Celery beat not starting**:
   - Check Redis connectivity
   - Verify Celery configuration
   - Check environment variables
   - Review Celery logs

2. **Jobs not executing**:
   - Verify schedule syntax
   - Check task registration
   - Monitor Redis for scheduled tasks
   - Review worker logs

3. **Job failures**:
   - Check task implementation
   - Verify dependencies
   - Review error logs
   - Test retry mechanisms

4. **Timing issues**:
   - Verify timezone settings
   - Check system clock synchronization
   - Validate cron expressions
   - Test schedule manually

5. **Resource constraints**:
   - Monitor system resources
   - Check Redis memory usage
   - Optimize task execution
   - Scale workers if needed

## Next Steps
Proceed to Chunk 22: Docker Service Management or Chunk 23: Local Development Management depending on your deployment method.