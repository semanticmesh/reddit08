# Installation Chunk 20: Lexicon Initialization

## Overview
This installation chunk initializes the vocabulary and classification data (lexicon) for the CRE Intelligence Platform using TF-IDF phrase mining.

## Prerequisites
- Repository cloned (Chunk 07)
- Data directory setup completed (Chunk 13)
- Data source configuration completed (Chunk 19)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Activate Virtual Environment (for local development)
If using local development setup:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Prepare Lexicon Directory
Ensure the lexicon directory exists and is writable:
```bash
# Check if lexicon directory exists
ls -la data/lexicon/

# Create directory if it doesn't exist
mkdir -p data/lexicon/

# Set proper permissions
chmod 755 data/lexicon/
```

### 4. Initialize Lexicon with TF-IDF Phrase Mining
Run the TF-IDF phrase mining script to initialize the lexicon:
```bash
# Run lexicon initialization with default parameters
python src/scripts/refresh_tfidf_via_mcp.py

# Or run with specific parameters
python src/scripts/refresh_tfidf_via_mcp.py --corpus last_month --top-k 150

# For more control, specify additional options
python src/scripts/refresh_tfidf_via_mcp.py \
  --corpus last_quarter \
  --top-k 200 \
  --min-freq 5 \
  --max-ngram 3
```

### 5. Monitor Lexicon Initialization Process
Watch the initialization process for any errors or warnings:
```bash
# The script will show output similar to:
# Loading corpus data...
# Processing 10,000 documents...
# Extracting phrases...
# Generating TF-IDF scores...
# Saving lexicon to data/lexicon/...
# Lexicon initialization complete!
```

### 6. Verify Lexicon Files
Check that lexicon files were created successfully:
```bash
# List lexicon files
ls -la data/lexicon/

# Check specific lexicon files
ls -la data/lexicon/tfidf_lexicon.json
ls -la data/lexicon/phrase_clusters.json
ls -la data/lexicon/category_keywords.json
```

### 7. Validate Lexicon Content
Examine the lexicon content to ensure it was generated correctly:
```bash
# View lexicon content (first 20 lines)
head -n 20 data/lexicon/tfidf_lexicon.json

# Check JSON syntax
python -m json.tool data/lexicon/tfidf_lexicon.json > /dev/null && echo "Valid JSON"

# View phrase clusters
head -n 20 data/lexicon/phrase_clusters.json
```

### 8. Test Lexicon Functionality
Test that the lexicon can be loaded and used by the application:
```bash
# Run lexicon test script
python src/scripts/test_lexicon.py

# Or use Makefile command if available
make test-lexicon
```

### 9. Update Lexicon Configuration
If needed, update the lexicon configuration:
```bash
# Edit lexicon configuration file
nano config/lexicon_config.json
# or
code config/lexicon_config.json
# or
vim config/lexicon_config.json
```

Example lexicon configuration:
```json
{
  "tfidf_settings": {
    "max_features": 10000,
    "ngram_range": [1, 3],
    "min_df": 2,
    "max_df": 0.95
  },
  "phrase_mining": {
    "min_phrase_freq": 5,
    "max_phrase_length": 5,
    "threshold": 0.7
  },
  "categories": [
    "market_analysis",
    "property_management",
    "investment",
    "tenant_relations",
    "facility_management"
  ]
}
```

### 10. Set Lexicon File Permissions
Set appropriate permissions for lexicon files:
```bash
chmod 644 data/lexicon/*.json
```

### 11. Schedule Regular Lexicon Updates
Set up scheduled updates for the lexicon:
```bash
# Add to crontab for weekly updates
crontab -e

# Add this line for weekly lexicon updates on Sundays at 2 AM
0 2 * * 0 cd /path/to/reddit08 && python src/scripts/refresh_tfidf_via_mcp.py --corpus last_week --top-k 150
```

For Docker deployment:
```bash
# Use Docker cron or external scheduler
# Example docker-compose configuration for scheduled tasks
```

## Verification
After completing the above steps, you should have:
- [ ] Lexicon directory created and accessible
- [ ] TF-IDF lexicon generated successfully
- [ ] Phrase clusters created
- [ ] Category keywords identified
- [ ] Lexicon files properly formatted
- [ ] Lexicon loadable by application
- [ ] Lexicon functionality tested
- [ ] Lexicon configuration updated (if needed)
- [ ] Lexicon files secured with appropriate permissions
- [ ] Regular updates scheduled (optional)

## Troubleshooting
If lexicon initialization fails:

1. **Insufficient data**:
   - Ensure data has been collected from configured sources
   - Check that data directories contain content
   - Run data collection scripts first

2. **Memory errors**:
   - Reduce the corpus size: `--corpus last_week` instead of `last_quarter`
   - Decrease `--top-k` value
   - Increase system memory or use cloud resources

3. **File permission errors**:
   - Check directory permissions: `ls -la data/lexicon/`
   - Ensure write access to lexicon directory
   - Run with appropriate privileges

4. **JSON parsing errors**:
   - Validate JSON syntax in configuration files
   - Check for encoding issues
   - Verify file integrity

5. **TF-IDF computation errors**:
   - Check sklearn installation
   - Verify data format and preprocessing
   - Reduce ngram range or max_features

6. **Phrase mining failures**:
   - Check NLTK installation and data
   - Verify minimum frequency thresholds
   - Adjust phrase mining parameters

## Next Steps
Proceed to Chunk 21: Scheduled Jobs Setup to configure automated data collection and processing tasks.