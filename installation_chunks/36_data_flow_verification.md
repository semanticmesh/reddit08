# Installation Chunk 36: Data Flow Verification

## Overview
This installation chunk covers how to verify and optimize the data flow within the CRE Intelligence Platform, including data collection, processing, storage, and retrieval pipelines.

## Prerequisites
- Database initialization completed (Chunk 12)
- Data directory setup completed (Chunk 13)
- Data source configuration completed (Chunk 19)
- Lexicon initialization completed (Chunk 20)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Understand Data Flow Architecture

#### Review Data Flow Documentation
```bash
# Examine data flow architecture in documentation
cat DEPLOYMENT_ARCHITECTURE.md | grep -A 50 "Data Flow"

# Expected data flow:
# 1. Data Collection (Reddit, News, Twitter)
# 2. Data Processing (NLP, Sentiment Analysis)
# 3. Data Storage (PostgreSQL, Redis Cache)
# 4. Data Analysis (Market Intelligence)
# 5. Data Presentation (API Endpoints)
```

#### Analyze Data Processing Pipeline
```bash
# Review data processing components
ls -la src/mcp/fastapi_app/data_processing/
ls -la src/mcp/fastapi_app/intelligence/

# Check data models
cat src/mcp/fastapi_app/models/*.py | grep -E "class.*Model"

# Review database schema
cat scripts/init-db.sql
```

### 3. Verify Current Data Flow

#### Check Data Collection Services
```bash
# Test Reddit data collection
docker-compose exec app python src/scripts/test_reddit_collection.py

# Test News data collection
docker-compose exec app python src/scripts/test_news_collection.py

# Test Twitter data collection
docker-compose exec app python src/scripts/test_twitter_collection.py

# Check collection logs
docker-compose logs app | grep -E "(collect|fetch|retrieve)"
```

#### Verify Data Processing Pipeline
```bash
# Test data processing functions
docker-compose exec app python src/scripts/test_data_processing.py

# Check processing logs
docker-compose logs celery-worker | grep -E "(process|analyze|transform)"

# Verify NLP processing
docker-compose exec app python src/scripts/test_nlp_processing.py

# Check sentiment analysis
docker-compose exec app python src/scripts/test_sentiment_analysis.py
```

#### Validate Data Storage
```bash
# Check database tables
docker-compose exec postgres psql -U user -d reddit08_db -c "\dt"

# Verify data insertion
docker-compose exec postgres psql -U user -d reddit08_db -c "SELECT COUNT(*) FROM posts;"
docker-compose exec postgres psql -U user -d reddit08_db -c "SELECT COUNT(*) FROM keywords;"
docker-compose exec postgres psql -U user -d reddit08_db -c "SELECT COUNT(*) FROM market_analysis;"

# Check Redis cache
docker-compose exec redis redis-cli info keyspace
docker-compose exec redis redis-cli dbsize
```

### 4. Test Data Flow End-to-End

#### Execute Complete Data Flow Test
```bash
# Create end-to-end data flow test script
nano scripts/test_data_flow.py
```

