import pytest
import asyncio
import os
import sys
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.integration.integration_layer import IntegrationLayer, IntegrationConfig
from dynamic.story_selector import StorySelector
from main import BMADOrchestrator


class TestBMADOrchestrator:
    """Test suite for the BMADOrchestrator class."""
    
    @pytest.fixture
    def mock_story_selector(self):
        """Create a mock story selector."""
        with patch('dynamic.story_selector.StorySelector') as mock:
            selector = MagicMock()
            selector.list_stories.return_value = ['Test Story 1', 'Test Story 2']
            selector.select_story.return_value = {
                'id': 'TEST-01',
                'name': 'Test Story 1',
                'priority': 'P0',
                'tasks': []
            }
            selector.select_by_priority.return_value = [
                {'id': 'TEST-01', 'name': 'Test Story 1', 'priority': 'P0'}
            ]
            mock.return_value = selector
            yield mock
            
    @pytest.fixture
    def mock_integration_layer(self):
        """Create a mock integration layer."""
        with patch('src.integration.integration_layer.IntegrationLayer') as mock:
            integration = MagicMock()
            integration.translate_story_format.return_value = {
                'translated_story': 'data'
            }
            integration.send_to_bmad.return_value = {
                'status': 'success',
                'execution_id': '123'
            }
            integration.close.return_value = None
            mock.return_value = integration
            yield mock
            
    @pytest.fixture
    def orchestrator(self, mock_story_selector, mock_integration_layer):
        """Create a BMADOrchestrator instance with mocked dependencies."""
        config = {
            'goose_api_endpoint': 'http://test-goose/api',
            'bmad_endpoint': 'http://test-bmad/api',
            'auth_token': 'test-token',
            'timeout': 10,
            'stories_dir': 'test_stories'
        }
        
        orchestrator = BMADOrchestrator(config)
        orchestrator.story_selector = mock_story_selector.return_value
        orchestrator.integration_layer = mock_integration_layer.return_value
        
        return orchestrator
        
    @pytest.mark.asyncio
    async def test_initialize(self):
        """Test orchestrator initialization."""
        with patch('src.integration.integration_layer.IntegrationLayer') as mock_integration, \
             patch('dynamic.story_selector.StorySelector') as mock_selector:
            
            config = {
                'goose_api_endpoint': 'http://test-goose/api',
                'bmad_endpoint': 'http://test-bmad/api',
                'auth_token': 'test-token'
            }
            
            orchestrator = BMADOrchestrator(config)
            await orchestrator.initialize()
            
            # Check that integration layer was created with correct config
            mock_integration.assert_called_once()
            call_args = mock_integration.call_args[1]
            assert call_args['goose_api_endpoint'] == 'http://test-goose/api'
            assert call_args['bmad_api_endpoint'] == 'http://test-bmad/api'
            assert call_args['auth_token'] == 'test-token'
            
            # Check that story selector was created
            mock_selector.assert_called_once()
            
            # Check that components were set
            assert orchestrator.integration_layer is not None
            assert orchestrator.story_selector is not None
            
    @pytest.mark.asyncio
    async def test_shutdown(self, orchestrator):
        """Test orchestrator shutdown."""
        await orchestrator.shutdown()
        
        # Check that integration layer close was called
        orchestrator.integration_layer.close.assert_called_once()
        
    def test_list_available_stories(self, orchestrator):
        """Test listing available stories."""
        stories = orchestrator.list_available_stories()
        
        # Check that story selector method was called
        orchestrator.story_selector.list_stories.assert_called_once()
        
        # Check that stories are returned
        assert len(stories) == 2
        
    def test_get_story_by_name(self, orchestrator):
        """Test getting a story by name."""
        story = orchestrator.get_story_by_name('Test Story 1')
        
        # Check that story selector method was called
        orchestrator.story_selector.select_story.assert_called_once_with('Test Story 1')
        
        # Check that story is returned
        assert story['name'] == 'Test Story 1'
        assert story['id'] == 'TEST-01'
        
    def test_get_story_by_name_not_found(self, orchestrator):
        """Test getting a non-existent story by name."""
        orchestrator.story_selector.select_story.return_value = None
        
        story = orchestrator.get_story_by_name('Non-existent Story')
        
        assert story is None
        
    def test_get_stories_by_priority(self, orchestrator):
        """Test getting stories by priority."""
        stories = orchestrator.get_stories_by_priority('P0')
        
        # Check that story selector method was called
        orchestrator.story_selector.select_by_priority.assert_called_once_with('P0')
        
        # Check that stories are returned
        assert len(stories) == 1
        assert stories[0]['priority'] == 'P0'
        
    @pytest.mark.asyncio
    async def test_execute_story_success(self, orchestrator):
        """Test successful story execution."""
        story_params = {'param1': 'value1'}
        result = await orchestrator.execute_story('Test Story 1', story_params)
        
        # Check that story was selected
        orchestrator.story_selector.select_story.assert_called_once_with('Test Story 1')
        
        # Check that story was translated
        orchestrator.integration_layer.translate_story_format.assert_called_once()
        call_args = orchestrator.integration_layer.translate_story_format.call_args[0][0]
        assert call_args['story']['name'] == 'Test Story 1'
        assert call_args['parameters'] == story_params
        
        # Check that story was sent to BMAD
        orchestrator.integration_layer.send_to_bmad.assert_called_once()
        call_args = orchestrator.integration_layer.send_to_bmad.call_args[0][0]
        assert call_args['translated_story'] == 'data'
        
        # Check that result is returned
        assert result['status'] == 'success'
        assert result['execution_id'] == '123'
        
    @pytest.mark.asyncio
    async def test_execute_story_not_found(self, orchestrator):
        """Test executing a non-existent story."""
        orchestrator.story_selector.select_story.return_value = None
        
        with pytest.raises(ValueError, match="Story 'Non-existent Story' not found"):
            await orchestrator.execute_story('Non-existent Story')
            
    @pytest.mark.asyncio
    async def test_execute_story_integration_error(self, orchestrator):
        """Test handling of integration errors during story execution."""
        # Make integration layer raise an exception
        orchestrator.integration_layer.send_to_bmad.side_effect = Exception("Integration error")
        
        with pytest.raises(Exception, match="Integration error"):
            await orchestrator.execute_story('Test Story 1')
            
    @pytest.mark.asyncio
    async def test_execute_story_not_initialized(self):
        """Test executing a story when orchestrator is not initialized."""
        orchestrator = BMADOrchestrator()
        
        with pytest.raises(RuntimeError, match="BMAD Orchestrator not initialized"):
            await orchestrator.execute_story('Test Story 1')
            
    @pytest.mark.asyncio
    async def test_execute_all_stories(self, orchestrator):
        """Test executing all stories."""
        stories = [
            {'name': 'Story 1', 'id': 'S1', 'priority': 'P0'},
            {'name': 'Story 2', 'id': 'S2', 'priority': 'P1'}
        ]
        
        # Mock story selector to return stories
        orchestrator.story_selector.list_stories.return_value = ['Story 1', 'Story 2']
        orchestrator.story_selector.select_story.side_effect = stories
        
        results = await orchestrator.execute_all_stories()
        
        # Check that each story was executed
        assert len(results) == 2
        assert 'Story 1' in results
        assert 'Story 2' in results
        assert results['Story 1']['status'] == 'success'
        assert results['Story 2']['status'] == 'success'
        
        # Check that integration layer methods were called for each story
        assert orchestrator.integration_layer.send_to_bmad.call_count == 2
        
    @pytest.mark.asyncio
    async def test_execute_all_stories_with_priority(self, orchestrator):
        """Test executing all stories with priority filter."""
        stories = [
            {'name': 'P0 Story', 'id': 'P0', 'priority': 'P0'}
        ]
        
        # Mock story selector to return stories for priority filter
        orchestrator.story_selector.select_by_priority.return_value = stories
        
        results = await orchestrator.execute_all_stories(priority='P0')
        
        # Check that only P0 stories were executed
        assert len(results) == 1
        assert 'P0 Story' in results
        
        # Check that priority filter was used
        orchestrator.story_selector.select_by_priority.assert_called_once_with('P0')
        
    @pytest.mark.asyncio
    async def test_execute_all_stories_with_error(self, orchestrator):
        """Test executing all stories with some failures."""
        stories = [
            {'name': 'Success Story', 'id': 'S1', 'priority': 'P0'},
            {'name': 'Error Story', 'id': 'E1', 'priority': 'P1'}
        ]
        
        # Mock story selector to return stories
        orchestrator.story_selector.list_stories.return_value = ['Success Story', 'Error Story']
        orchestrator.story_selector.select_story.side_effect = stories
        
        # Make one execution fail
        orchestrator.integration_layer.send_to_bmad.side_effect = [
            {'status': 'success', 'execution_id': '123'},
            Exception("Execution failed")
        ]
        
        results = await orchestrator.execute_all_stories()
        
        # Check that both stories have results
        assert len(results) == 2
        assert results['Success Story']['status'] == 'success'
        assert 'error' in results['Error Story']
        assert results['Error Story']['error'] == 'Execution failed'
        
    @pytest.mark.asyncio
    async def test_execute_story_calls_integration_methods(self, orchestrator):
        """Test that execute_story properly calls integration layer methods."""
        await orchestrator.execute_story('Test Story 1', {'param': 'value'})
        
        # Check that translate_story_format was called with correct data
        call_args = orchestrator.integration_layer.translate_story_format.call_args[0][0]
        assert call_args['story']['name'] == 'Test Story 1'
        assert call_args['parameters'] == {'param': 'value'}
        
        # Check that send_to_bmad was called
        orchestrator.integration_layer.send_to_bmad.assert_called_once()
