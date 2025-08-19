# Installation Chunk 38: Celery Worker Setup

## Overview
This installation chunk covers how to configure and manage Celery workers for background task processing in the CRE Intelligence Platform, including worker configuration, task routing, and performance optimization.

## Prerequisites
- Redis installation and setup completed (Chunk 05)
- Docker service deployment completed (Chunk 10)
- Local development dependency installation completed (Chunk 11)
- Docker service management completed (Chunk 22)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Understand Celery Architecture

#### Review Celery Configuration
```bash
# Examine Celery configuration in docker-compose.yml
cat docker-compose.yml | grep -A 20 -B 5 "celery-worker"

# Expected Celery worker configuration:
# celery-worker:
#   build:
#     context: .
#     dockerfile: Dockerfile
#   command: python -m celery -A src.mcp.fastapi_app.tasks worker --loglevel=info
#   environment:
#     # ... environment variables
#   volumes:
#     # ... volume mappings
#   depends_on:
#     - postgres
#     - redis
```

#### Analyze Celery Task Implementation
```bash
# Review Celery task implementations
ls -la src/mcp/fastapi_app/tasks/
cat src/mcp/fastapi_app/tasks/__init__.py
cat src/mcp/fastapi_app/tasks/data_processing_tasks.py
cat src/mcp/fastapi_app/tasks/intelligence_tasks.py
cat src/mcp/fastapi_app/tasks/notification_tasks.py

# Check Celery configuration
cat src/mcp/fastapi_app/celery_config.py
```

### 3. Verify Celery Worker Configuration

#### Check Celery Environment Variables
```bash
# Verify Celery environment variables
cat .env | grep -E "(CELERY|REDIS|BROKER)"

# Expected environment variables:
# CELERY_BROKER_URL=redis://redis:6379/0
# CELERY_RESULT_BACKEND=redis://redis:6379/0
# CELERY_TASK_SERIALIZER=json
# CELERY_RESULT_SERIALIZER=json
# CELERY_ACCEPT_CONTENT=['json']

# For Docker deployment
cat .env.docker | grep -E "(CELERY|REDIS|BROKER)"
```

#### Test Celery Worker Connectivity
```bash
# Test Redis connectivity for Celery
docker-compose exec redis redis-cli ping

# Check Celery broker connection
docker-compose exec celery-worker python -c "
import celery
from src.mcp.fastapi_app.celery_app import celery_app
try:
    inspect = celery_app.control.inspect()
    stats = inspect.stats()
    if stats:
        print('✓ Celery broker connection successful')
        print(f'  Workers: {len(stats)}')
        for worker, worker_stats in stats.items():
            print(f'  Worker {worker}: {worker_stats.get(\"processed\", 0)} tasks processed')
    else:
        print('⚠ No workers found')
except Exception as e:
    print(f'✗ Celery broker connection failed: {e}')
"

# Verify Celery configuration
docker-compose exec celery-worker python -c "
from src.mcp.fastapi_app.celery_app import celery_app
print('Celery configuration:')
print(f'  Broker URL: {celery_app.conf.broker_url}')
print(f'  Result backend: {celery_app.conf.result_backend}')
print(f'  Task serializer: {celery_app.conf.task_serializer}')
print(f'  Result serializer: {celery_app.conf.result_serializer}')
"
```

### 4. Test Celery Worker Functionality

#### Create Celery Worker Test Script
```bash
# Create Celery worker test script
nano scripts/test_celery_worker.py
```

