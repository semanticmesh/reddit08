# Installation Chunk 37: External API Integration Testing

## Overview
This installation chunk covers how to test and verify external API integrations for the CRE Intelligence Platform, including Reddit API, News API, Twitter API, and OpenAI API.

## Prerequisites
- API key configuration completed (Chunk 14)
- API key troubleshooting completed (Chunk 32)
- Data source configuration completed (Chunk 19)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Understand External API Integrations

#### Review API Integration Documentation
```bash
# Examine API integration documentation
cat INSTALLATION_GUIDE.md | grep -A 50 "API Keys Required"

# Expected API integrations:
# 1. OpenAI API - For AI-powered intelligence analysis
# 2. Reddit API - For accessing Reddit data
# 3. News API - For news data integration
# 4. Twitter API - For Twitter data integration
```

#### Analyze API Client Implementation
```bash
# Review API client implementations
ls -la src/mcp/fastapi_app/clients/
cat src/mcp/fastapi_app/clients/openai_client.py
cat src/mcp/fastapi_app/clients/reddit_client.py
cat src/mcp/fastapi_app/clients/news_client.py
cat src/mcp/fastapi_app/clients/twitter_client.py

# Check API configuration
cat src/mcp/fastapi_app/config/api_config.py
```

### 3. Verify API Key Configuration

#### Check API Keys
```bash
# Verify all required API keys are configured
cat .env | grep -E "(OPENAI|REDDIT|NEWS|TWITTER)"

# Expected environment variables:
# OPENAI_API_KEY=sk-...
# REDDIT_CLIENT_ID=...
# REDDIT_CLIENT_SECRET=...
# NEWS_API_KEY=...
# TWITTER_BEARER_TOKEN=...

# For Docker deployment
cat .env.docker | grep -E "(OPENAI|REDDIT|NEWS|TWITTER)"
```

#### Test API Key Validity
```bash
# Test OpenAI API key
OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d'=' -f2)
if [ -n "$OPENAI_API_KEY" ]; then
    curl -s -X GET "https://api.openai.com/v1/models" \
      -H "Authorization: Bearer $OPENAI_API_KEY" \
      -H "Content-Type: application/json" | grep -q "data" && echo "✓ OpenAI API key valid" || echo "✗ OpenAI API key invalid"
else
    echo "⚠ OpenAI API key not configured"
fi

# Test Reddit API credentials
REDDIT_CLIENT_ID=$(grep REDDIT_CLIENT_ID .env | cut -d'=' -f2)
REDDIT_CLIENT_SECRET=$(grep REDDIT_CLIENT_SECRET .env | cut -d'=' -f2)
if [ -n "$REDDIT_CLIENT_ID" ] && [ -n "$REDDIT_CLIENT_SECRET" ]; then
    curl -s -X POST "https://www.reddit.com/api/v1/access_token" \
      -H "User-Agent: CRE Intelligence Platform" \
      -u "$REDDIT_CLIENT_ID:$REDDIT_CLIENT_SECRET" \
      -d "grant_type=client_credentials" | grep -q "access_token" && echo "✓ Reddit API credentials valid" || echo "✗ Reddit API credentials invalid"
else
    echo "⚠ Reddit API credentials not configured"
fi

# Test News API key
NEWS_API_KEY=$(grep NEWS_API_KEY .env | cut -d'=' -f2)
if [ -n "$NEWS_API_KEY" ]; then
    curl -s "https://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=$NEWS_API_KEY" \
      | grep -q "articles" && echo "✓ News API key valid" || echo "✗ News API key invalid"
else
    echo "⚠ News API key not configured"
fi

# Test Twitter API key
TWITTER_BEARER_TOKEN=$(grep TWITTER_BEARER_TOKEN .env | cut -d'=' -f2)
if [ -n "$TWITTER_BEARER_TOKEN" ]; then
    curl -s "https://api.twitter.com/2/tweets/search/recent?query=real estate" \
      -H "Authorization: Bearer $TWITTER_BEARER_TOKEN" \
      | grep -q "data" && echo "✓ Twitter API key valid" || echo "✗ Twitter API key invalid"
else
    echo "⚠ Twitter API key not configured"
fi
```

