"""
BMAD Agent Coordination Layer
Coordinates agent activities and interactions.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

class AgentStatus(Enum):
    """Status of an agent."""
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"

@dataclass
class AgentInfo:
    """Information about an agent."""
    id: str
    name: str
    capabilities: List[str]
    status: AgentStatus
    current_task: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AgentCoordinator:
    """Coordinates agent activities and interactions."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agents: Dict[str, AgentInfo] = {}
        self.agent_tasks: Dict[str, asyncio.Task] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.lock = asyncio.Lock()
        
    async def register_agent(self, agent_id: str, name: str, capabilities: List[str]) -> AgentInfo:
        """Register a new agent."""
        async with self.lock:
            if agent_id in self.agents:
                raise ValueError(f"Agent {agent_id} already exists")
                
            agent = AgentInfo(
                id=agent_id,
                name=name,
                capabilities=capabilities,
                status=AgentStatus.IDLE
            )
            
            self.agents[agent_id] = agent
            self.logger.info(f"Registered agent: {agent_id} ({name})")
            
            return agent
            
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent."""
        async with self.lock:
            if agent_id not in self.agents:
                return False
                
            # Cancel any running tasks
            if agent_id in self.agent_tasks:
                self.agent_tasks[agent_id].cancel()
                del self.agent_tasks[agent_id]
                
            del self.agents[agent_id]
            self.logger.info(f"Unregistered agent: {agent_id}")
            
            return True
            
    async def assign_task(self, agent_id: str, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Assign a task to an agent."""
        async with self.lock:
            if agent_id not in self.agents:
                return False
                
            agent = self.agents[agent_id]
            if agent.status != AgentStatus.IDLE:
                self.logger.warning(f"Agent {agent_id} is not idle (current status: {agent.status})")
                return False
                
            # Update agent status
            agent.status = AgentStatus.RUNNING
            agent.current_task = task_id
            
            # Create and start task
            task = asyncio.create_task(self._execute_agent_task(agent_id, task_id, task_data))
            self.agent_tasks[agent_id] = task
            
            return True
            
    async def _execute_agent_task(self, agent_id: str, task_id: str, task_data: Dict[str, Any]) -> None:
        """Execute a task for an agent."""
        try:
            agent = self.agents[agent_id]
            
            # Execute the task (implementation specific to agent type)
            result = await self._execute_task_for_agent(agent, task_data)
            
            # Update agent status
            async with self.lock:
                agent.status = AgentStatus.COMPLETED
                agent.current_task = None
                
            self.logger.info(f"Agent {agent_id} completed task {task_id}")
            
        except asyncio.CancelledError:
            self.logger.info(f"Task {task_id} for agent {agent_id} was cancelled")
        except Exception as e:
            self.logger.error(f"Error executing task {task_id} for agent {agent_id}: {e}")
            async with self.lock:
                agent.status = AgentStatus.ERROR
                agent.current_task = None
        finally:
            # Clean up task
            if agent_id in self.agent_tasks:
                del self.agent_tasks[agent_id]
                
    async def _execute_task_for_agent(self, agent: AgentInfo, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task for an agent."""
        # This should be implemented based on agent capabilities
        # For now, return a simple success response
        await asyncio.sleep(1)  # Simulate work
        return {"status": "success", "task_id": agent.current_task}
        
    async def get_agent_status(self, agent_id: str) -> Optional[AgentInfo]:
        """Get the status of an agent."""
        return self.agents.get(agent_id)
        
    async def list_agents(self, status_filter: Optional[AgentStatus] = None) -> List[AgentInfo]:
        """List all agents, optionally filtered by status."""
        agents = list(self.agents.values())
        
        if status_filter:
            agents = [agent for agent in agents if agent.status == status_filter]
            
        return agents
        
    async def cancel_agent_task(self, agent_id: str) -> bool:
        """Cancel the current task for an agent."""
        async with self.lock:
            if agent_id not in self.agents or agent_id not in self.agent_tasks:
                return False
                
            # Cancel the task
            self.agent_tasks[agent_id].cancel()
            
            # Update agent status
            self.agents[agent_id].status = AgentStatus.IDLE
            self.agents[agent_id].current_task = None
            
            # Clean up
            del self.agent_tasks[agent_id]
            
            return True
