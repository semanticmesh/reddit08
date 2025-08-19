# Installation Chunk 16: Local Development Server Startup

## Overview
This installation chunk starts the CRE Intelligence Platform server in local development mode.

## Prerequisites
- Python virtual environment setup completed (Chunk 03)
- Local development dependency installation completed (Chunk 11)
- Local development environment configuration completed (Chunk 09)
- Database initialization completed (Chunk 12)
- API key configuration completed (Chunk 14)

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

### 3. Verify Environment Configuration
Check that environment variables are properly set:
```bash
# Check key environment variables
echo $POSTGRES_HOST
echo $POSTGRES_DB
echo $POSTGRES_USER
```

### 4. Start Development Server
Start the FastAPI development server with auto-reload:
```bash
make serve
```

Alternatively, start the server directly:
```bash
uvicorn src.mcp.fastapi_app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Monitor Server Startup
Watch the server startup logs for any errors:
```bash
# The server should show output similar to:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process [pid] using watchgod
# INFO:     Started server process [pid]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

### 6. Test Server Accessibility
Test that the server is accessible:
```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response: {"status":"healthy"}
```

### 7. Access API Documentation
Open the API documentation in your browser:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

### 8. Test API Endpoints
Test a few key API endpoints:
```bash
# Test basic API endpoint
curl http://localhost:8000/

# Test version endpoint
curl http://localhost:8000/version
```

### 9. Verify Auto-reload Functionality
Test that the auto-reload feature works:
1. Make a small change to a Python file in the `src/` directory
2. Save the file
3. Observe the server automatically restart in the terminal

### 10. Check Server Logs
Monitor the server logs for any warnings or errors:
```bash
# If started with make serve, logs will appear in the terminal
# If started directly, you can redirect logs to a file:
uvicorn src.mcp.fastapi_app.main:app --reload --host 0.0.0.0 --port 8000 > server.log 2>&1
```

## Verification
After completing the above steps, you should have:
- [ ] Development server started successfully
- [ ] Server accessible at http://localhost:8000
- [ ] Health endpoint returning healthy status
- [ ] API documentation accessible
- [ ] Key API endpoints responding correctly
- [ ] Auto-reload functionality working
- [ ] No critical errors in server logs

## Troubleshooting
If the development server fails to start:

1. **Port already in use**:
   - Check if another process is using port 8000: `netstat -an | grep :8000`
   - Kill the process or use a different port: `uvicorn src.mcp.fastapi_app.main:app --reload --port 8001`

2. **Import errors**:
   - Verify virtual environment is activated
   - Check that all dependencies are installed: `pip list`
   - Reinstall dependencies: `pip install -r requirements.txt`

3. **Database connection errors**:
   - Verify PostgreSQL is running
   - Check database credentials in .env
   - Test database connection manually: `psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB`

4. **API key errors**:
   - Verify all required API keys are set in .env
   - Check for typos in environment variable names
   - Test API keys individually

5. **Module not found errors**:
   - Ensure you're in the project root directory
   - Check PYTHONPATH: `echo $PYTHONPATH`
   - Add project root to PYTHONPATH if needed: `export PYTHONPATH=/path/to/reddit08:$PYTHONPATH`

6. **Permission errors**:
   - Ensure you have read/write permissions to project directory
   - Check file permissions: `ls -la`

## Next Steps
Proceed to Chunk 17: Service Health Checks to perform comprehensive health verification.