Example Celery worker test script:
```python
#!/usr/bin/env python3
import asyncio
import time
from datetime import datetime
from src.mcp.fastapi_app.celery_app import celery_app
from src.mcp.fastapi_app.tasks.data_processing_tasks import process_data_task
from src.mcp.fastapi_app.tasks.intelligence_tasks import analyze_market_sentiment_task

async def test_celery_worker_functionality():
    """Test Celery worker functionality"""
    print("Testing Celery worker functionality...")
    start_time = datetime.now()
    
    try:
        # 1. Test basic task execution
        print("1. Testing basic task execution...")
        result = process_data_task.delay(
            data={"test": "data", "timestamp": str(datetime.now())},
            processing_type="test"
        )
        
        # Wait for task completion
        task_result = result.get(timeout=30)
        print(f"   ✓ Basic task executed successfully")
        print(f"   Task result: {task_result}")
        
        # 2. Test market analysis task
        print("2. Testing market analysis task...")
        market_data = {
            "market": "test_market",
            "posts": [
                {"title": "Test post 1", "content": "This is a test post about real estate"},
                {"title": "Test post 2", "content": "Another test post with market information"}
            ]
        }
        
        analysis_result = analyze_market_sentiment_task.delay(market_data)
        analysis_task_result = analysis_result.get(timeout=60)
        print(f"   ✓ Market analysis task executed successfully")
        print(f"   Analysis result keys: {list(analysis_task_result.keys()) if analysis_task_result else 'None'}")
        
        # 3. Test task chaining
        print("3. Testing task chaining...")
        chain_result = (
            process_data_task.s(
                data={"chain": "test", "step": 1},
                processing_type="chain_step_1"
            ) |
            process_data_task.s(
                data={"chain": "test", "step": 2},
                processing_type="chain_step_2"
            )
        ).apply_async()
        
        chained_result = chain_result.get(timeout=30)
        print(f"   ✓ Task chaining successful")
        print(f"   Chained result: {chained_result}")
        
        # 4. Test task groups
        print("4. Testing task groups...")
        from celery import group
        
        group_tasks = group([
            process_data_task.s(
                data={"group": "test", "item": i},
                processing_type=f"group_item_{i}"
            ) for i in range(3)
        ])
        
        group_result = group_tasks.apply_async()
        group_results = group_result.get(timeout=30)
        print(f"   ✓ Task groups successful")
        print(f"   Group results count: {len(group_results)}")
        
        # 5. Test task monitoring
        print("5. Testing task monitoring...")
        inspect = celery_app.control.inspect()
        
        # Get active tasks
        active_tasks = inspect.active()
        print(f"   Active tasks: {len(active_tasks) if active_tasks else 0} workers")
        
        # Get task statistics
        stats = inspect.stats()
        if stats:
            for worker, worker_stats in stats.items():
                print(f"   Worker {worker} stats:")
                print(f"     Processed: {worker_stats.get('total', {}).get('tasks', 0)}")
                print(f"     Active: {len(active_tasks.get(worker, [])) if active_tasks else 0}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"Celery worker functionality test completed in {duration:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"✗ Celery worker test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_celery_worker_functionality())
    exit(0 if success else 1)
```

#### Test Celery Worker Performance
```bash
# Create Celery performance test script
nano scripts/test_celery_performance.py
```

