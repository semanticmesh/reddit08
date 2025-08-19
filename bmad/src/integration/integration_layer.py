"""
Goose-BMAD Integration Layer
Handles communication and data exchange between Goose and BMAD systems.
"""

import json
import logging
import asyncio
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import httpx
import yaml

@dataclass
class IntegrationConfig:
    """Configuration for the integration layer."""
    goose_api_endpoint: str = "http://localhost:3000/api"
    bmad_api_endpoint: str = "http://localhost:8080/api"
    auth_token: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    stories_dir: str = "bmad/stories"

class IntegrationLayer:
    """Integration layer between Goose and BMAD systems."""
    
    def __init__(self, config: Optional[IntegrationConfig] = None):
        self.config = config or IntegrationConfig()
        self.logger = logging.getLogger(__name__)
        self.http_client = httpx.AsyncClient(
            timeout=self.config.timeout,
            headers={"Authorization": f"Bearer {self.config.auth_token}"} if self.config.auth_token else {}
        )
        
    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
        
    async def send_to_goose(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send data to Goose API."""
        try:
            response = await self.http_client.post(
                f"{self.config.goose_api_endpoint}/stories/execute",
                json=data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to send data to Goose: {e}")
            raise
            
    async def send_to_bmad(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send data to BMAD API."""
        try:
            response = await self.http_client.post(
                f"{self.config.bmad_api_endpoint}/stories/execute",
                json=data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to send data to BMAD: {e}")
            raise
            
    async def translate_story_format(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate story format between Goose and BMAD."""
        # Convert Goose format to BMAD format
        translated = {
            "id": story_data.get("id", "auto-generated"),
            "name": story_data.get("name", "Untitled Story"),
            "description": story_data.get("description", ""),
            "priority": story_data.get("priority", "P1"),
            "tasks": story_data.get("tasks", []),
            "outputs": story_data.get("outputs", {}),
            "acceptance_criteria": story_data.get("acceptance_criteria", {})
        }
        
        # Add BMAD-specific metadata if present
        if "bmad_metadata" in story_data:
            translated.update(story_data["bmad_metadata"])
            
        return translated
        
    async def sync_state(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync state between Goose and BMAD systems."""
        # Implement state synchronization logic
        return {
            "status": "synced",
            "timestamp": state_data.get("timestamp"),
            "changes": state_data.get("changes", [])
        }
        
    def load_story_from_file(self, story_path: str) -> Dict[str, Any]:
        """Load a story from a file."""
        try:
            with open(story_path, 'r') as f:
                content = f.read()
                
            # Parse YAML from the content
            story_docs = content.strip().split("\n---\n")
            for doc in story_docs:
                doc_clean = "\n".join(line for line in doc.splitlines() if not line.strip().startswith('#'))
                story = yaml.safe_load(doc_clean)
                if story:
                    return story
                    
            return {}
        except Exception as e:
            self.logger.error(f"Failed to load story from {story_path}: {e}")
            return {}
            
    def save_story_to_file(self, story_data: Dict[str, Any], filename: str) -> str:
        """Save a story to a file."""
        stories_dir = self.config.stories_dir
        if not os.path.exists(stories_dir):
            os.makedirs(stories_dir)
            
        file_path = os.path.join(stories_dir, filename)
        
        try:
            with open(file_path, 'w') as f:
                yaml.dump(story_data, f, default_flow_style=False)
            return file_path
        except Exception as e:
            self.logger.error(f"Failed to save story to {file_path}: {e}")
            raise
            
    def list_available_stories(self) -> List[Dict[str, Any]]:
        """List all available stories from the stories directory."""
        stories = []
        stories_file = os.path.join(self.config.stories_dir, "bmad_stories.txt")
        
        if not os.path.exists(stories_file):
            self.logger.warning(f"Stories file not found: {stories_file}")
            return stories
            
        try:
            with open(stories_file, 'r') as f:
                content = f.read()
                
            story_docs = content.strip().split("\n---\n")
            for doc in story_docs:
                doc_clean = "\n".join(line for line in doc.splitlines() if not line.strip().startswith('#'))
                story = yaml.safe_load(doc_clean)
                if story:
                    stories.append(story)
                    
        except Exception as e:
            self.logger.error(f"Failed to list stories: {e}")
            
        return stories
