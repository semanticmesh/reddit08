# mcp/native_server/server.py
"""
Native MCP Server Implementation for CRE Intelligence
Provides the same tools as FastAPI but through MCP protocol
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import websockets
from websockets.server import WebSocketServerProtocol

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the core implementations from FastAPI module
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from mcp.fastapi_app.main import (
    PayloadOptimizer,
    PhraseMiner,
    ClientSideFilterEngine,
    LocalSubTargeting,
    VerticalSpecializer,
    DualSortStrategy
)

# ============================================================================
# MCP Protocol Implementation
# ============================================================================

@dataclass
class MCPMessage:
    """MCP Protocol Message"""
    id: str
    method: str
    params: Dict[str, Any]
    
    @classmethod
    def from_json(cls, data: str) -> 'MCPMessage':
        """Parse MCP message from JSON"""
        parsed = json.loads(data)
        return cls(
            id=parsed.get('id', ''),
            method=parsed.get('method', ''),
            params=parsed.get('params', {})
        )
    
    def to_response(self, result: Any = None, error: Any = None) -> str:
        """Create response message"""
        response = {
            'id': self.id,
            'jsonrpc': '2.0'
        }
        
        if error:
            response['error'] = {
                'code': -32603,
                'message': str(error)
            }
        else:
            response['result'] = result
            
        return json.dumps(response)

@dataclass
class MCPToolDefinition:
    """MCP Tool Definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Any  # Callable

# ============================================================================
# MCP Server Implementation
# ============================================================================