Example end-to-end data flow test:
```python
#!/usr/bin/env python3
import asyncio
import psycopg2
import redis
import os
from datetime import datetime

async def test_data_flow():
    """Test complete data flow from collection to presentation"""
    
    print("Starting end-to-end data flow test...")
    start_time = datetime.now()
    
    # 1. Test data collection
    print("1. Testing data collection...")
    try:
        # Import collection modules
        from src.mcp.fastapi_app.data_collection.reddit_collector import RedditCollector
        from src.mcp.fastapi_app.data_collection.news_collector import NewsCollector
        
        # Test Reddit collection
        reddit_collector = RedditCollector()
        reddit_data = await reddit_collector.collect_subreddit_posts("realestate", limit=5)
        print(f"   Collected {len(reddit_data)} Reddit posts")
        
        # Test News collection
        news_collector = NewsCollector()
        news_data = await news_collector.collect_news("real estate", limit=5)
        print(f"   Collected {len(news_data)} news articles")
        
    except Exception as e:
        print(f"   Data collection failed: {e}")
        return False
    
    # 2. Test data processing
    print("2. Testing data processing...")
    try:
        # Import processing modules
        from src.mcp.fastapi_app.data_processing.text_processor import TextProcessor
        from src.mcp.fastapi_app.data_processing.sentiment_analyzer import SentimentAnalyzer
        
        # Process sample data
        processor = TextProcessor()
        processed_data = []
        
        for post in reddit_data[:2]:  # Process first 2 posts
            processed = processor.process_text(post.get('title', '') + ' ' + post.get('content', ''))
            processed_data.append(processed)
        
        print(f"   Processed {len(processed_data)} data items")
        
        # Analyze sentiment
        analyzer = SentimentAnalyzer()
        sentiment_results = []
        
        for processed in processed_data:
            sentiment = analyzer.analyze_sentiment(processed)
            sentiment_results.append(sentiment)
        
        print(f"   Analyzed sentiment for {len(sentiment_results)} items")
        
    except Exception as e:
        print(f"   Data processing failed: {e}")
        return False
    
    # 3. Test data storage
    print("3. Testing data storage...")
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'postgres'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'reddit08_db'),
            user=os.getenv('POSTGRES_USER', 'user'),
            password=os.getenv('POSTGRES_PASSWORD', 'password')
        )
        cursor = conn.cursor()
        
        # Insert test data
        for i, post in enumerate(reddit_data[:2]):
            cursor.execute("""
                INSERT INTO posts (platform, author, title, content, created_at, sentiment_score)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                'reddit',
                post.get('author', 'test_user'),
                post.get('title', f'Test Post {i}'),
                post.get('content', f'Test content {i}'),
                datetime.now(),
                sentiment_results[i] if i < len(sentiment_results) else 0.0
            ))
        
        conn.commit()
        print(f"   Inserted {len(reddit_data[:2])} test records")
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM posts WHERE title LIKE 'Test Post%'")
        count = cursor.fetchone()[0]
        print(f"   Verified {count} test records in database")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   Data storage failed: {e}")
        return False
    
    # 4. Test data retrieval
    print("4. Testing data retrieval...")
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'postgres'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'reddit08_db'),
            user=os.getenv('POSTGRES_USER', 'user'),
            password=os.getenv('POSTGRES_PASSWORD', 'password')
        )
        cursor = conn.cursor()
        
        # Retrieve test data
        cursor.execute("SELECT id, title, sentiment_score FROM posts WHERE title LIKE 'Test Post%' ORDER BY created_at DESC LIMIT 5")
        results = cursor.fetchall()
        
        print(f"   Retrieved {len(results)} test records")
        for row in results:
            print(f"     ID: {row[0]}, Title: {row[1]}, Sentiment: {row[2]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   Data retrieval failed: {e}")
        return False
    
    # 5. Test cache usage
    print("5. Testing cache usage...")
    try:
        # Connect to Redis
        r = redis.Redis(
            host=os.getenv('REDIS_HOST', 'redis'),
            port=os.getenv('REDIS_PORT', '6379'),
            db=0,
            decode_responses=True
        )
        
        # Test cache operations
        cache_key = f"test_data_flow_{start_time.timestamp()}"
        cache_data = {"test": "data", "timestamp": str(datetime.now())}
        
        # Set cache
        r.setex(cache_key, 300, str(cache_data))  # Cache for 5 minutes
        print("   Set data in cache")
        
        # Get cache
        cached_value = r.get(cache_key)
        if cached_value:
            print("   Retrieved data from cache")
        else:
            print("   Cache retrieval failed")
        
        # Delete cache
        r.delete(cache_key)
        print("   Deleted data from cache")
        
    except Exception as e:
        print(f"   Cache operations failed: {e}")
        return False
    
    # 6. Test API endpoints
    print("6. Testing API endpoints...")
    try:
        import requests
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("   Health endpoint OK")
        else:
            print(f"   Health endpoint failed: {response.status_code}")
        
        # Test data endpoint
        response = requests.get("http://localhost:8000/api/v1/data/processed?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   Data endpoint returned {len(data)} items")
        else:
            print(f"   Data endpoint failed: {response.status_code}")
        
    except Exception as e:
        print(f"   API endpoint testing failed: {e}")
        return False
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"End-to-end data flow test completed in {duration:.2f} seconds")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_data_flow())
    if success:
        print("✓ All data flow tests passed")
    else:
        print("✗ Data flow tests failed")
```

