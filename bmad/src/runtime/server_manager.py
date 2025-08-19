"""
BMAD Server Manager
Manages the overall server lifecycle, configuration, and resource coordination.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .server import RuntimeServer, RuntimeConfig


@dataclass
class ServerManagerConfig:
    """Configuration for the server manager."""
    host: str = "localhost"
    port: int = 8080
    max_concurrent_stories: int = 10
    story_timeout: int = 300
    enable_logging: bool = True
    log_level: str = "INFO"
    log_file: str = "logs/bmad_runtime.log"


class ServerManager:
    """Main server manager class that coordinates the BMAD runtime server."""
    
    def __init__(self, config: Optional[ServerManagerConfig] = None):
        """Initialize the server manager.
        
        Args:
            config: Configuration for the server manager. If None, default configuration is used.
        """
        self.config = config or ServerManagerConfig()
        self.logger = self._setup_logging()
        self.runtime_server: Optional[RuntimeServer] = None
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger(__name__)
        
        if self.config.enable_logging:
            # Create logs directory if it doesn't exist
            import os
            os.makedirs(os.path.dirname(self.config.log_file), exist_ok=True)
            
            # Configure logging
            logging.basicConfig(
                level=getattr(logging, self.config.log_level.upper()),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(self.config.log_file),
                    logging.StreamHandler()
                ]
            )
        
        return logger
    
    async def start(self) -> None:
        """Start the server manager and runtime server."""
        if self.is_running:
            self.logger.warning("Server manager is already running")
            return
            
        self.logger.info("Starting BMAD Server Manager...")
        
        try:
            # Create runtime server configuration
            runtime_config = RuntimeConfig(
                host=self.config.host,
                port=self.config.port,
                max_concurrent_stories=self.config.max_concurrent_stories,
                story_timeout=self.config.story_timeout
            )
            
            # Initialize the runtime server
            self.runtime_server = RuntimeServer(runtime_config)
            
            # Start the runtime server
            await self.runtime_server.start()
            self.is_running = True
            
            self.logger.info(f"BMAD Server Manager started successfully on {self.config.host}:{self.config.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start server manager: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the server manager and runtime server."""
        if not self.is_running:
            self.logger.warning("Server manager is not running")
            return
            
        self.logger.info("Stopping BMAD Server Manager...")
        
        try:
            if self.runtime_server:
                await self.runtime_server.stop()
                
            self.is_running = False
            self.shutdown_event.set()
            self.logger.info("BMAD Server Manager stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping server manager: {e}")
            raise
    
    async def wait_for_shutdown(self) -> None:
        """Wait for the shutdown signal."""
        await self.shutdown_event.wait()
    
    async def execute_story(self, story_id: str, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a BMAD story through the runtime server.
        
        Args:
            story_id: Unique identifier for the story
            story_data: Story data to execute
            
        Returns:
            Dictionary containing execution results
        """
        if not self.is_running or not self.runtime_server:
            raise RuntimeError("Server manager is not running")
            
        return await self.runtime_server.execute_story(story_id, story_data)
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the server manager.
        
        Returns:
            Dictionary containing server status information
        """
        return {
            "is_running": self.is_running,
            "host": self.config.host,
            "port": self.config.port,
            "max_concurrent_stories": self.config.max_concurrent_stories,
            "story_timeout": self.config.story_timeout,
            "runtime_server_running": self.runtime_server is not None if self.is_running else False
        }