Example Celery performance test script:
```python
#!/usr/bin/env python3
import time
import statistics
from datetime import datetime
from src.mcp.fastapi_app.celery_app import celery_app
from src.mcp.fastapi_app.tasks.data_processing_tasks import process_data_task

def test_celery_performance():
    """Test Celery worker performance"""
    print("Testing Celery worker performance...")
    
    # Test parameters
    num_tasks = 100
    task_data = {"test": "performance", "timestamp": str(datetime.now())}
    
    try:
        # Measure task submission time
        print(f"Submitting {num_tasks} tasks...")
        start_submit_time = time.time()
        
        task_results = []
        for i in range(num_tasks):
            result = process_data_task.delay(
                data=task_data,
                processing_type=f"performance_test_{i}"
            )
            task_results.append(result)
        
        submit_duration = time.time() - start_submit_time
        print(f"✓ Submitted {num_tasks} tasks in {submit_duration:.2f} seconds")
        print(f"  Average submission time: {submit_duration/num_tasks*1000:.2f} ms per task")
        
        # Measure task completion time
        print("Waiting for task completion...")
        start_completion_time = time.time()
        
        task_completion_times = []
        successful_tasks = 0
        
        for i, result in enumerate(task_results):
            try:
                task_start_time = time.time()
                task_result = result.get(timeout=30)
                task_duration = time.time() - task_start_time
                task_completion_times.append(task_duration)
                
                if task_result:
                    successful_tasks += 1
                    
            except Exception as e:
                print(f"  Task {i} failed: {e}")
        
        completion_duration = time.time() - start_completion_time
        print(f"✓ Completed {successful_tasks}/{num_tasks} tasks in {completion_duration:.2f} seconds")
        
        if task_completion_times:
            avg_completion_time = statistics.mean(task_completion_times)
            median_completion_time = statistics.median(task_completion_times)
            max_completion_time = max(task_completion_times)
            min_completion_time = min(task_completion_times)
            
            print(f"  Average completion time: {avg_completion_time*1000:.2f} ms")
            print(f"  Median completion time: {median_completion_time*1000:.2f} ms")
            print(f"  Min completion time: {min_completion_time*1000:.2f} ms")
            print(f"  Max completion time: {max_completion_time*1000:.2f} ms")
        
        # Test worker resource usage
        print("Testing worker resource usage...")
        inspect = celery_app.control.inspect()
        
        # Get worker stats
        stats = inspect.stats()
        if stats:
            for worker, worker_stats in stats.items():
                print(f"  Worker {worker} resource usage:")
                print(f"    Processed tasks: {worker_stats.get('total', {}).get('tasks', 0)}")
                print(f"    Active threads: {worker_stats.get('pool', {}).get('active', 0)}")
                print(f"    Max threads: {worker_stats.get('pool', {}).get('max-concurrency', 0)}")
        
        print("✓ Celery performance test completed")
        return True
        
    except Exception as e:
        print(f"✗ Celery performance test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_celery_performance()
    exit(0 if success else 1)
```

### 5. Monitor Celery Worker Status

#### Create Celery Monitoring Script
```bash
# Create Celery monitoring script
nano scripts/monitor_celery.py
```

