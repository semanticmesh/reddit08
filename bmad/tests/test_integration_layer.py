import pytest
import asyncio
import os
import sys
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.integration.integration_layer import IntegrationLayer, IntegrationConfig


class TestIntegrationLayer:
    """Test suite for the IntegrationLayer class."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return IntegrationConfig(
            goose_api_endpoint="http://test-goose/api",
            bmad_api_endpoint="http://test-bmad/api",
            auth_token="test-token",
            timeout=10,
            stories_dir="test_stories"
        )
        
    @pytest.fixture
    def integration_layer(self, config):
        """Create an IntegrationLayer instance with test config."""
        return IntegrationLayer(config)
        
    @pytest.mark.asyncio
    async def test_send_to_goose_success(self, integration_layer):
        """Test successful sending to Goose API."""
        mock_response = {
            "status": "success",
            "story_id": "123"
        }
        
        with patch.object(integration_layer.http_client, 'post') as mock_post:
            mock_post.return_value = MagicMock()
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status.return_value = None
            
            result = await integration_layer.send_to_goose({"test": "data"})
            
            assert result == mock_response
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[1]['json'] == {"test": "data"}
            assert "goose-api" in call_args[0][0]
            
    @pytest.mark.asyncio
    async def test_send_to_bmad_success(self, integration_layer):
        """Test successful sending to BMAD API."""
        mock_response = {
            "status": "success",
            "execution_id": "456"
        }
        
        with patch.object(integration_layer.http_client, 'post') as mock_post:
            mock_post.return_value = MagicMock()
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status.return_value = None
            
            result = await integration_layer.send_to_bmad({"test": "data"})
            
            assert result == mock_response
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[1]['json'] == {"test": "data"}
            assert "bmad-api" in call_args[0][0]
            
    @pytest.mark.asyncio
    async def test_send_to_goose_http_error(self, integration_layer):
        """Test handling of HTTP errors when sending to Goose."""
        import httpx
        
        with patch.object(integration_layer.http_client, 'post') as mock_post:
            mock_post.side_effect = httpx.HTTPError("Connection error")
            
            with pytest.raises(httpx.HTTPError):
                await integration_layer.send_to_goose({"test": "data"})
                
    def test_translate_story_format(self, integration_layer):
        """Test story format translation."""
        story_data = {
            "id": "test-id",
            "name": "Test Story",
            "description": "A test story",
            "priority": "P0",
            "tasks": [{"action": "test_action"}],
            "outputs": {"result": "output"},
            "acceptance_criteria": {"criteria": "must pass"},
            "bmad_metadata": {"custom_field": "value"}
        }
        
        result = integration_layer.translate_story_format(story_data)
        
        assert result["id"] == "test-id"
        assert result["name"] == "Test Story"
        assert result["priority"] == "P0"
        assert result["tasks"] == [{"action": "test_action"}]
        assert result["bmad_metadata"]["custom_field"] == "value"
        
    def test_sync_state(self, integration_layer):
        """Test state synchronization."""
        state_data = {
            "timestamp": "2023-01-01T00:00:00Z",
            "changes": [{"type": "add", "id": "123"}]
        }
        
        result = integration_layer.sync_state(state_data)
        
        assert result["status"] == "synced"
        assert result["timestamp"] == "2023-01-01T00:00:00Z"
        assert result["changes"] == [{"type": "add", "id": "123"}]
        
    def test_load_story_from_file(self, integration_layer, tmp_path):
        """Test loading a story from a file."""
        story_content = """
id: FILE-TEST-01
name: File Test Story
priority: P0
tasks:
  - action: file_test_action
    parameters: {"test": true}
"""
        
        story_file = tmp_path / "test_story.txt"
        story_file.write_text(story_content)
        
        result = integration_layer.load_story_from_file(str(story_file))
        
        assert result["id"] == "FILE-TEST-01"
        assert result["name"] == "File Test Story"
        assert result["priority"] == "P0"
        assert result["tasks"][0]["action"] == "file_test_action"
        
    def test_load_story_from_nonexistent_file(self, integration_layer):
        """Test loading a story from a non-existent file."""
        result = integration_layer.load_story_from_file("nonexistent_file.txt")
        assert result == {}
        
    def test_save_story_to_file(self, integration_layer, tmp_path):
        """Test saving a story to a file."""
        story_data = {
            "id": "SAVE-TEST-01",
            "name": "Save Test Story",
            "priority": "P0",
            "tasks": []
        }
        
        stories_dir = str(tmp_path / "stories")
        file_path = integration_layer.save_story_to_file(story_data, "save_test_story.txt")
        
        # Check file was created
        assert os.path.exists(file_path)
        
        # Check file content
        with open(file_path, 'r') as f:
            saved_content = f.read()
            
        loaded_story = integration_layer.load_story_from_file(file_path)
        assert loaded_story["id"] == "SAVE-TEST-01"
        assert loaded_story["name"] == "Save Test Story"
        
    def test_save_story_creates_directory(self, integration_layer, tmp_path):
        """Test that save_story creates the stories directory if it doesn't exist."""
        stories_dir = str(tmp_path / "new_stories")
        os.rmdir(stories_dir)  # Remove directory to test creation
        
        story_data = {"id": "TEST", "name": "Test", "priority": "P0"}
        file_path = integration_layer.save_story_to_file(story_data, "test_story.txt")
        
        assert os.path.exists(stories_dir)
        assert os.path.exists(file_path)
        
    def test_list_available_stories(self, integration_layer, tmp_path):
        """Test listing available stories."""
        # Create a mock stories file
        stories_dir = str(tmp_path / "stories")
        os.makedirs(stories_dir, exist_ok=True)
        
        stories_file = os.path.join(stories_dir, "bmad_stories.txt")
        with open(stories_file, 'w') as f:
            f.write("""
---
id: LIST-TEST-01
name: List Test Story 1
priority: P0
---
id: LIST-TEST-02
name: List Test Story 2
priority: P1
""")
        
        # Update config to use test directory
        integration_layer.config.stories_dir = stories_dir
        
        stories = integration_layer.list_available_stories()
        
        assert len(stories) == 2
        story_names = [s["name"] for s in stories]
        assert "List Test Story 1" in story_names
        assert "List Test Story 2" in story_names
        
    @pytest.mark.asyncio
    async def test_close_http_client(self, integration_layer):
        """Test closing the HTTP client."""
        with patch.object(integration_layer.http_client, 'aclose') as mock_close:
            await integration_layer.close()
            mock_close.assert_called_once()
            
    def test_default_config(self):
        """Test default configuration values."""
        config = IntegrationConfig()
        
        assert config.goose_api_endpoint == "http://localhost:3000/api"
        assert config.bmad_api_endpoint == "http://localhost:8080/api"
        assert config.auth_token is None
        assert config.timeout == 30
        assert config.max_retries == 3
