"""
Resilience Testing for GooseAgent Stability
Tests for automatic recovery, fallback, and resilience features
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any
import httpx

# Import our resilience components
from src.goose.resilient_agent import ResilientGooseAgent, ResilientAgentConfig
from src.orchestration.dual_agent_coordinator import DualAgentCoordinator, DualAgentConfig
from src.orchestration.circuit_breaker import CircuitBreaker, CircuitBreakerOpen
from src.context.sliding_window_manager import SlidingWindowContextManager, ContextConfig
from src.orchestration.story_fragmenter import StoryFragmenter, FragmentationConfig
from src.knowledge.incremental_knowledge_base import IncrementalKnowledgeBase, KnowledgeConfig
from src.monitoring.agent_monitor import AgentMonitor, MonitorConfig

@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing"""
    with patch('src.goose.resilient_agent.httpx.AsyncClient') as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def resilient_agent(mock_http_client):
    """Create a ResilientGooseAgent for testing"""
    config = ResilientAgentConfig(max_retries=2, timeout=5, heartbeat_interval=1)
    agent = ResilientGooseAgent(config)
    # Replace the http client with the mock
    agent.http_client = mock_http_client
    return agent

@pytest.fixture
def dual_coordinator():
    """Create a DualAgentCoordinator for testing"""
    config = DualAgentConfig()
    return DualAgentCoordinator(config)

@pytest.fixture
def circuit_breaker():
    """Create a CircuitBreaker for testing"""
    return CircuitBreaker(failure_threshold=3, recovery_timeout=10)

@pytest.fixture
def context_manager():
    """Create a SlidingWindowContextManager for testing"""
    config = ContextConfig(max_tokens=1000, max_context_items=10)
    return SlidingWindowContextManager(config)

@pytest.fixture
def story_fragmenter():
    """Create a StoryFragmenter for testing"""
    config = FragmentationConfig(max_story_size=100, max_tasks_per_fragment=3)
    return StoryFragmenter(config)

@pytest.fixture
def knowledge_base():
    """Create an IncrementalKnowledgeBase for testing"""
    config = KnowledgeConfig(storage_path="/tmp/test_knowledge", enable_persistence=False)
    return IncrementalKnowledgeBase(config)

@pytest.fixture
def agent_monitor():
    """Create an AgentMonitor for testing"""
    config = MonitorConfig(
        health_check_interval=1,
        alert_thresholds={
            "response_time": 5000,  # ms
            "error_rate": 0.05,     # 5%
            "token_usage": 90000,   # tokens
            "connection_drops": 3   # count
        }
    )
    return AgentMonitor(config)

