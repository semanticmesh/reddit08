# Installation Chunk 03: Python Virtual Environment Setup

## Overview
This installation chunk sets up a Python virtual environment for local development of the CRE Intelligence Platform.

## Prerequisites
- System requirements verification completed (Chunk 01)
- Python 3.8 or higher installed

## Procedure

### 1. Create Virtual Environment
Navigate to your project directory (or where you plan to clone the repository):
```bash
# Create a new directory for the project (if needed)
mkdir cre-intelligence-platform
cd cre-intelligence-platform

# Create virtual environment
python -m venv venv
```

On Windows, you might need to use:
```bash
python -m venv venv
```

### 2. Activate Virtual Environment
On Windows:
```bash
# Command Prompt
venv\Scripts\activate

# PowerShell
venv\Scripts\Activate.ps1
```

On macOS/Linux:
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your command prompt, indicating the virtual environment is active.

### 3. Upgrade pip
Ensure you have the latest version of pip:
```bash
python -m pip install --upgrade pip
```

### 4. Verify Virtual Environment
Check that you're using the virtual environment's Python:
```bash
which python
# On Windows: where python
```

The output should point to your virtual environment directory.

Check pip version:
```bash
pip --version
```

### 5. Install Basic Development Tools
Install some essential development tools:
```bash
pip install wheel
```

## Verification
After completing the above steps, you should have:
- [ ] Virtual environment created
- [ ] Virtual environment activated
- [ ] pip upgraded to latest version
- [ ] Basic development tools installed

## Troubleshooting
If you encounter issues:

1. **Activation fails on Windows PowerShell**:
   ```bash
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Python command not found**:
   - Ensure Python is in your PATH
   - Try using `python3` instead of `python`

3. **Permission errors**:
   - Run command prompt/terminal as administrator
   - On Windows, try using `py -m venv venv`

## Next Steps
Proceed to:
- Chunk 04: PostgreSQL Installation and Setup
- Chunk 05: Redis Installation and Setup
- Chunk 06: Git Installation Verification
- Chunk 07: Repository Cloning

Note: For Docker deployment, you can skip Chunks 04 and 05 as database services will be containerized.