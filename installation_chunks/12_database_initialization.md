# Installation Chunk 12: Database Initialization

## Overview
This installation chunk initializes the database for the CRE Intelligence Platform.

## Prerequisites
- PostgreSQL installation and setup completed (Chunk 04)
- Local development dependency installation completed (Chunk 11) OR
- Docker service deployment completed (Chunk 10)

## Procedure

### For Local Development Setup

#### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

#### 2. Activate Virtual Environment
Activate your Python virtual environment:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

#### 3. Verify Database Connection
Test the database connection with configured settings:
```bash
# Test connection using psql
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB
```

When prompted, enter the password for the PostgreSQL user.

#### 4. Create Database (if not exists)
If the database doesn't exist, create it:
```bash
# Connect to PostgreSQL as postgres user
psql -h localhost -p 5432 -U postgres

# Create the database
CREATE DATABASE reddit08;
\q
```

#### 5. Initialize Data Directories
Create the necessary data directories:
```bash
make data-init
```

This command creates:
- `data/raw/`
- `data/processed/`
- `data/lexicon/`
- `data/cache/`
- `config/`

#### 6. Run Database Initialization
Initialize the database schema:
```bash
make db-init
```

This command runs database migrations to set up the required tables.

#### 7. Verify Database Initialization
Check that the database tables were created:
```bash
# Connect to the database
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB

# List tables
\dt

# Exit
\q
```

### For Docker Deployment

#### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

#### 2. Verify Docker Services
Ensure Docker services are running:
```bash
docker-compose ps
```

#### 3. Check Database Service
Verify the PostgreSQL service is running:
```bash
docker-compose ps postgres
```

#### 4. Initialize Database via Docker
The database should be automatically initialized by the Docker setup. However, if needed, you can run initialization commands:
```bash
# Execute database initialization script
docker-compose exec postgres psql -U user -d reddit08_db -f /docker-entrypoint-initdb.d/init-db.sql
```

#### 5. Verify Database Initialization
Check that the database tables were created:
```bash
# Connect to the database
docker-compose exec postgres psql -U user -d reddit08_db

# List tables
\dt

# Exit
\q
```

## Verification
After completing the above steps, you should have:
- [ ] Database connection verified
- [ ] Database `reddit08` created (if needed)
- [ ] Data directories initialized
- [ ] Database schema initialized
- [ ] Required tables created and verified

## Troubleshooting
If database initialization fails:

1. **Connection failed**:
   - Verify PostgreSQL service is running
   - Check PostgreSQL credentials are correct
   - Ensure PostgreSQL is accepting connections on localhost
   - Check firewall settings

2. **Database doesn't exist**:
   - Create the database manually using `CREATE DATABASE`
   - Verify the database name matches configuration

3. **Permission denied**:
   - Check PostgreSQL user permissions
   - Verify the user has CREATE privileges
   - Check `pg_hba.conf` authentication settings

4. **Migration errors**:
   - Check database connection settings
   - Verify all dependencies are installed
   - Run migrations with verbose output: `alembic upgrade head --verbose`

5. **Table creation failed**:
   - Check for syntax errors in SQL scripts
   - Verify PostgreSQL version compatibility
   - Check available disk space

## Next Steps
Proceed to Chunk 13: Data Directory Setup to ensure all data directories are properly configured.