Example Celery monitoring script:
```python
#!/usr/bin/env python3
import json
import time
from datetime import datetime
from src.mcp.fastapi_app.celery_app import celery_app

class CeleryMonitor:
    """Monitor Celery worker status and performance"""
    
    def __init__(self):
        self.app = celery_app
    
    def get_worker_status(self):
        """Get current worker status"""
        try:
            inspect = self.app.control.inspect()
            
            # Get active workers
            active_workers = inspect.active()
            worker_count = len(active_workers) if active_workers else 0
            
            # Get worker stats
            stats = inspect.stats()
            
            # Get active tasks
            active_tasks = inspect.active()
            active_task_count = sum(len(tasks) for tasks in active_tasks.values()) if active_tasks else 0
            
            # Get scheduled tasks
            scheduled_tasks = inspect.scheduled()
            scheduled_task_count = sum(len(tasks) for tasks in scheduled_tasks.values()) if scheduled_tasks else 0
            
            # Get reserved tasks
            reserved_tasks = inspect.reserved()
            reserved_task_count = sum(len(tasks) for tasks in reserved_tasks.values()) if reserved_tasks else 0
            
            return {
                'timestamp': datetime.now().isoformat(),
                'worker_count': worker_count,
                'active_task_count': active_task_count,
                'scheduled_task_count': scheduled_task_count,
                'reserved_task_count': reserved_task_count,
                'workers': stats if stats else {}
            }
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def monitor_workers(self, interval=30):
        """Monitor workers continuously"""
        print("Starting Celery worker monitoring...")
        print(f"Monitoring interval: {interval} seconds")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        try:
            while True:
                status = self.get_worker_status()
                
                # Save status to log file
                with open("logs/celery_monitoring.json", "a") as f:
                    f.write(json.dumps(status) + "\n")
                
                # Display status
                timestamp = status['timestamp']
                print(f"[{timestamp}] Celery Worker Status:")
                
                if 'error' in status:
                    print(f"  ✗ Error: {status['error']}")
                else:
                    print(f"  ✓ Workers: {status['worker_count']}")
                    print(f"  Active tasks: {status['active_task_count']}")
                    print(f"  Scheduled tasks: {status['scheduled_task_count']}")
                    print(f"  Reserved tasks: {status['reserved_task_count']}")
                    
                    # Display worker details
                    if status['workers']:
                        print("  Worker details:")
                        for worker_name, worker_stats in status['workers'].items():
                            print(f"    {worker_name}:")
                            print(f"      Processed: {worker_stats.get('total', {}).get('tasks', 0)}")
                            print(f"      Active threads: {worker_stats.get('pool', {}).get('active', 0)}")
                
                print("-" * 50)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
    
    def get_task_statistics(self):
        """Get task processing statistics"""
        try:
            inspect = self.app.control.inspect()
            stats = inspect.stats()
            
            if not stats:
                return {"error": "No workers found"}
            
            total_processed = 0
            worker_details = {}
            
            for worker, worker_stats in stats.items():
                processed = worker_stats.get('total', {}).get('tasks', 0)
                total_processed += processed
                worker_details[worker] = {
                    'processed': processed,
                    'active_threads': worker_stats.get('pool', {}).get('active', 0),
                    'max_threads': worker_stats.get('pool', {}).get('max-concurrency', 0)
                }
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_processed_tasks': total_processed,
                'workers': worker_details
            }
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

if __name__ == "__main__":
    monitor = CeleryMonitor()
    
    if len(open(__file__).readlines()) > 1:  # Simple check to avoid immediate execution
        # Run continuous monitoring if requested
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
            monitor.monitor_workers()
        else:
            # Run single status check
            status = monitor.get_worker_status()
            print(json.dumps(status, indent=2))
```

### 6. Configure Celery Worker Optimization

#### Optimize Celery Worker Configuration
```bash
# Create optimized Celery configuration
nano src/mcp/fastapi_app/celery_optimized_config.py
```

Example optimized Celery configuration:
```python
#!/usr/bin/env python3
from celery import Celery
import os

def create_optimized_celery_app():
    """Create optimized Celery app configuration"""
    
    # Get configuration from environment
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # Create Celery app
    app = Celery('reddit08_celery')
    
    # Configure Celery
    app.conf.update(
        broker_url=broker_url,
        result_backend=result_backend,
        
        # Task serialization
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        
        # Worker configuration
        worker_prefetch_multiplier=1,  # Process one task at a time
        worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
        worker_max_memory_per_child=100000,  # Restart worker after 100MB memory usage
        
        # Task routing
        task_routes={
            'data_processing_tasks.process_data_task': {'queue': 'data_processing'},
            'intelligence_tasks.analyze_market_sentiment_task': {'queue': 'intelligence'},
            'notification_tasks.send_notification_task': {'queue': 'notifications'},
        },
        
        # Queue configuration
        task_default_queue='default',
        task_default_exchange='default',
        task_default_routing_key='default',
        
        # Result configuration
        result_expires=3600,  # Results expire after 1 hour
        result_cache_max=1000,  # Cache up to 1000 results
        
        # Task time limits
        task_soft_time_limit=300,  # 5 minutes soft limit
        task_time_limit=600,  # 10 minutes hard limit
        
        # Worker concurrency
        worker_concurrency=int(os.getenv('CELERY_WORKER_CONCURRENCY', '4')),
        
        # Beat scheduler
        beat_schedule={
            'process-daily-data': {
                'task': 'data_processing_tasks.process_daily_data_task',
                'schedule': 86400.0,  # Every 24 hours
            },
            'analyze-market-sentiment': {
                'task': 'intelligence_tasks.analyze_market_sentiment_task',
                'schedule': 3600.0,  # Every hour
            },
        },
    )
    
    return app

# Create optimized app instance
optimized_celery_app = create_optimized_celery_app()

# Configure worker-specific settings
def configure_worker_settings(worker_name: str):
    """Configure settings for specific worker types"""
    worker_configs = {
        'data_processor': {
            'worker_prefetch_multiplier': 1,
            'worker_concurrency': 2,
            'task_time_limit': 900,  # 15 minutes for data processing
        },
        'intelligence_analyzer': {
            'worker_prefetch_multiplier': 1,
            'worker_concurrency': 1,  # Single thread for AI tasks
            'task_time_limit': 1800,  # 30 minutes for AI processing
        },
        'notification_sender': {
            'worker_prefetch_multiplier': 10,  # Can handle multiple notifications
            'worker_concurrency': 4,
            'task_time_limit': 300,  # 5 minutes for notifications
        }
    }
    
    config = worker_configs.get(worker_name, {})
    for key, value in config.items():
        optimized_celery_app.conf[key] = value
    
    return optimized_celery_app
```

