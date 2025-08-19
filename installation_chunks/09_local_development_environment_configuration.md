# Installation Chunk 09: Local Development Environment Configuration

## Overview
This installation chunk configures the environment variables for local development of the CRE Intelligence Platform.

## Prerequisites
- Python virtual environment setup completed (Chunk 03)
- PostgreSQL installation and setup completed (Chunk 04)
- Redis installation and setup completed (Chunk 05)
- Repository cloned (Chunk 07)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Activate Virtual Environment
Activate your Python virtual environment:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Create Local Environment File
Copy the local development environment template:
```bash
cp .env.example .env
```

### 4. Configure PostgreSQL Connection
Edit the `.env` file to configure PostgreSQL connection:
```bash
# Open the file in your preferred editor
nano .env
# or
code .env
# or
vim .env
```

Set PostgreSQL connection details:
```env
# Database connection settings
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=reddit08
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
```

### 5. Configure Connection Pool Settings
Adjust connection pool settings for optimal performance:
```env
# Connection pool settings
POSTGRES_POOL_SIZE=10
POSTGRES_MAX_OVERFLOW=20
POSTGRES_POOL_TIMEOUT=30
```

### 6. Configure SSL Settings
Set SSL settings based on your PostgreSQL configuration:
```env
# SSL settings
POSTGRES_SSL_MODE=prefer
POSTGRES_SSL_CERT_FILE=
POSTGRES_SSL_KEY_FILE=
```

### 7. Configure Connection Settings
Set additional connection settings:
```env
# Connection settings
POSTGRES_ECHO=false
POSTgreSQL_POOL_RECYCLE=3600
```

### 8. Configure Database Setup Settings
Set database setup options:
```env
# Database setup settings
POSTGRES_CREATE_DB=true
POSTGRES_CREATE_EXTENSION=true
```

### 9. Verify Environment Configuration
Check that all required variables are set:
```bash
# View the environment file
cat .env

# Verify PostgreSQL settings
grep -E "(POSTGRES_HOST|POSTGRES_PORT|POSTGRES_DB|POSTGRES_USER)" .env
```

### 10. Test Database Connection
Test the database connection with the configured settings:
```bash
# Test connection using psql
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB
```

When prompted, enter the password for the PostgreSQL user.

### 11. Secure Environment File
Set appropriate permissions for the environment file:
```bash
chmod 600 .env
```

### 12. Configure Additional Development Settings
For development, you might want to enable debug mode:
```bash
# Add to .env file
DEBUG=true
LOG_LEVEL=DEBUG
```

## Verification
After completing the above steps, you should have:
- [ ] Local development environment file created from template
- [ ] PostgreSQL connection details configured
- [ ] Connection pool settings configured
- [ ] SSL settings configured
- [ ] Connection settings configured
- [ ] Database setup settings configured
- [ ] Database connection tested successfully
- [ ] Environment file secured with appropriate permissions
- [ ] Additional development settings configured (optional)

## Troubleshooting
If environment configuration fails:

1. **Database connection failed**:
   - Verify PostgreSQL service is running
   - Check PostgreSQL credentials are correct
   - Ensure PostgreSQL is accepting connections on localhost
   - Verify the database `reddit08` exists

2. **Permission issues**:
   - Check file permissions: `ls -l .env`
   - Ensure the file is readable by your user

3. **Syntax errors**:
   - Ensure there are no spaces around `=` signs
   - Check for proper quoting of values with spaces or special characters

4. **Environment variables not loading**:
   - Verify the virtual environment is activated
   - Check that the application loads the `.env` file correctly

## Next Steps
Proceed to Chunk 11: Local Development Dependency Installation to install the required Python packages.