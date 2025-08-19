# Installation Chunk 04: PostgreSQL Installation and Setup

## Overview
This installation chunk installs and configures PostgreSQL for local development of the CRE Intelligence Platform.

## Prerequisites
- System requirements verification completed (Chunk 01)
- Administrative access to install PostgreSQL

## Procedure

### 1. Install PostgreSQL
#### Windows
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer with default settings
3. During installation, note the password for the `postgres` user
4. Accept default port (5432)

#### macOS
Using Homebrew:
```bash
brew install postgresql
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### CentOS/RHEL/Fedora
```bash
sudo yum install postgresql-server postgresql-contrib
# or for newer versions:
sudo dnf install postgresql-server postgresql-contrib
```

### 2. Start PostgreSQL Service
#### Windows
PostgreSQL service should start automatically after installation.

#### macOS
```bash
brew services start postgresql
```

#### Linux
```bash
# Ubuntu/Debian
sudo systemctl start postgresql
sudo systemctl enable postgresql

# CentOS/RHEL/Fedora
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 3. Verify PostgreSQL Installation
Check PostgreSQL version:
```bash
psql --version
```

Expected output: PostgreSQL version 12 or higher

### 4. Configure PostgreSQL User
#### Windows/macOS/Linux
Switch to the postgres user and access PostgreSQL:
```bash
sudo -u postgres psql
```

Set a password for the postgres user:
```sql
ALTER USER postgres PASSWORD 'your_secure_password';
\q
```

### 5. Test PostgreSQL Connection
Connect to PostgreSQL with the postgres user:
```bash
psql -U postgres -h localhost -p 5432
```

When prompted, enter the password you set.

List databases:
```sql
\l
```

Exit PostgreSQL:
```sql
\q
```

### 6. Create Database for CRE Intelligence Platform
Connect to PostgreSQL:
```bash
psql -U postgres -h localhost -p 5432
```

Create the database:
```sql
CREATE DATABASE reddit08;
```

Verify the database was created:
```sql
\l
```

Exit PostgreSQL:
```sql
\q
```

## Verification
After completing the above steps, you should have:
- [ ] PostgreSQL 12 or higher installed
- [ ] PostgreSQL service running
- [ ] PostgreSQL user configured with password
- [ ] Connection to PostgreSQL verified
- [ ] Database `reddit08` created

## Troubleshooting
If PostgreSQL is not working:

1. **Service not starting**:
   - Check if port 5432 is already in use
   - Verify PostgreSQL configuration files
   - Check service status: `sudo systemctl status postgresql`

2. **Connection refused**:
   - Ensure PostgreSQL is listening on localhost
   - Check `postgresql.conf` for `listen_addresses`
   - Check `pg_hba.conf` for authentication settings

3. **Authentication failed**:
   - Verify password is correct
   - Check `pg_hba.conf` authentication method
   - Ensure user exists: `SELECT usename FROM pg_user;`

## Next Steps
Proceed to Chunk 05: Redis Installation and Setup or Chunk 07: Repository Cloning.