### 5. Monitor Data Flow Performance

#### Create Data Flow Monitoring Script
```bash
# Create data flow monitoring script
nano scripts/monitor_data_flow.py
```

Example data flow monitoring script:
```python
#!/usr/bin/env python3
import psycopg2
import redis
import json
import time
from datetime import datetime
import os

def monitor_database_metrics():
    """Monitor database performance metrics"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'postgres'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'reddit08_db'),
            user=os.getenv('POSTGRES_USER', 'user'),
            password=os.getenv('POSTGRES_PASSWORD', 'password')
        )
        cursor = conn.cursor()
        
        # Get table row counts
        tables = ['posts', 'keywords', 'market_analysis']
        row_counts = {}
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                row_counts[table] = count
            except:
                row_counts[table] = "Error"
        
        # Get database size
        cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
        db_size = cursor.fetchone()[0]
        
        # Get active connections
        cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
        active_connections = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            "row_counts": row_counts,
            "database_size": db_size,
            "active_connections": active_connections
        }
    except Exception as e:
        return {"error": str(e)}

def monitor_cache_metrics():
    """Monitor Redis cache metrics"""
    try:
        r = redis.Redis(
            host=os.getenv('REDIS_HOST', 'redis'),
            port=os.getenv('REDIS_PORT', '6379'),
            db=0,
            decode_responses=True
        )
        
        info = r.info()
        
        return {
            "used_memory": info.get('used_memory_human', 'N/A'),
            "connected_clients": info.get('connected_clients', 'N/A'),
            "total_commands_processed": info.get('total_commands_processed', 'N/A'),
            "keyspace_hits": info.get('keyspace_hits', 'N/A'),
            "keyspace_misses": info.get('keyspace_misses', 'N/A')
        }
    except Exception as e:
        return {"error": str(e)}

def monitor_data_flow_performance():
    """Monitor data flow performance continuously"""
    print("Starting data flow performance monitoring...")
    
    while True:
        timestamp = datetime.now().isoformat()
        
        # Monitor database metrics
        db_metrics = monitor_database_metrics()
        
        # Monitor cache metrics
        cache_metrics = monitor_cache_metrics()
        
        # Save monitoring data
        monitoring_data = {
            "timestamp": timestamp,
            "database_metrics": db_metrics,
            "cache_metrics": cache_metrics
        }
        
        with open("logs/data_flow_monitoring.json", "a") as f:
            f.write(json.dumps(monitoring_data) + "\n")
        
        # Display summary
        print(f"[{timestamp}] Data flow monitoring completed")
        print(f"  Database: {db_metrics.get('row_counts', {})}")
        print(f"  Cache: {cache_metrics.get('used_memory', 'N/A')} used")
        
        # Wait before next check
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    monitor_data_flow_performance()
```

### 6. Troubleshoot Data Flow Issues

#### Diagnose Data Flow Problems
```bash
# Check for data flow errors in logs
docker-compose logs --since="1h" | grep -E "(error|failed|exception)" | grep -E "(data|process|collect|store)"

# Monitor data processing workers
docker-compose logs celery-worker | grep -E "(task|process|error)"

# Check database connection errors
docker-compose logs app | grep -E "(database|postgres)" | grep -E "(error|failed)"

# Monitor cache errors
docker-compose logs app | grep -E "(redis|cache)" | grep -E "(error|failed)"
```