### 4. Test Individual API Integrations

#### Test OpenAI API Integration
```bash
# Create OpenAI API test script
nano scripts/test_openai_api.py
```

Example OpenAI API test script:
```python
#!/usr/bin/env python3
import os
import openai
from dotenv import load_dotenv
import asyncio

async def test_openai_integration():
    """Test OpenAI API integration"""
    print("Testing OpenAI API integration...")
    
    # Load environment variables
    load_dotenv()
    
    # Configure OpenAI client
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai.api_key:
        print("✗ OpenAI API key not configured")
        return False
    
    try:
        # Test API connectivity
        print("1. Testing API connectivity...")
        models = openai.Model.list()
        print(f"   ✓ API connected successfully")
        print(f"   Available models: {len(models['data'])}")
        
        # Test chat completion
        print("2. Testing chat completion...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is commercial real estate?"}
            ],
            max_tokens=100
        )
        
        answer = response['choices'][0]['message']['content']
        print(f"   ✓ Chat completion successful")
        print(f"   Response: {answer[:50]}...")
        
        # Test embedding generation
        print("3. Testing embedding generation...")
        embedding_response = openai.Embedding.create(
            input="Commercial real estate market analysis",
            model="text-embedding-ada-002"
        )
        
        embedding = embedding_response['data'][0]['embedding']
        print(f"   ✓ Embedding generation successful")
        print(f"   Embedding dimensions: {len(embedding)}")
        
        print("✓ All OpenAI API tests passed")
        return True
        
    except openai.error.AuthenticationError as e:
        print(f"✗ Authentication error: {e}")
        return False
    except openai.error.RateLimitError as e:
        print(f"⚠ Rate limit exceeded: {e}")
        return True  # This is expected in some cases
    except openai.error.APIError as e:
        print(f"✗ API error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_openai_integration())
    exit(0 if success else 1)
```

#### Test Reddit API Integration
```bash
# Create Reddit API test script
nano scripts/test_reddit_api.py
```

Example Reddit API test script:
```python
#!/usr/bin/env python3
import os
import praw
from dotenv import load_dotenv
import asyncio

async def test_reddit_integration():
    """Test Reddit API integration"""
    print("Testing Reddit API integration...")
    
    # Load environment variables
    load_dotenv()
    
    # Configure Reddit client
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent="CRE Intelligence Platform"
    )
    
    if not reddit.read_only:
        print("✗ Reddit credentials not configured")
        return False
    
    try:
        # Test API connectivity
        print("1. Testing API connectivity...")
        reddit.user.me()
        print("   ✓ API connected successfully")
        
        # Test subreddit access
        print("2. Testing subreddit access...")
        subreddit = reddit.subreddit('realestate')
        posts = list(subreddit.hot(limit=5))
        print(f"   ✓ Subreddit access successful")
        print(f"   Retrieved {len(posts)} posts")
        
        # Test post details
        print("3. Testing post details...")
        if posts:
            post = posts[0]
            print(f"   Post title: {post.title[:50]}...")
            print(f"   Post author: {post.author}")
            print(f"   Post score: {post.score}")
        
        # Test search functionality
        print("4. Testing search functionality...")
        search_results = list(reddit.subreddit('all').search('commercial real estate', limit=3))
        print(f"   ✓ Search successful")
        print(f"   Found {len(search_results)} search results")
        
        print("✓ All Reddit API tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Reddit API error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_reddit_integration())
    exit(0 if success else 1)
```

#### Test News API Integration
```bash
# Create News API test script
nano scripts/test_news_api.py
```

