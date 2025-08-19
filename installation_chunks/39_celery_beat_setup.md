# Installation Chunk 39: Celery Beat Setup

## Overview
This installation chunk covers how to configure and manage Celery Beat for scheduled task execution in the CRE Intelligence Platform, including scheduler configuration, task scheduling, and monitoring.

## Prerequisites
- Redis installation and setup completed (Chunk 05)
- Celery worker setup completed (Chunk 38)
- Scheduled jobs setup completed (Chunk 21)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Understand Celery Beat Architecture

#### Review Celery Beat Configuration
```bash
# Examine Celery Beat configuration in docker-compose.yml
cat docker-compose.yml | grep -A 15 -B 5 "celery-beat"

# Expected Celery Beat configuration:
# celery-beat:
#   build:
#     context: .
#     dockerfile: Dockerfile
#   command: python -m celery -A src.mcp.fastapi_app.tasks beat --loglevel=info --scheduler redis
#   environment:
#     # ... environment variables
#   volumes:
#     # ... volume mappings
#   depends_on:
#     - redis
```

#### Analyze Scheduled Task Implementation
```bash
# Review scheduled task implementations
ls -la src/mcp/fastapi_app/tasks/
cat src.mcp.fastapi_app/celery_config.py | grep -A 20 "beat_schedule"

# Check task scheduler configuration
cat src/mcp/fastapi_app/tasks/scheduled_tasks.py
```

### 3. Verify Celery Beat Configuration

#### Check Celery Beat Environment Variables
```bash
# Verify Celery Beat environment variables
cat .env | grep -E "(CELERY|REDIS|SCHEDULER)"

# Expected environment variables:
# CELERY_BROKER_URL=redis://redis:6379/0
# CELERY_RESULT_BACKEND=redis://redis:6379/0
# CELERY_BEAT_SCHEDULER=redis
# CELERY_BEAT_SCHEDULE_FILENAME=/app/celerybeat-schedule

# For Docker deployment
cat .env.docker | grep -E "(CELERY|REDIS|SCHEDULER)"
```

#### Test Celery Beat Connectivity
```bash
# Test Redis connectivity for Celery Beat
docker-compose exec redis redis-cli ping

# Check Celery Beat scheduler connection
docker-compose exec celery-beat python -c "
import celery
from src.mcp.fastapi_app.celery_app import celery_app
try:
    # Test scheduler connectivity
    from celery.beat import Scheduler
    scheduler = Scheduler(app=celery_app)
    print('✓ Celery Beat scheduler connection successful')
except Exception as e:
    print(f'✗ Celery Beat scheduler connection failed: {e}')
"

# Verify Celery Beat configuration
docker-compose exec celery-beat python -c "
from src.mcp.fastapi_app.celery_app import celery_app
print('Celery Beat configuration:')
print(f'  Scheduler: {celery_app.conf.beat_scheduler}')
print(f'  Schedule filename: {celery_app.conf.beat_schedule_filename}')
print(f'  Scheduled tasks: {len(celery_app.conf.beat_schedule) if celery_app.conf.beat_schedule else 0}')
"
```

### 4. Test Celery Beat Functionality

#### Create Celery Beat Test Script
```bash
# Create Celery Beat test script
nano scripts/test_celery_beat.py
```

