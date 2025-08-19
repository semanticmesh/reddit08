#!/usr/bin/env python3
"""
CRE Intelligence Platform Setup Script
This script sets up the basic environment and runs the application
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def create_directories():
    """Create necessary directories for the application"""
    directories = ['data', 'logs', 'data/raw', 'data/processed', 'data/cache']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def setup_database():
    """Set up the SQLite database"""
    db_path = "reddit08.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create basic tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            post_id TEXT NOT NULL,
            title TEXT,
            content TEXT,
            author TEXT,
            created_at TIMESTAMP,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_url TEXT,
            metadata TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT UNIQUE NOT NULL,
            category TEXT,
            frequency INTEGER DEFAULT 1,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database setup completed")

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=False)
    print("Dependencies installation completed")

def run_application():
    """Run the FastAPI application"""
    print("Starting the CRE Intelligence Platform...")
    print("Access the API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    # Set environment variables
    os.environ.setdefault('PYTHONPATH', str(Path.cwd()))
    
    # Run the application
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "src.mcp.fastapi_app.main:app", 
        "--reload", 
        "--port", "8000"
    ])

if __name__ == "__main__":
    print("=== CRE Intelligence Platform Setup ===")
    
    # Check if we're in the correct directory
    if not Path("requirements.txt").exists():
        print("Error: requirements.txt not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Setup steps
    create_directories()
    setup_database()
    install_dependencies()
    
    print("\n=== Setup Complete ===")
    print("Starting the application...")
    
    try:
        run_application()
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)