#### Implement Worker Health Checks
```bash
# Create worker health check script
nano scripts/health_check_celery.py
```

Example worker health check script:
```python
#!/usr/bin/env python3
import sys
import time
from datetime import datetime
from src.mcp.fastapi_app.celery_app import celery_app

def health_check_celery():
    """Perform health check on Celery workers"""
    print("Performing Celery worker health check...")
    
    try:
        # Check broker connectivity
        print("1. Checking broker connectivity...")
        inspect = celery_app.control.inspect()
        
        # Ping workers
        ping_result = inspect.ping()
        if ping_result:
            print(f"   ✓ Broker connectivity OK")
            print(f"   Active workers: {len(ping_result)}")
            for worker, response in ping_result.items():
                print(f"   Worker {worker}: {response}")
        else:
            print("   ✗ No workers responding to ping")
            return False
        
        # Check active tasks
        print("2. Checking active tasks...")
        active_tasks = inspect.active()
        if active_tasks is not None:
            active_count = sum(len(tasks) for tasks in active_tasks.values())
            print(f"   ✓ Active tasks: {active_count}")
        else:
            print("   ⚠ Could not retrieve active tasks")
        
        # Check worker stats
        print("3. Checking worker stats...")
        stats = inspect.stats()
        if stats:
            print(f"   ✓ Worker stats retrieved")
            for worker, worker_stats in stats.items():
                processed = worker_stats.get('total', {}).get('tasks', 0)
                active_threads = worker_stats.get('pool', {}).get('active', 0)
                print(f"   Worker {worker}: {processed} tasks processed, {active_threads} active threads")
        else:
            print("   ⚠ Could not retrieve worker stats")
        
        # Test task execution
        print("4. Testing task execution...")
        from src.mcp.fastapi_app.tasks.data_processing_tasks import process_data_task
        
        # Send a simple test task
        test_task = process_data_task.delay(
            data={"health_check": True, "timestamp": str(datetime.now())},
            processing_type="health_check"
        )
        
        # Wait for result with timeout
        try:
            result = test_task.get(timeout=30)
            print(f"   ✓ Task execution successful")
            print(f"   Task result: {result}")
        except Exception as e:
            print(f"   ✗ Task execution failed: {e}")
            return False
        
        print("✓ All Celery worker health checks passed")
        return True
        
    except Exception as e:
        print(f"✗ Celery health check failed: {e}")
        return False

def detailed_health_check():
    """Perform detailed health check"""
    print("Performing detailed Celery health check...")
    
    try:
        inspect = celery_app.control.inspect()
        
        # Get detailed worker information
        registered_tasks = inspect.registered()
        active_tasks = inspect.active()
        scheduled_tasks = inspect.scheduled()
        reserved_tasks = inspect.reserved()
        
        print("Detailed Worker Information:")
        
        if registered_tasks:
            print("  Registered Tasks:")
            for worker, tasks in registered_tasks.items():
                print(f"    {worker}: {len(tasks)} tasks")
                for task in tasks[:5]:  # Show first 5 tasks
                    print(f"      - {task}")
                if len(tasks) > 5:
                    print(f"      ... and {len(tasks) - 5} more")
        
        if active_tasks:
            print("  Active Tasks:")
            for worker, tasks in active_tasks.items():
                print(f"    {worker}: {len(tasks)} active tasks")
                for task in tasks:
                    print(f"      - {task.get('name', 'Unknown')} (ID: {task.get('id', 'Unknown')})")
        
        if scheduled_tasks:
            print("  Scheduled Tasks:")
            for worker, tasks in scheduled_tasks.items():
                print(f"    {worker}: {len(tasks)} scheduled tasks")
        
        if reserved_tasks:
            print("  Reserved Tasks:")
            for worker, tasks in reserved_tasks.items():
                print(f"    {worker}: {len(tasks)} reserved tasks")
        
        # Check queue lengths
        print("  Queue Information:")
        try:
            from redis import Redis
            import os
            
            redis_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
            redis_client = Redis.from_url(redis_url)
            
            # Check default queue
            default_queue_length = redis_client.llen('celery')
            print(f"    Default queue length: {default_queue_length}")
            
            # Check other queues
            queues = ['data_processing', 'intelligence', 'notifications']
            for queue in queues:
                queue_length = redis_client.llen(queue)
                print(f"    {queue} queue length: {queue_length}")
                
        except Exception as e:
            print(f"    Queue length check failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Detailed health check failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--detailed":
        success = detailed_health_check()
    else:
        success = health_check_celery()
    
    exit(0 if success else 1)
```

