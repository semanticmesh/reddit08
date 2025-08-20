"""
Circuit Breaker Pattern Implementation
Prevents cascading failures in distributed systems
"""
import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional, Dict
import functools

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failure threshold exceeded, calls blocked
    HALF_OPEN = "half_open" # Testing if service recovered

class CircuitBreakerException(Exception):
    """Base exception for circuit breaker"""
    pass

class CircuitBreakerOpen(CircuitBreakerException):
    """Exception raised when circuit breaker is open"""
    pass

class CircuitBreaker:
    """Circuit breaker implementation for preventing cascading failures"""
    
    def __init__(
        self, 
        failure_threshold: int = 5, 
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
        self.lock = asyncio.Lock()
        
        logger.info(f"Circuit breaker initialized with threshold={failure_threshold}, timeout={recovery_timeout}")
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator for protecting functions with circuit breaker"""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with self.lock:
                if self.state == CircuitState.OPEN:
                    if self._should_attempt_reset():
                        self.state = CircuitState.HALF_OPEN
                        logger.info("Circuit breaker half-open, testing service")
                    else:
                        raise CircuitBreakerOpen("Circuit breaker is OPEN")
            
            try:
                result = await func(*args, **kwargs)
                await self._on_success()
                return result
            except self.expected_exception as e:
                await self._on_failure()
                raise
            except Exception as e:
                # Unexpected exception, still count as failure for safety
                await self._on_failure()
                raise
        
        return wrapper
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call a function protected by the circuit breaker"""
        async with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker half-open, testing service")
                else:
                    raise CircuitBreakerOpen("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except self.expected_exception as e:
            await self._on_failure()
            raise
        except Exception as e:
            # Unexpected exception, still count as failure for safety
            await self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        if self.last_failure_time is None:
            return False
        return datetime.now() >= self.last_failure_time + timedelta(seconds=self.recovery_timeout)
    
    async def _on_success(self) -> None:
        """Handle successful call"""
        async with self.lock:
            self.failure_count = 0
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                logger.info("Circuit breaker closed, service recovered")
            elif self.state == CircuitState.OPEN:
                # This shouldn't happen, but just in case
                self.state = CircuitState.CLOSED
                logger.warning("Circuit breaker closed unexpectedly")
    
    async def _on_failure(self) -> None:
        """Handle failed call"""
        async with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.state == CircuitState.HALF_OPEN:
                # Failed during test, go back to open
                self.state = CircuitState.OPEN
                logger.warning("Circuit breaker opened, service test failed")
            elif self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
                # Threshold exceeded, open circuit
                self.state = CircuitState.OPEN
                logger.error(f"Circuit breaker opened after {self.failure_count} failures")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state information"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "recovery_timeout": self.recovery_timeout
        }
    
    async def reset(self) -> None:
        """Reset the circuit breaker to closed state"""
        async with self.lock:
            self.failure_count = 0
            self.last_failure_time = None
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker manually reset to closed")