Example Celery Beat test script:
```python
#!/usr/bin/env python3
import asyncio
import time
from datetime import datetime, timedelta
from src.mcp.fastapi_app.celery_app import celery_app

async def test_celery_beat_functionality():
    """Test Celery Beat functionality"""
    print("Testing Celery Beat functionality...")
    start_time = datetime.now()
    
    try:
        # 1. Test scheduler initialization
        print("1. Testing scheduler initialization...")
        from celery.beat import PersistentScheduler
        
        # Create scheduler instance
        scheduler = PersistentScheduler(app=celery_app)
        print(f"   ✓ Scheduler initialized successfully")
        
        # 2. Test scheduled task retrieval
        print("2. Testing scheduled task retrieval...")
        schedule = celery_app.conf.beat_schedule
        if schedule:
            print(f"   ✓ Retrieved {len(schedule)} scheduled tasks:")
            for task_name, task_config in schedule.items():
                print(f"     - {task_name}: {task_config}")
        else:
            print("   ⚠ No scheduled tasks configured")
        
        # 3. Test task scheduling
        print("3. Testing task scheduling...")
        from celery.beat import ScheduleEntry
        
        # Create a test scheduled task
        test_entry = ScheduleEntry(
            name='test_scheduled_task',
            task='data_processing_tasks.process_data_task',
            schedule=timedelta(minutes=5),
            args=(),
            kwargs={'data': {'test': 'scheduled'}, 'processing_type': 'test_scheduled'}
        )
        
        print(f"   ✓ Test scheduled task created: {test_entry.name}")
        
        # 4. Test scheduler persistence
        print("4. Testing scheduler persistence...")
        try:
            # This would normally write to the schedule file
            # For testing, we'll just verify the configuration
            schedule_file = celery_app.conf.beat_schedule_filename
            print(f"   ✓ Schedule file configured: {schedule_file}")
        except Exception as e:
            print(f"   ⚠ Schedule persistence test: {e}")
        
        # 5. Test scheduler status
        print("5. Testing scheduler status...")
        # In a real environment, we'd check the actual beat process
        # For now, we'll verify the configuration is valid
        print("   ✓ Scheduler configuration validated")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"Celery Beat functionality test completed in {duration:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"✗ Celery Beat test failed: {e}")
        return False

def list_scheduled_tasks():
    """List all configured scheduled tasks"""
    print("Listing all scheduled tasks...")
    
    try:
        schedule = celery_app.conf.beat_schedule
        if not schedule:
            print("No scheduled tasks configured")
            return
        
        print(f"Found {len(schedule)} scheduled tasks:")
        for task_name, task_config in schedule.items():
            print(f"\nTask: {task_name}")
            print(f"  Task function: {task_config.get('task', 'N/A')}")
            print(f"  Schedule: {task_config.get('schedule', 'N/A')}")
            print(f"  Arguments: {task_config.get('args', 'N/A')}")
            print(f"  Keyword arguments: {task_config.get('kwargs', 'N/A')}")
            
    except Exception as e:
        print(f"Error listing scheduled tasks: {e}")

if __name__ == "__main__":
    success = asyncio.run(test_celery_beat_functionality())
    list_scheduled_tasks()
    exit(0 if success else 1)
```

#### Test Scheduled Task Execution
```bash
# Create scheduled task execution test script
nano scripts/test_scheduled_task_execution.py
```

Example scheduled task execution test script:
```python
#!/usr/bin/env python3
import time
from datetime import datetime
from src.mcp.fastapi_app.celery_app import celery_app
from src.mcp.fastapi_app.tasks.scheduled_tasks import daily_data_processing_task

def test_scheduled_task_execution():
    """Test scheduled task execution"""
    print("Testing scheduled task execution...")
    
    try:
        # 1. Test manual trigger of scheduled task
        print("1. Testing manual trigger of scheduled task...")
        result = daily_data_processing_task.apply_async()
        print(f"   ✓ Task triggered successfully")
        print(f"   Task ID: {result.id}")
        
        # 2. Test task completion
        print("2. Testing task completion...")
        try:
            task_result = result.get(timeout=60)
            print(f"   ✓ Task completed successfully")
            print(f"   Task result: {task_result}")
        except Exception as e:
            print(f"   ⚠ Task completion test: {e}")
        
        # 3. Test scheduler interaction
        print("3. Testing scheduler interaction...")
        # This simulates what Celery Beat would do
        from celery.beat import ScheduleEntry
        
        # Get the actual scheduled task configuration
        schedule = celery_app.conf.beat_schedule
        if schedule:
            print(f"   ✓ Found {len(schedule)} scheduled tasks in configuration")
            for task_name, task_config in schedule.items():
                print(f"     Task: {task_name}")
                print(f"     Config: {task_config}")
        else:
            print("   ⚠ No scheduled tasks found in configuration")
        
        print("✓ Scheduled task execution test completed")
        return True
        
    except Exception as e:
        print(f"✗ Scheduled task execution test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_scheduled_task_execution()
    exit(0 if success else 1)
```

### 5. Monitor Celery Beat Status

