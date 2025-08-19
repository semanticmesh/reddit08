# Installation Chunk 05: Redis Installation and Setup

## Overview
This installation chunk installs and configures Redis for local development of the CRE Intelligence Platform.

## Prerequisites
- System requirements verification completed (Chunk 01)
- Administrative access to install Redis

## Procedure

### 1. Install Redis
#### Windows
Option 1: Using Chocolatey
```bash
choco install redis
```

Option 2: Download from https://github.com/microsoftarchive/redis/releases
1. Download Redis-x64-*.zip
2. Extract to a folder (e.g., C:\Redis)
3. Add the folder to your system PATH

Option 3: Using Windows Subsystem for Linux (WSL)
```bash
sudo apt update
sudo apt install redis-server
```

#### macOS
Using Homebrew:
```bash
brew install redis
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install redis-server
```

#### CentOS/RHEL/Fedora
```bash
sudo yum install redis
# or for newer versions:
sudo dnf install redis
```

### 2. Start Redis Service
#### Windows
If installed via Chocolatey or manually:
```bash
redis-server
```

If using WSL:
```bash
sudo service redis-server start
```

#### macOS
Using Homebrew:
```bash
brew services start redis
```

#### Linux
```bash
# Ubuntu/Debian
sudo systemctl start redis
sudo systemctl enable redis

# CentOS/RHEL/Fedora
sudo systemctl start redis
sudo systemctl enable redis
```

### 3. Verify Redis Installation
Check Redis version:
```bash
redis-server --version
```

Expected output: Redis server version 6.0 or higher

### 4. Test Redis Connection
Connect to Redis CLI:
```bash
redis-cli
```

Test the connection:
```bash
ping
```

Expected output: PONG

Set a test key:
```bash
set test "CRE Intelligence Platform"
get test
```

Expected output: "CRE Intelligence Platform"

Exit Redis CLI:
```bash
exit
```

### 5. Configure Redis (Optional)
#### Basic Configuration
Edit the Redis configuration file:
- Windows: redis.windows.conf (in Redis installation directory)
- macOS: /usr/local/etc/redis.conf
- Linux: /etc/redis/redis.conf

Common settings to adjust:
```conf
# Bind to localhost only for security
bind 127.0.0.1

# Set a password (uncomment and set)
# requirepass your_strong_password_here

# Memory management
maxmemory 256mb
maxmemory-policy allkeys-lru
```

After making changes, restart Redis service.

### 6. Verify Redis Service Status
#### Windows
```bash
tasklist | findstr redis
```

#### macOS/Linux
```bash
sudo systemctl status redis
```

## Verification
After completing the above steps, you should have:
- [ ] Redis 6.0 or higher installed
- [ ] Redis service running
- [ ] Connection to Redis verified with ping command
- [ ] Test key-value pair successfully set and retrieved

## Troubleshooting
If Redis is not working:

1. **Service not starting**:
   - Check if port 6379 is already in use
   - Verify Redis configuration files
   - Check service status: `sudo systemctl status redis`

2. **Connection refused**:
   - Ensure Redis is listening on localhost
   - Check `bind` setting in redis.conf
   - Verify firewall settings

3. **Authentication failed**:
   - If password is set, use: `redis-cli -a your_password`
   - Check `requirepass` setting in redis.conf

## Next Steps
Proceed to Chunk 06: Git Installation Verification or Chunk 07: Repository Cloning.