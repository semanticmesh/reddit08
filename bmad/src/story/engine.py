"""
BMAD Story Engine
Handles YAML story parsing, validation and execution.
"""

import yaml
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class StoryStep:
    """Represents a single step in a BMAD story."""
    id: str
    action: str
    parameters: Dict[str, Any]
    next_steps: List[str]
    conditions: Optional[Dict[str, Any]] = None
    
@dataclass
class Story:
    """Represents a BMAD story."""
    id: str
    name: str
    description: str
    version: str
    steps: List[StoryStep]
    metadata: Optional[Dict[str, Any]] = None

class StoryEngine:
    """Engine for parsing and executing BMAD stories."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.stories: Dict[str, Story] = {}
        
    def load_story_from_yaml(self, yaml_content: str) -> Story:
        """Load a story from YAML content."""
        try:
            data = yaml.safe_load(yaml_content)
            return self._parse_story_data(data)
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML: {e}")
            raise
            
    def _parse_story_data(self, data: Dict[str, Any]) -> Story:
        """Parse story data into Story object."""
        steps = []
        for step_data in data.get('steps', []):
            step = StoryStep(
                id=step_data['id'],
                action=step_data['action'],
                parameters=step_data.get('parameters', {}),
                next_steps=step_data.get('next_steps', []),
                conditions=step_data.get('conditions')
            )
            steps.append(step)
            
        return Story(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            version=data.get('version', '1.0.0'),
            steps=steps,
            metadata=data.get('metadata')
        )
        
    def execute_story(self, story_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a story by its ID."""
        if story_id not in self.stories:
            raise ValueError(f"Story {story_id} not found")
            
        story = self.stories[story_id]
        return self._execute_story_steps(story, context or {})
        
    def _execute_story_steps(self, story: Story, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all steps in a story."""
        results = []
        current_step_id = story.steps[0].id if story.steps else None
        
        while current_step_id:
            step = next((s for s in story.steps if s.id == current_step_id), None)
            if not step:
                break
                
            result = self._execute_step(step, context)
            results.append(result)
            
            # Determine next step
            if step.conditions and self._evaluate_conditions(step.conditions, context):
                current_step_id = step.next_steps[0] if step.next_steps else None
            else:
                current_step_id = step.next_steps[1] if len(step.next_steps) > 1 else None
                
        return {"story_id": story.id, "results": results}
        
    def _execute_step(self, step: StoryStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single story step."""
        # Implementation for step execution
        return {"step_id": step.id, "status": "completed"}
        
    def _evaluate_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate step conditions."""
        # Implementation for condition evaluation
        return True
