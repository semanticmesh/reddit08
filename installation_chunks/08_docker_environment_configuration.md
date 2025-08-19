# Installation Chunk 08: Docker Environment Configuration

## Overview
This installation chunk configures the environment variables for Docker deployment of the CRE Intelligence Platform.

## Prerequisites
- Docker installation and verification completed (Chunk 02)
- Repository cloned (Chunk 07)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Create Docker Environment File
Copy the Docker environment template:
```bash
cp .env.docker .env
```

### 3. Configure API Keys
Edit the `.env` file to add your API keys:
```bash
# Open the file in your preferred editor
nano .env
# or
code .env
# or
vim .env
```

Required API keys to configure:
```env
# API Keys - IMPORTANT: Set these with real values
OPENAI_API_KEY=your_openai_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
NEWS_API_KEY=your_news_api_key_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
```

### 4. Configure Database Credentials
Set secure database credentials:
```env
# Database configuration
DATABASE_URL=postgresql://user:password@postgres:5432/reddit08_db

# For production, change the default credentials:
# DATABASE_URL=postgresql://your_user:your_secure_password@postgres:5432/reddit08_db
```

### 5. Configure Application Settings
Adjust application settings as needed:
```env
# Application settings
DEBUG=false
LOG_LEVEL=INFO
MAX_WORKERS=4

# Security
SECRET_KEY=your_secret_key_here_change_this_in_production

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### 6. Configure Data Directories
Verify data directory settings:
```env
# Data directories
DATA_DIR=/app/data
LOGS_DIR=/app/logs
CONFIG_DIR=/app/config
```

### 7. Configure Celery Settings
Review Celery configuration:
```env
# Celery configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
CELERY_ACCEPT_CONTENT=['json']
```

### 8. Configure Intelligence Service Settings
Adjust intelligence service settings:
```env
# Intelligence service settings
INTELLIGENCE_ENABLED=true
INTELLIGENCE_CACHE_TTL=3600  # 1 hour in seconds
INTELLIGENCE_MAX_CONCURRENT_REQUESTS=10
```

### 9. Configure Monitoring and Logging
Set up monitoring and logging:
```env
# Monitoring and logging
SENTRY_DSN=your_sentry_dsn_here
LOG_FILE_LEVEL=INFO
LOG_CONSOLE_LEVEL=DEBUG
```

### 10. Verify Environment Configuration
Check that all required variables are set:
```bash
# View the environment file
cat .env

# Verify specific variables
grep -E "(OPENAI_API_KEY|REDDIT_CLIENT_ID|REDDIT_CLIENT_SECRET)" .env
```

### 11. Secure Environment File
Set appropriate permissions for the environment file:
```bash
chmod 600 .env
```

## Verification
After completing the above steps, you should have:
- [ ] Docker environment file created from template
- [ ] All required API keys configured
- [ ] Secure database credentials set
- [ ] Application settings configured
- [ ] Data directories configured
- [ ] Celery settings configured
- [ ] Intelligence service settings configured
- [ ] Monitoring and logging configured
- [ ] Environment file secured with appropriate permissions

## Troubleshooting
If environment configuration fails:

1. **Missing API keys**:
   - Verify all required API keys are set
   - Check for typos in variable names
   - Ensure values are properly quoted

2. **Invalid database URL**:
   - Verify the format: `postgresql://user:password@host:port/database`
   - Ensure special characters in passwords are URL-encoded

3. **Permission issues**:
   - Check file permissions: `ls -l .env`
   - Ensure the file is readable by the Docker containers

4. **Syntax errors**:
   - Ensure there are no spaces around `=` signs
   - Check for proper quoting of values with spaces or special characters

## Next Steps
Proceed to Chunk 10: Docker Service Deployment to start the CRE Intelligence Platform services.