class TestResilientGooseAgent:
    """Tests for ResilientGooseAgent"""
    
    @pytest.mark.asyncio
    async def test_successful_connection(self, resilient_agent, mock_http_client):
        """Test successful connection to GooseAgent"""
        mock_http_client.get.return_value = AsyncMock(status_code=200)
        
        result = await resilient_agent.connect("http://test-api")
        
        assert result is True
        assert resilient_agent.connection_state == "connected"
        assert resilient_agent.agent == "http://test-api"
    
    @pytest.mark.asyncio
    async def test_failed_connection(self, resilient_agent, mock_http_client):
        """Test failed connection to GooseAgent"""
        mock_http_client.get.side_effect = Exception("Connection failed")
        
        result = await resilient_agent.connect("http://test-api")
        
        assert result is False
        assert resilient_agent.connection_state == "disconnected"
    
    @pytest.mark.asyncio
    async def test_heartbeat_mechanism(self, resilient_agent, mock_http_client):
        """Test heartbeat mechanism"""
        mock_http_client.get.return_value = AsyncMock(status_code=200)
        
        # Connect first
        await resilient_agent.connect("http://test-api")
        assert resilient_agent.connection_state == "connected"
        
        # Test ping
        mock_http_client.get.reset_mock()
        await resilient_agent.ping()
        
        mock_http_client.get.assert_called_once_with("http://test-api/health")
    
    @pytest.mark.asyncio
    async def test_execute_with_fallback(self, resilient_agent, mock_http_client):
        """Test execution with fallback to QWEN3"""
        # Mock successful connection
        mock_http_client.get.return_value = AsyncMock(status_code=200)
        await resilient_agent.connect("http://test-api")
        
        # Mock successful task execution
        mock_response = Mock()
        mock_response.json = Mock(return_value={"status": "success", "result": "test"})
        mock_response.raise_for_status = Mock()
        mock_http_client.post = AsyncMock(return_value=mock_response)
        
        task = {"name": "test_task", "data": "test_data"}
        result = await resilient_agent.execute_with_fallback(task)
        
        assert result["status"] == "success"
        assert result["result"] == "test"
    
    @pytest.mark.asyncio
    async def test_execute_with_fallback_failure(self, resilient_agent, mock_http_client):
        """Test execution with fallback when GooseAgent fails"""
        # Mock successful connection
        mock_http_client.get.return_value = AsyncMock(status_code=200)
        await resilient_agent.connect("http://test-api")
        
        # Mock failed task execution
        mock_http_client.post.side_effect = httpx.RequestError("Task failed")
        
        task = {"name": "test_task", "data": "test_data"}
        
        # Mock QWEN3 fallback
        async def mock_qwen3_fallback(task_data):
            return {"status": "success", "result": "qwen3_fallback"}
        
        result = await resilient_agent.execute_with_fallback(task, mock_qwen3_fallback)
        
        assert result["status"] == "success"
        assert result["result"] == "qwen3_fallback"

class TestDualAgentCoordinator:
    """Tests for DualAgentCoordinator"""
    
    @pytest.mark.asyncio
    async def test_story_execution_with_decomposition(self, dual_coordinator):
        """Test story execution with automatic decomposition"""
        # Mock the GooseAgent connection
        with patch.object(dual_coordinator.goose_agent, 'connect', AsyncMock()):
            with patch.object(dual_coordinator.goose_agent, 'execute_with_fallback', AsyncMock()) as mock_execute:
                # Mock successful execution
                mock_execute.return_value = {"status": "success", "result": "test"}
                
                # Large story that should be decomposed
                large_story = {
                    "id": "test_story",
                    "name": "Test Story",
                    "tasks": [{"task": f"task_{i}"} for i in range(10)],  # 10 tasks, should split
                    "outputs": {},
                    "acceptance_criteria": {}
                }
                
                # Mock QWEN3 validation
                with patch.object(dual_coordinator.qwen3_supervisor, 'validate_story', AsyncMock()) as mock_validate:
                    mock_validate.return_value = {
                        "valid": True,
                        "requires_decomposition": True,
                        "estimated_tokens": 15000
                    }
                    
                    result = await dual_coordinator.execute_story(large_story)
                    
                    # Should have decomposed into multiple subtasks
                    assert result["status"] == "success"
                    assert "results" in result

