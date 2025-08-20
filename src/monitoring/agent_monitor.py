"""
Agent Monitor
Comprehensive monitoring and health checking for agents
"""
import asyncio
import logging
from typing import Dict, Any, Optional, Deque
from dataclasses import dataclass
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MonitorConfig:
    """Configuration for AgentMonitor"""
    health_check_interval: int = 30  # seconds
    metrics_window_size: int = 100
    alert_thresholds: Dict[str, Any] = None
    enable_persistence: bool = True

class HealthStatus:
    """Health status representation"""
    
    def __init__(self):
        self.status = "unknown"
        self.degraded = False
        self.last_check = None
        self.metrics = {}
        self.alerts = []
    
    def is_healthy(self) -> bool:
        return self.status == "healthy"
    
    def is_degraded(self) -> bool:
        return self.degraded or self.status == "degraded"

class AgentMonitor:
    """Comprehensive agent monitoring and health checking"""
    
    def __init__(self, config: Optional[MonitorConfig] = None):
        self.config = config or MonitorConfig(
            alert_thresholds={
                "response_time": 5000,  # ms
                "error_rate": 0.05,     # 5%
                "token_usage": 90000,   # tokens
                "connection_drops": 3   # count
            }
        )
        
        self.metrics = {
            'response_times': deque(maxlen=self.config.metrics_window_size),
            'token_usage': deque(maxlen=self.config.metrics_window_size),
            'error_rates': deque(maxlen=self.config.metrics_window_size),
            'connection_status': deque(maxlen=self.config.metrics_window_size),
            'last_successful_call': None,
            'total_calls': 0,
            'failed_calls': 0
        }
        
        self.health_status = HealthStatus()
        self.logger = logging.getLogger(__name__)
    
    async def monitor_health(self):
        """Continuous health monitoring"""
        while True:
            try:
                # In a real implementation, this would check actual agent health
                await asyncio.sleep(self.config.health_check_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
    
    async def check_agent_health(self, agent_checker: callable) -> HealthStatus:
        """Check agent health using provided checker function"""
        health = HealthStatus()
        health.last_check = datetime.now()
        
        try:
            # Get agent metrics
            metrics = await agent_checker()
            
            # Update our metrics
            self._update_metrics(metrics)
            
            # Determine health status
            health.metrics = metrics
            health.status = self._determine_health_status(metrics)
            health.degraded = self._is_degraded(metrics)
            
            self.health_status = health
            return health
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            health.status = "unhealthy"
            health.degraded = True
            health.alerts.append(f"Health check error: {str(e)}")
            self.health_status = health
            return health
    
    def _update_metrics(self, metrics: Dict[str, Any]):
        """Update internal metrics storage"""
        if not metrics:
            return
            
        if "response_time" in metrics:
            self.metrics['response_times'].append(metrics["response_time"])
            
        if "token_usage" in metrics:
            self.metrics['token_usage'].append(metrics["token_usage"])
            
        if "error_rate" in metrics:
            self.metrics['error_rates'].append(metrics["error_rate"])
            
        if "connection_status" in metrics:
            self.metrics['connection_status'].append(metrics["connection_status"])
            
        self.metrics['total_calls'] += 1
        if metrics.get("success") is False:
            self.metrics['failed_calls'] += 1
    
    def _determine_health_status(self, metrics: Dict[str, Any]) -> str:
        """Determine overall health status based on metrics"""
        if self._is_degraded(metrics):
            return "degraded"
        return "healthy"
    
    def _is_degraded(self, metrics: Dict[str, Any]) -> bool:
        """Check if agent is degraded based on thresholds"""
        if not metrics:
            return False
            
        thresholds = self.config.alert_thresholds
        if not thresholds:
            return False
        
        # Check response time
        if ("response_time" in metrics and 
            metrics["response_time"] > thresholds.get("response_time", float('inf'))):
            return True
            
        # Check error rate
        if ("error_rate" in metrics and 
            metrics["error_rate"] > thresholds.get("error_rate", float('inf'))):
            return True
            
        # Check token usage
        if ("token_usage" in metrics and 
            metrics["token_usage"] > thresholds.get("token_usage", float('inf'))):
            return True
            
        return False
    
    def publish_metrics(self, metrics: Dict[str, Any]):
        """Publish metrics to monitoring system"""
        # In a real implementation, this would send metrics to a monitoring system
        pass
    
    async def alert_and_mitigate(self, health: HealthStatus):
        """Alert on health issues and attempt mitigation"""
        # In a real implementation, this would send alerts and attempt recovery
        pass