#### Resolve Data Flow Issues
```bash
# Restart data processing workers
docker-compose restart celery-worker
docker-compose restart celery-beat

# Check database connectivity
docker-compose exec app python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'postgres'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'reddit08_db'),
        user=os.getenv('POSTGRES_USER', 'user'),
        password=os.getenv('POSTGRES_PASSWORD', 'password')
    )
    print('Database connection successful')
    conn.close()
except Exception as e:
    print(f'Database connection failed: {e}')
"

# Check Redis connectivity
docker-compose exec app python -c "
import redis
import os
try:
    r = redis.Redis(
        host=os.getenv('REDIS_HOST', 'redis'),
        port=os.getenv('REDIS_PORT', '6379'),
        db=0
    )
    r.ping()
    print('Redis connection successful')
except Exception as e:
    print(f'Redis connection failed: {e}')
"

# Verify data processing modules
docker-compose exec app python -c "
from src.mcp.fastapi_app.data_processing.text_processor import TextProcessor
from src.mcp.fastapi_app.data_processing.sentiment_analyzer import SentimentAnalyzer
print('Data processing modules loaded successfully')
"
```

### 7. Optimize Data Flow Performance

#### Implement Data Flow Optimization
```bash
# Optimize database queries
# Edit src/mcp/fastapi_app/database/optimized_queries.py

import asyncio
from typing import List, Dict
import psycopg2.extras

class OptimizedDataFlow:
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def batch_insert_posts(self, posts: List[Dict]) -> int:
        """Batch insert posts for better performance"""
        if not posts:
            return 0
        
        cursor = self.db.cursor()
        
        # Prepare batch insert query
        insert_query = """
            INSERT INTO posts (platform, author, title, content, created_at, sentiment_score)
            VALUES %s
            ON CONFLICT (platform, created_at, author) DO NOTHING
        """
        
        # Prepare data tuples
        data_tuples = [
            (
                post['platform'],
                post['author'],
                post['title'],
                post['content'],
                post['created_at'],
                post.get('sentiment_score', 0.0)
            )
            for post in posts
        ]
        
        # Execute batch insert
        psycopg2.extras.execute_values(
            cursor, insert_query, data_tuples, template=None, page_size=100
        )
        
        inserted_count = cursor.rowcount
        self.db.commit()
        cursor.close()
        
        return inserted_count
    
    async def batch_process_and_store(self, raw_data: List[Dict]) -> Dict:
        """Batch process and store data efficiently"""
        # Process data in parallel
        processed_data = await asyncio.gather(*[
            self.process_single_item(item) for item in raw_data
        ])
        
        # Batch store processed data
        stored_count = await self.batch_insert_posts(processed_data)
        
        return {
            "processed_count": len(processed_data),
            "stored_count": stored_count
        }
    
    async def process_single_item(self, item: Dict) -> Dict:
        """Process a single data item"""
        # Implement efficient processing logic
        # This is a simplified example
        return {
            "platform": item.get("platform", "unknown"),
            "author": item.get("author", "unknown"),
            "title": item.get("title", ""),
            "content": item.get("content", ""),
            "created_at": item.get("created_at"),
            "sentiment_score": self.calculate_sentiment(item.get("content", ""))
        }
    
    def calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score (simplified)"""
        # Implement efficient sentiment calculation
        positive_words = ["good", "great", "excellent", "positive"]
        negative_words = ["bad", "terrible", "awful", "negative"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        return (positive_count - negative_count) / max(len(text.split()), 1)
```

