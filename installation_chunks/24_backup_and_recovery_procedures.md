# Installation Chunk 24: Backup and Recovery Procedures

## Overview
This installation chunk covers backup and recovery procedures for the CRE Intelligence Platform, including data, configuration, and service recovery.

## Prerequisites
- System requirements verification completed (Chunk 01)
- Database initialization completed (Chunk 12)
- Data directory setup completed (Chunk 13)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Database Backup Procedures

#### For PostgreSQL (Local Development)
```bash
# Create database backup
pg_dump -h localhost -p 5432 -U postgres -d reddit08 > backups/reddit08_$(date +%Y%m%d_%H%M%S).sql

# Create compressed backup
pg_dump -h localhost -p 5432 -U postgres -d reddit08 | gzip > backups/reddit08_$(date +%Y%m%d_%H%M%S).sql.gz

# Create backup with custom format (for faster restore)
pg_dump -h localhost -p 5432 -U postgres -d reddit08 -Fc > backups/reddit08_$(date +%Y%m%d_%H%M%S).dump

# Backup specific tables
pg_dump -h localhost -p 5432 -U postgres -d reddit08 -t table_name > backups/table_backup_$(date +%Y%m%d_%H%M%S).sql
```

#### For PostgreSQL (Docker Deployment)
```bash
# Create database backup from Docker container
docker-compose exec postgres pg_dump -U user -d reddit08_db > backups/reddit08_$(date +%Y%m%d_%H%M%S).sql

# Create backup using docker run
docker run --rm \
  --network reddit08-network \
  -v $(pwd)/backups:/backups \
  postgres:15-alpine \
  pg_dump -h postgres -U user -d reddit08_db > /backups/reddit08_$(date +%Y%m%d_%H%M%S).sql
```

### 3. Data Directory Backup Procedures
```bash
# Create backup of data directories
tar -czf backups/data_$(date +%Y%m%d_%H%M%S).tar.gz data/

# Create backup of specific data subdirectories
tar -czf backups/raw_data_$(date +%Y%m%d_%H%M%S).tar.gz data/raw/
tar -czf backups/processed_data_$(date +%Y%m%d_%H%M%S).tar.gz data/processed/
tar -czf backups/lexicon_data_$(date +%Y%m%d_%H%M%S).tar.gz data/lexicon/

# Create backup of logs
tar -czf backups/logs_$(date +%Y%m%d_%H%M%S).tar.gz logs/

# Create backup of configuration
tar -czf backups/config_$(date +%Y%m%d_%H%M%S).tar.gz config/
```

### 4. Configuration Backup Procedures
```bash
# Backup environment files
cp .env backups/env_$(date +%Y%m%d_%H%M%S).env
cp .env.docker backups/env_docker_$(date +%Y%m%d_%H%M%S).env
cp .env.example backups/env_example_$(date +%Y%m%d_%H%M%S).env

# Backup docker-compose configuration
cp docker-compose.yml backups/docker-compose_$(date +%Y%m%d_%H%M%S).yml

# Backup application configuration
cp -r config/ backups/config_$(date +%Y%m%d_%H%M%S)/
```

### 5. Automated Backup Setup

#### For Local Development (using cron)
```bash
# Edit crontab
crontab -e

# Add daily database backup at 2 AM
0 2 * * * cd /path/to/reddit08 && pg_dump -h localhost -p 5432 -U postgres -d reddit08 > backups/reddit08_$(date +\%Y\%m\%d_\%H\%M\%S).sql

# Add weekly data backup on Sundays at 3 AM
0 3 * * 0 cd /path/to/reddit08 && tar -czf backups/data_$(date +\%Y\%m\%d_\%H\%M\%S).tar.gz data/

# Add monthly configuration backup on 1st at 4 AM
0 4 1 * * cd /path/to/reddit08 && cp .env backups/env_$(date +\%Y\%m\%d_\%H\%M\%S).env
```

#### For Docker Deployment (using Docker cron or external scheduler)
```bash
# Create backup script
nano scripts/backup.sh
```

Example backup script:
```bash
#!/bin/bash
cd /app
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump -U user -d reddit08_db > /app/backups/reddit08_${DATE}.sql

# Data directory backup
tar -czf /app/backups/data_${DATE}.tar.gz /app/data/

# Configuration backup
cp /app/.env /app/backups/env_${DATE}.env

# Clean old backups (keep last 30 days)
find /app/backups -name "*.sql" -mtime +30 -delete
find /app/backups -name "*.tar.gz" -mtime +30 -delete
find /app/backups -name "*.env" -mtime +30 -delete
```

Make script executable:
```bash
chmod +x scripts/backup.sh
```