Example News API test script:
```python
#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv
import json

def test_news_integration():
    """Test News API integration"""
    print("Testing News API integration...")
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('NEWS_API_KEY')
    
    if not api_key:
        print("✗ News API key not configured")
        return False
    
    try:
        # Test API connectivity
        print("1. Testing API connectivity...")
        response = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={
                'sources': 'techcrunch',
                'apiKey': api_key
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ API connected successfully")
            print(f"   Retrieved {data.get('totalResults', 0)} articles")
        else:
            print(f"   ✗ API connection failed: {response.status_code}")
            return False
        
        # Test search functionality
        print("2. Testing search functionality...")
        search_response = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                'q': 'commercial real estate',
                'sortBy': 'publishedAt',
                'apiKey': api_key
            },
            timeout=30
        )
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            print(f"   ✓ Search successful")
            print(f"   Found {search_data.get('totalResults', 0)} articles")
            
            # Display sample article
            if search_data.get('articles'):
                article = search_data['articles'][0]
                print(f"   Sample article: {article.get('title', '')[:50]}...")
        else:
            print(f"   ✗ Search failed: {search_response.status_code}")
            return False
        
        # Test sources endpoint
        print("3. Testing sources endpoint...")
        sources_response = requests.get(
            "https://newsapi.org/v2/sources",
            params={'apiKey': api_key},
            timeout=30
        )
        
        if sources_response.status_code == 200:
            sources_data = sources_response.json()
            print(f"   ✓ Sources endpoint successful")
            print(f"   Available sources: {len(sources_data.get('sources', []))}")
        else:
            print(f"   ✗ Sources endpoint failed: {sources_response.status_code}")
            return False
        
        print("✓ All News API tests passed")
        return True
        
    except requests.exceptions.Timeout:
        print("✗ Request timeout")
        return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Request error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_news_integration()
    exit(0 if success else 1)
```

#### Test Twitter API Integration
```bash
# Create Twitter API test script
nano scripts/test_twitter_api.py
```

Example Twitter API test script:
```python
#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv
import json

def test_twitter_integration():
    """Test Twitter API integration"""
    print("Testing Twitter API integration...")
    
    # Load environment variables
    load_dotenv()
    
    # Get Bearer Token
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    
    if not bearer_token:
        print("✗ Twitter Bearer Token not configured")
        return False
    
    headers = {"Authorization": f"Bearer {bearer_token}"}
    
    try:
        # Test API connectivity
        print("1. Testing API connectivity...")
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/recent",
            headers=headers,
            params={
                'query': 'real estate -is:retweet',
                'max_results': 10
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ API connected successfully")
            print(f"   Retrieved {len(data.get('data', []))} tweets")
            
            # Display sample tweet
            if data.get('data'):
                tweet = data['data'][0]
                print(f"   Sample tweet: {tweet.get('text', '')[:50]}...")
        elif response.status_code == 401:
            print("   ✗ Authentication failed - check Bearer Token")
            return False
        elif response.status_code == 429:
            print("   ⚠ Rate limit exceeded")
            return True
        else:
            print(f"   ✗ API connection failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Test user lookup
        print("2. Testing user lookup...")
        user_response = requests.get(
            "https://api.twitter.com/2/users/by/username/Twitter",
            headers=headers,
            timeout=30
        )
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"   ✓ User lookup successful")
            print(f"   User ID: {user_data.get('data', {}).get('id', 'N/A')}")
        else:
            print(f"   ⚠ User lookup failed: {user_response.status_code}")
        
        # Test rate limit headers
        print("3. Testing rate limit information...")
        if 'x-rate-limit-remaining' in response.headers:
            remaining = response.headers['x-rate-limit-remaining']
            reset_time = response.headers.get('x-rate-limit-reset', 'N/A')
            print(f"   ✓ Rate limit info available")
            print(f"   Requests remaining: {remaining}")
            print(f"   Reset time: {reset_time}")
        else:
            print("   ⚠ Rate limit headers not available")
        
        print("✓ Twitter API tests completed")
        return True
        
    except requests.exceptions.Timeout:
        print("✗ Request timeout")
        return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Request error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_twitter_integration()
    exit(0 if success else 1)
```

### 5. Run Comprehensive API Integration Tests

#### Execute All API Tests
```bash
# Make test scripts executable
chmod +x scripts/test_openai_api.py
chmod +x scripts/test_reddit_api.py
chmod +x scripts/test_news_api.py
chmod +x scripts/test_twitter_api.py

# Run all API integration tests
echo "Running OpenAI API tests..."
python scripts/test_openai_api.py

echo "Running Reddit API tests..."
python scripts/test_reddit_api.py

echo "Running News API tests..."
python scripts/test_news_api.py

echo "Running Twitter API tests..."
python scripts/test_twitter_api.py
```