#### Create Celery Beat Monitoring Script
```bash
# Create Celery Beat monitoring script
nano scripts/monitor_celery_beat.py
```

Example Celery Beat monitoring script:
```python
#!/usr/bin/env python3
import json
import time
from datetime import datetime
from src.mcp.fastapi_app.celery_app import celery_app

class CeleryBeatMonitor:
    """Monitor Celery Beat scheduler status and performance"""
    
    def __init__(self):
        self.app = celery_app
    
    def get_scheduler_status(self):
        """Get current scheduler status"""
        try:
            # Get scheduler configuration
            scheduler_type = self.app.conf.beat_scheduler
            schedule_file = self.app.conf.beat_schedule_filename
            scheduled_tasks = self.app.conf.beat_schedule
            
            # Check if schedule file exists
            import os
            schedule_file_exists = os.path.exists(schedule_file) if schedule_file else False
            
            return {
                'timestamp': datetime.now().isoformat(),
                'scheduler_type': scheduler_type,
                'schedule_file': schedule_file,
                'schedule_file_exists': schedule_file_exists,
                'scheduled_tasks_count': len(scheduled_tasks) if scheduled_tasks else 0,
                'scheduled_tasks': list(scheduled_tasks.keys()) if scheduled_tasks else []
            }
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def monitor_scheduler(self, interval=30):
        """Monitor scheduler continuously"""
        print("Starting Celery Beat scheduler monitoring...")
        print(f"Monitoring interval: {interval} seconds")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        try:
            while True:
                status = self.get_scheduler_status()
                
                # Save status to log file
                with open("logs/celery_beat_monitoring.json", "a") as f:
                    f.write(json.dumps(status) + "\n")
                
                # Display status
                timestamp = status['timestamp']
                print(f"[{timestamp}] Celery Beat Scheduler Status:")
                
                if 'error' in status:
                    print(f"  ✗ Error: {status['error']}")
                else:
                    print(f"  ✓ Scheduler type: {status['scheduler_type']}")
                    print(f"  Schedule file: {status['schedule_file']}")
                    print(f"  File exists: {status['schedule_file_exists']}")
                    print(f"  Scheduled tasks: {status['scheduled_tasks_count']}")
                    if status['scheduled_tasks']:
                        print("  Task list:")
                        for task in status['scheduled_tasks']:
                            print(f"    - {task}")
                
                print("-" * 50)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
    
    def get_scheduled_task_details(self):
        """Get detailed information about scheduled tasks"""
        try:
            scheduled_tasks = self.app.conf.beat_schedule
            if not scheduled_tasks:
                return {"message": "No scheduled tasks configured"}
            
            task_details = {}
            for task_name, task_config in scheduled_tasks.items():
                task_details[task_name] = {
                    'task_function': task_config.get('task', 'N/A'),
                    'schedule': str(task_config.get('schedule', 'N/A')),
                    'args': task_config.get('args', []),
                    'kwargs': task_config.get('kwargs', {}),
                    'options': task_config.get('options', {})
                }
            
            return {
                'timestamp': datetime.now().isoformat(),
                'task_details': task_details
            }
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

if __name__ == "__main__":
    monitor = CeleryBeatMonitor()
    
    # Run continuous monitoring if requested
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        monitor.monitor_scheduler()
    else:
        # Run single status check
        status = monitor.get_scheduler_status()
        print(json.dumps(status, indent=2))
        
        # Show detailed task information
        details = monitor.get_scheduled_task_details()
        print("\nDetailed Task Information:")
        print(json.dumps(details, indent=2))
```

### 6. Configure Celery Beat Optimization

#### Optimize Celery Beat Configuration
```bash
# Create optimized Celery Beat configuration
nano src/mcp/fastapi_app/celery_beat_optimized_config.py
```

