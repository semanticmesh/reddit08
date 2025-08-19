# Installation Chunk 11: Local Development Dependency Installation

## Overview
This installation chunk installs the Python dependencies for local development of the CRE Intelligence Platform.

## Prerequisites
- Python virtual environment setup completed (Chunk 03)
- Repository cloned (Chunk 07)
- Local development environment configuration completed (Chunk 09)

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

### 3. Install Core Dependencies
Install the core Python dependencies:
```bash
pip install -r requirements.txt
```

This command will install all packages listed in the `requirements.txt` file.

### 4. Install Development Dependencies
Install development dependencies and extras:
```bash
pip install -e ".[dev]"
```

This command will:
- Install the package in development mode
- Install development dependencies
- Install pre-commit hooks

### 5. Install Pre-commit Hooks
Set up pre-commit hooks for code quality:
```bash
pre-commit install
```

This will install hooks that run automatically before each commit to check code quality.

### 6. Verify Installation
Check that all dependencies are installed:
```bash
# List installed packages
pip list

# Check specific packages
pip show fastapi uvicorn pandas numpy
```

### 7. Test Installation
Run a basic import test to verify dependencies work:
```bash
python -c "import fastapi; import uvicorn; import pandas; print('All dependencies imported successfully')"
```

### 8. Run Code Quality Checks
Run the code quality checks to ensure everything is set up correctly:
```bash
# Run linter checks
make lint

# Run format checks
make format-check
```

### 9. Run Tests
Run the test suite to verify everything works:
```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration
```

## Verification
After completing the above steps, you should have:
- [ ] Core Python dependencies installed
- [ ] Development dependencies installed
- [ ] Pre-commit hooks installed
- [ ] Dependencies verified with pip list
- [ ] Basic import test successful
- [ ] Code quality checks pass
- [ ] Tests run successfully

## Troubleshooting
If dependency installation fails:

1. **Package installation errors**:
   - Ensure you're in the virtual environment
   - Check internet connection
   - Try upgrading pip: `pip install --upgrade pip`

2. **Compilation errors**:
   - Install build tools:
     - Windows: Install Microsoft C++ Build Tools
     - macOS: Install Xcode Command Line Tools
     - Linux: `sudo apt install build-essential`

3. **Permission errors**:
   - Ensure you're in the virtual environment
   - Check that you have write permissions to the virtual environment directory

4. **Version conflicts**:
   - Try installing with `--force-reinstall`: `pip install --force-reinstall -r requirements.txt`
   - Check `requirements_compatible.txt` for compatible versions

5. **Pre-commit hook issues**:
   - Run `pre-commit install` again
   - Check that pre-commit is installed: `pip show pre-commit`

## Next Steps
Proceed to Chunk 12: Database Initialization to set up the database for the CRE Intelligence Platform.