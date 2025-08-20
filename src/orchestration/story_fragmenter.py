"""
Story Fragmenter
Breaks large BMAD stories into manageable fragments
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import copy

logger = logging.getLogger(__name__)

@dataclass
class FragmentationConfig:
    """Configuration for story fragmentation"""
    max_story_size: int = 10000  # tokens
    max_tasks_per_fragment: int = 10
    preserve_context: bool = True
    create_dependencies: bool = True

class StoryFragmenter:
    """Fragment large BMAD stories into smaller, manageable pieces"""
    
    def __init__(self, config: Optional[FragmentationConfig] = None):
        self.config = config or FragmentationConfig()
        self.logger = logging.getLogger(__name__)
    
    def fragment_story(self, story: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Break a large story into manageable fragments"""
        estimated_tokens = self._estimate_story_tokens(story)
        
        # If story is small enough and has few tasks, return as-is
        tasks = story.get("tasks", [])
        if (estimated_tokens <= self.config.max_story_size and 
            len(tasks) <= self.config.max_tasks_per_fragment):
            self.logger.debug(f"Story is small ({estimated_tokens} tokens, {len(tasks)} tasks), returning as-is")
            return [story]
        
        self.logger.info(f"Fragmenting large story ({estimated_tokens} tokens)")
        
        # Fragment based on tasks
        tasks = story.get("tasks", [])
        if not tasks:
            # No tasks to fragment, return original
            return [story]
        
        fragments = []
        fragment_counter = 0
        
        # Split tasks into chunks
        for i in range(0, len(tasks), self.config.max_tasks_per_fragment):
            task_chunk = tasks[i:i + self.config.max_tasks_per_fragment]
            fragment_counter += 1
            
            # Create fragment
            fragment = self._create_fragment(story, task_chunk, fragment_counter)
            fragments.append(fragment)
        
        # Add dependencies between fragments if needed
        if self.config.create_dependencies and len(fragments) > 1:
            fragments = self._add_fragment_dependencies(fragments)
        
        self.logger.info(f"Created {len(fragments)} fragments from story")
        return fragments
    
    def _estimate_story_tokens(self, story: Dict[str, Any]) -> int:
        """Estimate the number of tokens in a story"""
        # Simple estimation: characters / 4
        story_str = str(story)
        return len(story_str) // 4
    
    def _create_fragment(self, original_story: Dict[str, Any], tasks: List[Dict], fragment_id: int) -> Dict[str, Any]:
        """Create a fragment from a task chunk"""
        # Deep copy the original story to preserve structure
        fragment = copy.deepcopy(original_story)
        
        # Update ID and name
        original_id = fragment.get("id", "story")
        fragment["id"] = f"{original_id}_fragment_{fragment_id}"
        
        original_name = fragment.get("name", "Story")
        fragment["name"] = f"{original_name} - Fragment {fragment_id}"
        
        # Replace tasks with the chunk
        fragment["tasks"] = tasks
        
        # Add fragment metadata
        fragment["fragment_metadata"] = {
            "fragment_id": fragment_id,
            "total_fragments": 0,  # Will be updated later
            "fragmented_at": "2025-08-19T00:00:00Z",  # Placeholder
            "estimated_tokens": self._estimate_story_tokens(fragment)
        }
        
        return fragment
    
    def _add_fragment_dependencies(self, fragments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add dependencies between fragments to ensure proper execution order"""
        if len(fragments) <= 1:
            return fragments
        
        # Update total fragment count in metadata
        total_fragments = len(fragments)
        for fragment in fragments:
            if "fragment_metadata" in fragment:
                fragment["fragment_metadata"]["total_fragments"] = total_fragments
        
        # Add dependencies (each fragment depends on the previous one)
        for i in range(1, len(fragments)):
            current_fragment = fragments[i]
            previous_fragment = fragments[i-1]
            
            # Add dependency on previous fragment
            if "dependencies" not in current_fragment:
                current_fragment["dependencies"] = []
            
            current_fragment["dependencies"].append({
                "fragment_id": previous_fragment["id"],
                "type": "sequential"
            })
        
        return fragments
    
    def can_fragment(self, story: Dict[str, Any]) -> bool:
        """Check if a story can/should be fragmented"""
        estimated_tokens = self._estimate_story_tokens(story)
        tasks = story.get("tasks", [])
        
        return (
            estimated_tokens > self.config.max_story_size or
            len(tasks) > self.config.max_tasks_per_fragment
        )
    
    def get_fragmentation_info(self, story: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about how a story would be fragmented"""
        estimated_tokens = self._estimate_story_tokens(story)
        tasks = story.get("tasks", [])
        
        would_fragment = self.can_fragment(story)
        estimated_fragments = 1
        
        if would_fragment:
            estimated_fragments = max(
                1,
                (estimated_tokens // self.config.max_story_size) + 1,
                (len(tasks) // self.config.max_tasks_per_fragment) + 1
            )
        
        return {
            "estimated_tokens": estimated_tokens,
            "task_count": len(tasks),
            "would_fragment": would_fragment,
            "estimated_fragments": estimated_fragments,
            "max_story_size": self.config.max_story_size,
            "max_tasks_per_fragment": self.config.max_tasks_per_fragment
        }