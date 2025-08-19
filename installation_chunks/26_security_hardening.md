# Installation Chunk 26: Security Hardening

## Overview
This installation chunk covers security hardening measures for the CRE Intelligence Platform, including authentication, authorization, encryption, and system security.

## Prerequisites
- System requirements verification completed (Chunk 01)
- API key configuration completed (Chunk 14)
- Monitoring setup completed (Chunk 25)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Secure Environment Variables

#### Set Strong Secrets
```bash
# Generate strong secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env file with strong secrets
nano .env
```

Example secure environment configuration:
```env
# Security settings
SECRET_KEY=your_strong_secret_key_here_change_this_in_production
DEBUG=false
LOG_LEVEL=INFO

# Database security
POSTGRES_PASSWORD=your_strong_database_password
REDIS_PASSWORD=your_strong_redis_password

# API security
API_RATE_LIMIT=100/minute
API_THROTTLE_RATE=5/second
```

#### Set File Permissions
```bash
# Secure environment files
chmod 600 .env
chmod 600 .env.docker
chmod 600 .env.example

# Secure configuration directories
chmod 700 config/
chmod 700 data/
chmod 700 logs/
```

### 3. Implement Authentication and Authorization

#### Configure JWT Authentication
```bash
# Install authentication dependencies
pip install python-jose[cryptography] passlib[bcrypt]
```

Edit authentication configuration:
```python
# Edit src/mcp/fastapi_app/auth/config.py
import os
from datetime import timedelta

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

#### Set Up User Management
```bash
# Create users table in database
python src/scripts/setup_users.py

# Create initial admin user
python src/scripts/create_admin_user.py
```

### 4. Enable HTTPS and SSL/TLS

#### For Docker Deployment - Configure Nginx SSL
Edit `nginx.conf` to include SSL configuration:
```nginx
# Add SSL server block to nginx.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Include existing location blocks
    include /etc/nginx/conf.d/default.conf;
}
```

#### Generate Self-Signed Certificates (for testing)
```bash
# Create SSL directory
mkdir -p ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/nginx.key \
    -out ssl/nginx.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

### 5. Implement Security Headers

#### Update Nginx Configuration
Add security headers to `nginx.conf`:
```nginx
# Add to server block
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' ws: wss:; frame-ancestors 'none';" always;
```

### 6. Configure CORS and Rate Limiting

#### Set Up CORS Configuration
```python
# Edit src/mcp/fastapi_app/config.py
from fastapi.middleware.cors import CORSMiddleware

CORS_ORIGINS = [
    "https://your-domain.com",
    "https://www.your-domain.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]
```

#### Configure Rate Limiting
```python
# Edit src/mcp/fastapi_app/middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Add to main application
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### 7. Secure Database Connections

#### Update PostgreSQL Configuration
Edit `docker-compose.yml` to include database security:
```yaml
# Update postgres service
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_DB: reddit08_db
    POSTGRES_USER: reddit08_user
    POSTGRES_PASSWORD: your_strong_password_here  # Use strong password
  command: >
    postgres
    -c log_statement=ddl
    -c log_connections=on
    -c log_disconnections=on
    -c password_encryption=scram-sha-256
```

#### Update Redis Configuration
Edit `redis.conf` for security:
```conf
# Enable password authentication
requirepass your_strong_redis_password

# Bind to localhost only
bind 127.0.0.1

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command KEYS ""
rename-command CONFIG ""
```

### 8. Implement Input Validation and Sanitization

#### Add Input Validation
```python
# Edit src/mcp/fastapi_app/schemas/validation.py
from pydantic import BaseModel, validator
import re

class UserInput(BaseModel):
    username: str
    email: str
    content: str
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', v):
            raise ValueError('Username must be 3-20 characters, alphanumeric or underscore')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v
```

### 9. Set Up Security Scanning

#### Install Security Tools
```bash
# Install security scanning tools
pip install bandit safety

# Install Docker security scanning
docker scan --accept-license
```

#### Run Security Scans
```bash
# Run bandit security scan
bandit -r src/