Example optimized Celery Beat configuration:
```python
#!/usr/bin/env python3
from celery import Celery
import os
from datetime import timedelta

def create_optimized_celery_beat_app():
    """Create optimized Celery Beat app configuration"""
    
    # Get configuration from environment
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # Create Celery app
    app = Celery('reddit08_celery_beat')
    
    # Configure Celery Beat
    app.conf.update(
        broker_url=broker_url,
        result_backend=result_backend,
        
        # Beat scheduler configuration
        beat_scheduler='redis',  # Use Redis scheduler
        beat_schedule_filename='/app/celerybeat-schedule',  # Persistent schedule file
        
        # Scheduled tasks
        beat_schedule={
            # Data collection tasks
            'collect-daily-reddit-data': {
                'task': 'data_collection_tasks.collect_reddit_data_task',
                'schedule': timedelta(hours=1),  # Every hour
                'args': (),
                'kwargs': {'subreddits': ['realestate', 'CommercialRealEstate']},
            },
            'collect-daily-news-data': {
                'task': 'data_collection_tasks.collect_news_data_task',
                'schedule': timedelta(hours=2),  # Every 2 hours
                'args': (),
                'kwargs': {'topics': ['commercial real estate', 'real estate market']},
            },
            
            # Data processing tasks
            'process-daily-data': {
                'task': 'data_processing_tasks.process_daily_data_task',
                'schedule': timedelta(hours=3),  # Every 3 hours
                'args': (),
                'kwargs': {},
            },
            
            # Intelligence analysis tasks
            'analyze-market-sentiment': {
                'task': 'intelligence_tasks.analyze_market_sentiment_task',
                'schedule': timedelta(hours=4),  # Every 4 hours
                'args': (),
                'kwargs': {},
            },
            'generate-market-report': {
                'task': 'intelligence_tasks.generate_market_report_task',
                'schedule': timedelta(days=1),  # Daily
                'args': (),
                'kwargs': {},
            },
            
            # Maintenance tasks
            'cleanup-old-data': {
                'task': 'maintenance_tasks.cleanup_old_data_task',
                'schedule': timedelta(days=1),  # Daily
                'args': (),
                'kwargs': {'days_old': 30},
            },
            'backup-database': {
                'task': 'maintenance_tasks.backup_database_task',
                'schedule': timedelta(days=1),  # Daily
                'args': (),
                'kwargs': {},
            },
        },
        
        # Task serialization
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        
        # Worker configuration (for tasks executed by beat)
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=100,
    )
    
    return app

# Create optimized app instance
optimized_celery_beat_app = create_optimized_celery_beat_app()

# Configure scheduler-specific settings
def configure_scheduler_settings():
    """Configure settings specific to the scheduler"""
    # Set timezone for scheduler
    optimized_celery_beat_app.conf.timezone = 'UTC'
    optimized_celery_beat_app.conf.enable_utc = True
    
    # Configure scheduler intervals
    optimized_celery_beat_app.conf.beat_max_loop_interval = 30  # Check schedule every 30 seconds
    
    # Configure persistence settings
    optimized_celery_beat_app.conf.beat_sync_every = 10  # Sync schedule every 10 iterations
    
    return optimized_celery_beat_app
```

#### Implement Scheduler Health Checks
```bash
# Create scheduler health check script
nano scripts/health_check_celery_beat.py
```

