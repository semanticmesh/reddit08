# Installation Chunk 32: API Key Troubleshooting

## Overview
This installation chunk covers how to diagnose and resolve API key authentication issues for the CRE Intelligence Platform, including missing keys, invalid keys, rate limiting, and integration problems.

## Prerequisites
- API key configuration completed (Chunk 14)
- Service health checks completed (Chunk 17)
- Troubleshooting common issues completed (Chunk 28)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Verify API Key Configuration

#### Check Environment Variables
```bash
# Check all API key environment variables
cat .env | grep -E "(API_KEY|OPENAI|REDDIT|NEWS|TWITTER)"

# Expected variables:
# OPENAI_API_KEY=your_openai_api_key_here
# REDDIT_CLIENT_ID=your_reddit_client_id_here
# REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
# NEWS_API_KEY=your_news_api_key_here
# TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here

# For Docker deployment, check .env.docker
cat .env.docker | grep -E "(API_KEY|OPENAI|REDDIT|NEWS|TWITTER)"
```

#### Validate API Key Format
```bash
# Check OpenAI API key format (should start with sk-)
grep OPENAI_API_KEY .env | cut -d'=' -f2 | grep -E "^sk-[a-zA-Z0-9]{48}$"

# Check Reddit API key format
grep REDDIT_CLIENT_ID .env | cut -d'=' -f2 | wc -c  # Should be 14 characters
grep REDDIT_CLIENT_SECRET .env | cut -d'=' -f2 | wc -c  # Should be 27 characters

# Check News API key format
grep NEWS_API_KEY .env | cut -d'=' -f2 | wc -c  # Should be 32 characters

# Check Twitter Bearer Token format
grep TWITTER_BEARER_TOKEN .env | cut -d'=' -f2 | grep -E "^AAAAAAAAAAAAAAAAAAAAA"
```

### 3. Test API Key Validity

#### Test OpenAI API Key
```bash
# Test OpenAI API key validity
OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d'=' -f2)
curl -X GET "https://api.openai.com/v1/models" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json"

# Expected response: HTTP 200 with model list
# Error response: Check error message for specific issue
```

#### Test Reddit API Credentials
```bash
# Test Reddit API credentials
REDDIT_CLIENT_ID=$(grep REDDIT_CLIENT_ID .env | cut -d'=' -f2)
REDDIT_CLIENT_SECRET=$(grep REDDIT_CLIENT_SECRET .env | cut -d'=' -f2)
REDDIT_USERNAME="your_reddit_username"  # Add to .env
REDDIT_PASSWORD="your_reddit_password"  # Add to .env

# Get access token
curl -X POST "https://www.reddit.com/api/v1/access_token" \
  -H "User-Agent: CRE Intelligence Platform" \
  -u "$REDDIT_CLIENT_ID:$REDDIT_CLIENT_SECRET" \
  -d "grant_type=password&username=$REDDIT_USERNAME&password=$REDDIT_PASSWORD"

# Expected response: JSON with access_token field
# Error response: Check error message for specific issue
```

#### Test News API Key
```bash
# Test News API key
NEWS_API_KEY=$(grep NEWS_API_KEY .env | cut -d'=' -f2)
curl "https://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=$NEWS_API_KEY"

# Expected response: HTTP 200 with articles
# Error response: Check error message for specific issue
```

#### Test Twitter API Key
```bash
# Test Twitter API key
TWITTER_BEARER_TOKEN=$(grep TWITTER_BEARER_TOKEN .env | cut -d'=' -f2)
curl "https://api.twitter.com/2/tweets/search/recent?query=python" \
  -H "Authorization: Bearer $TWITTER_BEARER_TOKEN"

# Expected response: HTTP 200 with tweets
# Error response: Check error message for specific issue
```

### 4. Common API Key Error Diagnostics

