"""
Incremental Knowledge Base
Implements incremental updates to prevent full reloads
"""
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class KnowledgeConfig:
    """Configuration for incremental knowledge base"""
    storage_path: str = "data/knowledge"
    checkpoint_frequency: int = 10  # updates
    max_cache_size: int = 1000
    enable_persistence: bool = True

class IncrementalKnowledgeBase:
    """Incremental knowledge base with delta updates"""
    
    def __init__(self, config: Optional[KnowledgeConfig] = None):
        self.config = config or KnowledgeConfig()
        self.knowledge = {}
        self.delta_log: List[Dict[str, Any]] = []
        self.update_count = 0
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)
        
        # Ensure storage path exists
        Path(self.config.storage_path).mkdir(parents=True, exist_ok=True)
        
        # Load existing knowledge if available
        self._load_persistent_knowledge()
    
    def _load_persistent_knowledge(self):
        """Load knowledge from persistent storage"""
        if not self.config.enable_persistence:
            return
            
        knowledge_file = Path(self.config.storage_path) / "knowledge.json"
        if knowledge_file.exists():
            try:
                with open(knowledge_file, 'r') as f:
                    self.knowledge = json.load(f)
                self.logger.info(f"Loaded knowledge base with {len(self.knowledge)} entries")
            except Exception as e:
                self.logger.warning(f"Failed to load knowledge base: {e}")
    
    async def update_incremental(self, delta: Dict[str, Any]) -> None:
        """Update knowledge base incrementally without full reload"""
        async with self.lock:
            # Apply delta to knowledge base
            self.apply_delta(delta)
            
            # Log the delta
            self.delta_log.append({
                "timestamp": datetime.now().isoformat(),
                "delta": delta,
                "update_id": self.update_count
            })
            
            self.update_count += 1
            
            # Persist checkpoint if needed
            if (self.config.enable_persistence and 
                self.update_count % self.config.checkpoint_frequency == 0):
                await self.persist_checkpoint()
            
            self.logger.debug(f"Applied incremental update {self.update_count}")
    
    def apply_delta(self, delta: Dict[str, Any]) -> None:
        """Apply a delta update to the knowledge base"""
        for key, value in delta.items():
            if key.startswith("+"):  # Add operation
                actual_key = key[1:]
                self.knowledge[actual_key] = value
            elif key.startswith("-"):  # Remove operation
                actual_key = key[1:]
                self.knowledge.pop(actual_key, None)
            elif key.startswith("~"):  # Update operation
                actual_key = key[1:]
                if actual_key in self.knowledge:
                    # Merge update
                    if isinstance(self.knowledge[actual_key], dict) and isinstance(value, dict):
                        self.knowledge[actual_key].update(value)
                    else:
                        self.knowledge[actual_key] = value
            else:  # Direct assignment
                self.knowledge[key] = value
    
    async def persist_checkpoint(self) -> None:
        """Persist current knowledge to checkpoint"""
        if not self.config.enable_persistence:
            return
            
        try:
            knowledge_file = Path(self.config.storage_path) / "knowledge.json"
            with open(knowledge_file, 'w') as f:
                json.dump(self.knowledge, f, indent=2, default=str)
            
            # Also save delta log
            delta_file = Path(self.config.storage_path) / "delta_log.json"
            with open(delta_file, 'w') as f:
                json.dump(self.delta_log, f, indent=2, default=str)
                
            self.logger.info(f"Persisted knowledge checkpoint with {len(self.knowledge)} entries")
        except Exception as e:
            self.logger.error(f"Failed to persist knowledge checkpoint: {e}")
    
    def get_knowledge(self, key: str = None) -> Any:
        """Get knowledge by key or all knowledge"""
        if key is None:
            return self.knowledge.copy()
        return self.knowledge.get(key)
    
    def query_knowledge(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Query knowledge base with filters"""
        results = {}
        
        for k, v in self.knowledge.items():
            match = True
            for qk, qv in query.items():
                if isinstance(v, dict) and qk in v:
                    if v[qk] != qv:
                        match = False
                        break
                elif qk == "key" and k != qv:
                    match = False
                    break
                    
            if match:
                results[k] = v
                
        return results
    
    async def merge_knowledge(self, other_knowledge: Dict[str, Any]) -> None:
        """Merge knowledge from another source"""
        async with self.lock:
            self.knowledge.update(other_knowledge)
            self.update_count += 1
            
            if self.config.enable_persistence:
                await self.persist_checkpoint()
    
    def get_delta_log(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get recent delta log entries"""
        if limit:
            return self.delta_log[-limit:]
        return self.delta_log.copy()
    
    async def rollback_to_checkpoint(self, checkpoint_id: int = None) -> bool:
        """Rollback to a specific checkpoint"""
        if not self.config.enable_persistence:
            return False
            
        try:
            # If no checkpoint specified, use last persisted state
            if checkpoint_id is None:
                self._load_persistent_knowledge()
                self.logger.info("Rolled back to last persisted checkpoint")
                return True
            
            # Find checkpoint in delta log
            for i, delta_entry in enumerate(reversed(self.delta_log)):
                if delta_entry.get("update_id") == checkpoint_id:
                    # Rebuild knowledge up to this point
                    self.knowledge = {}
                    self._load_persistent_knowledge()
                    
                    # Apply all deltas up to checkpoint
                    for entry in self.delta_log[:len(self.delta_log)-i]:
                        self.apply_delta(entry["delta"])
                    
                    self.logger.info(f"Rolled back to checkpoint {checkpoint_id}")
                    return True
            
            self.logger.warning(f"Checkpoint {checkpoint_id} not found")
            return False
        except Exception as e:
            self.logger.error(f"Failed to rollback to checkpoint: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        return {
            "total_entries": len(self.knowledge),
            "total_updates": self.update_count,
            "delta_log_size": len(self.delta_log),
            "storage_path": self.config.storage_path,
            "last_update": self.delta_log[-1]["timestamp"] if self.delta_log else None
        }