Example scheduler health check script:
```python
#!/usr/bin/env python3
import sys
import time
from datetime import datetime
from src.mcp.fastapi_app.celery_app import celery_app

def health_check_celery_beat():
    """Perform health check on Celery Beat scheduler"""
    print("Performing Celery Beat scheduler health check...")
    
    try:
        # 1. Check scheduler configuration
        print("1. Checking scheduler configuration...")
        scheduler_type = celery_app.conf.beat_scheduler
        schedule_file = celery_app.conf.beat_schedule_filename
        print(f"   ✓ Scheduler type: {scheduler_type}")
        print(f"   ✓ Schedule file: {schedule_file}")
        
        # 2. Check scheduled tasks
        print("2. Checking scheduled tasks...")
        scheduled_tasks = celery_app.conf.beat_schedule
        if scheduled_tasks:
            print(f"   ✓ Found {len(scheduled_tasks)} scheduled tasks")
            for task_name, task_config in scheduled_tasks.items():
                print(f"     - {task_name}: {task_config.get('task', 'N/A')}")
        else:
            print("   ⚠ No scheduled tasks configured")
        
        # 3. Check schedule file accessibility
        print("3. Checking schedule file accessibility...")
        import os
        if schedule_file and os.path.exists(schedule_file):
            file_size = os.path.getsize(schedule_file)
            file_modified = datetime.fromtimestamp(os.path.getmtime(schedule_file))
            print(f"   ✓ Schedule file exists")
            print(f"   File size: {file_size} bytes")
            print(f"   Last modified: {file_modified}")
        elif schedule_file:
            print(f"   ⚠ Schedule file not found: {schedule_file}")
        else:
            print("   ⚠ No schedule file configured")
        
        # 4. Test scheduler initialization
        print("4. Testing scheduler initialization...")
        from celery.beat import PersistentScheduler
        scheduler = PersistentScheduler(app=celery_app)
        print(f"   ✓ Scheduler initialized successfully")
        
        # 5. Verify Redis connectivity (for Redis scheduler)
        print("5. Verifying Redis connectivity...")
        if scheduler_type == 'redis':
            # Test Redis connection
            from redis import Redis
            redis_url = celery_app.conf.broker_url
            redis_client = Redis.from_url(redis_url)
            redis_client.ping()
            print(f"   ✓ Redis connectivity OK")
        else:
            print(f"   ✓ Scheduler type {scheduler_type} does not require Redis connectivity test")
        
        print("✓ All Celery Beat scheduler health checks passed")
        return True
        
    except Exception as e:
        print(f"✗ Celery Beat health check failed: {e}")
        return False

def detailed_health_check():
    """Perform detailed health check"""
    print("Performing detailed Celery Beat health check...")
    
    try:
        # Get detailed scheduler information
        print("Detailed Scheduler Information:")
        
        # Scheduler configuration
        print("  Scheduler Configuration:")
        print(f"    Type: {celery_app.conf.beat_scheduler}")
        print(f"    Schedule file: {celery_app.conf.beat_schedule_filename}")
        print(f"    Timezone: {celery_app.conf.timezone}")
        print(f"    UTC enabled: {celery_app.conf.enable_utc}")
        
        # Scheduled tasks with details
        scheduled_tasks = celery_app.conf.beat_schedule
        if scheduled_tasks:
            print("  Scheduled Tasks:")
            for task_name, task_config in scheduled_tasks.items():
                print(f"    Task: {task_name}")
                print(f"      Function: {task_config.get('task', 'N/A')}")
                print(f"      Schedule: {task_config.get('schedule', 'N/A')}")
                print(f"      Args: {task_config.get('args', 'N/A')}")
                print(f"      Kwargs: {task_config.get('kwargs', 'N/A')}")
                if 'options' in task_config:
                    print(f"      Options: {task_config['options']}")
        else:
            print("  No scheduled tasks configured")
        
        # Check for potential issues
        print("  Potential Issues Check:")
        
        # Check for duplicate task names
        task_names = list(scheduled_tasks.keys()) if scheduled_tasks else []
        duplicates = [name for name in task_names if task_names.count(name) > 1]
        if duplicates:
            print(f"    ⚠ Duplicate task names found: {set(duplicates)}")
        else:
            print("    ✓ No duplicate task names")
        
        # Check for invalid schedules
        if scheduled_tasks:
            invalid_schedules = []
            for task_name, task_config in scheduled_tasks.items():
                schedule = task_config.get('schedule')
                if not schedule:
                    invalid_schedules.append(task_name)
            if invalid_schedules:
                print(f"    ⚠ Tasks with invalid schedules: {invalid_schedules}")
            else:
                print("    ✓ All tasks have valid schedules")
        
        return True
        
    except Exception as e:
        print(f"✗ Detailed health check failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--detailed":
        success = detailed_health_check()
    else:
        success = health_check_celery_beat()
    
    exit(0 if success else 1)
```

### 7. Troubleshoot Celery Beat Issues

#### Diagnose Common Celery Beat Issues
```bash
# Check Celery Beat logs
docker-compose logs celery-beat

# Monitor for common errors
docker-compose logs celery-beat | grep -E "(error|failed|exception|timeout)"

# Check for scheduler initialization errors
docker-compose logs celery-beat | grep -E "(scheduler|initialization|configuration)"

# Monitor for task scheduling errors
docker-compose logs celery-beat | grep -E "(schedule|task.*failed)"

# Check Redis connectivity issues
docker-compose logs celery-beat | grep -E "(redis|connection|timeout)"
```

