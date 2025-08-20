"""
Dual Agent Coordinator
Orchestrates both GooseAgent and QWEN3 in a supervisor-worker pattern
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
from datetime import datetime

# Import our resilient agent
from src.goose.resilient_agent import ResilientGooseAgent, ResilientAgentConfig

logger = logging.getLogger(__name__)

@dataclass
class DualAgentConfig:
    """Configuration for DualAgentCoordinator"""
    checkpoint_frequency: str = "per_task"
    max_task_size: int = 5000
    timeout_per_task: int = 60
    enable_fallback: bool = True

class QWEN3Supervisor:
    """QWEN3 supervisor implementation (placeholder)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def validate_story(self, story: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a BMAD story"""
        # In a real implementation, this would use QWEN3 to validate the story
        return {
            "valid": True,
            "requires_decomposition": len(str(story)) > 5000,
            "estimated_tokens": len(str(story)) // 4,
            "validation_notes": "Story appears valid"
        }
        
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task with QWEN3 as fallback"""
        # In a real implementation, this would use QWEN3 to execute the task
        return {
            "status": "success",
            "result": f"QWEN3 executed task: {task.get('name', 'unnamed')}",
            "execution_time": 0.1
        }

class BMADStory:
    """BMAD Story representation"""
    
    def __init__(self, story_data: Dict[str, Any]):
        self.id = story_data.get("id")
        self.name = story_data.get("name")
        self.tasks = story_data.get("tasks", [])
        self.outputs = story_data.get("outputs", {})
        self.acceptance_criteria = story_data.get("acceptance_criteria", {})
        self.raw_data = story_data
        
    def estimated_tokens(self) -> int:
        """Estimate the number of tokens in the story"""
        return len(str(self.raw_data)) // 4

class DualAgentCoordinator:
    """Dual Agent Coordinator for GooseAgent and QWEN3"""
    
    def __init__(self, config: Optional[DualAgentConfig] = None):
        self.config = config or DualAgentConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize agents
        goose_config = ResilientAgentConfig()
        self.goose_agent = ResilientGooseAgent(goose_config)
        self.qwen3_supervisor = QWEN3Supervisor()
        
        # For checkpointing intermediate results
        self.checkpoint_storage: Dict[str, Any] = {}
        
        # Task queue for processing
        self.task_queue: asyncio.Queue = asyncio.Queue()
    
    async def execute_story(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute BMAD story with dual-agent coordination"""
        story = BMADStory(story_data)
        
        # QWEN3 validates and monitors
        validation = await self.qwen3_supervisor.validate_story(story_data)
        
        if validation.get("requires_decomposition", False):
            # Break into smaller chunks for GooseAgent
            subtasks = await self.decompose_story(story)
            results = []
            
            for subtask in subtasks:
                # Execute with automatic failover
                result = await self.execute_subtask_with_failover(subtask)
                results.append(result)
                
                # Save intermediate state
                await self.checkpoint_state(subtask, result)
            
            return self.merge_results(results)
        else:
            # Execute directly with GooseAgent
            return await self.goose_agent.execute_with_fallback(
                story_data,
                self.qwen3_supervisor.execute_task
            )
    
    async def decompose_story(self, story: BMADStory) -> List[Dict[str, Any]]:
        """Decompose a large story into smaller subtasks"""
        subtasks = []
        
        # If story has many tasks, break them into chunks
        if len(story.tasks) > 3:  # For testing, use small chunks
            for i in range(0, len(story.tasks), 3):
                task_chunk = story.tasks[i:i+3]
                subtask = {
                    "id": f"{story.id}_part_{i//3 + 1}",
                    "name": f"{story.name} - Part {i//3 + 1}",
                    "tasks": task_chunk,
                    "outputs": story.outputs,
                    "acceptance_criteria": story.acceptance_criteria
                }
                subtasks.append(subtask)
        else:
            # Just return the original story as a single task
            subtasks.append(story.raw_data)
            
        self.logger.info(f"Decomposed story into {len(subtasks)} subtasks")
        return subtasks
    
    async def execute_subtask_with_failover(self, subtask: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a subtask with automatic failover to QWEN3"""
        try:
            return await self.goose_agent.execute_with_fallback(
                subtask,
                self.qwen3_supervisor.execute_task
            )
        except Exception as e:
            self.logger.error(f"Failed to execute subtask: {e}")
            # Try one more time with QWEN3 directly
            return await self.qwen3_supervisor.execute_task(subtask)
    
    async def checkpoint_state(self, subtask: Dict[str, Any], result: Dict[str, Any]):
        """Save intermediate state/checkpoint"""
        if self.config.checkpoint_frequency == "per_task":
            checkpoint_id = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.checkpoint_storage[checkpoint_id] = {
                "subtask": subtask,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            self.logger.info(f"Checkpoint saved: {checkpoint_id}")
    
    def merge_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge results from multiple subtasks"""
        merged = {
            "status": "success",
            "results": results,
            "merged_at": datetime.now().isoformat(),
            "total_subtasks": len(results)
        }
        
        # Try to combine results meaningfully
        combined_output = {}
        for result in results:
            if isinstance(result, dict) and "result" in result:
                # Add to combined output
                result_data = result.get("result", {})
                # Handle case where result is a string or other non-dict type
                if isinstance(result_data, dict):
                    combined_output.update(result_data)
                elif isinstance(result_data, str):
                    combined_output[result_data] = True
                else:
                    # For other types, convert to string
                    combined_output[str(result_data)] = True
        
        merged["combined_result"] = combined_output
        return merged
    
    async def close(self):
        """Close the coordinator"""
        await self.goose_agent.close()
        self.logger.info("DualAgentCoordinator closed")