#!/usr/bin/env python3
"""
BMAD Main Entry Point
Orchestrates story execution, manages the dynamic story selection mechanism,
and coordinates between Goose and BMAD systems.
"""

import asyncio
import logging
import argparse
import sys
import os
from typing import Dict, Any, List, Optional

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.integration.integration_layer import IntegrationLayer, IntegrationConfig
from dynamic.story_selector import StorySelector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bmad_main.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class BMADOrchestrator:
    """Main orchestrator for BMAD stories."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.integration_layer = None
        self.story_selector = None
        
    async def initialize(self):
        """Initialize the orchestrator components."""
        logger.info("Initializing BMAD Orchestrator...")
        
        # Initialize integration layer
        integration_config = IntegrationConfig(
            goose_api_endpoint=self.config.get('goose_api_endpoint', 'http://localhost:3000/api'),
            bmad_api_endpoint=self.config.get('bmad_api_endpoint', 'http://localhost:8080/api'),
            auth_token=self.config.get('auth_token'),
            timeout=self.config.get('timeout', 30),
            stories_dir=self.config.get('stories_dir', 'stories')
        )
        self.integration_layer = IntegrationLayer(integration_config)
        
        # Initialize story selector
        stories_dir = self.config.get('stories_dir', 'stories')
        self.story_selector = StorySelector(stories_dir)
        
        logger.info("BMAD Orchestrator initialized successfully")
        
    async def shutdown(self):
        """Shutdown the orchestrator components."""
        logger.info("Shutting down BMAD Orchestrator...")
        if self.integration_layer:
            await self.integration_layer.close()
        logger.info("BMAD Orchestrator shutdown complete")
        
    def list_available_stories(self) -> List[Dict[str, Any]]:
        """List all available stories."""
        if not self.story_selector:
            return []
        stories = []
        for story_name in self.story_selector.list_stories():
            story = self.story_selector.select_story(story_name)
            if story:
                stories.append(story)
        return stories
        
    def get_story_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a story by name."""
        if not self.story_selector:
            return None
        return self.story_selector.select_story(name)
        
    def get_stories_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """Get stories by priority."""
        if not self.story_selector:
            return []
        return self.story_selector.select_by_priority(priority)
        
    async def execute_story(self, story_name: str, story_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a specific story."""
        if not self.story_selector or not self.integration_layer:
            raise RuntimeError("BMAD Orchestrator not initialized")
            
        # Get the story
        story = self.story_selector.select_story(story_name)
        if not story:
            raise ValueError(f"Story '{story_name}' not found")
            
        logger.info(f"Executing story: {story_name}")
        
        # Prepare story execution data
        story_data = {
            "story": story,
            "parameters": story_params or {},
            "execution_id": f"exec_{story_name}_{int(asyncio.get_event_loop().time())}"
        }
        
        try:
            # Translate story format for execution
            translated_story = await self.integration_layer.translate_story_format(story_data)
            
            # Execute the story through the integration layer
            result = await self.integration_layer.send_to_bmad(translated_story)
            
            logger.info(f"Story {story_name} executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute story {story_name}: {e}")
            raise
            
    async def execute_all_stories(self, priority: str = None) -> Dict[str, Any]:
        """Execute all stories, optionally filtered by priority."""
        if priority:
            stories = self.get_stories_by_priority(priority)
        else:
            stories = self.list_available_stories()
            
        results = {}
        for story in stories:
            try:
                result = await self.execute_story(story.get("name"))
                results[story.get("name")] = result
            except Exception as e:
                logger.error(f"Failed to execute story {story.get('name')}: {e}")
                results[story.get("name")] = {"error": str(e)}
                
        return results


async def main():
    """Main entry point for the BMAD application."""
    parser = argparse.ArgumentParser(description="BMAD - Business Model As Documents")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--list-stories", action="store_true", help="List available stories")
    parser.add_argument("--execute-story", help="Name of story to execute")
    parser.add_argument("--priority", help="Filter stories by priority (P0, P1, P2, etc.)")
    parser.add_argument("--execute-all", action="store_true", help="Execute all stories")
    parser.add_argument("--goose-endpoint", default="http://localhost:3000/api", help="Goose API endpoint")
    parser.add_argument("--bmad-endpoint", default="http://localhost:8080/api", help="BMAD API endpoint")
    parser.add_argument("--auth-token", help="Authorization token")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    
    args = parser.parse_args()
    
    # Load configuration
    config = {
        "goose_api_endpoint": args.goose_endpoint,
        "bmad_api_endpoint": args.bmad_endpoint,
        "auth_token": args.auth_token,
        "timeout": args.timeout,
        "stories_dir": "stories"
    }
    
    # Create and initialize orchestrator
    orchestrator = BMADOrchestrator(config)
    await orchestrator.initialize()
    
    try:
        if args.list_stories:
            stories = orchestrator.list_available_stories()
            print("\nAvailable Stories:")
            for story in stories:
                print(f"- {story.get('name')} (ID: {story.get('id')}, Priority: {story.get('priority')})")
                
        elif args.execute_story:
            result = await orchestrator.execute_story(args.execute_story)
            print(f"\nStory execution result: {result}")
            
        elif args.execute_all:
            results = await orchestrator.execute_all_stories(args.priority)
            print(f"\nStory execution results:")
            for story_name, result in results.items():
                status = result.get("status", "completed")
                print(f"- {story_name}: {status}")
                
        else:
            parser.print_help()
            
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
