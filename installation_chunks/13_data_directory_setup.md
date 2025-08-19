# Installation Chunk 13: Data Directory Setup

## Overview
This installation chunk sets up the required data directories for the CRE Intelligence Platform.

## Prerequisites
- Repository cloned (Chunk 07)
- Database initialization completed (Chunk 12)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Create Data Directories
Create the required data directories using the Makefile command:
```bash
make data-init
```

This command creates the following directory structure:
- `data/`
  - `raw/` - Raw collected data from Reddit and other sources
  - `processed/` - Processed and analyzed data
  - `cache/` - Redis cache and temporary files
  - `lexicon/` - Vocabulary and classification data
  - `logs/` - Application logs
- `config/` - Configuration files

### 3. Verify Directory Creation
Check that all directories were created:
```bash
# List data directories
ls -la data/

# Check individual directories
ls -la data/raw/
ls -la data/processed/
ls -la data/cache/
ls -la data/lexicon/
ls -la data/logs/
ls -la config/
```

### 4. Set Directory Permissions
Ensure proper permissions for data directories:
```bash
# Set ownership (Linux/macOS)
sudo chown -R $USER:$USER data/
sudo chown -R $USER:$USER config/

# Set permissions
chmod -R 755 data/
chmod -R 755 config/
```

On Windows, ensure your user has full control of these directories.

### 5. Verify Directory Structure
Confirm the complete directory structure:
```bash
tree data/
tree config/
```

Expected structure:
```
data/
├── raw/
├── processed/
├── cache/
├── lexicon/
└── logs/
config/
```

### 6. Test Directory Write Access
Test that the application can write to these directories:
```bash
# Test write access to each directory
touch data/raw/test.txt && rm data/raw/test.txt
touch data/processed/test.txt && rm data/processed/test.txt
touch data/cache/test.txt && rm data/cache/test.txt
touch data/lexicon/test.txt && rm data/lexicon/test.txt
touch data/logs/test.txt && rm data/logs/test.txt
touch config/test.txt && rm config/test.txt
```

### 7. Configure Directory Settings (if needed)
If using Docker, verify that the volume mappings in `docker-compose.yml` match your directory structure:
```yaml
volumes:
  - ./data:/app/data
  - ./logs:/app/logs
  - ./config:/app/config
```

### 8. Clean Data Directories (if needed)
If you need to clean the data directories:
```bash
make data-clean
```

This command removes all files from the data directories but keeps the directory structure.

## Verification
After completing the above steps, you should have:
- [ ] Data directory structure created
- [ ] All required subdirectories created
- [ ] Proper permissions set
- [ ] Directory write access verified
- [ ] Directory structure matches expected layout

## Troubleshooting
If data directory setup fails:

1. **Permission denied**:
   - Check user permissions on parent directory
   - Ensure you have write access to the project directory
   - Run with elevated privileges if needed (Linux/macOS)

2. **Directory already exists**:
   - Remove existing directories if they conflict
   - Use `make data-clean` to clean existing directories

3. **Disk space issues**:
   - Check available disk space: `df -h`
   - Free up space if needed

4. **Path issues**:
   - Ensure you're in the correct project directory
   - Check that the Makefile exists and is executable

5. **Makefile not found**:
   - Verify the Makefile exists in the project root
   - Install make if not available:
     - Ubuntu/Debian: `sudo apt install make`
     - macOS: `brew install make`
     - Windows: Install Git for Windows which includes make

## Next Steps
Proceed to Chunk 14: API Key Configuration to set up the required API keys for the CRE Intelligence Platform.