### 6. Database Recovery Procedures

#### For PostgreSQL (Local Development)
```bash
# Restore from SQL backup
psql -h localhost -p 5432 -U postgres -d reddit08 < backups/reddit08_backup.sql

# Restore from compressed backup
gunzip -c backups/reddit08_backup.sql.gz | psql -h localhost -p 5432 -U postgres -d reddit08

# Restore from custom format backup
pg_restore -h localhost -p 5432 -U postgres -d reddit08 backups/reddit08_backup.dump

# Restore specific tables
psql -h localhost -p 5432 -U postgres -d reddit08 < backups/table_backup.sql
```

#### For PostgreSQL (Docker Deployment)
```bash
# Restore database from backup
docker-compose exec -T postgres psql -U user -d reddit08_db < backups/reddit08_backup.sql

# Restore using docker run
docker run --rm \
  --network reddit08-network \
  -v $(pwd)/backups:/backups \
  -i postgres:15-alpine \
  psql -h postgres -U user -d reddit08_db < /backups/reddit08_backup.sql
```

### 7. Data Directory Recovery Procedures
```bash
# Restore data directories from backup
tar -xzf backups/data_backup.tar.gz -C /

# Restore specific data subdirectories
tar -xzf backups/raw_data_backup.tar.gz -C /
tar -xzf backups/processed_data_backup.tar.gz -C /
tar -xzf backups/lexicon_data_backup.tar.gz -C /

# Restore logs (if needed)
tar -xzf backups/logs_backup.tar.gz -C /

# Restore configuration
tar -xzf backups/config_backup.tar.gz -C /
```

### 8. Configuration Recovery Procedures
```bash
# Restore environment file
cp backups/env_backup.env .env

# Restore docker-compose configuration
cp backups/docker-compose_backup.yml docker-compose.yml

# Restore application configuration
cp -r backups/config_backup/ config/
```

### 9. Verify Backup Integrity
```bash
# Test database backup integrity
pg_restore --list backups/reddit08_backup.dump

# Test data backup integrity
tar -tzf backups/data_backup.tar.gz

# Test configuration backup integrity
ls -la backups/env_backup.env
```

### 10. Backup Storage and Security
```bash
# Set proper permissions for backup directory
chmod 700 backups/
chown $USER:$USER backups/

# Encrypt sensitive backups
gpg --symmetric --cipher-algo AES256 backups/reddit08_sensitive_backup.sql

# Decrypt encrypted backups
gpg --decrypt backups/reddit08_sensitive_backup.sql.gpg > reddit08_sensitive_backup.sql

# Store backups in secure location
rsync -av backups/ user@backup-server:/backup/reddit08/
```

### 11. Backup Monitoring and Alerts
```bash
# Create backup verification script
nano scripts/verify_backup.sh
```

Example verification script:
```bash
#!/bin/bash
# Check if backup was created today
if [ -f backups/reddit08_$(date +%Y%m%d)*.sql ]; then
    echo "Database backup successful"
else
    echo "Database backup failed" | mail -s "Backup Alert" admin@example.com
fi

# Check backup file size
if [ $(stat -f%z backups/reddit08_$(date +%Y%m%d)*.sql) -lt 1000 ]; then
    echo "Backup file too small" | mail -s "Backup Alert" admin@example.com
fi
```

## Verification
After completing the above steps, you should have:
- [ ] Database backup procedures established
- [ ] Data directory backup procedures established
- [ ] Configuration backup procedures established
- [ ] Automated backup setup configured
- [ ] Database recovery procedures tested
- [ ] Data directory recovery procedures tested
- [ ] Configuration recovery procedures tested
- [ ] Backup integrity verification procedures
- [ ] Backup storage and security measures
- [ ] Backup monitoring and alerting configured

## Troubleshooting
If backup and recovery issues occur:

1. **Backup fails**:
   - Check disk space: `df -h`
   - Verify database connectivity
   - Check file permissions
   - Review backup script errors

2. **Restore fails**:
   - Verify backup file integrity
   - Check database version compatibility
   - Review restore log errors
   - Ensure sufficient disk space

3. **Permission errors**:
   - Check user permissions
   - Verify file ownership
   - Review directory permissions
   - Check SELinux/AppArmor settings

4. **Network issues** (Docker):
   - Verify Docker network connectivity
   - Check container status
   - Review network configuration
   - Test container-to-container communication

5. **Storage issues**:
   - Monitor disk space usage
   - Check backup retention policies
   - Review storage quotas
   - Optimize backup compression

## Next Steps
Proceed to Chunk 25: Monitoring Setup to configure comprehensive monitoring for the CRE Intelligence Platform.