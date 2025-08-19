"""
BMAD Dynamic Story Selection Mechanism
Responsible for selecting the optimal story to execute based on various criteria.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import yaml
from pathlib import Path

class StoryPriority(Enum):
    """Story priority levels."""
    P0 = "P0"  # Critical - must execute
    P1 = "P1"  # High - should execute soon
    P2 = "P2"  # Medium - can wait
    P3 = "P3"  # Low - lowest priority

class SelectionCriteria(Enum):
    """Selection evaluation criteria."""
    PRIORITY = "priority"
    DEPENDENCY = "dependency"
    CONTEXT = "context"
    TIME_SINCE_LAST_RUN = "time_since_last_run"
    BUSINESS_IMPACT = "business_impact"
    RESOURCE_REQUIREMENT = "resource_requirement"
    QUALITY_THRESHOLD = "quality_threshold"
    GEOGRAPHIC_COVERAGE = "geographic_coverage"
    VERTICAL_COVERAGE = "vertical_coverage"

@dataclass
class StoryInstance:
    """Represents an instance of a story with metadata."""
    story_id: str
    name: str
    priority: StoryPriority
    epic: str
    dependencies: List[str] = field(default_factory=list)
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    success_rate: float = 0.0
    business_impact_score: float = 0.5
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    geographic_targets: Set[str] = field(default_factory=set)
    vertical_targets: Set[str] = field(default_factory=set)
    quality_thresholds: Dict[str, float] = field(default_factory=dict)
    context_requirements: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    cooldown_hours: int = 0
    
@dataclass
class SelectionResult:
    """Result of story selection process."""
    selected_story: Optional[StoryInstance]
    selection_score: float
    evaluation_metrics: Dict[str, Any]
    rejection_reasons: List[str] = field(default_factory=list)
    competing_stories: List[StoryInstance] = field(default_factory=list)
    
class DynamicStorySelector:
    """Main story selection mechanism for BMAD system."""
    
    def __init__(self, stories_directory: str = "bmad/stories", 
                 config_directory: str = "bmad/config"):
        self.logger = logging.getLogger(__name__)
        self.stories_directory = Path(stories_directory)
        self.config_directory = Path(config_directory)
        
        # Load and parse all available stories
        self.available_stories: Dict[str, StoryInstance] = {}
        self.selection_weights = {
            SelectionCriteria.PRIORITY.value: 0.3,
            SelectionCriteria.DEPENDENCY.value: 0.2,
            SelectionCriteria.CONTEXT.value: 0.15,
            SelectionCriteria.TIME_SINCE_LAST_RUN.value: 0.15,
            SelectionCriteria.BUSINESS_IMPACT.value: 0.1,
            SelectionCriteria.RESOURCE_REQUIREMENT.value: 0.05,
            SelectionCriteria.QUALITY_THRESHOLD.value: 0.05
        }
        
        # State tracking
        self.execution_history: Dict[str, List[datetime]] = {}
        self.context_state: Dict[str, Any] = {}
        self.resource_capacity: Dict[str, float] = {}
        
        self._initialize_selector()
        
    def _initialize_selector(self):
        """Initialize the story selector by loading all available stories."""
        try:
            self._load_stories_from_yaml()
            self._load_selection_config()
            self.logger.info(f"Initialized story selector with {len(self.available_stories)} stories")
        except Exception as e:
            self.logger.error(f"Error initializing story selector: {e}")
            raise
            
    def _load_stories_from_yaml(self):
        """Load all stories from YAML files."""
        if not self.stories_directory.exists():
            self.logger.warning(f"Stories directory not found: {self.stories_directory}")
            return
            
        for story_file in self.stories_directory.glob("*.yml"):
            try:
                with open(story_file, 'r', encoding='utf-8') as f:
                    story_data = yaml.safe_load(f)
                    story_instance = self._parse_story_to_instance(story_data, story_file.stem)
                    self.available_stories[story_instance.story_id] = story_instance
            except Exception as e:
                self.logger.error(f"Error loading story {story_file}: {e}")
                continue
                
    def _parse_story_to_instance(self, story_data: Dict[str, Any], file_name: str) -> StoryInstance:
        """Parse YAML story data into StoryInstance."""
        priority = StoryPriority(story_data.get('priority', 'P2'))
        
        # Extract dependencies from tasks
        dependencies = []
        if 'tasks' in story_data:
            for task_name, task_actions in story_data['tasks'].items():
                for action in task_actions:
                    if isinstance(action, dict) and 'source' in action:
                        # Simple dependency detection based on file paths
                        if isinstance(action['source'], str):
                            if 'data/raw' in action['source']:
                                dependencies.append('raw_data_available')
                            if 'data/processed' in action['source']:
                                dependencies.append('processed_data_available')
                                
        # Parse geographic targets from context
        geo_targets = set()
        if 'context' in story_data and 'sources' in story_data['context']:
            for source in story_data['context']['sources']:
                if 'path' in source:
                    source_path = source['path']
                    if source_path.startswith('config/cities.yml') or 'metro' in source_path:
                        geo_targets.update(['nyc', 'sf', 'chicago', 'la', 'boston'])
                        
        # Parse vertical targets
        vertical_targets = set()
        if 'context' in story_data:
            for key, value in story_data['context'].items():
                if isinstance(value, dict) and 'verticals' in value:
                    for vertical in value['verticals']:
                        vertical_targets.add(vertical)
                        
        return StoryInstance(
            story_id=story_data['id'],
            name=story_data['name'],
            priority=priority,
            epic=story_data.get('epic', 'General'),
            dependencies=dependencies,
            geographic_targets=geo_targets,
            vertical_targets=vertical_targets,
            business_impact_score=self._calculate_business_impact(story_data),
            quality_thresholds=story_data.get('acceptance_criteria', {}).get('quality', {}),
            context_requirements=self._parse_context_requirements(story_data),
            cooldown_hours=self._parse_cooldown(story_data)
        )
        
    def _calculate_business_impact(self, story_data: Dict[str, Any]) -> float:
        """Calculate business impact score for a story."""
        score = 0.5  # Base score
        
        # Priority-based scoring
        if story_data.get('priority') == 'P0':
            score += 0.3
        elif story_data.get('priority') == 'P1':
            score += 0.2
        elif story_data.get('priority') == 'P2':
            score += 0.1
            
        # Epic-based scoring
        epic = story_data.get('epic', 'General')
        if epic == 'Payload Optimization':
            score += 0.1
        elif epic == 'Quality Control':
            score += 0.15
            
        return min(score, 1.0)
        
    def _parse_context_requirements(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse context requirements from story data."""
        requirements = {}
        
        if 'context' in story_data:
            context = story_data['context']
            
            # Extract source requirements
            if 'sources' in context:
                required_files = []
                for source in context['sources']:
                    if isinstance(source, dict) and 'path' in source:
                        required_files.append(source['path'])
                requirements['required_files'] = required_files
                
            # Extract parameter requirements
            if 'parameters' in context:
                requirements['parameters'] = context['parameters']
                
        return requirements
        
    def _parse_cooldown(self, story_data: Dict[str, Any]) -> int:
        """Parse cooldown period from story data."""
        return story_data.get('monitoring', {}).get('scheduled_execution', {}).get('frequency_hours', 0)
        
    def _load_selection_config(self):
        """Load selection configuration from files."""
        config_file = self.config_directory / "selection_config.yml"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    self.selection_weights.update(config.get('selection_weights', {}))
                    self.resource_capacity.update(config.get('resource_capacity', {}))
            except Exception as e:
                self.logger.error(f"Error loading selection config: {e}")
                
    async def select_story(self, current_context: Optional[Dict[str, Any]] = None) -> SelectionResult:
        """Select the best story to execute based on current state and context."""
        current_context = current_context or {}
        
        # Filter available stories based on basic criteria
        eligible_stories = self._filter_eligible_stories(current_context)
        
        if not eligible_stories:
            return SelectionResult(
                selected_story=None,
                selection_score=0.0,
                evaluation_metrics={},
                rejection_reasons=["No eligible stories available"]
            )
            
        # Score all eligible stories
        story_scores = []
        for story in eligible_stories:
            score = await self._evaluate_story(story, current_context)
            story_scores.append((story, score))
            
        # Sort by score and select the best
        story_scores.sort(key=lambda x: x[1], reverse=True)
        selected_story = story_scores[0][0] if story_scores else None
        selection_score = story_scores[0][1] if story_scores else 0.0
        
        # Generate evaluation metrics
        evaluation_metrics = {
            'total_eligible_stories': len(eligible_stories),
            'average_score': sum(score for _, score in story_scores) / len(story_scores) if story_scores else 0,
            'priority_distribution': self._get_priority_distribution(eligible_stories),
            'context_match_score': await self._calculate_context_match(selected_story, current_context) if selected_story else 0
        }
        
        return SelectionResult(
            selected_story=selected_story,
            selection_score=selection_score,
            evaluation_metrics=evaluation_metrics,
            competing_stories=[story for story, _ in story_scores[1:4]] if len(story_scores) > 1 else []
        )
        
    def _filter_eligible_stories(self, context: Dict[str, Any]) -> List[StoryInstance]:
        """Filter stories based on basic eligibility criteria."""
        eligible = []
        
        for story in self.available_stories.values():
            # Check if story is enabled
            if not story.enabled:
                continue
                
            # Check cooldown period
            if story.last_executed and story.cooldown_hours > 0:
                time_since_last = datetime.now() - story.last_executed
                if time_since_last.total_seconds() < story.cooldown_hours * 3600:
                    continue
                    
            # Check dependencies
            if not self._check_dependencies_met(story):
                continue
                
            # Check resource requirements
            if not self._check_resource_requirements(story, context):
                continue
                
            # Check context requirements
            if not self._check_context_requirements(story, context):
                continue
                
            # Check geographic coverage
            if not self._check_geographic_coverage(story, context):
                continue
                
            eligible.append(story)
            
        return eligible
        
    def _check_dependencies_met(self, story: StoryInstance) -> bool:
        """Check if all story dependencies are met."""
        if not story.dependencies:
            return True
            
        for dependency in story.dependencies:
            if dependency == 'raw_data_available':
                # Check if we have recent raw data
                if 'data/raw' not in self.context_state:
                    return False
            elif dependency == 'processed_data_available':
                # Check if we have recent processed data
                if 'data/processed' not in self.context_state:
                    return False
            # Add more dependency checks as needed
            
        return True
        
    def _check_resource_requirements(self, story: StoryInstance, context: Dict[str, Any]) -> bool:
        """Check if resource requirements are met."""
        resources = story.resource_requirements
        
        for resource, required_amount in resources.items():
            available_amount = self.resource_capacity.get(resource, 0)
            if available_amount < required_amount:
                return False
                
        return True
        
    def _check_context_requirements(self, story: StoryInstance, context: Dict[str, Any]) -> bool:
        """Check if context requirements are met."""
        # Check required files
        if 'required_files' in story.context_requirements:
            for file_path in story.context_requirements['required_files']:
                if not self._file_exists(file_path):
                    return False
                    
        # Check parameters
        if 'parameters' in story.context_requirements:
            for param, value in story.context_requirements['parameters'].items():
                if context.get(param) != value:
                    return False
                    
        return True
        
    def _check_geographic_coverage(self, story: StoryInstance, context: Dict[str, Any]) -> bool:
        """Check if geographic coverage requirements are met."""
        if not story.geographic_targets:
            return True
            
        # Check context for geographic information
        target_areas = context.get('target_areas', set())
        
        # Find intersection of story targets and current context targets
        overlap = story.geographic_targets.intersection(target_areas)
        
        # At least 50% overlap required
        return len(overlap) >= len(story.geographic_targets) * 0.5
        
    def _file_exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        path = Path(file_path)
        return path.exists()
        
    async def _evaluate_story(self, story: StoryInstance, context: Dict[str, Any]) -> float:
        """Evaluate a story based on multiple criteria."""
        scores = {}
        
        # Priority score
        priority_score = self._calculate_priority_score(story)
        scores[SelectionCriteria.PRIORITY.value] = priority_score
        
        # Dependency score
        dependency_score = self._calculate_dependency_score(story)
        scores[SelectionCriteria.DEPENDENCY.value] = dependency_score
        
        # Context score
        context_score = await self._calculate_context_score(story, context)
        scores[SelectionCriteria.CONTEXT.value] = context_score
        
        # Time since last run score
        time_score = self._calculate_time_score(story)
        scores[SelectionCriteria.TIME_SINCE_LAST_RUN.value] = time_score
        
        # Business impact score
        business_score = story.business_impact_score
        scores[SelectionCriteria.BUSINESS_IMPACT.value] = business_score
        
        # Resource requirement score
        resource_score = self._calculate_resource_score(story, context)
        scores[SelectionCriteria.RESOURCE_REQUIREMENT.value] = resource_score
        
        # Quality threshold score
        quality_score = self._calculate_quality_score(story)
        scores[SelectionCriteria.QUALITY_THRESHOLD.value] = quality_score
        
        # Weighted sum
        total_score = 0.0
        for criterion, score in scores.items():
            weight = self.selection_weights.get(criterion, 0.1)
            total_score += score * weight
            
        return min(total_score, 1.0)
        
    def _calculate_priority_score(self, story: StoryInstance) -> float:
        """Calculate priority score."""
        priority_scores = {
            StoryPriority.P0: 1.0,
            StoryPriority.P1: 0.8,
            StoryPriority.P2: 0.6,
            StoryPriority.P3: 0.4
        }
        return priority_scores.get(story.priority, 0.5)
        
    def _calculate_dependency_score(self, story: StoryInstance) -> float:
        """Calculate dependency fulfillment score."""
        if not story.dependencies:
            return 1.0
            
        met_dependencies = 0
        for dependency in story.dependencies:
            if self._dependency_met(dependency):
                met_dependencies += 1
                
        return met_dependencies / len(story.dependencies)
        
    def _dependency_met(self, dependency: str) -> bool:
        """Check if a specific dependency is met."""
        if dependency == 'raw_data_available':
            return self._check_raw_data_available()
        elif dependency == 'processed_data_available':
            return self._check_processed_data_available()
        return False
        
    def _check_raw_data_available(self) -> bool:
        """Check if raw data is available."""
        raw_data_path = Path("data/raw")
        if not raw_data_path.exists():
            return False
        return any(raw_data_path.glob("*.jsonl"))
        
    def _check_processed_data_available(self) -> bool:
        """Check if processed data is available."""
        processed_data_path = Path("data/processed")
        if not processed_data_path.exists():
            return False
        return any(processed_data_path.glob("*.jsonl"))
        
    async def _calculate_context_score(self, story: StoryInstance, context: Dict[str, Any]) -> float:
        """Calculate context match score."""
        score = 0.0
        max_score = 0.0
        
        # Check geographic targets
        if story.geographic_targets:
            target_areas = context.get('target_areas', set())
            geo_overlap = story.geographic_targets.intersection(target_areas)
            geo_score = len(geo_overlap) / len(story.geographic_targets) if story.geographic_targets else 0
            score += geo_score * 0.4
            max_score += 0.4
            
        # Check vertical targets
        if story.vertical_targets:
            current_verticals = context.get('verticals', set())
            vert_overlap = story.vertical_targets.intersection(current_verticals)
            vert_score = len(vert_overlap) / len(story.vertical_targets) if story.vertical_targets else 0
            score += vert_score * 0.3
            max_score += 0.3
            
        # Check business focus
        business_focus = context.get('business_focus', 'general')
        if business_focus != 'general':
            if business_focus.lower() in story.epic.lower() or story.epic.lower() in business_focus.lower():
                score += 0.3
            max_score += 0.3
            
        return score if max_score > 0 else 1.0
        
    def _calculate_time_score(self, story: StoryInstance) -> float:
        """Calculate time-based execution score."""
        if story.last_executed is None:
            return 1.0
            
        hours_since_last = (datetime.now() - story.last_executed).total_seconds() / 3600
        
        # Different execution intervals based on priority
        if story.priority == StoryPriority.P0:
            target_interval = 4  # Every 4 hours
        elif story.priority == StoryPriority.P1:
            target_interval = 24  # Daily
        elif story.priority == StoryPriority.P2:
            target_interval = 72  # Every 3 days
        else:
            target_interval = 168  # Weekly
            
        # Calculate score based on time elapsed
        if hours_since_last >= target_interval:
            return 1.0
        else:
            return hours_since_last / target_interval
            
    def _calculate_resource_score(self, story: StoryInstance, context: Dict[str, Any]) -> float:
        """Calculate resource availability score."""
        resources = story.resource_requirements
        
        if not resources:
            return 1.0
            
        total_score = 0.0
        for resource, required_amount in resources.items():
            available_amount = self.resource_capacity.get(resource, 0)
            if available_amount >= required_amount:
                total_score += 1.0
            else:
                # Partial score based on availability
                total_score += available_amount / required_amount
                
        return total_score / len(resources)
        
    def _calculate_quality_score(self, story: StoryInstance) -> float:
        """Calculate quality threshold score."""
        if not story.quality_thresholds:
            return 1.0
            
        # Check if recent executions meet quality thresholds
        if story.execution_count > 0:
            return story.success_rate
        else:
            return 0.5  # Default score for unexecuted stories
            
    def _get_priority_distribution(self, stories: List[StoryInstance]) -> Dict[str, int]:
        """Get distribution of priorities in a list of stories."""
        distribution = {priority.value: 0 for priority in StoryPriority}
        for story in stories:
            distribution[story.priority.value] += 1
        return distribution
        
    async def _calculate_context_match(self, story: StoryInstance, context: Dict[str, Any]) -> float:
        """Calculate overall context match score."""
        return await self._calculate_context_score(story, context)
        
    async def update_execution_result(self, story_id: str, success: bool, 
                                 execution_time: float, resource_usage: Dict[str, Any]):
        """Update the selector with the result of story execution."""
        if story_id not in self.available_stories:
            return
            
        story = self.available_stories[story_id]
        
        # Update execution history
        if story_id not in self.execution_history:
            self.execution_history[story_id] = []
        self.execution_history[story_id].append(datetime.now())
        
        # Update last execution time
        story.last_executed = datetime.now()
        story.execution_count += 1
        
        # Update success rate
        previous_success_rate = story.success_rate
        if story.execution_count == 1:
            story.success_rate = 1.0 if success else 0.0
        else:
            # Exponential moving average
            alpha = 0.3  # Weight for new result
            story.success_rate = (alpha * (1.0 if success else 0.0) + 
                               (1 - alpha) * previous_success_rate)
        
        # Update resource capacity
        for resource, usage in resource_usage.items():
            current_capacity = self.resource_capacity.get(resource, 1.0)
            self.resource_capacity[resource] = max(0, current_capacity - usage)
            
        self.logger.info(f"Updated execution result for story {story_id}: "
                        f"success={success}, new_success_rate={story.success_rate:.2f}")
        
    async def recover_resources(self):
        """Recover resource capacity based on time elapsed."""
        for resource, current_capacity in self.resource_capacity.items():
            # Recover 10% of capacity each hour
            if current_capacity < 1.0:
                recovery_rate = 0.1
                self.resource_capacity[resource] = min(1.0, current_capacity + recovery_rate)
                
    def get_story_status(self) -> Dict[str, Any]:
        """Get the current status of all stories."""
        status = {
            'total_stories': len(self.available_stories),
            'enabled_stories': len([s for s in self.available_stories.values() if s.enabled]),
            'last_execution': {},
            'success_rates': {},
            'priority_distribution': {}
        }
        
        for story_id, story in self.available_stories.items():
            status['last_execution'][story_id] = story.last_executed.isoformat() if story.last_executed else None
            status['success_rates'][story_id] = story.success_rate
            
        priority_dist = {}
        for priority in StoryPriority:
            priority_dist[priority.value] = len([s for s in self.available_stories.values() 
                                               if s.priority == priority and s.enabled])
        status['priority_distribution'] = priority_dist
        
        return status