#### Create Comprehensive API Test Suite
```bash
# Create comprehensive API test suite
nano scripts/test_all_apis.py
```

Example comprehensive API test suite:
```python
#!/usr/bin/env python3
import asyncio
import sys
from typing import List, Tuple

async def run_api_test(test_name: str, test_function) -> Tuple[str, bool, str]:
    """Run a single API test and return results"""
    try:
        print(f"Running {test_name}...")
        result = await test_function() if asyncio.iscoroutinefunction(test_function) else test_function()
        status = "✓" if result else "✗"
        return test_name, result, status
    except Exception as e:
        return test_name, False, f"✗ Error: {str(e)}"

async def test_openai_integration():
    """Test OpenAI API integration"""
    # Import and run OpenAI test
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_openai", "scripts/test_openai_api.py")
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        return await test_module.test_openai_integration()
    except Exception as e:
        print(f"OpenAI test error: {e}")
        return False

async def test_reddit_integration():
    """Test Reddit API integration"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_reddit", "scripts/test_reddit_api.py")
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        return await test_module.test_reddit_integration()
    except Exception as e:
        print(f"Reddit test error: {e}")
        return False

def test_news_integration():
    """Test News API integration"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_news", "scripts/test_news_api.py")
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        return test_module.test_news_integration()
    except Exception as e:
        print(f"News test error: {e}")
        return False

def test_twitter_integration():
    """Test Twitter API integration"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_twitter", "scripts/test_twitter_api.py")
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        return test_module.test_twitter_integration()
    except Exception as e:
        print(f"Twitter test error: {e}")
        return False

async def run_comprehensive_api_tests():
    """Run all API integration tests"""
    print("Running comprehensive API integration tests...")
    print("=" * 50)
    
    # Define tests
    tests = [
        ("OpenAI API Integration", test_openai_integration),
        ("Reddit API Integration", test_reddit_integration),
        ("News API Integration", test_news_integration),
        ("Twitter API Integration", test_twitter_integration)
    ]
    
    # Run tests concurrently
    results = await asyncio.gather(
        *[run_api_test(name, func) for name, func in tests],
        return_exceptions=True
    )
    
    # Process results
    print("\n" + "=" * 50)
    print("API Integration Test Results:")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            test_name = tests[i][0]
            print(f"{test_name}: ✗ Exception: {result}")
        else:
            test_name, success, status = result
            print(f"{test_name}: {status}")
            if success:
                passed += 1
    
    print("=" * 50)
    print(f"Summary: {passed}/{total} API tests passed")
    
    if passed == total:
        print("✓ All API integration tests passed!")
        return True
    else:
        print("✗ Some API integration tests failed!")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_api_tests())
    exit(0 if success else 1)
```

### 6. Monitor API Usage and Performance

#### Create API Monitoring Script
```bash
# Create API monitoring script
nano scripts/monitor_api_usage.py
```