# Run safety check for vulnerable dependencies
safety check

# Run Docker security scan
docker scan reddit08-app
```

### 10. Configure Firewall (for local deployment)

#### Set Up UFW Firewall
```bash
# Install UFW (Ubuntu/Debian)
sudo apt install ufw

# Enable firewall
sudo ufw enable

# Allow necessary ports
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5432/tcp  # PostgreSQL (if needed)
sudo ufw allow 6379/tcp  # Redis (if needed)

# Deny all other incoming connections
sudo ufw default deny incoming

# Allow outgoing connections
sudo ufw default allow outgoing
```

### 11. Implement Security Logging

#### Configure Security Event Logging
```python
# Edit src/mcp/fastapi_app/logging/security.py
import logging
from datetime import datetime

security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Create security log handler
handler = logging.FileHandler('logs/security.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
security_logger.addHandler(handler)

def log_security_event(event_type, user_id=None, details=None):
    security_logger.info(f"SECURITY_EVENT: {event_type} | User: {user_id} | Details: {details}")
```

### 12. Set Up Regular Security Updates

#### Configure Automatic Updates
```bash
# For Ubuntu/Debian
sudo apt install unattended-upgrades

# Configure automatic updates
sudo dpkg-reconfigure -plow unattended-upgrades

# Edit update configuration
sudo nano /etc/apt/apt.conf.d/50unattended-upgrades
```

#### Schedule Security Scans
```bash
# Add to crontab for regular security scans
crontab -e

# Weekly security scan on Sundays at 2 AM
0 2 * * 0 cd /path/to/reddit08 && bandit -r src/ > logs/security_scan_$(date +\%Y\%m\%d).log 2>&1

# Daily dependency security check
0 3 * * * cd /path/to/reddit08 && safety check > logs/safety_check_$(date +\%Y\%m\%d).log 2>&1
```

### 13. Verify Security Configuration
```bash
# Test HTTPS configuration
curl -I https://localhost

# Test security headers
curl -I -H "Accept: text/html" https://localhost

# Test database security
docker-compose exec postgres psql -U reddit08_user -d reddit08_db -c "SELECT version();"

# Test Redis security
docker-compose exec redis redis-cli ping

# Verify file permissions
ls -la .env
ls -la config/
ls -la data/
```

## Verification
After completing the above steps, you should have:
- [ ] Environment variables secured with strong secrets
- [ ] Authentication and authorization implemented
- [ ] HTTPS/SSL enabled with proper certificates
- [ ] Security headers configured
- [ ] CORS and rate limiting configured
- [ ] Database connections secured
- [ ] Input validation and sanitization implemented
- [ ] Security scanning tools installed and configured
- [ ] Firewall configured (for local deployment)
- [ ] Security logging implemented
- [ ] Regular security updates configured
- [ ] Security configuration verified

## Troubleshooting
If security hardening issues occur:

1. **SSL/TLS configuration issues**:
   - Verify certificate files exist and are readable
   - Check certificate validity and expiration
   - Review Nginx SSL configuration
   - Test with SSL labs test

2. **Authentication failures**:
   - Verify secret keys are correctly configured
   - Check user credentials and permissions
   - Review authentication middleware configuration
   - Test with sample authentication requests

3. **CORS issues**:
   - Verify allowed origins are correctly configured
   - Check CORS middleware order
   - Review request headers
   - Test with different origins

4. **Rate limiting issues**:
   - Verify rate limit configuration
   - Check Redis connectivity for rate limiting
   - Review rate limit exceeded responses
   - Test with multiple rapid requests

5. **Database security issues**:
   - Verify database passwords are strong
   - Check database user permissions
   - Review database connection settings
   - Test database access restrictions

6. **Security scan failures**:
   - Review scan results and recommendations
   - Address identified vulnerabilities
   - Update dependencies with security issues
   - Re-run scans after fixes

## Next Steps
Proceed to Chunk 27: Performance Optimization to optimize the CRE Intelligence Platform for better performance.