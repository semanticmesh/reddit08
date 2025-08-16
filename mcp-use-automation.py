# scripts/mcp_client_base.py
"""Base MCP client for automation scripts"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# This is a simplified MCP Use implementation
# Replace with actual mcp-use library when available
class MCPClient:
    """MCP Client for tool automation"""
    
    def __init__(self, server_url: str, api_key: Optional[str] = None):
        self.server_url = server_url
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.logger = logging.getLogger(__name__)
        
    async def connect(self):
        """Connect to MCP server"""
        self.logger.info(f"Connecting to MCP server: {self.server_url}")
        # Implement actual connection logic
        return True
        
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool"""
        self.logger.info(f"Calling tool: {tool_name} with params: {params}")
        
        # In production, this would make actual MCP calls
        # For now, make HTTP requests to FastAPI endpoints
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.server_url}/{tool_name}",
                json=params
            )
            return response.json()
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        self.logger.info("Disconnecting from MCP server")
        return True

# Load environment variables
load_dotenv()

def get_mcp_client(service: str = "fastapi") -> MCPClient:
    """Get configured MCP client for a service"""
    
    service_urls = {
        "fastapi": os.getenv("FASTAPI_MCP_URL", "http://localhost:8000"),
        "bmad": os.getenv("BMAD_MCP_URL", "ws://localhost:8001/mcp"),
        "reddit": os.getenv("REDDIT_MCP_URL", "ws://localhost:8002/mcp"),
        "phrase": os.getenv("PHRASE_MCP_URL", "ws://localhost:8003/mcp"),
    }
    
    return MCPClient(service_urls.get(service, service_urls["fastapi"]))

# ============================================================================
# scripts/run_filter_via_mcp.py
"""Execute filtering pipeline via MCP"""

import asyncio
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.mcp_client_base import get_mcp_client

async def run_filter(
    date_start: str,
    date_end: str,
    keywords: list = None,
    city: str = None,
    output_dir: str = None
):
    """Run client-side filtering via MCP"""
    
    client = get_mcp_client("fastapi")
    
    try:
        await client.connect()
        
        # Prepare filter request
        filter_params = {
            "date_start": date_start,
            "date_end": date_end,
            "keywords": keywords or [],
            "exclude_keywords": [],
            "quality_thresholds": {
                "min_length": 50,
                "max_length": 10000,
                "min_score": 1
            },
            "semantic_similarity_threshold": 0.4,
            "city": city
        }
        
        print(f"Running filter for {date_start} to {date_end}")
        if keywords:
            print(f"Keywords: {', '.join(keywords)}")
        if city:
            print(f"City: {city}")
        
        # Execute filtering
        result = await client.call_tool("filter_posts", filter_params)
        
        # Process results
        if result.get("ok"):
            print(f"✓ Filtered {result['filtered_count']} posts from {result['initial_count']}")
            print(f"  Retention rate: {result['retention_rate']:.2%}")
            print(f"  Output: {result['output_path']}")
            
            # Save filter report if output directory specified
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                
                report_path = output_path / f"filter_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(report_path, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"  Report saved: {report_path}")
            
            return result
        else:
            print(f"✗ Filtering failed: {result.get('message', 'Unknown error')}")
            return None
            
    finally:
        await client.disconnect()

def main():
    parser = argparse.ArgumentParser(description="Run CRE post filtering via MCP")
    parser.add_argument("--start", default=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                      help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default=datetime.now().strftime("%Y-%m-%d"),
                      help="End date (YYYY-MM-DD)")
    parser.add_argument("--keywords", nargs="+", help="Filter keywords")
    parser.add_argument("--city", help="Target city/metro")
    parser.add_argument("--output", help="Output directory for reports")
    
    args = parser.parse_args()
    
    asyncio.run(run_filter(
        date_start=args.start,
        date_end=args.end,
        keywords=args.keywords,
        city=args.city,
        output_dir=args.output
    ))

if __name__ == "__main__":
    main()