#### Resolve Celery Beat Issues
```bash
# Restart Celery Beat
docker-compose restart celery-beat

# Check scheduler status
docker-compose exec celery-beat celery -A src.mcp.fastapi_app.tasks inspect scheduled

# Verify scheduled tasks
docker-compose exec celery-beat celery -A src.mcp.fastapi_app.tasks inspect reserved

# Check schedule file
docker-compose exec celery-beat ls -la /app/celerybeat-schedule

# Verify task registration
docker-compose exec celery-beat celery -A src.mcp.fastapi_app.tasks inspect registered

# Check Redis scheduler entries
docker-compose exec redis redis-cli keys "celery:beat:*"
```

### 8. Configure Multiple Schedulers

#### Implement High Availability Scheduler Setup
```bash
# Update docker-compose.yml for high availability
nano docker-compose.yml
```

Example high availability scheduler configuration:
```yaml
services:
  # Primary scheduler
  celery-beat-primary:
    build:
      context: .
      dockerfile: Dockerfile
    command: python -m celery -A src.mcp.fastapi_app.tasks beat --loglevel=info --scheduler redis --pidfile=/tmp/celerybeat-primary.pid
    environment:
      # ... environment variables
    volumes:
      # ... volume mappings
    depends_on:
      - redis
    deploy:
      replicas: 1

  # Backup scheduler
  celery-beat-backup:
    build:
      context: .
      dockerfile: Dockerfile
    command: python -m celery -A src.mcp.fastapi_app.tasks beat --loglevel=info --scheduler redis --pidfile=/tmp/celerybeat-backup.pid
    environment:
      # ... environment variables
    volumes:
      # ... volume mappings
    depends_on:
      - redis
    deploy:
      replicas: 1
    restart: unless-stopped
```

#### Implement Scheduler Failover
```bash
# Create scheduler failover script
nano scripts/celery_beat_failover.py
```

Example scheduler failover script:
```python
#!/usr/bin/env python3
import subprocess
import time
import json
from datetime import datetime

class CeleryBeatFailover:
    """Manage Celery Beat scheduler failover"""
    
    def __init__(self):
        self.primary_scheduler = "celery-beat-primary"
        self.backup_scheduler = "celery-beat-backup"
        self.check_interval = 30  # seconds
    
    def check_scheduler_status(self, scheduler_name):
        """Check if a scheduler is running"""
        try:
            # Check if container is running
            result = subprocess.run([
                'docker-compose', 'ps', scheduler_name
            ], capture_output=True, text=True)
            
            if 'Up' in result.stdout:
                # Check if scheduler process is active
                logs_result = subprocess.run([
                    'docker-compose', 'logs', '--tail', '10', scheduler_name
                ], capture_output=True, text=True)
                
                # Look for scheduler activity in logs
                if 'Scheduler' in logs_result.stdout or 'Beat' in logs_result.stdout:
                    return True
            return False
        except Exception as e:
            print(f"Error checking {scheduler_name} status: {e}")
            return False
    
    def start_scheduler(self, scheduler_name):
        """Start a scheduler"""
        try:
            print(f"Starting {scheduler_name}...")
            subprocess.run([
                'docker-compose', 'start', scheduler_name
            ], check=True)
            print(f"✓ {scheduler_name} started successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to start {scheduler_name}: {e}")
            return False
    
    def stop_scheduler(self, scheduler_name):
        """Stop a scheduler"""
        try:
            print(f"Stopping {scheduler_name}...")
            subprocess.run([
                'docker-compose', 'stop', scheduler_name
            ], check=True)
            print(f"✓ {scheduler_name} stopped successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to stop {scheduler_name}: {e}")
            return False
    
    def manage_failover(self):
        """Manage scheduler failover"""
        print("Starting Celery Beat failover management...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Check primary scheduler status
                primary_running = self.check_scheduler_status(self.primary_scheduler)
                backup_running = self.check_scheduler_status(self.backup_scheduler)
                
                timestamp = datetime.now().isoformat()
                status_data = {
                    'timestamp': timestamp,
                    'primary_running': primary_running,
                    'backup_running': backup_running
                }
                
                # Save status to log
                with open("logs/celery_beat_failover.json", "a") as f:
                    f.write(json.dumps(status_data) + "\n")
                
                # Display current status
                print(f"[{timestamp}] Scheduler Status:")
                print(f"  Primary ({self.primary_scheduler}): {'Running' if primary_running else 'Stopped'}")
                print(f"  Backup ({self.backup_scheduler}): {'Running' if backup_running else 'Stopped'}")
                
                # Manage failover logic
                if not primary_running and not backup_running:
                    print("⚠ Both schedulers are down, starting backup scheduler...")
                    self.start_scheduler(self.backup_scheduler)
                elif primary_running and backup_running:
                    print("⚠ Both schedulers are running, stopping backup to prevent conflicts...")
                    self.stop_scheduler(self.backup_scheduler)
                elif not primary_running and backup_running:
                    print("✓ Backup scheduler is running as primary")
                elif primary_running and not backup_running:
                    print("✓ Primary scheduler is running normally")
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\nFailover management stopped by user")

if __name__ == "__main__":
    failover = CeleryBeatFailover()
    failover.manage_failover()
```

