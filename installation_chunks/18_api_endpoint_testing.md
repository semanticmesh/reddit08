# Installation Chunk 18: API Endpoint Testing

## Overview
This installation chunk tests all API endpoints of the CRE Intelligence Platform to ensure they are working correctly.

## Prerequisites
- Service health checks completed (Chunk 17)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Test Root Endpoint
Test the root API endpoint:
```bash
# Test GET request to root endpoint
curl -X GET http://localhost:8000/ \
  -H "Content-Type: application/json"

# Expected response: Welcome message or API information
```

### 3. Test Health Endpoint
Test the health check endpoint:
```bash
# Test GET request to health endpoint
curl -X GET http://localhost:8000/health \
  -H "Content-Type: application/json"

# Expected response: {"status":"healthy"}
```

### 4. Test Version Endpoint
Test the version endpoint:
```bash
# Test GET request to version endpoint
curl -X GET http://localhost:8000/version \
  -H "Content-Type: application/json"

# Expected response: Version information
```

### 5. Test Authentication Endpoints
Test authentication-related endpoints:
```bash
# Test login endpoint (if available)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpassword"
  }'

# Test token refresh endpoint (if available)
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### 6. Test Data Collection Endpoints
Test data collection endpoints:
```bash
# Test Reddit data collection endpoint
curl -X POST http://localhost:8000/api/v1/data/reddit/collect \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["r/realestate", "r/commercialrealestate"],
    "limit": 100
  }'

# Test news data collection endpoint
curl -X POST http://localhost:8000/api/v1/data/news/collect \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["commercial real estate", "office space"],
    "sources": ["reuters", "bloomberg"]
  }'
```

### 7. Test Data Processing Endpoints
Test data processing endpoints:
```bash
# Test data processing endpoint
curl -X POST http://localhost:8000/api/v1/data/process \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data_id": "12345",
    "processing_type": "sentiment_analysis"
  }'

# Test batch processing endpoint
curl -X POST http://localhost:8000/api/v1/data/process/batch \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data_ids": ["12345", "67890"],
    "processing_type": "keyword_extraction"
  }'
```

### 8. Test Intelligence Endpoints
Test intelligence analysis endpoints:
```bash
# Test market analysis endpoint
curl -X POST http://localhost:8000/api/v1/intelligence/market-analysis \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "New York",
    "property_type": "office",
    "timeframe": "monthly"
  }'

# Test trend analysis endpoint
curl -X POST http://localhost:8000/api/v1/intelligence/trend-analysis \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["rental rates", "vacancy rates"],
    "timeframe": "quarterly"
  }'
```

### 9. Test Data Retrieval Endpoints
Test data retrieval endpoints:
```bash
# Test get processed data endpoint
curl -X GET "http://localhost:8000/api/v1/data/processed?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"

# Test get specific data by ID
curl -X GET http://localhost:8000/api/v1/data/processed/12345 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### 10. Test Configuration Endpoints
Test configuration management endpoints:
```bash
# Test get configuration
curl -X GET http://localhost:8000/api/v1/config \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"

# Test update configuration
curl -X PUT http://localhost:8000/api/v1/config \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "settings": {
      "max_workers": 8,
      "cache_ttl": 7200
    }
  }'
```

### 11. Test Error Handling
Test error handling for invalid requests:
```bash
# Test 404 error
curl -X GET http://localhost:8000/api/v1/nonexistent \
  -H "Content-Type: application/json"

# Test validation error
curl -X POST http://localhost:8000/api/v1/data/process \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "invalid_field": "invalid_value"
  }'
```

### 12. Test Rate Limiting
Test rate limiting functionality:
```bash
# Make multiple rapid requests to test rate limiting
for i in {1..20}; do
  curl -X GET http://localhost:8000/health \
    -H "Content-Type: application/json"
  sleep 0.1
done
```

### 13. Test WebSocket Endpoints
Test WebSocket connections (if available):
```bash
# Test WebSocket connection using wscat or similar tool
# wscat -c ws://localhost:8000/ws
```

### 14. Run Automated API Tests
Run the built-in API test suite:
```bash
# Run API tests
make test-api

# Or run specific API tests
python -m pytest src/tests/api/ -v
```

## Verification
After completing the above steps, you should have:
- [ ] Root endpoint responding correctly
- [ ] Health endpoint returning healthy status
- [ ] Version endpoint returning version information
- [ ] Authentication endpoints working (if applicable)
- [ ] Data collection endpoints processing requests
- [ ] Data processing endpoints working correctly
- [ ] Intelligence analysis endpoints returning results
- [ ] Data retrieval endpoints returning data
- [ ] Configuration endpoints managing settings
- [ ] Error handling working properly
- [ ] Rate limiting functioning correctly
- [ ] WebSocket endpoints working (if applicable)
- [ ] Automated API tests passing

## Troubleshooting
If API endpoint testing fails:

1. **Endpoint not found (404)**:
   - Check API route definitions
   - Verify the endpoint path is correct
   - Check if the service is running

2. **Authentication failed (401/403)**:
   - Verify authentication tokens are valid
   - Check user permissions
   - Test authentication endpoints

3. **Invalid request data (422)**:
   - Check request payload format
   - Verify required fields are present
   - Check data types

4. **Server errors (500)**:
   - Check server logs for error details
   - Verify dependencies are installed
   - Check database connectivity

5. **Rate limiting errors (429)**:
   - Check rate limiting configuration
   - Implement proper request throttling
   - Verify Redis connectivity for rate limiting

6. **Timeout errors**:
   - Check service performance
   - Increase timeout settings if needed
   - Optimize slow endpoints

## Next Steps
Proceed to Chunk 19: Data Source Configuration to set up data sources for the CRE Intelligence Platform.