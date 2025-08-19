#!/usr/bin/env python3
"""
BMAD Runtime Server
Main entry point for the BMAD runtime system.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the bmad directory to the path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bmad.src.runtime.server_manager import ServerManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bmad_runtime.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the BMAD Runtime Server."""
    logger.info("Starting BMAD Runtime Server...")
    
    try:
        # Initialize the server manager
        server_manager = ServerManager()
        
        # Start the server
        await server_manager.start()
        
        logger.info("BMAD Runtime Server started successfully")
        
        # Keep the server running
        await server_manager.wait_for_shutdown()
        
    except Exception as e:
        logger.error(f"Error starting BMAD Runtime Server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