### 7. Troubleshoot Celery Worker Issues

#### Diagnose Common Celery Issues
```bash
# Check Celery worker logs
docker-compose logs celery-worker

# Monitor for common errors
docker-compose logs celery-worker | grep -E "(error|failed|exception|timeout)"

# Check for memory issues
docker-compose logs celery-worker | grep -E "(memory|oom|killed)"

# Monitor for task failures
docker-compose logs celery-worker | grep -E "(task.*failed|traceback)"

# Check Redis connectivity issues
docker-compose logs celery-worker | grep -E "(redis|connection|timeout)"
```

#### Resolve Celery Worker Issues
```bash
# Restart Celery workers
docker-compose restart celery-worker

# Check worker status
docker-compose exec celery-worker celery -A src.mcp.fastapi_app.tasks inspect ping

# Check active tasks
docker-compose exec celery-worker celery -A src.mcp.fastapi_app.tasks inspect active

# Check worker statistics
docker-compose exec celery-worker celery -A src.mcp.fastapi_app.tasks inspect stats

# Verify task registration
docker-compose exec celery-worker celery -A src.mcp.fastapi_app.tasks inspect registered

# Check queue status
docker-compose exec redis redis-cli llen celery
docker-compose exec redis redis-cli llen data_processing
docker-compose exec redis redis-cli llen intelligence
```

### 8. Scale Celery Workers

#### Configure Multiple Worker Types
```bash
# Update docker-compose.yml for multiple worker types
nano docker-compose.yml
```

