# Installation Chunk 19: Data Source Configuration

## Overview
This installation chunk configures the data sources for the CRE Intelligence Platform, including Reddit, news APIs, and other data providers.

## Prerequisites
- Repository cloned (Chunk 07)
- API key configuration completed (Chunk 14)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Configure Reddit Data Sources
Edit the Reddit configuration file:
```bash
# Create or edit the Reddit configuration file
nano config/reddit_sources.json
# or
code config/reddit_sources.json
# or
vim config/reddit_sources.json
```

Add or update Reddit subreddits and configuration:
```json
{
  "subreddits": [
    "realestate",
    "commercialrealestate",
    "realestateinvesting",
    "landlord",
    "apartments",
    "RealEstateTechnology",
    "PropertyManagement",
    "CommercialRealEstate",
    "RealEstatePhotography"
  ],
  "post_limit": 1000,
  "comment_depth": 5,
  "sort_type": "new",
  "time_filter": "week"
}
```

### 3. Configure News Data Sources
Edit the news configuration file:
```bash
# Create or edit the news configuration file
nano config/news_sources.json
# or
code config/news_sources.json
# or
vim config/news_sources.json
```

Add or update news sources and configuration:
```json
{
  "sources": [
    "reuters",
    "bloomberg",
    "cnbc",
    "forbes",
    "wallstreetjournal",
    "realestateworld",
    "propertyweek",
    "commercialobserver"
  ],
  "categories": [
    "business",
    "real-estate",
    "finance",
    "economy"
  ],
  "keywords": [
    "commercial real estate",
    "office space",
    "retail property",
    "industrial real estate",
    "residential real estate",
    "property management",
    "real estate investment"
  ],
  "article_limit": 100
}
```

### 4. Configure Twitter Data Sources (if applicable)
Edit the Twitter configuration file:
```bash
# Create or edit the Twitter configuration file
nano config/twitter_sources.json
# or
code config/twitter_sources.json
# or
vim config/twitter_sources.json
```

Add or update Twitter configuration:
```json
{
  "hashtags": [
    "#CommercialRealEstate",
    "#RealEstate",
    "#PropertyManagement",
    "#RealEstateInvesting",
    "#OfficeSpace",
    "#RetailProperty"
  ],
  "keywords": [
    "commercial real estate",
    "office leasing",
    "property management",
    "real estate investment"
  ],
  "user_accounts": [
    "realestate",
    "commercialre",
    "propertyweek",
    "realestatemag"
  ],
  "tweet_limit": 500,
  "time_filter": "week"
}
```

### 5. Configure Data Collection Schedules
Edit the data collection schedule configuration:
```bash
# Create or edit the schedule configuration file
nano config/data_collection_schedule.json
# or
code config/data_collection_schedule.json
# or
vim config/data_collection_schedule.json
```

Add or update data collection schedules:
```json
{
  "reddit_collection": {
    "schedule": "0 */6 * * *",
    "description": "Collect Reddit data every 6 hours"
  },
  "news_collection": {
    "schedule": "0 9 * * *",
    "description": "Collect news data daily at 9 AM"
  },
  "twitter_collection": {
    "schedule": "0 */4 * * *",
    "description": "Collect Twitter data every 4 hours"
  },
  "data_processing": {
    "schedule": "30 */6 * * *",
    "description": "Process collected data every 6 hours"
  }
}
```

### 6. Configure Data Filtering Rules
Edit the data filtering configuration:
```bash
# Create or edit the filtering configuration file
nano config/data_filters.json
# or
code config/data_filters.json
# or
vim config/data_filters.json
```

Add or update data filtering rules:
```json
{
  "reddit_filters": {
    "min_upvotes": 5,
    "exclude_keywords": [
      "spam",
      "self-promotion",
      "advertisement"
    ],
    "required_keywords": [
      "commercial",
      "real estate",
      "property",
      "office",
      "retail",
      "industrial"
    ]
  },
  "news_filters": {
    "min_word_count": 200,
    "exclude_sources": [
      "tabloid-news"
    ],
    "required_categories": [
      "business",
      "real-estate",
      "finance"
    ]
  },
  "twitter_filters": {
    "min_retweets": 2,
    "exclude_keywords": [
      "promotional",
      "ad",
      "sponsored"
    ],
    "required_keywords": [
      "commercial real estate",
      "office space",
      "property management"
    ]
  }
}
```

### 7. Verify Configuration Files
Check that all configuration files are properly formatted:
```bash
# Verify JSON syntax
python -m json.tool config/reddit_sources.json
python -m json.tool config/news_sources.json
python -m json.tool config/twitter_sources.json
python -m json.tool config/data_collection_schedule.json
python -m json.tool config/data_filters.json
```

### 8. Test Data Source Configuration
Test that the configuration files can be loaded by the application:
```bash
# Test configuration loading
python src/scripts/test_config.py

# Or use Makefile command if available
make test-config
```

### 9. Validate Data Source Access
Test access to configured data sources:
```bash
# Test Reddit access
python src/scripts/test_reddit_access.py

# Test news API access
python src/scripts/test_news_access.py

# Test Twitter access (if applicable)
python src/scripts/test_twitter_access.py
```

### 10. Set Configuration File Permissions
Set appropriate permissions for configuration files:
```bash
chmod 644 config/*.json
```

## Verification
After completing the above steps, you should have:
- [ ] Reddit data sources configured
- [ ] News data sources configured
- [ ] Twitter data sources configured (if applicable)
- [ ] Data collection schedules configured
- [ ] Data filtering rules configured
- [ ] Configuration files properly formatted
- [ ] Configuration files loadable by application
- [ ] Data source access validated
- [ ] Configuration files secured with appropriate permissions

## Troubleshooting
If data source configuration fails:

1. **JSON syntax errors**:
   - Use a JSON validator to check syntax
   - Ensure proper use of commas, brackets, and quotes
   - Check for trailing commas

2. **Configuration file not found**:
   - Verify file paths are correct
   - Check that files exist in the config directory
   - Ensure proper file permissions

3. **Data source access denied**:
   - Verify API keys are correct
   - Check data source account permissions
   - Test API access manually

4. **Invalid configuration values**:
   - Check value types (string, number, boolean)
   - Verify required fields are present
   - Check for valid enum values

5. **Schedule format errors**:
   - Verify cron schedule format
   - Use a cron expression validator
   - Test schedule expressions

## Next Steps
Proceed to Chunk 20: Lexicon Initialization to set up the vocabulary and classification data for the CRE Intelligence Platform.