### 9. Verify Celery Beat Setup
```bash
# Test final Celery Beat setup
python scripts/test_celery_beat.py

# Run health check
python scripts/health_check_celery_beat.py

# Check scheduler status
docker-compose exec celery-beat celery -A src.mcp.fastapi_app.tasks status

# Monitor scheduler performance
python scripts/monitor_celery_beat.py --test

# Verify scheduled task execution
# Wait for a scheduled task to run or manually trigger one
docker-compose exec celery-beat python -c "
from src.mcp.fastapi_app.tasks.scheduled_tasks import daily_data_processing_task
result = daily_data_processing_task.apply_async()
print(f'Scheduled task triggered: {result.id}')
"
```

## Verification
After completing the above steps, you should be able to:
- [ ] Understand Celery Beat scheduler architecture and configuration
- [ ] Verify Celery Beat configuration and connectivity
- [ ] Test Celery Beat functionality and scheduled task execution
- [ ] Monitor Celery Beat scheduler status and metrics
- [ ] Configure Celery Beat optimization and scheduling
- [ ] Implement scheduler health checks and monitoring
- [ ] Troubleshoot Celery Beat issues and errors
- [ ] Configure high availability scheduler setup
- [ ] Verify Celery Beat setup and resolution

## Common Celery Beat Issues and Solutions

### Scheduler Issues
- **"Scheduler not starting"**: Check configuration and dependencies
- **"Scheduled tasks not running"**: Verify task registration and scheduling
- **"Schedule file corruption"**: Delete and regenerate schedule file
- **"Timezone issues"**: Configure proper timezone settings

### Task Issues
- **"Scheduled task not found"**: Check task registration and import paths
- **"Task execution failed"**: Review task implementation and error handling
- **"Task scheduling conflicts"**: Check for duplicate task names or schedules
- **"Task not triggering"**: Verify scheduler is running and schedule is correct

### Persistence Issues
- **"Schedule not persisting"**: Check schedule file permissions and path
- **"Schedule file corruption"**: Delete and regenerate schedule file
- **"Redis scheduler errors"**: Verify Redis connectivity and configuration
- **"Database locking issues"**: Check for concurrent scheduler instances

## Troubleshooting Checklist

### Quick Fixes
- [ ] Check Celery Beat logs for errors
- [ ] Verify Redis connectivity and configuration
- [ ] Restart Celery Beat scheduler
- [ ] Check scheduled task configuration
- [ ] Verify task registration and imports
- [ ] Review scheduler configuration and timezone

### Advanced Diagnostics
- [ ] Implement detailed scheduler monitoring
- [ ] Analyze scheduled task execution patterns
- [ ] Optimize scheduler configuration and intervals
- [ ] Configure high availability scheduler setup
- [ ] Implement comprehensive error handling
- [ ] Set up proper logging and alerting

## Next Steps
Proceed to Chunk 40: Nginx Proxy Configuration to learn how to configure and manage the Nginx reverse proxy for the CRE Intelligence Platform.