#### "Invalid API Key" Errors
```bash
# Check for invalid API key errors in logs
tail -f logs/app.log | grep -i "invalid.*api.*key"

# For Docker deployment
docker-compose logs app | grep -i "invalid.*api.*key"

# Common causes:
# 1. Key is expired or revoked
# 2. Key is incorrectly formatted
# 3. Key is for wrong service
# 4. Key has wrong permissions

# Solutions:
# 1. Generate new API key from service provider
# 2. Verify key format matches expected pattern
# 3. Check service provider documentation
# 4. Ensure key has required permissions
```

#### "API Rate Limit Exceeded" Errors
```bash
# Check for rate limit errors
tail -f logs/app.log | grep -i "rate.*limit\|429"

# For Docker deployment
docker-compose logs app | grep -i "rate.*limit\|429"

# Check current rate limit status
curl -I "https://api.openai.com/v1/models" \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Look for headers:
# X-RateLimit-Limit: Maximum requests per period
# X-RateLimit-Remaining: Remaining requests
# X-RateLimit-Reset: Time when limit resets

# Implement rate limiting in application
# Check src/mcp/fastapi_app/middleware/rate_limit.py
```

#### "Authentication Failed" Errors
```bash
# Check for authentication errors
tail -f logs/app.log | grep -i "authentication.*failed\|unauthorized\|401\|403"

# For Docker deployment
docker-compose logs app | grep -i "authentication.*failed\|unauthorized\|401\|403"

# Common authentication issues:
# 1. Missing API key in request
# 2. Incorrect API key in .env file
# 3. Expired or revoked API key
# 4. Wrong authentication header format

# Solutions:
# 1. Verify API key is set in environment
# 2. Check .env file for correct key values
# 3. Regenerate API keys if expired
# 4. Review authentication header implementation
```

### 5. Environment Variable Issues

#### Check Environment Variable Loading
```bash
# Test environment variable loading
python -c "
import os
from dotenv import load_dotenv

load_dotenv()
print('OPENAI_API_KEY:', '***' if os.getenv('OPENAI_API_KEY') else 'Not set')
print('REDDIT_CLIENT_ID:', '***' if os.getenv('REDDIT_CLIENT_ID') else 'Not set')
print('REDDIT_CLIENT_SECRET:', '***' if os.getenv('REDDIT_CLIENT_SECRET') else 'Not set')
print('NEWS_API_KEY:', '***' if os.getenv('NEWS_API_KEY') else 'Not set')
print('TWITTER_BEARER_TOKEN:', '***' if os.getenv('TWITTER_BEARER_TOKEN') else 'Not set')
"

# Check if .env file is being loaded
echo "DEBUG: Environment file loaded" >> logs/debug.log
cat .env >> logs/debug.log
```

#### Verify File Permissions
```bash
# Check .env file permissions
ls -la .env
ls -la .env.docker

# Set secure permissions
chmod 600 .env
chmod 600 .env.docker

# Check if file is readable by application
python -c "
try:
    with open('.env', 'r') as f:
        content = f.read()
        if 'OPENAI_API_KEY' in content:
            print('Environment file is readable')
        else:
            print('Environment file may be corrupted')
except Exception as e:
    print(f'Cannot read environment file: {e}')
"
```

### 6. Network and Connectivity Issues

#### Check Internet Connectivity
```bash
# Test internet connectivity
ping -c 3 google.com

# Test API endpoints directly
curl -I https://api.openai.com
curl -I https://oauth.reddit.com
curl -I https://newsapi.org
curl -I https://api.twitter.com

# Check DNS resolution
nslookup api.openai.com
nslookup oauth.reddit.com
nslookup newsapi.org
nslookup api.twitter.com

# Test with timeout
curl --connect-timeout 10 https://api.openai.com
```

#### Check Proxy and Firewall Settings
```bash
# Check if behind proxy
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Test without proxy
curl --noproxy "*" https://api.openai.com

# Check firewall settings
sudo ufw status
# Ensure outbound connections are allowed

# For corporate networks, check:
# 1. Proxy configuration
# 2. SSL certificate interception
# 3. Network security policies
```

### 7. Application-Level Troubleshooting

