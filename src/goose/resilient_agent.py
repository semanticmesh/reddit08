"""
Resilient Goose Agent Implementation
Wrapper around GooseAgent with automatic recovery and resilience features
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ResilientAgentConfig:
    """Configuration for ResilientGooseAgent"""
    max_retries: int = 3
    timeout: int = 30
    heartbeat_interval: int = 10
    max_context_tokens: int = 100000

class ResilientGooseAgent:
    """Resilient wrapper around GooseAgent with automatic recovery"""
    
    def __init__(self, config: Optional[ResilientAgentConfig] = None):
        self.config = config or ResilientAgentConfig()
        self.agent = None
        self.connection_state = "disconnected"
        self.last_heartbeat = None
        self.heartbeat_task = None
        self.http_client = httpx.AsyncClient(timeout=self.config.timeout)
        
    async def connect(self, goose_api_endpoint: str = "http://localhost:3000/api"):
        """Connect to Goose API"""
        try:
            # Validate URL format
            if not goose_api_endpoint.startswith(("http://", "https://")):
                raise ValueError("Request URL is missing an 'http://' or 'https://' protocol.")
            # Test connection
            response = await self.http_client.get(f"{goose_api_endpoint}/health")
            response.raise_for_status()
            
            self.agent = goose_api_endpoint
            self.connection_state = "connected"
            self.last_heartbeat = datetime.now()
            
            # Start heartbeat monitoring
            self.heartbeat_task = asyncio.create_task(self.maintain_connection())
            
            logger.info("Successfully connected to GooseAgent")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to GooseAgent: {e}")
            self.connection_state = "disconnected"
            return False
    
    async def maintain_connection(self):
        """Heartbeat mechanism to detect silent drops"""
        while True:
            try:
                if self.connection_state == "connected":
                    # Send lightweight ping every heartbeat_interval seconds
                    await self.ping()
                    self.last_heartbeat = datetime.now()
                else:
                    await self.reconnect()
            except Exception as e:
                logger.warning(f"Heartbeat failed: {e}")
                await self.reconnect()
            
            await asyncio.sleep(self.config.heartbeat_interval)
    
    async def ping(self):
        """Send a lightweight ping to check connection"""
        if not self.agent:
            raise Exception("Not connected to GooseAgent")
            
        try:
            response = await self.http_client.get(f"{self.agent}/health")
            response.raise_for_status()
            return True
        except Exception as e:
            logger.warning(f"Ping failed: {e}")
            raise
    
    async def reconnect(self):
        """Reconnect to GooseAgent"""
        logger.info("Attempting to reconnect to GooseAgent")
        self.connection_state = "reconnecting"
        
        for attempt in range(self.config.max_retries):
            try:
                if await self.connect(self.agent):
                    logger.info(f"Successfully reconnected on attempt {attempt + 1}")
                    return True
            except Exception as e:
                logger.warning(f"Reconnection attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        self.connection_state = "disconnected"
        logger.error("Failed to reconnect to GooseAgent after all attempts")
        return False
    
    async def execute_with_fallback(self, task: Dict[str, Any], qwen3_fallback=None):
        """Execute task with automatic fallback to QWEN3"""
        try:
            if self.connection_state != "connected":
                await self.reconnect()
                
            result = await self.execute_task(task)
            return result
            
        except (TimeoutError, ConnectionError, httpx.RequestError) as e:
            logger.info("Falling back to QWEN3 supervisor")
            if qwen3_fallback:
                return await qwen3_fallback(task)
            else:
                raise Exception(f"Task execution failed and no fallback available: {e}")
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task with the GooseAgent"""
        if not self.agent:
            raise Exception("Not connected to GooseAgent")
            
        try:
            response = await self.http_client.post(
                f"{self.agent}/stories/execute",
                json=task
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.RequestError as e:
            self.connection_state = "disconnected"
            raise ConnectionError(f"Failed to execute task: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error executing task: {e}")
    
    async def close(self):
        """Close the agent connection"""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            
        if self.http_client:
            await self.http_client.aclose()
            
        self.connection_state = "disconnected"
        logger.info("Closed GooseAgent connection")