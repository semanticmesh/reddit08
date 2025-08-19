# Installation Chunk 27: Performance Optimization

## Overview
This installation chunk covers performance optimization techniques for the CRE Intelligence Platform, including database tuning, caching strategies, and application performance improvements.

## Prerequisites
- System requirements verification completed (Chunk 01)
- Database initialization completed (Chunk 12)
- Monitoring setup completed (Chunk 25)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Database Performance Optimization

#### PostgreSQL Optimization
Edit PostgreSQL configuration for better performance:
```bash
# For Docker deployment, update docker-compose.yml
# Add to postgres service environment or command:

# Update postgres service in docker-compose.yml
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_DB: reddit08_db
    POSTGRES_USER: reddit08_user
    POSTGRES_PASSWORD: your_password
  command: >
    postgres
    -c shared_buffers=256MB
    -c effective_cache_size=1GB
    -c maintenance_work_mem=64MB
    -c checkpoint_completion_target=0.9
    -c wal_buffers=16MB
    -c default_statistics_target=100
    -c random_page_cost=1.1
    -c effective_io_concurrency=200
    -c work_mem=32MB
    -c min_wal_size=1GB
    -c max_wal_size=4GB
```

#### Create Database Indexes
```bash
# Create performance indexes
python src/scripts/create_indexes.py
```

Example index creation script:
```python
#!/usr/bin/env python3
import psycopg2
import os

def create_indexes():
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'reddit08'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'password')
    )
    cursor = conn.cursor()
    
    # Create indexes for common queries
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(platform);",
        "CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author);",
        "CREATE INDEX IF NOT EXISTS idx_posts_title_gin ON posts USING gin(to_tsvector('english', title));",
        "CREATE INDEX IF NOT EXISTS idx_keywords_term ON keywords(term);",
        "CREATE INDEX IF NOT EXISTS idx_keywords_category ON keywords(category);"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database indexes created successfully")

if __name__ == "__main__":
    create_indexes()
```

### 3. Redis Caching Optimization

#### Configure Redis for Performance
Edit `redis.conf` for better caching performance:
```conf
# Memory management
maxmemory 512mb
maxmemory-policy allkeys-lfu

# Persistence optimization
save 900 1
save 300 10
save 60 10000

# Network optimization
tcp-keepalive 300
timeout 0

# Performance tuning
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
lazyfree-lazy-server-del yes
replica-lazy-flush yes

# Active defragmentation
activedefrag yes
```

#### Implement Application-Level Caching
```python
# Edit src/mcp/fastapi_app/cache/redis_cache.py
import redis
import json
from typing import Optional, Any
import os

class RedisCache:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=os.getenv('REDIS_PORT', '6379'),
            db=0,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        try:
            serialized_value = json.dumps(value)
            return self.redis_client.setex(key, expire, serialized_value)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        try:
            return self.redis_client.delete(key) > 0
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
```

### 4. Application Performance Optimization

#### Optimize API Endpoints
```python
# Edit src/mcp/fastapi_app/api/optimized_endpoints.py
from fastapi import APIRouter, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
import asyncio

router = APIRouter()

@router.get("/api/v1/data/processed")
@cache(expire=300)  # Cache for 5 minutes
async def get_processed_data(limit: int = 100, offset: int = 0):
    # Optimized data retrieval with caching
    cached_data = await FastAPICache.get_backend().get(f"processed_data_{limit}_{offset}")
    if cached_data:
        return cached_data
    
    # Fetch data from database with optimized query
    data = await fetch_optimized_data(limit, offset)
    
    # Cache the result
    await FastAPICache.get_backend().set(f"processed_data_{limit}_{offset}", data, expire=300)
    return data

@router.get("/api/v1/intelligence/market-analysis")
@cache(expire=600)  # Cache for 10 minutes
async def get_market_analysis(location: str, timeframe: str = "monthly"):
    # Market analysis with caching
    cache_key = f"market_analysis_{location}_{timeframe}"
    cached_result = await FastAPICache.get_backend().get(cache_key)
    if cached_result:
        return cached_result
    
    # Perform analysis with optimized algorithms
    result = await perform_optimized_analysis(location, timeframe)
    
    # Cache the result
    await FastAPICache.get_backend().set(cache_key, result, expire=600)
    return result
```

#### Implement Connection Pooling
```python
# Edit src/mcp/fastapi_app/database/connection_pool.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import os

# Create connection pool for better performance
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/reddit08_db")

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Set to True for debugging
)

# Connection pool monitoring
def get_pool_status():
    return {
        "pool_size": engine.pool.size(),
        "checked_in": engine.pool.checkedin(),
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow()
    }
```

### 5. Asynchronous Processing Optimization

#### Optimize Celery Configuration
Edit Celery configuration for better performance:
```python
# Edit src/mcp/fastapi_app/celery_config.py
from celery.schedules import crontab

# Performance-optimized Celery configuration
broker_url = "redis://redis:6379/0"
result_backend = "redis://redis:6379/0"

# Worker configuration
worker_prefetch_multiplier = 1
task_acks_late = True
worker_max_tasks_per_child = 1000
worker_concurrency = 4

# Task routing for performance
task_routes = {
    'src.mcp.fastapi_app.tasks.collect_reddit_data': {'queue': 'data_collection'},
    'src.mcp.fastapi_app.tasks.process_collected_data': {'queue': 'data_processing'},
    'src.mcp.fastapi_app.tasks.generate_market_reports': {'queue': 'reporting'},
}

# Beat schedule
beat_schedule = {
    'collect-reddit-data': {
        'task': 'src.mcp.fastapi_app.tasks.collect_reddit_data',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    'process-collected-data': {
        'task': 'src.mcp.fastapi_app.tasks.process_collected_data',
        'schedule': crontab(minute=30, hour='*/6'),
    },
}
```