#### Configure Data Flow Caching
```bash
# Implement intelligent caching strategy
# Edit src/mcp/fastapi_app/cache/data_flow_cache.py

import redis
import json
import hashlib
from typing import Optional, Any
import os

class DataFlowCache:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'redis'),
            port=os.getenv('REDIS_PORT', '6379'),
            db=1,  # Use different database for data flow cache
            decode_responses=True
        )
    
    def get_cache_key(self, data_type: str, parameters: dict) -> str:
        """Generate consistent cache key"""
        key_data = f"{data_type}:{json.dumps(parameters, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_processed_data(self, data_type: str, parameters: dict) -> Optional[Any]:
        """Get processed data from cache"""
        cache_key = self.get_cache_key(data_type, parameters)
        cached_data = self.redis_client.get(cache_key)
        
        if cached_data:
            try:
                return json.loads(cached_data)
            except:
                return None
        return None
    
    def set_processed_data(self, data_type: str, parameters: dict, data: Any, expire: int = 3600) -> bool:
        """Store processed data in cache"""
        cache_key = self.get_cache_key(data_type, parameters)
        try:
            serialized_data = json.dumps(data)
            return self.redis_client.setex(cache_key, expire, serialized_data)
        except:
            return False
```

### 8. Verify Data Flow Resolution
```bash
# Test final data flow implementation
python scripts/test_data_flow.py

# Run data flow monitoring
python scripts/monitor_data_flow.py --test

# Check data flow performance
docker-compose exec app python -c "
from src.mcp.fastapi_app.database.optimized_queries import OptimizedDataFlow
print('Optimized data flow modules loaded successfully')
"

# Verify cache implementation
docker-compose exec app python -c "
from src.mcp.fastapi_app.cache.data_flow_cache import DataFlowCache
cache = DataFlowCache()
test_data = {'test': 'data'}
cache.set_processed_data('test', {'param': 'value'}, test_data)
retrieved = cache.get_processed_data('test', {'param': 'value'})
print('Cache implementation working:', retrieved == test_data)
"

# Run end-to-end data flow test
curl -X POST http://localhost:8000/api/v1/data/flow/test \
  -H "Content-Type: application/json" \
  -d '{"test_size": 10}'
```

## Verification
After completing the above steps, you should be able to:
- [ ] Understand data flow architecture and components
- [ ] Verify current data flow implementation
- [ ] Test data flow end-to-end
- [ ] Monitor data flow performance and metrics
- [ ] Troubleshoot data flow issues and problems
- [ ] Optimize data flow performance and efficiency
- [ ] Implement data flow caching strategies
- [ ] Verify data flow resolution

## Common Data Flow Issues and Solutions

### Collection Issues
- **"Data collection failed"**: Check API keys and network connectivity
- **"Rate limit exceeded"**: Implement proper rate limiting
- **"Invalid data format"**: Verify data parsing and validation
- **"Source unavailable"**: Check external service status

### Processing Issues
- **"Processing timeout"**: Optimize processing algorithms
- **"Memory overflow"**: Implement batch processing
- **"Invalid data"**: Add data validation and error handling
- **"Processing queue full"**: Scale processing workers

### Storage Issues
- **"Database connection failed"**: Check database connectivity
- **"Insert failed"**: Verify database schema and constraints
- **"Storage full"**: Monitor disk space and implement cleanup
- **"Slow queries"**: Optimize database indexes and queries

### Retrieval Issues
- **"Cache miss"**: Optimize cache strategy and size
- **"Slow response"**: Implement pagination and caching
- **"Data inconsistency"**: Ensure data integrity and transactions
- **"API errors"**: Check API implementation and error handling

## Troubleshooting Checklist

### Quick Fixes
- [ ] Check data flow logs for errors
- [ ] Verify database connectivity
- [ ] Test Redis cache operations
- [ ] Restart data processing workers
- [ ] Check API key validity
- [ ] Monitor system resources

### Advanced Diagnostics
- [ ] Analyze data flow performance metrics
- [ ] Implement detailed logging
- [ ] Test individual data flow components
- [ ] Monitor database query performance
- [ ] Optimize data processing algorithms
- [ ] Scale data processing infrastructure

## Next Steps
Proceed to Chunk 37: External API Integration Testing to learn how to test and verify external API integrations for the CRE Intelligence Platform.