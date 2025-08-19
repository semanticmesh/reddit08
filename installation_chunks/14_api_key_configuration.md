# Installation Chunk 14: API Key Configuration

## Overview
This installation chunk configures the required API keys for the CRE Intelligence Platform to access external services.

## Prerequisites
- Repository cloned (Chunk 07)
- Environment configuration completed (Chunk 08 for Docker or Chunk 09 for local development)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Identify Required API Keys
The CRE Intelligence Platform requires the following API keys:

1. **OpenAI API Key** - For AI-powered intelligence analysis
2. **Reddit API Credentials** - For accessing Reddit data
   - Client ID
   - Client Secret
3. **News API Key** - For news data integration (optional)
4. **Twitter Bearer Token** - For Twitter data integration (optional)

### 3. Obtain API Keys

#### OpenAI API Key
1. Go to https://platform.openai.com/
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new secret key
5. Copy the key for later use

#### Reddit API Credentials
1. Go to https://www.reddit.com/prefs/apps
2. Sign up or log in to your Reddit account
3. Click "Create App" or "Create Another App"
4. Fill in the form:
   - Name: CRE Intelligence Platform
   - App type: Select "script"
   - Description: Commercial Real Estate Intelligence Platform
   - About URL: (leave blank)
   - Redirect URI: http://localhost:8000/callback
5. Click "Create app"
6. Copy the Client ID (under the app name) and Client Secret

#### News API Key (Optional)
1. Go to https://newsapi.org/
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Copy your API key

#### Twitter Bearer Token (Optional)
1. Go to https://developer.twitter.com/
2. Apply for a developer account
3. Create a new app
4. Navigate to the app's "Keys and tokens" section
5. Generate a Bearer Token
6. Copy the token

### 4. Configure API Keys for Docker Deployment
Edit the `.env` file:
```bash
# Open the file in your preferred editor
nano .env
# or
code .env
# or
vim .env
```

Add or update the following lines:
```env
# API Keys - IMPORTANT: Set these with real values
OPENAI_API_KEY=your_openai_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
NEWS_API_KEY=your_news_api_key_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
```

### 5. Configure API Keys for Local Development
Edit the `.env` file:
```bash
# Open the file in your preferred editor
nano .env
# or
code .env
# or
vim .env
```

Add the API keys to your local environment file. For local development, you might also need to set:
```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Reddit API Credentials
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here

# Optional API Keys
NEWS_API_KEY=your_news_api_key_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
```

### 6. Verify API Key Configuration
Check that API keys are properly set:
```bash
# For Docker deployment
grep -E "(OPENAI_API_KEY|REDDIT_CLIENT_ID|REDDIT_CLIENT_SECRET)" .env

# For local development
grep -E "(OPENAI_API_KEY|REDDIT_CLIENT_ID|REDDIT_CLIENT_SECRET)" .env
```

### 7. Test API Key Functionality
Test that the API keys work correctly:

#### Test OpenAI API Key
```bash
# Test using curl
curl -X POST https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json"
```

#### Test Reddit API Credentials
```bash
# Test using curl
curl -X POST https://www.reddit.com/api/v1/access_token \
  -H "User-Agent: CRE Intelligence Platform" \
  -u "$REDDIT_CLIENT_ID:$REDDIT_CLIENT_SECRET" \
  -d "grant_type=client_credentials"
```

### 8. Secure API Keys
Set appropriate permissions for the environment file:
```bash
chmod 600 .env
```

## Verification
After completing the above steps, you should have:
- [ ] OpenAI API key obtained and configured
- [ ] Reddit API credentials (Client ID and Client Secret) obtained and configured
- [ ] News API key obtained and configured (optional)
- [ ] Twitter Bearer Token obtained and configured (optional)
- [ ] API keys added to environment file
- [ ] API key functionality tested
- [ ] Environment file secured with appropriate permissions

## Troubleshooting
If API key configuration fails:

1. **Invalid API key**:
   - Verify the API key is correct and active
   - Check for extra spaces or characters
   - Regenerate the API key if needed

2. **Reddit API authentication failed**:
   - Verify Client ID and Client Secret are correct
   - Check that the Reddit app is configured as "script" type
   - Ensure the User-Agent header is set correctly

3. **OpenAI API access denied**:
   - Check that your OpenAI account has API access
   - Verify billing information is set up
   - Check API key quota and limits

4. **Environment variables not loading**:
   - Verify the environment file is in the correct location
   - Check that the application loads environment variables correctly
   - Restart services after updating API keys

5. **Permission issues**:
   - Check file permissions: `ls -l .env`
   - Ensure the file is readable by the application

## Next Steps
For Docker deployment, proceed to Chunk 15: Docker Service Verification.

For local development, proceed to Chunk 16: Local Development Server Startup.