Example API monitoring script:
```python
#!/usr/bin/env python3
import os
import json
import time
from datetime import datetime
from typing import Dict, Any
import requests

class APIMonitor:
    def __init__(self):
        self.api_configs = {
            'openai': {
                'name': 'OpenAI API',
                'key_env': 'OPENAI_API_KEY',
                'base_url': 'https://api.openai.com',
                'endpoint': '/v1/models'
            },
            'reddit': {
                'name': 'Reddit API',
                'key_env': 'REDDIT_CLIENT_ID',
                'base_url': 'https://oauth.reddit.com',
                'endpoint': '/api/v1/me'
            },
            'news': {
                'name': 'News API',
                'key_env': 'NEWS_API_KEY',
                'base_url': 'https://newsapi.org',
                'endpoint': '/v1/sources'
            },
            'twitter': {
                'name': 'Twitter API',
                'key_env': 'TWITTER_BEARER_TOKEN',
                'base_url': 'https://api.twitter.com',
                'endpoint': '/2/users/me'
            }
        }
    
    def check_api_status(self, api_name: str) -> Dict[str, Any]:
        """Check the status of a specific API"""
        config = self.api_configs[api_name]
        api_key = os.getenv(config['key_env'])
        
        if not api_key:
            return {
                'api': config['name'],
                'status': 'not_configured',
                'message': 'API key not configured'
            }
        
        try:
            headers = {}
            params = {}
            
            # Set appropriate headers and parameters
            if api_name == 'openai':
                headers['Authorization'] = f"Bearer {api_key}"
            elif api_name == 'reddit':
                # Reddit requires OAuth, so we'll just check if key exists
                return {
                    'api': config['name'],
                    'status': 'configured',
                    'message': 'API key configured (OAuth required for full test)'
                }
            elif api_name == 'news':
                params['apiKey'] = api_key
            elif api_name == 'twitter':
                headers['Authorization'] = f"Bearer {api_key}"
            
            # Make test request
            url = f"{config['base_url']}{config['endpoint']}"
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            return {
                'api': config['name'],
                'status': 'available' if response.status_code == 200 else 'unavailable',
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'message': 'API is accessible' if response.status_code == 200 else f'API returned {response.status_code}'
            }
            
        except requests.exceptions.Timeout:
            return {
                'api': config['name'],
                'status': 'timeout',
                'message': 'Request timed out'
            }
        except requests.exceptions.RequestException as e:
            return {
                'api': config['name'],
                'status': 'error',
                'message': f'Request error: {str(e)}'
            }
        except Exception as e:
            return {
                'api': config['name'],
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }
    
    def monitor_all_apis(self) -> Dict[str, Any]:
        """Monitor all configured APIs"""
        timestamp = datetime.now().isoformat()
        results = {}
        
        for api_name in self.api_configs:
            results[api_name] = self.check_api_status(api_name)
        
        return {
            'timestamp': timestamp,
            'results': results
        }
    
    def run_continuous_monitoring(self, interval: int = 300):
        """Run continuous API monitoring"""
        print("Starting continuous API monitoring...")
        print(f"Monitoring interval: {interval} seconds")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        try:
            while True:
                timestamp = datetime.now().isoformat()
                results = self.monitor_all_apis()
                
                # Save results
                with open("logs/api_monitoring.json", "a") as f:
                    f.write(json.dumps(results) + "\n")
                
                # Display summary
                print(f"[{timestamp}] API Monitoring Results:")
                for api_name, result in results['results'].items():
                    status_icon = "✓" if result['status'] == 'available' else "✗" if result['status'] == 'unavailable' else "⚠"
                    print(f"  {status_icon} {result['api']}: {result['status']}")
                    if 'response_time' in result:
                        print(f"    Response time: {result['response_time']:.2f}s")
                
                print("-" * 50)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")

if __name__ == "__main__":
    monitor = APIMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        monitor.run_continuous_monitoring()
    else:
        results = monitor.monitor_all_apis()
        print(json.dumps(results, indent=2))
```

### 7. Troubleshoot API Integration Issues

#### Diagnose Common API Issues
```bash
# Check for API errors in logs
docker-compose logs --since="1h" | grep -E "(API|error|failed)" | grep -E "(openai|reddit|news|twitter)"

# Monitor rate limit errors
docker-compose logs app | grep -E "(rate.*limit|429)"

# Check authentication errors
docker-compose logs app | grep -E "(401|403|unauthorized)"

# Monitor timeout errors
docker-compose logs app | grep -E "(timeout|deadline)"
```

#### Resolve API Integration Issues
```bash
# Test API connectivity from container
docker-compose exec app python -c "
import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    response = requests.get('https://api.openai.com/v1/models', 
                          headers={'Authorization': f'Bearer {api_key}'})
    print(f'OpenAI API status: {response.status_code}')
else:
    print('OpenAI API key not configured')
"

# Check API rate limits
docker-compose exec app python -c "
import requests
api_key = '$OPENAI_API_KEY'
if api_key:
    response = requests.get('https://api.openai.com/v1/models', 
                          headers={'Authorization': f'Bearer {api_key}'})
    print('Rate limit headers:')
    for header in ['x-ratelimit-limit', 'x-ratelimit-remaining', 'x-ratelimit-reset']:
        if header in response.headers:
            print(f'  {header}: {response.headers[header]}')
"

# Verify API client configuration
docker-compose exec app python -c "
from src.mcp.fastapi_app.clients.openai_client import OpenAIClient
from src.mcp.fastapi_app.clients.reddit_client import RedditClient
print('API clients loaded successfully')
"
```

