"""
BMAD State Management System
Handles state management for BMAD components.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

class StateType(Enum):
    """Types of state that can be managed."""
    STORY = "story"
    AGENT = "agent"
    GLOBAL = "global"
    SESSION = "session"

@dataclass
class StateData:
    """Represents state data."""
    id: str
    type: StateType
    data: Dict[str, Any]
    timestamp: float
    version: int = 1

class StateManager:
    """Manages state for BMAD components."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.state_store: Dict[str, StateData] = {}
        self.lock = asyncio.Lock()
        
    async def save_state(self, state_id: str, state_type: StateType, data: Dict[str, Any]) -> StateData:
        """Save state data."""
        async with self.lock:
            timestamp = asyncio.get_event_loop().time()
            
            # Check if state already exists
            if state_id in self.state_store:
                existing_state = self.state_store[state_id]
                new_version = existing_state.version + 1
                # Create new state to preserve history
                state_data = StateData(
                    id=state_id,
                    type=state_type,
                   =data,
                    timestamp=timestamp,
                    version=new_version
                )
                # Store in history (could be implemented later)
                self.state_store[state_id] = state_data
            else:
                state_data = StateData(
                    id=state_id,
                    type=state_type,
                    data=data,
                    timestamp=timestamp
                )
                self.state_store[state_id] = state_data
                
            return state_data
            
    async def load_state(self, state_id: str) -> Optional[StateData]:
        """Load state data."""
        return self.state_store.get(state_id)
        
    async def update_state(self, state_id: str, updates: Dict[str, Any]) -> Optional[StateData]:
        """Update existing state data."""
        current_state = await self.load_state(state_id)
        if current_state is None:
            return None
            
        # Merge updates
        updated_data = {**current_state.data, **updates}
        
        return await self.save_state(state_id, current_state.type, updated_data)
        
    async def delete_state(self, state_id: str) -> bool:
        """Delete state data."""
        async with self.lock:
            if state_id in self.state_store:
                del self.state_store[state_id]
                return True
            return False
            
    async def list_states_by_type(self, state_type: StateType) -> List[StateData]:
        """List all states of a specific type."""
        return [state for state in self.state_store.values() if state.type == state_type]
        
    async def get_state_history(self, state_id: str) -> List[StateData]:
        """Get history for a state (if implemented)."""
        # Implementation would need to preserve historical versions
        current_state = await self.load_state(state_id)
        return [current_state] if current_state else []
        
    async def persist_to_disk(self, filepath: str) -> None:
        """Persist all state data to disk."""
        serializable_data = {
            state_id: {
                "id": state.id,
                "type": state.type.value,
                "data": state.data,
                "timestamp": state.timestamp,
                "version": state.version
            }
            for state_id, state in self.state_store.items()
        }
        
        with open(filepath, 'w') as f:
            json.dump(serializable_data, f, indent=2)
            
    async def load_from_disk(self, filepath: str) -> None:
        """Load state data from disk."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        self.state_store.clear()
        
        for state_id, state_data in data.items():
            state = StateData(
                id=state_data["id"],
                type=StateType(state_data["type"]),
                data=state_data["data"],
                timestamp=state_data["timestamp"],
                version=state_data.get("version", 1)
            )
            self.state_store[state_id] = state