# ============================================================================
# scripts/refresh_tfidf_via_mcp.py
"""Refresh TF-IDF vocabulary via MCP"""

import asyncio
import argparse
import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from scripts.mcp_client_base import get_mcp_client

async def refresh_tfidf(
    corpus_source: str = "last_month",
    top_k: int = 100,
    categories: list = None
):
    """Refresh TF-IDF vocabulary via MCP"""
    
    client = get_mcp_client("fastapi")
    
    try:
        await client.connect()
        
        # Prepare mining request
        mining_params = {
            "corpus_source": corpus_source,
            "ngram_range": [1, 3],
            "top_k": top_k,
            "domain_categories": categories or [
                "financial", "legal", "operational", "market", "development"
            ]
        }
        
        print(f"Mining phrases from {corpus_source}")
        print(f"Extracting top {top_k} terms")
        
        # Execute phrase mining
        result = await client.call_tool("mine_phrases", mining_params)
        
        # Process results
        if result.get("ok"):
            print(f"✓ Extracted {result['total_terms_extracted']} terms")
            print(f"  Top terms saved to: {result['lexicon_path']}")
            print(f"  Emerging terms: {len(result.get('emerging_terms', []))}")
            
            # Display top terms by category
            if result.get('classified_terms'):
                print("\nTop terms by category:")
                for category, terms in result['classified_terms'].items():
                    if terms:
                        print(f"  {category}: {len(terms)} terms")
                        # Show first 3 terms
                        for term in terms[:3]:
                            if isinstance(term, tuple):
                                print(f"    - {term[0]} (score: {term[1]:.3f})")
                            else:
                                print(f"    - {term}")
            
            return result
        else:
            print(f"✗ Phrase mining failed: {result.get('message', 'Unknown error')}")
            return None
            
    finally:
        await client.disconnect()

def main():
    parser = argparse.ArgumentParser(description="Refresh TF-IDF vocabulary via MCP")
    parser.add_argument("--corpus", default="last_month",
                      help="Corpus source (last_month, last_week, all)")
    parser.add_argument("--top-k", type=int, default=100,
                      help="Number of top terms to extract")
    parser.add_argument("--categories", nargs="+",
                      help="Domain categories for classification")
    
    args = parser.parse_args()
    
    asyncio.run(refresh_tfidf(
        corpus_source=args.corpus,
        top_k=args.top_k,
        categories=args.categories
    ))

if __name__ == "__main__":
    main()

# ============================================================================
# scripts/expand_cities_via_mcp.py
"""Expand city/metro coverage via MCP"""

import asyncio
import argparse
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from scripts.mcp_client_base import get_mcp_client

async def expand_cities(
    metros: list,
    discover: bool = True,
    regional_keywords: dict = None
):
    """Expand city coverage via MCP"""
    
    client = get_mcp_client("fastapi")
    
    try:
        await client.connect()
        
        # Prepare targeting request
        targeting_params = {
            "metro_areas": metros,
            "discover_new_subs": discover,
            "regional_keywords": regional_keywords or {}
        }
        
        print(f"Expanding coverage for metros: {', '.join(metros)}")
        if discover:
            print("Discovering new subreddits enabled")
        
        # Execute local targeting
        result = await client.call_tool("target_local_subs", targeting_params)
        
        # Process results
        if result.get("ok"):
            print(f"✓ Targeted {result['metros_targeted']} metros")
            print(f"  Total subreddits: {result['total_subreddits']}")
            
            # Display metro details
            if result.get('metro_details'):
                for metro, details in result['metro_details'].items():
                    print(f"\n{metro.upper()}:")
                    print(f"  Subreddits: {len(details['subreddits'])}")
                    for sub in details['subreddits'][:5]:
                        print(f"    - {sub}")
                    print(f"  Keywords: {len(details['keywords'])}")
                    print(f"  Estimated volume: {details['estimated_volume']} posts/month")
            
            return result
        else:
            print(f"✗ City expansion failed: {result.get('message', 'Unknown error')}")
            return None
            
    finally:
        await client.disconnect()