### 8. Optimize API Integration Performance

#### Implement API Rate Limiting
```bash
# Create rate limiting implementation
nano src/mcp/fastapi_app/middleware/api_rate_limiter.py
```

Example rate limiting implementation:
```python
#!/usr/bin/env python3
import time
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class RateLimitInfo:
    """Rate limit information for an API"""
    calls_made: int
    reset_time: datetime
    max_calls: int
    window_seconds: int

class APIRateLimiter:
    """Rate limiter for external API calls"""
    
    def __init__(self):
        self.limits: Dict[str, RateLimitInfo] = {}
        self.default_limits = {
            'openai': {'max_calls': 60, 'window_seconds': 60},
            'reddit': {'max_calls': 100, 'window_seconds': 60},
            'news': {'max_calls': 100, 'window_seconds': 60},
            'twitter': {'max_calls': 300, 'window_seconds': 900}
        }
    
    def update_from_headers(self, api_name: str, headers: Dict[str, str]):
        """Update rate limit info from API response headers"""
        if 'x-ratelimit-remaining' in headers:
            remaining = int(headers['x-ratelimit-remaining'])
            limit = int(headers.get('x-ratelimit-limit', '0'))
            reset = int(headers.get('x-ratelimit-reset', '0'))
            
            self.limits[api_name] = RateLimitInfo(
                calls_made=limit - remaining,
                reset_time=datetime.fromtimestamp(reset),
                max_calls=limit,
                window_seconds=reset - int(time.time()) if reset > 0 else 60
            )
    
    async def wait_if_needed(self, api_name: str) -> bool:
        """Wait if rate limit would be exceeded"""
        now = datetime.now()
        
        # Get rate limit info
        limit_info = self.limits.get(api_name)
        default_limit = self.default_limits.get(api_name, {'max_calls': 60, 'window_seconds': 60})
        
        if not limit_info:
            # Initialize with default limits
            self.limits[api_name] = RateLimitInfo(
                calls_made=0,
                reset_time=now + timedelta(seconds=default_limit['window_seconds']),
                max_calls=default_limit['max_calls'],
                window_seconds=default_limit['window_seconds']
            )
            return False
        
        # Check if we need to reset the counter
        if now >= limit_info.reset_time:
            limit_info.calls_made = 0
            limit_info.reset_time = now + timedelta(seconds=limit_info.window_seconds)
        
        # Check if we're at the limit
        if limit_info.calls_made >= limit_info.max_calls:
            # Calculate wait time
            wait_time = (limit_info.reset_time - now).total_seconds()
            if wait_time > 0:
                print(f"Rate limit reached for {api_name}, waiting {wait_time:.1f} seconds...")
                await asyncio.sleep(wait_time)
                # Reset after waiting
                limit_info.calls_made = 0
                limit_info.reset_time = now + timedelta(seconds=limit_info.window_seconds)
                return True
        
        # Increment call counter
        limit_info.calls_made += 1
        return False
    
    def get_status(self, api_name: str) -> Dict[str, any]:
        """Get current rate limit status"""
        limit_info = self.limits.get(api_name)
        if not limit_info:
            return {'status': 'not_initialized'}
        
        now = datetime.now()
        remaining_calls = max(0, limit_info.max_calls - limit_info.calls_made)
        time_until_reset = max(0, (limit_info.reset_time - now).total_seconds())
        
        return {
            'status': 'active',
            'calls_made': limit_info.calls_made,
            'max_calls': limit_info.max_calls,
            'remaining_calls': remaining_calls,
            'time_until_reset': time_until_reset,
            'reset_time': limit_info.reset_time.isoformat()
        }

# Global rate limiter instance
rate_limiter = APIRateLimiter()
```

#### Implement API Client Retry Logic
```bash
# Create retry logic implementation
nano src/mcp/fastapi_app/utils/api_retry.py
```