Example multiple worker configuration:
```yaml
services:
  # Data processing workers
  celery-data-processor:
    build:
      context: .
      dockerfile: Dockerfile
    command: python -m celery -A src.mcp.fastapi_app.tasks worker --loglevel=info --queues=data_processing --hostname=data_processor@%h
    environment:
      # ... environment variables
    volumes:
      # ... volume mappings
    depends_on:
      - postgres
      - redis
    deploy:
      replicas: 2  # Scale to 2 workers

  # Intelligence analysis workers
  celery-intelligence-analyzer:
    build:
      context: .
      dockerfile: Dockerfile
    command: python -m celery -A src.mcp.fastapi_app.tasks worker --loglevel=info --queues=intelligence --hostname=intelligence_analyzer@%h
    environment:
      # ... environment variables
    volumes:
      # ... volume mappings
    depends_on:
      - postgres
      - redis
    deploy:
      replicas: 1  # Single worker for AI tasks

  # Notification workers
  celery-notification-sender:
    build:
      context: .
      dockerfile: Dockerfile
    command: python -m celery -A src.mcp.fastapi_app.tasks worker --loglevel=info --queues=notifications --hostname=notification_sender@%h
    environment:
      # ... environment variables
    volumes:
      # ... volume mappings
    depends_on:
      - postgres
      - redis
    deploy:
      replicas: 3  # Scale to 3 workers for notifications
```

#### Implement Auto-scaling
```bash
# Create auto-scaling script
nano scripts/auto_scale_celery.py
```

Example auto-scaling script:
```python
#!/usr/bin/env python3
import subprocess
import time
import json
from datetime import datetime

class CeleryAutoScaler:
    """Auto-scale Celery workers based on queue load"""
    
    def __init__(self):
        self.min_workers = {
            'data_processing': 1,
            'intelligence': 1,
            'notifications': 1
        }
        self.max_workers = {
            'data_processing': 5,
            'intelligence': 3,
            'notifications': 10
        }
        self.current_workers = {
            'data_processing': 1,
            'intelligence': 1,
            'notifications': 1
        }
    
    def get_queue_lengths(self):
        """Get current queue lengths from Redis"""
        try:
            result = subprocess.run([
                'docker-compose', 'exec', 'redis', 'redis-cli', 
                'llen', 'data_processing'
            ], capture_output=True, text=True)
            data_queue_length = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
            
            result = subprocess.run([
                'docker-compose', 'exec', 'redis', 'redis-cli', 
                'llen', 'intelligence'
            ], capture_output=True, text=True)
            intelligence_queue_length = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
            
            result = subprocess.run([
                'docker-compose', 'exec', 'redis', 'redis-cli', 
                'llen', 'notifications'
            ], capture_output=True, text=True)
            notifications_queue_length = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
            
            return {
                'data_processing': data_queue_length,
                'intelligence': intelligence_queue_length,
                'notifications': notifications_queue_length
            }
        except Exception as e:
            print(f"Error getting queue lengths: {e}")
            return {
                'data_processing': 0,
                'intelligence': 0,
                'notifications': 0
            }
    
    def calculate_required_workers(self, queue_lengths):
        """Calculate required number of workers based on queue lengths"""
        required_workers = {}
        
        # Data processing: 1 worker per 10 tasks
        required_workers['data_processing'] = max(
            self.min_workers['data_processing'],
            min(
                self.max_workers['data_processing'],
                max(1, queue_lengths['data_processing'] // 10)
            )
        )
        
        # Intelligence: 1 worker per 5 tasks (AI tasks are resource intensive)
        required_workers['intelligence'] = max(
            self.min_workers['intelligence'],
            min(
                self.max_workers['intelligence'],
                max(1, queue_lengths['intelligence'] // 5)
            )
        )
        
        # Notifications: 1 worker per 50 tasks
        required_workers['notifications'] = max(
            self.min_workers['notifications'],
            min(
                self.max_workers['notifications'],
                max(1, queue_lengths['notifications'] // 50)
            )
        )
        
        return required_workers
    
    def scale_workers(self, required_workers):
        """Scale workers to required numbers"""
        for queue, required_count in required_workers.items():
            current_count = self.current_workers[queue]
            
            if required_count > current_count:
                # Scale up
                print(f"Scaling up {queue} workers from {current_count} to {required_count}")
                # In a real implementation, this would use docker-compose scale
                # For now, we'll just update our tracking
                self.current_workers[queue] = required_count
            elif required_count < current_count:
                # Scale down
                print(f"Scaling down {queue} workers from {current_count} to {required_count}")
                self.current_workers[queue] = required_count
    
    def run_auto_scaling(self, interval=60):
        """Run auto-scaling continuously"""
        print("Starting Celery auto-scaling...")
        print(f"Scaling interval: {interval} seconds")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Get current queue lengths
                queue_lengths = self.get_queue_lengths()
                
                # Calculate required workers
                required_workers = self.calculate_required_workers(queue_lengths)
                
                # Scale workers
                self.scale_workers(required_workers)
                
                # Log scaling decisions
                timestamp = datetime.now().isoformat()
                scaling_data = {
                    'timestamp': timestamp,
                    'queue_lengths': queue_lengths,
                    'required_workers': required_workers,
                    'current_workers': self.current_workers.copy()
                }
                
                with open("logs/celery_scaling.json", "a") as f:
                    f.write(json.dumps(scaling_data) + "\n")
                
                # Display current status
                print(f"[{timestamp}] Auto-scaling status:")
                for queue in queue_lengths:
                    print(f"  {queue}: {queue_lengths[queue]} tasks, "
                          f"{self.current_workers[queue]} workers")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nAuto-scaling stopped by user")

if __name__ == "__main__":
    scaler = CeleryAutoScaler()
    scaler.run_auto_scaling()
```