#### Check API Client Configuration
```bash
# Check API client configuration files
cat src/mcp/fastapi_app/clients/openai_client.py
cat src/mcp/fastapi_app/clients/reddit_client.py
cat src/mcp/fastapi_app/clients/news_client.py
cat src/mcp/fastapi_app/clients/twitter_client.py

# Look for:
# 1. Correct API endpoint URLs
# 2. Proper header formatting
# 3. Correct error handling
# 4. Proper timeout settings
```

#### Test API Integration
```bash
# Run API integration tests
python -m pytest src/tests/integration/test_api_clients.py -v

# Run specific API tests
python src/scripts/test_openai_api.py
python src/scripts/test_reddit_api.py
python src/scripts/test_news_api.py
python src/scripts/test_twitter_api.py

# Check test results and error messages
```

### 8. Advanced Troubleshooting

#### Enable Debug Logging
```bash
# Enable debug logging for API calls
export DEBUG=true
export LOG_LEVEL=DEBUG

# Restart application
# For Docker
docker-compose down && docker-compose up -d

# For local development
pkill -f uvicorn
make serve

# Monitor debug logs
tail -f logs/app.log | grep -i "api\|request\|response"
```

#### Use API Debugging Tools
```bash
# Install API debugging tools
pip install httpie

# Test API calls with httpie
http --print=hHbB GET https://api.openai.com/v1/models \
  "Authorization: Bearer $OPENAI_API_KEY"

# Use verbose curl for detailed output
curl -v https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### 9. Verify API Key Resolution
```bash
# Test final API key functionality
python src/scripts/verify_all_apis.py

# Run health check endpoint
curl http://localhost:8000/health/apis

# Check application logs for API errors
tail -f logs/app.log | grep -i "api.*error\|key.*error"
```

## Verification
After completing the above steps, you should be able to:
- [ ] Verify API key configuration and format
- [ ] Test API key validity for all services
- [ ] Diagnose common API key errors
- [ ] Resolve rate limiting issues
- [ ] Handle authentication failures
- [ ] Fix environment variable problems
- [ ] Address network and connectivity issues
- [ ] Troubleshoot application-level problems
- [ ] Use advanced debugging techniques
- [ ] Verify API key resolution

## Common API Key Error Messages and Solutions

### OpenAI API Errors
- **"401 Unauthorized: Invalid Authentication"**: Check API key validity and format
- **"401 Unauthorized: Incorrect API key provided"**: Verify key in .env file
- **"429 Too Many Requests"**: Implement rate limiting or upgrade plan
- **"403 Forbidden: Insufficient permissions"**: Check API key permissions

### Reddit API Errors
- **"401 Unauthorized"**: Verify client ID, secret, and user credentials
- **"403 Forbidden"**: Check Reddit app permissions and user access
- **"invalid_grant"**: Verify username/password for script apps
- **"RATELIMIT"**: Implement proper rate limiting

### News API Errors
- **"apiKeyInvalid"**: Verify News API key is correct and active
- **"apiKeyMissing"**: Ensure API key is set in request
- **"tooManyRequests"**: Check rate limits and implement delays
- **"sourcesUnavailable"**: Verify source is available in free tier

### Twitter API Errors
- **"401 Unauthorized"**: Check Bearer Token validity
- **"403 Forbidden"**: Verify app permissions and user access
- **"429 Too Many Requests"**: Implement rate limiting
- **"Invalid Request"**: Check API endpoint and parameters

## Troubleshooting Checklist

### Quick Fixes
- [ ] Verify API keys in .env file
- [ ] Test API key validity with curl
- [ ] Check environment variable loading
- [ ] Verify internet connectivity
- [ ] Check application logs for errors
- [ ] Restart application services

### Advanced Diagnostics
- [ ] Enable debug logging
- [ ] Test with API debugging tools
- [ ] Check rate limit headers
- [ ] Verify SSL certificates
- [ ] Test network connectivity
- [ ] Review API client configuration

## Next Steps
Proceed to Chunk 33: Service Startup Order Verification to learn how to ensure proper service initialization sequence.