def main():
    parser = argparse.ArgumentParser(description="Expand city coverage via MCP")
    parser.add_argument("metros", nargs="+", help="Metro areas to target")
    parser.add_argument("--no-discover", action="store_true",
                      help="Disable subreddit discovery")
    parser.add_argument("--keywords", type=json.loads,
                      help="Regional keywords as JSON")
    
    args = parser.parse_args()
    
    asyncio.run(expand_cities(
        metros=args.metros,
        discover=not args.no_discover,
        regional_keywords=args.keywords
    ))

if __name__ == "__main__":
    main()

# ============================================================================
# scripts/run_full_pipeline.py
"""Execute complete intelligence pipeline via MCP"""

import asyncio
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
from typing import Dict, Any

sys.path.append(str(Path(__file__).parent.parent))

from scripts.mcp_client_base import get_mcp_client

async def run_full_pipeline(
    metros: list,
    verticals: list,
    date_start: str,
    date_end: str,
    output_dir: str = None
) -> Dict[str, Any]:
    """Execute complete CRE intelligence pipeline"""
    
    client = get_mcp_client("fastapi")
    results = {}
    
    try:
        await client.connect()
        
        print("=" * 60)
        print("CRE INTELLIGENCE PIPELINE")
        print("=" * 60)
        print(f"Metros: {', '.join(metros)}")
        print(f"Verticals: {', '.join(verticals)}")
        print(f"Date range: {date_start} to {date_end}")
        print("=" * 60)
        
        # Step 1: Optimize payloads
        print("\n[1/6] Optimizing Apify payloads...")
        subreddits = ["r/commercialrealestate"] + [f"r/{m}" for m in metros]
        
        payload_result = await client.call_tool("optimize_payload", {
            "subreddits": subreddits,
            "keywords": ["lease", "rent", "property", "commercial", "tenant"],
            "date_start": date_start,
            "date_end": date_end,
            "max_url_length": 512,
            "optimization_rounds": 3
        })
        results['payload_optimization'] = payload_result
        
        if payload_result.get('optimized_payload'):
            print(f"  ✓ Payload optimized, size: {payload_result['final_metrics']['url_length']} chars")
        
        # Step 2: Mine phrases
        print("\n[2/6] Mining phrases with TF-IDF...")
        phrase_result = await client.call_tool("mine_phrases", {
            "corpus_source": "last_month",
            "ngram_range": [1, 3],
            "top_k": 100,
            "domain_categories": ["financial", "legal", "operational", "market", "development"]
        })
        results['phrase_mining'] = phrase_result
        
        if phrase_result.get('ok'):
            print(f"  ✓ Extracted {phrase_result['total_terms_extracted']} terms")
            top_terms = [t['term'] for t in phrase_result.get('top_terms', [])[:10]]
        else:
            top_terms = []
        
        # Step 3: Filter posts
        print("\n[3/6] Filtering posts...")
        filter_result = await client.call_tool("filter_posts", {
            "date_start": date_start,
            "date_end": date_end,
            "keywords": top_terms,
            "exclude_keywords": [],
            "quality_thresholds": {
                "min_length": 50,
                "max_length": 10000,
                "min_score": 1
            },
            "semantic_similarity_threshold": 0.4
        })
        results['filtering'] = filter_result
        
        if filter_result.get('ok'):
            print(f"  ✓ Filtered {filter_result['filtered_count']} posts")
            print(f"    Retention rate: {filter_result['retention_rate']:.2%}")
        
        # Step 4: Target local subs
        print("\n[4/6] Targeting local subreddits...")
        local_result = await client.call_tool("target_local_subs", {
            "metro_areas": metros,
            "discover_new_subs": True,
            "regional_keywords": {}
        })
        results['local_targeting'] = local_result
        
        if local_result.get('ok'):
            print(f"  ✓ Targeted {local_result['metros_targeted']} metros")
            print(f"    Total subreddits: {local_result['total_subreddits']}")
        
        # Step 5: Specialize verticals
        print("\n[5/6] Analyzing verticals...")
        vertical_result = await client.call_tool("specialize_verticals", {
            "verticals": verticals,
            "custom_lexicons": {},
            "conflict_resolution": True
        })
        results['vertical_specialization'] = vertical_result
        
        if vertical_result.get('ok'):
            print(f"  ✓ Processed {vertical_result['verticals_processed']} verticals")
            
            # Show top opportunities
            if vertical_result.get('top_opportunities'):
                print("    Top opportunities:")
                for opp in vertical_result['top_opportunities'][:3]:
                    print(f"      - {opp['vertical']}: score {opp['score']:.2f}")
        
        # Step 6: Execute dual-sort
        print("\n[6/6] Executing dual-sort strategy...")
        dual_result = await client.call_tool("execute_dual_sort", {
            "timeframe_days": 30,
            "sort_strategies": ["new", "relevance"],
            "deduplication": True,
            "backfill_months": 0
        })
        results['dual_sort'] = dual_result
        
        if dual_result.get('ok'):
            print(f"  ✓ Collected {dual_result['total_posts_collected']} posts")
            print(f"    Unique posts: {dual_result['unique_posts']}")
            print(f"    Coverage score: {dual_result['coverage_score']:.2f}")
        
        # Generate summary
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETE")
        print("=" * 60)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'parameters': {
                'metros': metros,
                'verticals': verticals,
                'date_range': f"{date_start} to {date_end}"
            },
            'results': {
                'posts_processed': filter_result.get('filtered_count', 0),
                'terms_extracted': len(phrase_result.get('top_terms', [])),
                'metros_covered': len(metros),
                'verticals_analyzed': len(verticals),
                'unique_posts': dual_result.get('unique_posts', 0)
            },
            'success': all([
                payload_result.get('optimized_payload'),
                phrase_result.get('ok'),
                filter_result.get('ok'),
                local_result.get('ok'),
                vertical_result.get('ok'),
                dual_result.get('ok')
            ])
        }
        
        print(f"Success: {'✓' if summary['success'] else '✗'}")
        print(f"Posts processed: {summary['results']['posts_processed']}")
        print(f"Terms extracted: {summary['results']['terms_extracted']}")
        
        # Save results if output directory specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save full results
            results_path = output_path / f"pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_path, 'w') as f:
                json.dump({
                    'summary': summary,
                    'detailed_results': results
                }, f, indent=2, default=str)
            
            print(f"\nResults saved to: {results_path}")
        
        return summary
        
    except Exception as e:
        print(f"\n✗ Pipeline failed: {str(e)}")
        raise
        
    finally:
        await client.disconnect()