class CREIntelligenceMCPServer:
    """Native MCP Server for CRE Intelligence Tools"""
    
    def __init__(self, host: str = "localhost", port: int = 8001):
        self.host = host
        self.port = port
        self.tools: Dict[str, MCPToolDefinition] = {}
        self.connections: set = set()
        
        # Initialize tool implementations
        self.payload_optimizer = PayloadOptimizer()
        self.phrase_miner = PhraseMiner()
        self.filter_engine = ClientSideFilterEngine()
        self.local_targeter = LocalSubTargeting()
        self.vertical_specializer = VerticalSpecializer()
        self.dual_sort_strategy = DualSortStrategy()
        
        # Register tools
        self._register_tools()
        
    def _register_tools(self):
        """Register all available tools"""
        
        # Technique 1: Payload Optimization
        self.register_tool(
            name="optimize_payload",
            description="Iteratively refine Apify Actor JSON payloads",
            parameters={
                "subreddits": {"type": "array", "items": {"type": "string"}},
                "keywords": {"type": "array", "items": {"type": "string"}},
                "date_start": {"type": "string"},
                "date_end": {"type": "string"},
                "max_url_length": {"type": "integer", "default": 512},
                "optimization_rounds": {"type": "integer", "default": 3}
            },
            handler=self._handle_optimize_payload
        )
        
        # Technique 2: Phrase Mining
        self.register_tool(
            name="mine_phrases",
            description="Extract phrases using TF-IDF analysis",
            parameters={
                "corpus_source": {"type": "string", "default": "last_month"},
                "ngram_range": {"type": "array", "default": [1, 3]},
                "top_k": {"type": "integer", "default": 100},
                "domain_categories": {"type": "array", "items": {"type": "string"}}
            },
            handler=self._handle_mine_phrases
        )
        
        # Technique 3: Client-Side Filtering
        self.register_tool(
            name="filter_posts",
            description="Apply 6-stage filtering pipeline",
            parameters={
                "date_start": {"type": "string"},
                "date_end": {"type": "string"},
                "keywords": {"type": "array", "items": {"type": "string"}},
                "exclude_keywords": {"type": "array", "items": {"type": "string"}},
                "quality_thresholds": {"type": "object"},
                "semantic_similarity_threshold": {"type": "number"},
                "city": {"type": "string", "nullable": True}
            },
            handler=self._handle_filter_posts
        )
        
        # Technique 4: Local-Sub Targeting
        self.register_tool(
            name="target_local_subs",
            description="Target and expand local subreddit coverage",
            parameters={
                "metro_areas": {"type": "array", "items": {"type": "string"}},
                "discover_new_subs": {"type": "boolean", "default": True},
                "regional_keywords": {"type": "object"}
            },
            handler=self._handle_target_local_subs
        )
        
        # Technique 5: Vertical Specialization
        self.register_tool(
            name="specialize_verticals",
            description="Analyze and specialize for CRE verticals",
            parameters={
                "verticals": {"type": "array", "items": {"type": "string"}},
                "custom_lexicons": {"type": "object"},
                "conflict_resolution": {"type": "boolean", "default": True}
            },
            handler=self._handle_specialize_verticals
        )
        
        # Technique 6: Dual-Sort Strategy
        self.register_tool(
            name="execute_dual_sort",
            description="Execute dual-sort strategy with deduplication",
            parameters={
                "timeframe_days": {"type": "integer", "default": 30},
                "sort_strategies": {"type": "array", "items": {"type": "string"}},
                "deduplication": {"type": "boolean", "default": True},
                "backfill_months": {"type": "integer", "default": 0}
            },
            handler=self._handle_execute_dual_sort
        )
        
        # Meta tool: Execute full pipeline
        self.register_tool(
            name="execute_full_pipeline",
            description="Execute complete intelligence pipeline",
            parameters={
                "metros": {"type": "array", "items": {"type": "string"}},
                "verticals": {"type": "array", "items": {"type": "string"}},
                "date_start": {"type": "string"},
                "date_end": {"type": "string"}
            },
            handler=self._handle_full_pipeline
        )
        
        logger.info(f"Registered {len(self.tools)} MCP tools")
    
    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Any
    ):
        """Register a tool with the MCP server"""
        self.tools[name] = MCPToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler
        )
    
    async def _handle_optimize_payload(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payload optimization requests"""
        from mcp.fastapi_app.main import PayloadOptimizationRequest
        
        request = PayloadOptimizationRequest(**params)
        result = await self.payload_optimizer.optimize_payload(request)
        return result
    
    async def _handle_mine_phrases(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle phrase mining requests"""
        from mcp.fastapi_app.main import PhraseMiningRequest
        
        request = PhraseMiningRequest(**params)
        result = await self.phrase_miner.mine_phrases(request)
        return result
    
    async def _handle_filter_posts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle post filtering requests"""
        from mcp.fastapi_app.main import ClientSideFilterRequest
        
        request = ClientSideFilterRequest(**params)
        result = await self.filter_engine.filter_posts(request)
        return result
    
    async def _handle_target_local_subs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle local subreddit targeting requests"""
        from mcp.fastapi_app.main import LocalSubTargetingRequest
        
        request = LocalSubTargetingRequest(**params)
        result = await self.local_targeter.target_local_subs(request)
        return result
    
    async def _handle_specialize_verticals(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle vertical specialization requests"""
        from mcp.fastapi_app.main import VerticalSpecializationRequest, VerticalCategory
        
        # Convert string verticals to enum
        if 'verticals' in params:
            params['verticals'] = [VerticalCategory(v) for v in params['verticals']]
        
        request = VerticalSpecializationRequest(**params)
        result = await self.vertical_specializer.specialize_verticals(request)
        return result
    
    async def _handle_execute_dual_sort(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dual-sort strategy requests"""
        from mcp.fastapi_app.main import DualSortStrategyRequest, SortStrategy
        
        # Convert string strategies to enum
        if 'sort_strategies' in params:
            params['sort_strategies'] = [SortStrategy(s) for s in params['sort_strategies']]
        
        request = DualSortStrategyRequest(**params)
        result = await self.dual_sort_strategy.execute_dual_sort(request)
        return result
    
    async def _handle_full_pipeline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle full pipeline execution requests"""
        # Implement full pipeline orchestration
        results = {}
        
        try:
            # Step 1: Optimize payloads
            payload_params = {
                "subreddits": ["r/commercialrealestate"] + [f"r/{m}" for m in params['metros']],
                "keywords": ["lease", "rent", "property", "commercial", "tenant"],
                "date_start": params['date_start'],
                "date_end": params['date_end']
            }
            results['payload_optimization'] = await self._handle_optimize_payload(payload_params)
            
            # Step 2: Mine phrases
            phrase_params = {"corpus_source": "last_month", "top_k": 100}
            results['phrase_mining'] = await self._handle_mine_phrases(phrase_params)
            
            # Step 3: Filter posts
            top_terms = results['phrase_mining'].get('top_terms', [])[:10]
            filter_params = {
                "date_start": params['date_start'],
                "date_end": params['date_end'],
                "keywords": [t['term'] for t in top_terms] if top_terms else []
            }
            results['filtering'] = await self._handle_filter_posts(filter_params)
            
            # Step 4: Target local subs
            local_params = {"metro_areas": params['metros']}
            results['local_targeting'] = await self._handle_target_local_subs(local_params)
            
            # Step 5: Specialize verticals
            vertical_params = {"verticals": params['verticals']}
            results['vertical_specialization'] = await self._handle_specialize_verticals(vertical_params)
            
            # Step 6: Execute dual-sort
            dual_params = {"timeframe_days": 30, "sort_strategies": ["new", "relevance"]}
            results['dual_sort'] = await self._handle_execute_dual_sort(dual_params)
            
            return {
                'ok': True,
                'pipeline_complete': True,
                'techniques_executed': 6,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            return {
                'ok': False,
                'error': str(e),
                'results': results
            }
    
    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle incoming WebSocket connections"""
        
        self.connections.add(websocket)
        logger.info(f"New connection from {websocket.remote_address}")
        
        try:
            # Send server capabilities on connect
            await websocket.send(json.dumps({
                'type': 'capabilities',
                'tools': [
                    {
                        'name': tool.name,
                        'description': tool.description,
                        'parameters': tool.parameters
                    }
                    for tool in self.tools.values()
                ]
            }))
            
            # Handle messages
            async for message in websocket:
                try:
                    msg = MCPMessage.from_json(message)
                    logger.info(f"Received: {msg.method}")
                    
                    # Route to appropriate handler
                    if msg.method == "tools.list":
                        # List available tools
                        result = [
                            {
                                'name': tool.name,
                                'description': tool.description,
                                'parameters': tool.parameters
                            }
                            for tool in self.tools.values()
                        ]
                        await websocket.send(msg.to_response(result=result))
                        
                    elif msg.method == "tools.call":
                        # Execute tool
                        tool_name = msg.params.get('name')
                        tool_params = msg.params.get('params', {})
                        
                        if tool_name in self.tools:
                            tool = self.tools[tool_name]
                            try:
                                result = await tool.handler(tool_params)
                                await websocket.send(msg.to_response(result=result))
                            except Exception as e:
                                logger.error(f"Tool execution error: {str(e)}")
                                await websocket.send(msg.to_response(error=str(e)))
                        else:
                            await websocket.send(msg.to_response(error=f"Unknown tool: {tool_name}"))
                            
                    else:
                        await websocket.send(msg.to_response(error=f"Unknown method: {msg.method}"))
                        
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received")
                    await websocket.send(json.dumps({
                        'error': 'Invalid JSON'
                    }))
                except Exception as e:
                    logger.error(f"Message handling error: {str(e)}")
                    await websocket.send(json.dumps({
                        'error': str(e)
                    }))
                    
        except websockets.ConnectionClosed:
            logger.info(f"Connection closed from {websocket.remote_address}")
        finally:
            self.connections.remove(websocket)
    
    async def start(self):
        """Start the MCP server"""
        logger.info(f"Starting MCP server on ws://{self.host}:{self.port}")
        
        async with websockets.serve(
            self.handle_connection,
            self.host,
            self.port
        ):
            logger.info(f"MCP server listening on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever

# ============================================================================
# MCP Client for Testing
# ============================================================================

class MCPTestClient:
    """Test client for MCP server"""
    
    def __init__(self, url: str):
        self.url = url
        self.websocket = None
        
    async def connect(self):
        """Connect to MCP server"""
        self.websocket = await websockets.connect(self.url)
        
        # Receive capabilities
        capabilities = await self.websocket.recv()
        logger.info(f"Server capabilities: {capabilities}")
        
    async def list_tools(self) -> List[Dict]:
        """List available tools"""
        message = json.dumps({
            'id': '1',
            'method': 'tools.list',
            'params': {}
        })
        
        await self.websocket.send(message)
        response = await self.websocket.recv()
        result = json.loads(response)
        
        return result.get('result', [])
    
    async def call_tool(self, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool"""
        message = json.dumps({
            'id': '2',
            'method': 'tools.call',
            'params': {
                'name': name,
                'params': params
            }
        })
        
        await self.websocket.send(message)
        response = await self.websocket.recv()
        result = json.loads(response)
        
        if 'error' in result:
            raise Exception(result['error'])
            
        return result.get('result', {})
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.websocket:
            await self.websocket.close()

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run the MCP server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CRE Intelligence MCP Server")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8001, help="Server port")
    parser.add_argument("--test", action="store_true", help="Run test client")
    
    args = parser.parse_args()
    
    if args.test:
        # Run test client
        async def test():
            client = MCPTestClient(f"ws://{args.host}:{args.port}")
            
            try:
                await client.connect()
                
                # List tools
                tools = await client.list_tools()
                print(f"Available tools: {len(tools)}")
                for tool in tools:
                    print(f"  - {tool['name']}: {tool['description']}")
                
                # Test filter_posts
                result = await client.call_tool('filter_posts', {
                    'date_start': '2024-01-01',
                    'date_end': '2024-01-31',
                    'keywords': ['lease', 'rent']
                })
                print(f"Filter result: {result}")
                
            finally:
                await client.disconnect()
        
        asyncio.run(test())
    else:
        # Run server
        server = CREIntelligenceMCPServer(host=args.host, port=args.port)
        asyncio.run(server.start())

if __name__ == "__main__":
    main()