### 9. Verify Celery Worker Setup
```bash
# Test final Celery worker setup
python scripts/test_celery_worker.py

# Run health check
python scripts/health_check_celery.py

# Check worker status
docker-compose exec celery-worker celery -A src.mcp.fastapi_app.tasks status

# Monitor worker performance
python scripts/monitor_celery.py --test

# Verify task execution
curl -X POST http://localhost:8000/api/v1/tasks/test \
  -H "Content-Type: application/json" \
  -d '{"task_type": "data_processing", "data": {"test": "verification"}}'
```

## Verification
After completing the above steps, you should be able to:
- [ ] Understand Celery worker architecture and configuration
- [ ] Verify Celery worker configuration and connectivity
- [ ] Test Celery worker functionality and performance
- [ ] Monitor Celery worker status and metrics
- [ ] Configure Celery worker optimization and routing
- [ ] Implement worker health checks and monitoring
- [ ] Troubleshoot Celery worker issues and errors
- [ ] Scale Celery workers for different task types
- [ ] Verify Celery worker setup and resolution

## Common Celery Worker Issues and Solutions

### Connectivity Issues
- **"Connection refused"**: Check Redis connectivity and configuration
- **"Authentication failed"**: Verify Redis password and credentials
- **"Broker unavailable"**: Check Redis service status and network connectivity
- **"Timeout connecting"**: Increase connection timeout values

### Task Issues
- **"Task not found"**: Check task registration and import paths
- **"Task failed"**: Review task implementation and error handling
- **"Task timeout"**: Increase task time limits or optimize task code
- **"Memory exceeded"**: Implement memory limits and worker restarts

### Performance Issues
- **"Slow task processing"**: Optimize task code and database queries
- **"Queue buildup"**: Scale workers or optimize task processing
- **"High memory usage"**: Implement worker max memory limits
- **"Worker crashes"**: Add proper error handling and logging

## Troubleshooting Checklist

### Quick Fixes
- [ ] Check Celery worker logs for errors
- [ ] Verify Redis connectivity and configuration
- [ ] Restart Celery workers
- [ ] Check task queue lengths
- [ ] Monitor worker resource usage
- [ ] Review task implementation and dependencies

### Advanced Diagnostics
- [ ] Implement detailed worker monitoring
- [ ] Analyze task processing patterns
- [ ] Optimize worker configuration and routing
- [ ] Scale workers based on load
- [ ] Implement comprehensive error handling
- [ ] Configure proper task time limits and retries

## Next Steps
Proceed to Chunk 39: Celery Beat Setup to learn how to configure and manage scheduled tasks for the CRE Intelligence Platform.