### 6. Memory and CPU Optimization

#### Profile Application Performance
```bash
# Install profiling tools
pip install memory-profiler line-profiler

# Run memory profiling
python -m memory_profiler src/scripts/profile_memory.py

# Run line profiling
kernprof -l -v src/scripts/profile_performance.py
```

#### Optimize Data Processing
```python
# Edit src/mcp/fastapi_app/processing/optimized_processing.py
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import asyncio

class OptimizedDataProcessor:
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
    
    async def process_batch(self, data_batch):
        # Use vectorized operations for better performance
        df = pd.DataFrame(data_batch)
        
        # Vectorized text processing
        df['processed_text'] = df['content'].str.lower().str.replace(r'[^\w\s]', '', regex=True)
        
        # Parallel processing for heavy operations
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self.heavy_processing, df['processed_text'].tolist()))
        
        return results
    
    def heavy_processing(self, text):
        # Optimized processing function
        # Implement efficient algorithms here
        return text  # Placeholder
```

### 7. Load Testing and Performance Monitoring

#### Set Up Load Testing
```bash
# Install load testing tools
pip install locust pytest-benchmark

# Create load test script
nano tests/load_test.py
```

Example load test script:
```python
# tests/load_test.py
from locust import HttpUser, task, between

class Reddit08User(HttpUser):
    wait_time = between(1, 5)
    
    @task(3)
    def get_health(self):
        self.client.get("/health")
    
    @task(2)
    def get_processed_data(self):
        self.client.get("/api/v1/data/processed?limit=50")
    
    @task(1)
    def get_market_analysis(self):
        self.client.get("/api/v1/intelligence/market-analysis?location=NYC&timeframe=monthly")
    
    def on_start(self):
        # Login or setup if needed
        pass
```

Run load tests:
```bash
# Run load test
locust -f tests/load_test.py --host http://localhost:8000
```

### 8. Implement Caching Strategies

#### Multi-Level Caching
```python
# Edit src/mcp/fastapi_app/cache/multi_level_cache.py
class MultiLevelCache:
    def __init__(self):
        self.memory_cache = {}
        self.redis_cache = RedisCache()
    
    async def get(self, key: str):
        # Check memory cache first (fastest)
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # Check Redis cache second
        redis_value = await self.redis_cache.get(key)
        if redis_value:
            # Store in memory cache for faster access next time
            self.memory_cache[key] = redis_value
            return redis_value
        
        return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        # Set in both caches
        self.memory_cache[key] = value
        await self.redis_cache.set(key, value, expire)
```

### 9. Optimize Data Storage

#### Implement Data Archiving
```bash
# Create data archiving script
nano scripts/archive_old_data.py
```

Example archiving script:
```python
#!/usr/bin/env python3
import psycopg2
import os
from datetime import datetime, timedelta

def archive_old_data():
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'reddit08'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'password')
    )
    cursor = conn.cursor()
    
    # Archive data older than 90 days
    cutoff_date = datetime.now() - timedelta(days=90)
    
    # Move old data to archive table
    archive_query = """
    INSERT INTO posts_archive 
    SELECT * FROM posts 
    WHERE created_at < %s
    """
    
    cursor.execute(archive_query, (cutoff_date,))
    archived_count = cursor.rowcount
    
    # Delete archived data from main table
    delete_query = """
    DELETE FROM posts 
    WHERE created_at < %s
    """
    
    cursor.execute(delete_query, (cutoff_date,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"Archived {archived_count} old records")

if __name__ == "__main__":
    archive_old_data()
```

### 10. Verify Performance Improvements
```bash
# Run performance benchmarks
pytest tests/performance_test.py

# Monitor system resources
docker stats

# Check database performance
docker-compose exec postgres pg_stat_statements

# Monitor Redis performance
docker-compose exec redis redis-cli info stats

# Check application response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health
```

## Verification
After completing the above steps, you should have:
- [ ] Database performance optimized with proper configuration
- [ ] Database indexes created for common queries
- [ ] Redis caching configured for better performance
- [ ] Application-level caching implemented
- [ ] API endpoints optimized with caching
- [ ] Connection pooling configured
- [ ] Celery configuration optimized
- [ ] Memory and CPU usage optimized
- [ ] Load testing framework implemented
- [ ] Multi-level caching strategies
- [ ] Data archiving implemented
- [ ] Performance improvements verified

## Troubleshooting
If performance optimization issues occur:

1. **Database performance issues**:
   - Check PostgreSQL configuration parameters
   - Verify indexes are being used
   - Review query execution plans
   - Monitor database connections

2. **Caching issues**:
   - Verify Redis connectivity
   - Check cache hit rates
   - Review cache expiration settings
   - Monitor Redis memory usage

3. **API performance issues**:
   - Profile slow endpoints
   - Check connection pooling
   - Review database queries
   - Monitor response times

4. **Memory issues**:
   - Monitor memory usage
   - Check for memory leaks
   - Review object lifecycle
   - Optimize data structures

5. **CPU usage issues**:
   - Profile CPU-intensive operations
   - Check parallel processing configuration
   - Review algorithm efficiency
   - Monitor system load

## Next Steps
Proceed to Chunk 28: Troubleshooting Common Issues to address common problems that may arise during operation.