class TestCircuitBreaker:
    """Tests for CircuitBreaker"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_normal_operation(self, circuit_breaker):
        """Test circuit breaker in normal operation"""
        async def successful_function():
            return "success"
        
        # Should work normally
        result = await circuit_breaker.call(successful_function)
        assert result == "success"
        assert circuit_breaker.get_state()["state"] == "closed"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_open_state(self, circuit_breaker):
        """Test circuit breaker opens after failures"""
        async def failing_function():
            raise Exception("Failed")
        
        # Fail multiple times to open circuit
        for _ in range(circuit_breaker.failure_threshold):
            with pytest.raises(Exception):
                await circuit_breaker.call(failing_function)
        
        # Circuit should now be open
        assert circuit_breaker.get_state()["state"] == "open"
        
        # Next call should raise CircuitBreakerOpen
        with pytest.raises(CircuitBreakerOpen):
            await circuit_breaker.call(failing_function)

class TestContextManager:
    """Tests for SlidingWindowContextManager"""
    
    def test_context_addition_and_pruning(self, context_manager):
        """Test context addition and automatic pruning"""
        # Add some context
        for i in range(15):  # More than max_context_items
            context_manager.add_context(f"content_{i}", "normal")
        
        # Should be pruned to max size
        assert len(context_manager.context_window) <= context_manager.config.max_context_items
        
        # Add critical context (should not be pruned)
        context_manager.add_context("critical_content", "critical")
        assert len(context_manager.priority_context) == 1
    
    def test_token_limit_enforcement(self, context_manager):
        """Test token limit enforcement"""
        # Add large content to exceed token limit
        large_content = "x" * (context_manager.config.max_tokens * 2)  # Way over limit
        context_manager.add_context(large_content, "normal")
        
        # Should be pruned
        assert context_manager.get_total_tokens() <= context_manager.config.max_tokens

class TestStoryFragmenter:
    """Tests for StoryFragmenter"""
    
    def test_story_fragmentation(self, story_fragmenter):
        """Test story fragmentation"""
        # Large story that should be fragmented
        large_story = {
            "id": "large_story",
            "name": "Large Story",
            "tasks": [{"task": f"task_{i}"} for i in range(15)],  # 15 tasks, should split
            "outputs": {},
            "acceptance_criteria": {}
        }
        
        fragments = story_fragmenter.fragment_story(large_story)
        
        # Should have been fragmented
        assert len(fragments) > 1
        
        # Each fragment should have the right structure
        for i, fragment in enumerate(fragments):
            assert fragment["id"] == f"large_story_fragment_{i+1}"
            assert len(fragment["tasks"]) <= story_fragmenter.config.max_tasks_per_fragment

class TestIncrementalKnowledgeBase:
    """Tests for IncrementalKnowledgeBase"""
    
    @pytest.mark.asyncio
    async def test_incremental_updates(self, knowledge_base):
        """Test incremental knowledge updates"""
        # Initial state
        initial_count = len(knowledge_base.get_knowledge())
        
        # Apply delta update
        delta = {
            "new_key": "new_value",
            "+add_key": "add_value",
            "test_category": {"nested": "value"}
        }
        
        await knowledge_base.update_incremental(delta)
        
        # Should have new entries
        knowledge = knowledge_base.get_knowledge()
        assert len(knowledge) > initial_count
        assert knowledge["new_key"] == "new_value"
        assert knowledge["add_key"] == "add_value"
    
    def test_delta_operations(self, knowledge_base):
        """Test different delta operations"""
        # Add initial data
        knowledge_base.knowledge = {"existing": "value"}
        
        # Test add operation
        knowledge_base.apply_delta({"+new": "value"})
        assert knowledge_base.get_knowledge("new") == "value"
        
        # Test update operation
        knowledge_base.apply_delta({"~existing": "updated"})
        assert knowledge_base.get_knowledge("existing") == "updated"
        
        # Test remove operation
        knowledge_base.apply_delta({"-new": None})
        assert knowledge_base.get_knowledge("new") is None

class TestAgentMonitor:
    """Tests for AgentMonitor"""
    
    @pytest.mark.asyncio
    async def test_health_checking(self, agent_monitor):
        """Test agent health checking"""
        # Mock agent checker function
        async def mock_agent_checker():
            return {
                "response_time": 100,
                "token_usage": 5000,
                "error_rate": 0.01,
                "success": True
            }
        
        health = await agent_monitor.check_agent_health(mock_agent_checker)
        
        assert health.is_healthy()
        assert health.status == "healthy"
    
    @pytest.mark.asyncio
    async def test_degraded_detection(self, agent_monitor):
        """Test detection of degraded agent"""
        # Mock degraded agent
        async def mock_degraded_agent():
            return {
                "response_time": 10000,  # Way over threshold
                "token_usage": 5000,
                "error_rate": 0.01,
                "success": True
            }
        
        health = await agent_monitor.check_agent_health(mock_degraded_agent)
        
        print(f"Health status: {health.status}")
        print(f"Health degraded: {health.degraded}")
        print(f"Health metrics: {health.metrics}")
        
        assert health.is_degraded()
        assert health.status == "degraded"

if __name__ == "__main__":
    pytest.main([__file__])