Example retry logic implementation:
```python
#!/usr/bin/env python3
import asyncio
import time
from typing import Callable, Any, Optional
from functools import wraps

def retry_api_call(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retrying API calls with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Don't retry on authentication errors
                    if '401' in str(e) or '403' in str(e):
                        raise e
                    
                    # Don't retry if this is the last attempt
                    if attempt == max_retries:
                        raise e
                    
                    # Calculate delay with exponential backoff
                    wait_time = delay * (backoff ** attempt)
                    print(f"API call failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    print(f"Retrying in {wait_time:.1f} seconds...")
                    await asyncio.sleep(wait_time)
            
            # This should never be reached
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Don't retry on authentication errors
                    if '401' in str(e) or '403' in str(e):
                        raise e
                    
                    # Don't retry if this is the last attempt
                    if attempt == max_retries:
                        raise e
                    
                    # Calculate delay with exponential backoff
                    wait_time = delay * (backoff ** attempt)
                    print(f"API call failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    print(f"Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
            
            # This should never be reached
            raise last_exception
        
        # Return appropriate wrapper based on function type
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator
```

### 9. Verify API Integration Resolution
```bash
# Test final API integration implementation
python scripts/test_all_apis.py

# Run API monitoring
python scripts/monitor_api_usage.py

# Check rate limiting implementation
docker-compose exec app python -c "
from src.mcp.fastapi_app.middleware.api_rate_limiter import rate_limiter
print('Rate limiter loaded successfully')
status = rate_limiter.get_status('openai')
print(f'OpenAI rate limit status: {status}')
"

# Verify retry logic
docker-compose exec app python -c "
from src.mcp.fastapi_app.utils.api_retry import retry_api_call
print('Retry logic loaded successfully')
"

# Test API integration performance
ab -n 100 -c 10 http://localhost:8000/api/v1/intelligence/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Commercial real estate market trends"}'
```

## Verification
After completing the above steps, you should be able to:
- [ ] Understand external API integration architecture
- [ ] Verify API key configuration and validity
- [ ] Test individual API integrations thoroughly
- [ ] Run comprehensive API integration test suites
- [ ] Monitor API usage and performance metrics
- [ ] Troubleshoot API integration issues and errors
- [ ] Optimize API integration performance and reliability
- [ ] Implement rate limiting and retry logic
- [ ] Verify API integration resolution

## Common API Integration Issues and Solutions

### Authentication Issues
- **"401 Unauthorized"**: Check API key validity and format
- **"403 Forbidden"**: Verify API key permissions and scope
- **"Invalid credentials"**: Regenerate API keys and update configuration
- **"Authentication failed"**: Check authentication method and headers

### Rate Limiting Issues
- **"429 Too Many Requests"**: Implement proper rate limiting
- **"Rate limit exceeded"**: Add delays between API calls
- **"Quota exceeded"**: Upgrade API plan or optimize usage
- **"Request throttled"**: Implement exponential backoff

### Connectivity Issues
- **"Connection timeout"**: Check network connectivity and firewall
- **"DNS resolution failed"**: Verify DNS configuration
- **"Host unreachable"**: Check service availability
- **"SSL certificate error"**: Update SSL certificates or disable verification (not recommended)

### Data Issues
- **"Invalid response format"**: Check API documentation and parsing
- **"Missing required fields"**: Verify request parameters
- **"Data validation failed"**: Check data format and constraints
- **"Empty response"**: Verify API endpoint and parameters

## Troubleshooting Checklist

### Quick Fixes
- [ ] Verify API keys in .env file
- [ ] Test API connectivity with curl
- [ ] Check API documentation for changes
- [ ] Review API client implementation
- [ ] Monitor API usage and limits
- [ ] Check network connectivity and firewall

### Advanced Diagnostics
- [ ] Implement detailed API logging
- [ ] Monitor API performance metrics
- [ ] Test API endpoints individually
- [ ] Analyze API response patterns
- [ ] Implement comprehensive error handling
- [ ] Optimize API call frequency and batching

## Next Steps
Proceed to Chunk 38: Celery Worker Setup to learn how to configure and manage Celery workers for background task processing in the CRE Intelligence Platform.