def main():
    parser = argparse.ArgumentParser(description="Execute full CRE intelligence pipeline")
    parser.add_argument("--metros", nargs="+", 
                      default=["nyc", "sf", "chicago"],
                      help="Metro areas to analyze")
    parser.add_argument("--verticals", nargs="+",
                      default=["office", "retail", "industrial"],
                      help="Verticals to analyze")
    parser.add_argument("--start", 
                      default=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                      help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end",
                      default=datetime.now().strftime("%Y-%m-%d"),
                      help="End date (YYYY-MM-DD)")
    parser.add_argument("--output", help="Output directory for results")
    
    args = parser.parse_args()
    
    asyncio.run(run_full_pipeline(
        metros=args.metros,
        verticals=args.verticals,
        date_start=args.start,
        date_end=args.end,
        output_dir=args.output
    ))

if __name__ == "__main__":
    main()

# ============================================================================
# scripts/schedule_jobs.py
"""Schedule automated jobs using MCP Use"""

import asyncio
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging
import sys

sys.path.append(str(Path(__file__).parent.parent))

from scripts.run_filter_via_mcp import run_filter
from scripts.refresh_tfidf_via_mcp import refresh_tfidf
from scripts.expand_cities_via_mcp import expand_cities
from scripts.run_full_pipeline import run_full_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CREScheduler:
    """Scheduler for CRE intelligence automation"""
    
    def __init__(self):
        self.logger = logger
        
    async def daily_harvest(self):
        """Daily Reddit harvest and filtering"""
        self.logger.info("Starting daily harvest")
        
        try:
            # Run filter for last 24 hours
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            today = datetime.now().strftime("%Y-%m-%d")
            
            result = await run_filter(
                date_start=yesterday,
                date_end=today,
                keywords=["lease", "rent", "tenant", "commercial"],
                output_dir="data/daily"
            )
            
            if result:
                self.logger.info(f"Daily harvest complete: {result['filtered_count']} posts")
            else:
                self.logger.error("Daily harvest failed")
                
        except Exception as e:
            self.logger.error(f"Daily harvest error: {str(e)}")
    
    async def weekly_phrase_mining(self):
        """Weekly TF-IDF vocabulary refresh"""
        self.logger.info("Starting weekly phrase mining")
        
        try:
            result = await refresh_tfidf(
                corpus_source="last_week",
                top_k=150
            )
            
            if result:
                self.logger.info(f"Phrase mining complete: {result['total_terms_extracted']} terms")
            else:
                self.logger.error("Phrase mining failed")
                
        except Exception as e:
            self.logger.error(f"Phrase mining error: {str(e)}")
    
    async def monthly_expansion(self):
        """Monthly geographic expansion"""
        self.logger.info("Starting monthly expansion")
        
        try:
            # Expand to new tier 2 cities
            result = await expand_cities(
                metros=["austin", "denver", "seattle"],
                discover=True
            )
            
            if result:
                self.logger.info(f"Expansion complete: {result['total_subreddits']} subreddits")
            else:
                self.logger.error("Expansion failed")
                
        except Exception as e:
            self.logger.error(f"Expansion error: {str(e)}")
    
    async def weekly_intelligence_brief(self):
        """Weekly comprehensive intelligence report"""
        self.logger.info("Starting weekly intelligence brief")
        
        try:
            # Run full pipeline for the week
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            today = datetime.now().strftime("%Y-%m-%d")
            
            result = await run_full_pipeline(
                metros=["nyc", "sf", "chicago"],
                verticals=["office", "retail", "industrial"],
                date_start=week_ago,
                date_end=today,
                output_dir="data/weekly_briefs"
            )
            
            if result and result['success']:
                self.logger.info("Weekly brief complete")
                # Could add email notification here
            else:
                self.logger.error("Weekly brief failed")
                
        except Exception as e:
            self.logger.error(f"Weekly brief error: {str(e)}")
    
    def run_async_job(self, coro):
        """Helper to run async job in sync context"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(coro)
        finally:
            loop.close()
    
    def setup_schedule(self):
        """Configure job schedule"""
        # Daily jobs
        schedule.every().day.at("09:00").do(
            lambda: self.run_async_job(self.daily_harvest())
        )
        
        # Weekly jobs
        schedule.every().sunday.at("02:00").do(
            lambda: self.run_async_job(self.weekly_phrase_mining())
        )
        
        schedule.every().monday.at("08:00").do(
            lambda: self.run_async_job(self.weekly_intelligence_brief())
        )
        
        # Monthly jobs
        schedule.every(30).days.do(
            lambda: self.run_async_job(self.monthly_expansion())
        )
        
        self.logger.info("Schedule configured:")
        self.logger.info("  - Daily harvest: 09:00")
        self.logger.info("  - Weekly phrase mining: Sunday 02:00")
        self.logger.info("  - Weekly brief: Monday 08:00")
        self.logger.info("  - Monthly expansion: Every 30 days")
    
    def run(self):
        """Run the scheduler"""
        self.setup_schedule()
        self.logger.info("Scheduler started")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped")

def main():
    scheduler = CREScheduler()
    scheduler.run()

if __name__ == "__main__":
    main()