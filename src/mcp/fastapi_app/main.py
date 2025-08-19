# mcp/fastapi_app/main.py
"""
FastAPI MCP Server for CRE Intelligence
Implements all six intelligence techniques as MCP-accessible tools
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Set
from pathlib import Path
from datetime import datetime, date, timedelta
import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import hashlib
import re
from collections import Counter, defaultdict
import asyncio
import logging
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path configuration
BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "data"
RAW = DATA / "raw"
PROC = DATA / "processed"
LEX = DATA / "lexicon"
CFG = BASE / "config"
CACHE = DATA / "cache"

# Ensure directories exist
for dir_path in [RAW, PROC, LEX, CFG, CACHE]:
    dir_path.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="CRE Intelligence MCP Server",
    version="1.0.0",
    description="Complete implementation of six CRE intelligence techniques"
)

# ============================================================================
# Data Models
# ============================================================================

class SortStrategy(str, Enum):
    NEW = "new"
    RELEVANCE = "relevance"
    TOP = "top"
    HOT = "hot"

class VerticalCategory(str, Enum):
    OFFICE = "office"
    RETAIL = "retail"
    INDUSTRIAL = "industrial"
    MULTIFAMILY = "multifamily"
    HOSPITALITY = "hospitality"
    MIXED_USE = "mixed_use"

class PayloadOptimizationRequest(BaseModel):
    """Technique 1: Iterative JSON Refinement"""
    subreddits: List[str]
    keywords: List[str]
    date_start: str
    date_end: str
    max_url_length: int = Field(default=512, description="Reddit URL length limit")
    optimization_rounds: int = Field(default=3, description="Number of refinement iterations")

class PhraseMiningRequest(BaseModel):
    """Technique 2: Phrase Mining with TF-IDF"""
    corpus_source: str = Field(default="last_month", description="Source corpus for mining")
    ngram_range: tuple = Field(default=(1, 3), description="N-gram range for extraction")
    top_k: int = Field(default=100, description="Number of top phrases to extract")
    domain_categories: List[str] = Field(
        default=["financial", "legal", "operational", "market", "development"],
        description="Categories for term classification"
    )

class ClientSideFilterRequest(BaseModel):
    """Technique 3: Client-Side Filtering Pipeline"""
    date_start: str
    date_end: str
    keywords: List[str] = []
    exclude_keywords: List[str] = []
    quality_thresholds: Dict[str, float] = Field(
        default={"min_length": 50, "max_length": 10000, "min_score": 0.3}
    )
    semantic_similarity_threshold: float = Field(default=0.4)
    city: Optional[str] = None

class LocalSubTargetingRequest(BaseModel):
    """Technique 4: Local-Sub Geographic Targeting"""
    metro_areas: List[str]
    discover_new_subs: bool = Field(default=True)
    regional_keywords: Dict[str, List[str]] = Field(
        default={},
        description="Region-specific keywords for enhanced targeting"
    )

class VerticalSpecializationRequest(BaseModel):
    """Technique 5: Vertical/Niche Specialization"""
    verticals: List[VerticalCategory]
    custom_lexicons: Dict[str, List[str]] = Field(
        default={},
        description="Custom terms per vertical"
    )
    conflict_resolution: bool = Field(default=True)

class DualSortStrategyRequest(BaseModel):
    """Technique 6: Dual-Sort Strategy"""
    timeframe_days: int = Field(default=30)
    sort_strategies: List[SortStrategy] = Field(
        default=[SortStrategy.NEW, SortStrategy.RELEVANCE]
    )
    deduplication: bool = Field(default=True)
    backfill_months: int = Field(default=12)

# ============================================================================
# Technique 1: Iterative JSON Refinement / Payload Optimization
# ============================================================================

class PayloadOptimizer:
    """Implements iterative refinement of Apify Actor JSON payloads"""
    
    def __init__(self):
        self.optimization_history = []
        
    async def optimize_payload(self, request: PayloadOptimizationRequest) -> Dict:
        """Iteratively refine JSON payload for optimal Reddit API calls"""
        
        initial_payload = self._create_initial_payload(request)
        optimized = initial_payload.copy()
        
        for round_num in range(request.optimization_rounds):
            # Measure current payload efficiency
            metrics = self._measure_payload_metrics(optimized)
            
            # Apply optimization strategies
            if metrics['url_length'] > request.max_url_length:
                optimized = self._compress_boolean_clauses(optimized)
            
            if metrics['redundancy_score'] > 0.3:
                optimized = self._remove_redundant_terms(optimized)
            
            if metrics['coverage_gaps']:
                optimized = self._expand_coverage(optimized, request)
            
            # Track optimization history
            self.optimization_history.append({
                'round': round_num + 1,
                'metrics': metrics,
                'payload_size': len(json.dumps(optimized))
            })
        
        # Generate per-subreddit startUrls
        optimized['startUrls'] = self._generate_start_urls(optimized, request.subreddits)
        
        return {
            'optimized_payload': optimized,
            'optimization_history': self.optimization_history,
            'final_metrics': self._measure_payload_metrics(optimized),
            'saved_to': self._save_payload(optimized)
        }
    
    def _create_initial_payload(self, request: PayloadOptimizationRequest) -> Dict:
        """Create initial Apify Actor payload"""
        return {
            'searchQueries': request.keywords,
            'subreddits': request.subreddits,
            'dateFrom': request.date_start,
            'dateTo': request.date_end,
            'maxItems': 1000,
            'maxPostAge': 365,
            'sort': 'relevance',
            'skipComments': False
        }
    
    def _compress_boolean_clauses(self, payload: Dict) -> Dict:
        """Compress search queries using boolean operators"""
        if 'searchQueries' in payload and len(payload['searchQueries']) > 3:
            # Group similar terms with OR operators
            compressed = []
            for i in range(0, len(payload['searchQueries']), 3):
                group = payload['searchQueries'][i:i+3]
                compressed.append(' OR '.join(group))
            payload['searchQueries'] = compressed
        return payload
    
    def _remove_redundant_terms(self, payload: Dict) -> Dict:
        """Remove redundant search terms"""
        if 'searchQueries' in payload:
            unique_terms = list(set(payload['searchQueries']))
            payload['searchQueries'] = unique_terms
        return payload
    
    def _expand_coverage(self, payload: Dict, request: PayloadOptimizationRequest) -> Dict:
        """Expand coverage for missing areas"""
        # Add variations of key terms
        expanded_queries = payload.get('searchQueries', []).copy()
        for query in payload.get('searchQueries', []):
            if 'lease' in query.lower():
                expanded_queries.append(query.replace('lease', 'rental'))
            if 'commercial' in query.lower():
                expanded_queries.append(query.replace('commercial', 'CRE'))
        payload['searchQueries'] = list(set(expanded_queries))[:10]  # Limit to top 10
        return payload
    
    def _generate_start_urls(self, payload: Dict, subreddits: List[str]) -> List[str]:
        """Generate subreddit-specific start URLs"""
        urls = []
        for sub in subreddits:
            sub_clean = sub.replace('r/', '')
            urls.append(f"https://www.reddit.com/r/{sub_clean}/search?sort=relevance&restrict_sr=on&t=all")
        return urls
    
    def _measure_payload_metrics(self, payload: Dict) -> Dict:
        """Measure payload efficiency metrics"""
        payload_str = json.dumps(payload)
        return {
            'url_length': len(payload_str),
            'redundancy_score': self._calculate_redundancy(payload),
            'coverage_gaps': self._identify_coverage_gaps(payload),
            'query_complexity': len(payload.get('searchQueries', [])),
            'estimated_api_calls': len(payload.get('subreddits', [])) * len(payload.get('searchQueries', []))
        }
    
    def _calculate_redundancy(self, payload: Dict) -> float:
        """Calculate term redundancy score"""
        queries = payload.get('searchQueries', [])
        if not queries:
            return 0.0
        
        # Check for substring overlaps
        overlaps = 0
        for i, q1 in enumerate(queries):
            for q2 in queries[i+1:]:
                if q1.lower() in q2.lower() or q2.lower() in q1.lower():
                    overlaps += 1
        
        return overlaps / max(len(queries), 1)
    
    def _identify_coverage_gaps(self, payload: Dict) -> List[str]:
        """Identify potential coverage gaps"""
        gaps = []
        essential_terms = ['lease', 'rent', 'tenant', 'landlord', 'property', 'commercial']
        queries_lower = [q.lower() for q in payload.get('searchQueries', [])]
        
        for term in essential_terms:
            if not any(term in q for q in queries_lower):
                gaps.append(term)
        
        return gaps
    
    def _save_payload(self, payload: Dict) -> str:
        """Save optimized payload to disk"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = PROC / f"payloads/optimized_{timestamp}.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(payload, indent=2))
        return str(path)

# ============================================================================
# Technique 2: Phrase Mining with TF-IDF and Domain Classification
# ============================================================================

class PhraseMiner:
    """Advanced phrase mining with domain-specific classification"""
    
    def __init__(self):
        self.vectorizer = None
        self.domain_classifiers = self._initialize_domain_classifiers()
        
    def _initialize_domain_classifiers(self) -> Dict:
        """Initialize domain-specific term classifiers"""
        return {
            'financial': ['cam', 'nnn', 'triple net', 'opex', 'capex', 'roi', 'cap rate', 'noi'],
            'legal': ['lease', 'estoppel', 'snda', 'subordination', 'landlord', 'tenant', 'eviction'],
            'operational': ['hvac', 'maintenance', 'janitorial', 'utilities', 'parking', 'security'],
            'market': ['vacancy', 'absorption', 'pipeline', 'submarket', 'comps', 'asking rent'],
            'development': ['entitlement', 'zoning', 'permits', 'tpo', 'site plan', 'variance']
        }
    
    async def mine_phrases(self, request: PhraseMiningRequest) -> Dict:
        """Extract and classify domain-specific phrases"""
        
        # Load corpus
        corpus = await self._load_corpus(request.corpus_source)
        if not corpus:
            return {'ok': False, 'message': 'No corpus data available', 'terms': []}
        
        # Extract TF-IDF features
        tfidf_results = self._extract_tfidf_features(corpus, request.ngram_range, request.top_k)
        
        # Classify terms by domain
        classified_terms = self._classify_terms(
            tfidf_results['terms'], 
            request.domain_categories
        )
        
        # Calculate term importance scores
        term_scores = self._calculate_term_importance(tfidf_results, classified_terms)
        
        # Identify emerging terms (new this period vs last)
        emerging_terms = await self._identify_emerging_terms(term_scores)
        
        # Save to lexicon
        saved_path = self._save_to_lexicon(term_scores, classified_terms, emerging_terms)
        
        return {
            'ok': True,
            'total_terms_extracted': len(tfidf_results['terms']),
            'top_terms': term_scores[:request.top_k],
            'classified_terms': classified_terms,
            'emerging_terms': emerging_terms[:20],
            'lexicon_path': saved_path,
            'corpus_stats': {
                'documents': len(corpus),
                'unique_terms': len(tfidf_results['terms']),
                'avg_doc_length': np.mean([len(doc.split()) for doc in corpus])
            }
        }
    
    async def _load_corpus(self, source: str) -> List[str]:
        """Load text corpus from processed data"""
        corpus = []
        
        if source == "last_month":
            cutoff = datetime.utcnow() - timedelta(days=30)
            pattern = "filtered_*.jsonl"
        else:
            pattern = "*.jsonl"
            cutoff = datetime.utcnow() - timedelta(days=90)
        
        for file_path in PROC.glob(pattern):
            try:
                df = pd.read_json(file_path, lines=True)
                # Combine title and selftext
                texts = (df['title'].fillna('') + ' ' + df['selftext'].fillna('')).tolist()
                corpus.extend(texts)
            except Exception as e:
                logger.warning(f"Error loading {file_path}: {e}")
        
        return corpus
    
    def _extract_tfidf_features(self, corpus: List[str], ngram_range: tuple, top_k: int) -> Dict:
        """Extract TF-IDF features from corpus"""
        self.vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            max_features=5000,
            min_df=2,
            max_df=0.8,
            stop_words='english',
            token_pattern=r'\b[a-zA-Z][a-zA-Z]+\b'
        )
        
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Get top terms by average TF-IDF score
        avg_scores = tfidf_matrix.mean(axis=0).A1
        top_indices = avg_scores.argsort()[-top_k:][::-1]
        
        top_terms = [(feature_names[i], avg_scores[i]) for i in top_indices]
        
        return {
            'terms': top_terms,
            'feature_names': feature_names.tolist(),
            'matrix_shape': tfidf_matrix.shape
        }
    
    def _classify_terms(self, terms: List[tuple], categories: List[str]) -> Dict:
        """Classify terms into domain categories"""
        classified = {cat: [] for cat in categories}
        classified['uncategorized'] = []
        
        for term, score in terms:
            term_lower = term.lower()
            categorized = False
            
            for category, keywords in self.domain_classifiers.items():
                if category in categories:
                    for keyword in keywords:
                        if keyword in term_lower or term_lower in keyword:
                            classified[category].append((term, score))
                            categorized = True
                            break
                if categorized:
                    break
            
            if not categorized:
                classified['uncategorized'].append((term, score))
        
        return classified
    
    def _calculate_term_importance(self, tfidf_results: Dict, classified_terms: Dict) -> List[Dict]:
        """Calculate comprehensive term importance scores"""
        term_scores = []
        
        for term, tfidf_score in tfidf_results['terms']:
            # Find category
            category = 'uncategorized'
            for cat, terms_list in classified_terms.items():
                if any(t[0] == term for t in terms_list):
                    category = cat
                    break
            
            # Calculate composite score
            category_weight = 1.5 if category in ['financial', 'legal'] else 1.0
            composite_score = tfidf_score * category_weight
            
            term_scores.append({
                'term': term,
                'tfidf_score': float(tfidf_score),
                'category': category,
                'composite_score': float(composite_score),
                'ngram_size': len(term.split())
            })
        
        # Sort by composite score
        term_scores.sort(key=lambda x: x['composite_score'], reverse=True)
        
        return term_scores
    
    async def _identify_emerging_terms(self, current_terms: List[Dict]) -> List[Dict]:
        """Identify newly emerging terms compared to previous period"""
        emerging = []
        
        # Load previous lexicon
        prev_lexicon_files = sorted(LEX.glob("vocab_*.json"))
        if len(prev_lexicon_files) < 2:
            return []  # Need at least 2 periods for comparison
        
        try:
            prev_data = json.loads(prev_lexicon_files[-2].read_text())
            prev_terms = {t['term'] for t in prev_data.get('terms', [])}
            
            for term_data in current_terms:
                if term_data['term'] not in prev_terms:
                    emerging.append({
                        **term_data,
                        'status': 'new',
                        'emergence_score': term_data['composite_score'] * 1.5
                    })
        except Exception as e:
            logger.warning(f"Error identifying emerging terms: {e}")
        
        emerging.sort(key=lambda x: x['emergence_score'], reverse=True)
        return emerging
    
    def _save_to_lexicon(self, terms: List[Dict], classified: Dict, emerging: List[Dict]) -> str:
        """Save mining results to lexicon"""
        timestamp = datetime.utcnow().strftime("%Y-%m")
        
        lexicon_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'terms': terms[:100],  # Top 100
            'classified': {k: v[:20] for k, v in classified.items()},  # Top 20 per category
            'emerging': emerging[:20],  # Top 20 emerging
            'metadata': {
                'total_terms': len(terms),
                'categories': list(classified.keys()),
                'emerging_count': len(emerging)
            }
        }
        
        path = LEX / f"vocab_{timestamp}.json"
        path.write_text(json.dumps(lexicon_data, indent=2, default=str))
        
        return str(path)

# ============================================================================
# Technique 3: Client-Side Filtering Pipeline
# ============================================================================

class ClientSideFilterEngine:
    """6-stage client-side filtering pipeline"""
    
    def __init__(self):
        self.filter_stats = defaultdict(int)
        
    async def filter_posts(self, request: ClientSideFilterRequest) -> Dict:
        """Apply comprehensive 6-stage filtering pipeline"""
        
        # Load raw posts
        posts = await self._load_posts(request.date_start, request.date_end)
        initial_count = len(posts)
        
        if initial_count == 0:
            return {'ok': True, 'message': 'No posts to filter', 'stats': {}}
        
        # Stage 1: Temporal filtering
        posts = self._temporal_filter(posts, request.date_start, request.date_end)
        self.filter_stats['after_temporal'] = len(posts)
        
        # Stage 2: Keyword filtering
        posts = self._keyword_filter(posts, request.keywords, request.exclude_keywords)
        self.filter_stats['after_keyword'] = len(posts)
        
        # Stage 3: Quality filtering
        posts = self._quality_filter(posts, request.quality_thresholds)
        self.filter_stats['after_quality'] = len(posts)
        
        # Stage 4: Semantic similarity filtering
        if request.semantic_similarity_threshold > 0:
            posts = await self._semantic_filter(posts, request.keywords, request.semantic_similarity_threshold)
            self.filter_stats['after_semantic'] = len(posts)
        
        # Stage 5: Geographic filtering
        if request.city:
            posts = self._geographic_filter(posts, request.city)
            self.filter_stats['after_geographic'] = len(posts)
        
        # Stage 6: Deduplication
        posts = self._deduplicate(posts)
        self.filter_stats['after_dedup'] = len(posts)
        
        # Calculate relevance scores
        posts = self._calculate_relevance_scores(posts, request)
        
        # Save filtered results
        output_path = self._save_filtered(posts, request)
        
        return {
            'ok': True,
            'initial_count': initial_count,
            'filtered_count': len(posts),
            'retention_rate': len(posts) / max(initial_count, 1),
            'filter_stats': dict(self.filter_stats),
            'output_path': output_path,
            'top_posts': self._get_top_posts(posts, 5)
        }
    
    async def _load_posts(self, date_start: str, date_end: str) -> pd.DataFrame:
        """Load posts from raw data"""
        frames = []
        
        for file_path in RAW.glob("*.jsonl"):
            try:
                df = pd.read_json(file_path, lines=True)
                frames.append(df)
            except Exception as e:
                logger.warning(f"Error loading {file_path}: {e}")
        
        if not frames:
            return pd.DataFrame()
        
        return pd.concat(frames, ignore_index=True)
    
    def _temporal_filter(self, posts: pd.DataFrame, date_start: str, date_end: str) -> pd.DataFrame:
        """Filter posts by date range"""
        if posts.empty:
            return posts
        
        posts['created_date'] = pd.to_datetime(posts['created_utc'], unit='s')
        start = pd.to_datetime(date_start)
        end = pd.to_datetime(date_end)
        
        mask = (posts['created_date'] >= start) & (posts['created_date'] <= end)
        return posts[mask].copy()
    
    def _keyword_filter(self, posts: pd.DataFrame, keywords: List[str], exclude: List[str]) -> pd.DataFrame:
        """Filter by inclusion and exclusion keywords"""
        if posts.empty:
            return posts
        
        # Combine text fields
        posts['combined_text'] = posts['title'].fillna('') + ' ' + posts['selftext'].fillna('')
        
        # Include keywords (OR logic)
        if keywords:
            pattern = '|'.join([re.escape(kw) for kw in keywords])
            mask = posts['combined_text'].str.contains(pattern, case=False, na=False)
            posts = posts[mask]
        
        # Exclude keywords
        if exclude:
            pattern = '|'.join([re.escape(kw) for kw in exclude])
            mask = ~posts['combined_text'].str.contains(pattern, case=False, na=False)
            posts = posts[mask]
        
        return posts
    
    def _quality_filter(self, posts: pd.DataFrame, thresholds: Dict[str, float]) -> pd.DataFrame:
        """Filter by quality metrics"""
        if posts.empty:
            return posts
        
        # Length filtering
        posts['text_length'] = posts['selftext'].fillna('').str.len()
        
        min_len = thresholds.get('min_length', 50)
        max_len = thresholds.get('max_length', 10000)
        
        mask = (posts['text_length'] >= min_len) & (posts['text_length'] <= max_len)
        
        # Score filtering (if available)
        if 'score' in posts.columns:
            min_score = thresholds.get('min_score', 0)
            mask &= posts['score'] >= min_score
        
        return posts[mask]
    
    async def _semantic_filter(self, posts: pd.DataFrame, keywords: List[str], threshold: float) -> pd.DataFrame:
        """Filter by semantic similarity to keywords"""
        if posts.empty or not keywords:
            return posts
        
        # Create keyword embedding (simple approach - could use better embeddings)
        keyword_text = ' '.join(keywords)
        
        # Vectorize posts and keywords
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        try:
            all_texts = posts['combined_text'].tolist() + [keyword_text]
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            
            # Calculate similarities
            keyword_vector = tfidf_matrix[-1]
            post_vectors = tfidf_matrix[:-1]
            
            similarities = cosine_similarity(post_vectors, keyword_vector).flatten()
            
            # Filter by threshold
            mask = similarities >= threshold
            posts = posts[mask].copy()
            posts['semantic_score'] = similarities[mask]
            
        except Exception as e:
            logger.warning(f"Semantic filtering failed: {e}")
        
        return posts
    
    def _geographic_filter(self, posts: pd.DataFrame, city: str) -> pd.DataFrame:
        """Filter by geographic relevance"""
        if posts.empty:
            return posts
        
        # City-specific subreddit patterns
        city_patterns = {
            'nyc': ['nyc', 'newyork', 'manhattan', 'brooklyn', 'queens'],
            'sf': ['sanfrancisco', 'bayarea', 'sf', 'oakland'],
            'chicago': ['chicago', 'chicagoland'],
            'la': ['losangeles', 'la', 'socal'],
        }
        
        patterns = city_patterns.get(city.lower(), [city.lower()])
        
        # Check subreddit names
        pattern = '|'.join(patterns)
        mask = posts['subreddit'].str.contains(pattern, case=False, na=False)
        
        # Also check text content for city mentions
        text_mask = posts['combined_text'].str.contains(pattern, case=False, na=False)
        
        return posts[mask | text_mask]
    
    def _deduplicate(self, posts: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate posts"""
        if posts.empty:
            return posts
        
        # Remove exact duplicates by ID
        posts = posts.drop_duplicates(subset=['id'], keep='first')
        
        # Remove near-duplicates by title similarity
        posts['title_hash'] = posts['title'].fillna('').apply(
            lambda x: hashlib.md5(x.lower().strip().encode()).hexdigest()[:8]
        )
        posts = posts.drop_duplicates(subset=['title_hash'], keep='first')
        
        return posts
    
    def _calculate_relevance_scores(self, posts: pd.DataFrame, request: ClientSideFilterRequest) -> pd.DataFrame:
        """Calculate composite relevance scores"""
        if posts.empty:
            return posts
        
        posts['relevance_score'] = 0.0
        
        # Keyword match score
        if request.keywords:
            for keyword in request.keywords:
                mask = posts['combined_text'].str.contains(keyword, case=False, na=False)
                posts.loc[mask, 'relevance_score'] += 0.2
        
        # Quality score component
        if 'score' in posts.columns:
            posts['relevance_score'] += posts['score'] / posts['score'].max() * 0.3
        
        # Semantic score component (if available)
        if 'semantic_score' in posts.columns:
            posts['relevance_score'] += posts['semantic_score'] * 0.3
        
        # Recency score
        posts['days_old'] = (datetime.utcnow() - posts['created_date']).dt.days
        posts['recency_score'] = 1.0 / (1 + posts['days_old'] / 30)
        posts['relevance_score'] += posts['recency_score'] * 0.2
        
        # Normalize to 0-1
        if posts['relevance_score'].max() > 0:
            posts['relevance_score'] /= posts['relevance_score'].max()
        
        return posts.sort_values('relevance_score', ascending=False)
    
    def _save_filtered(self, posts: pd.DataFrame, request: ClientSideFilterRequest) -> str:
        """Save filtered posts"""
        if posts.empty:
            return "No posts to save"
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_path = PROC / f"filtered_{request.date_start}_{request.date_end}_{timestamp}.jsonl"
        
        # Select relevant columns
        columns_to_save = ['id', 'title', 'selftext', 'subreddit', 'created_utc', 
                          'score', 'url', 'relevance_score']
        columns_to_save = [col for col in columns_to_save if col in posts.columns]
        
        posts[columns_to_save].to_json(output_path, orient='records', lines=True)
        
        return str(output_path)
    
    def _get_top_posts(self, posts: pd.DataFrame, n: int = 5) -> List[Dict]:
        """Get top N posts by relevance"""
        if posts.empty:
            return []
        
        top = posts.nlargest(n, 'relevance_score')
        
        return top[['title', 'subreddit', 'relevance_score', 'url']].to_dict('records')

# ============================================================================
# Technique 4: Local-Sub Geographic Targeting
# ============================================================================

class LocalSubTargeting:
    """Geographic targeting and subreddit discovery"""
    
    def __init__(self):
        self.metro_configs = self._load_metro_configs()
        
    def _load_metro_configs(self) -> Dict:
        """Load metro area configurations"""
        config_path = CFG / "cities.yml"
        if config_path.exists():
            import yaml
            return yaml.safe_load(config_path.read_text())
        
        # Default configurations
        return {
            'metros': {
                'nyc': {
                    'subreddits': ['r/nyc', 'r/AskNYC', 'r/manhattan', 'r/brooklyn'],
                    'keywords': ['manhattan', 'brooklyn', 'queens', 'nyc', 'new york'],
                    'heuristics': {'rent_unit': 'psf', 'market_type': 'high_density'}
                },
                'sf': {
                    'subreddits': ['r/sanfrancisco', 'r/bayarea', 'r/oakland'],
                    'keywords': ['sf', 'bay area', 'silicon valley', 'san francisco'],
                    'heuristics': {'rent_unit': 'psf', 'market_type': 'tech_driven'}
                },
                'chicago': {
                    'subreddits': ['r/chicago', 'r/chicagosuburbs'],
                    'keywords': ['chicago', 'loop', 'chicagoland'],
                    'heuristics': {'rent_unit': 'psf', 'market_type': 'mixed'}
                }
            }
        }
    
    async def target_local_subs(self, request: LocalSubTargetingRequest) -> Dict:
        """Target and expand local subreddit coverage"""
        
        results = {}
        
        for metro in request.metro_areas:
            # Get existing configuration
            metro_config = self.metro_configs['metros'].get(metro, {})
            
            # Discover new subreddits if requested
            if request.discover_new_subs:
                new_subs = await self._discover_related_subs(metro, metro_config)
                metro_config['subreddits'] = list(set(metro_config.get('subreddits', []) + new_subs))
            
            # Apply regional keywords
            if metro in request.regional_keywords:
                metro_config['keywords'] = list(set(
                    metro_config.get('keywords', []) + request.regional_keywords[metro]
                ))
            
            # Analyze metro-specific patterns
            patterns = await self._analyze_metro_patterns(metro, metro_config)
            
            results[metro] = {
                'subreddits': metro_config.get('subreddits', []),
                'keywords': metro_config.get('keywords', []),
                'patterns': patterns,
                'estimated_volume': await self._estimate_post_volume(metro_config)
            }
        
        # Update configuration
        self._update_metro_configs(results)
        
        return {
            'ok': True,
            'metros_targeted': len(results),
            'total_subreddits': sum(len(r['subreddits']) for r in results.values()),
            'metro_details': results,
            'config_updated': str(CFG / "cities.yml")
        }
    
    async def _discover_related_subs(self, metro: str, config: Dict) -> List[str]:
        """Discover related subreddits for a metro area"""
        # In production, this would query Reddit API or use a graph of related subs
        # For now, return common patterns
        
        related_patterns = {
            'nyc': ['r/nycrealestate', 'r/nycjobs', 'r/newyorkcity'],
            'sf': ['r/sfrealestate', 'r/sfbayhousing', 'r/sanjose'],
            'chicago': ['r/chicagorealestate', 'r/chicagojobs'],
            'la': ['r/larealestate', 'r/socal', 'r/orangecounty'],
            'boston': ['r/bostonhousing', 'r/cambridge', 'r/somerville'],
        }
        
        return related_patterns.get(metro, [])
    
    async def _analyze_metro_patterns(self, metro: str, config: Dict) -> Dict:
        """Analyze posting patterns for a metro area"""
        patterns = {
            'peak_hours': [],
            'peak_days': [],
            'common_topics': [],
            'price_mentions': {'format': '', 'range': {}}
        }
        
        # Load recent posts for this metro
        try:
            metro_posts = []
            for sub in config.get('subreddits', []):
                sub_clean = sub.replace('r/', '')
                for file_path in PROC.glob(f"*{sub_clean}*.jsonl"):
                    df = pd.read_json(file_path, lines=True)
                    metro_posts.append(df)
            
            if metro_posts:
                df = pd.concat(metro_posts, ignore_index=True)
                
                # Analyze posting times
                df['hour'] = pd.to_datetime(df['created_utc'], unit='s').dt.hour
                df['day'] = pd.to_datetime(df['created_utc'], unit='s').dt.day_name()
                
                patterns['peak_hours'] = df['hour'].value_counts().head(3).index.tolist()
                patterns['peak_days'] = df['day'].value_counts().head(3).index.tolist()
                
                # Extract common topics
                text = ' '.join(df['title'].fillna('').tolist())
                words = text.lower().split()
                word_freq = Counter(words)
                patterns['common_topics'] = [w for w, _ in word_freq.most_common(10) 
                                            if len(w) > 4 and w not in ['would', 'could', 'should']]
                
        except Exception as e:
            logger.warning(f"Error analyzing patterns for {metro}: {e}")
        
        return patterns
    
    async def _estimate_post_volume(self, config: Dict) -> int:
        """Estimate post volume for a metro configuration"""
        # Simple estimation based on subreddit count
        # In production, would query actual volumes
        return len(config.get('subreddits', [])) * 50  # Rough estimate
    
    def _update_metro_configs(self, results: Dict):
        """Update metro configurations file"""
        self.metro_configs['metros'].update(results)
        
        config_path = CFG / "cities.yml"
        import yaml
        config_path.write_text(yaml.dump(self.metro_configs, default_flow_style=False))

# ============================================================================
# Technique 5: Vertical/Niche Specialization
# ============================================================================

class VerticalSpecializer:
    """Specialized targeting for CRE verticals"""
    
    def __init__(self):
        self.vertical_lexicons = self._initialize_vertical_lexicons()
        
    def _initialize_vertical_lexicons(self) -> Dict:
        """Initialize vertical-specific lexicons"""
        return {
            VerticalCategory.OFFICE: [
                'class a', 'class b', 'sublease', 'coworking', 'amenities',
                'conference room', 'reception', 'build-out', 'tenant improvement'
            ],
            VerticalCategory.RETAIL: [
                'foot traffic', 'anchor tenant', 'inline', 'pad site', 'drive-thru',
                'shopping center', 'strip mall', 'big box', 'qsr', 'fast casual'
            ],
            VerticalCategory.INDUSTRIAL: [
                'warehouse', 'distribution', 'logistics', 'loading dock', 'clear height',
                'cross-dock', 'rail served', 'cold storage', 'flex space'
            ],
            VerticalCategory.MULTIFAMILY: [
                'units', 'bedroom', 'amenities', 'pool', 'fitness', 'pet friendly',
                'concierge', 'parking ratio', 'occupancy', 'rent roll'
            ],
            VerticalCategory.HOSPITALITY: [
                'adr', 'revpar', 'occupancy rate', 'flag', 'franchise', 'boutique',
                'limited service', 'full service', 'extended stay'
            ],
            VerticalCategory.MIXED_USE: [
                'live work play', 'ground floor retail', 'residential over retail',
                'transit oriented', 'walkable', 'mixed income'
            ]
        }
    
    async def specialize_verticals(self, request: VerticalSpecializationRequest) -> Dict:
        """Apply vertical specialization to intelligence gathering"""
        
        results = {}
        
        for vertical in request.verticals:
            # Get base lexicon
            base_lexicon = self.vertical_lexicons.get(vertical, [])
            
            # Add custom terms
            if vertical.value in request.custom_lexicons:
                base_lexicon.extend(request.custom_lexicons[vertical.value])
            
            # Remove duplicates and conflicts
            if request.conflict_resolution:
                base_lexicon = self._resolve_lexicon_conflicts(base_lexicon, vertical)
            
            # Analyze vertical-specific patterns
            vertical_analysis = await self._analyze_vertical(vertical, base_lexicon)
            
            # Generate vertical-specific search strategies
            search_strategy = self._generate_vertical_strategy(vertical, vertical_analysis)
            
            results[vertical.value] = {
                'lexicon': base_lexicon,
                'analysis': vertical_analysis,
                'search_strategy': search_strategy,
                'estimated_relevance': vertical_analysis.get('relevance_score', 0)
            }
        
        # Save vertical configurations
        saved_path = self._save_vertical_configs(results)
        
        return {
            'ok': True,
            'verticals_processed': len(results),
            'vertical_details': results,
            'config_saved': saved_path,
            'top_opportunities': self._identify_top_opportunities(results)
        }
    
    def _resolve_lexicon_conflicts(self, lexicon: List[str], vertical: VerticalCategory) -> List[str]:
        """Resolve conflicts in vertical lexicons"""
        # Remove terms that conflict with this vertical
        conflict_terms = {
            VerticalCategory.OFFICE: ['residential', 'retail only'],
            VerticalCategory.RETAIL: ['office only', 'industrial'],
            VerticalCategory.INDUSTRIAL: ['retail', 'residential'],
            VerticalCategory.MULTIFAMILY: ['commercial only', 'industrial']
        }
        
        conflicts = conflict_terms.get(vertical, [])
        cleaned = [term for term in lexicon if not any(c in term.lower() for c in conflicts)]
        
        return list(set(cleaned))
    
    async def _analyze_vertical(self, vertical: VerticalCategory, lexicon: List[str]) -> Dict:
        """Analyze vertical-specific patterns and opportunities"""
        analysis = {
            'post_volume': 0,
            'relevance_score': 0.0,
            'trending_topics': [],
            'market_signals': [],
            'competitive_landscape': {}
        }
        
        # Load posts containing vertical terms
        try:
            vertical_posts = []
            for file_path in PROC.glob("filtered_*.jsonl"):
                df = pd.read_json(file_path, lines=True)
                
                # Filter for vertical relevance
                pattern = '|'.join([re.escape(term) for term in lexicon[:10]])  # Top 10 terms
                if pattern:
                    mask = df['selftext'].fillna('').str.contains(pattern, case=False, na=False)
                    vertical_df = df[mask]
                    if not vertical_df.empty:
                        vertical_posts.append(vertical_df)
            
            if vertical_posts:
                combined = pd.concat(vertical_posts, ignore_index=True)
                
                analysis['post_volume'] = len(combined)
                analysis['relevance_score'] = min(len(combined) / 100, 1.0)  # Normalize
                
                # Extract trending topics
                text = ' '.join(combined['title'].fillna('').tolist()[:100])
                words = [w for w in text.lower().split() if len(w) > 4]
                word_freq = Counter(words)
                analysis['trending_topics'] = [w for w, _ in word_freq.most_common(5)]
                
                # Identify market signals
                if 'lease' in text.lower():
                    analysis['market_signals'].append('leasing_activity')
                if 'sale' in text.lower() or 'acquisition' in text.lower():
                    analysis['market_signals'].append('transaction_activity')
                if 'development' in text.lower() or 'construction' in text.lower():
                    analysis['market_signals'].append('development_pipeline')
                
        except Exception as e:
            logger.warning(f"Error analyzing vertical {vertical}: {e}")
        
        return analysis
    
    def _generate_vertical_strategy(self, vertical: VerticalCategory, analysis: Dict) -> Dict:
        """Generate vertical-specific search strategy"""
        strategy = {
            'primary_terms': [],
            'secondary_terms': [],
            'exclude_terms': [],
            'target_subreddits': [],
            'monitoring_frequency': 'daily'
        }
        
        # Set vertical-specific strategies
        if vertical == VerticalCategory.OFFICE:
            strategy['primary_terms'] = ['office lease', 'sublease', 'coworking', 'hybrid work']
            strategy['target_subreddits'] = ['r/commercialrealestate', 'r/coworking']
            if analysis['post_volume'] > 100:
                strategy['monitoring_frequency'] = 'hourly'
                
        elif vertical == VerticalCategory.RETAIL:
            strategy['primary_terms'] = ['retail space', 'storefront', 'shopping center', 'foot traffic']
            strategy['target_subreddits'] = ['r/smallbusiness', 'r/entrepreneur']
            strategy['exclude_terms'] = ['online only', 'ecommerce only']
            
        elif vertical == VerticalCategory.INDUSTRIAL:
            strategy['primary_terms'] = ['warehouse', 'distribution center', 'logistics', 'last mile']
            strategy['target_subreddits'] = ['r/supplychain', 'r/logistics']
            
        elif vertical == VerticalCategory.MULTIFAMILY:
            strategy['primary_terms'] = ['apartment', 'rental', 'property management', 'tenant']
            strategy['target_subreddits'] = ['r/landlord', 'r/propertymanagement']
            
        return strategy
    
    def _identify_top_opportunities(self, results: Dict) -> List[Dict]:
        """Identify top opportunities across verticals"""
        opportunities = []
        
        for vertical, data in results.items():
            if data['analysis']['relevance_score'] > 0.5:
                opportunities.append({
                    'vertical': vertical,
                    'score': data['analysis']['relevance_score'],
                    'volume': data['analysis']['post_volume'],
                    'signals': data['analysis']['market_signals']
                })
        
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        return opportunities[:3]
    
    def _save_vertical_configs(self, results: Dict) -> str:
        """Save vertical configurations"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = CFG / f"verticals_{timestamp}.json"
        
        path.write_text(json.dumps(results, indent=2, default=str))
        return str(path)

# ============================================================================
# Technique 6: Dual-Sort Strategy Implementation
# ============================================================================

class DualSortStrategy:
    """Implement dual-sort strategy for comprehensive coverage"""
    
    def __init__(self):
        self.dedup_cache = set()
        
    async def execute_dual_sort(self, request: DualSortStrategyRequest) -> Dict:
        """Execute dual-sort strategy for comprehensive data collection"""
        
        results = {
            'collections': {},
            'deduplication_stats': {},
            'coverage_analysis': {},
            'backfill_results': {}
        }
        
        # Execute each sort strategy
        for strategy in request.sort_strategies:
            collection = await self._collect_with_strategy(
                strategy, 
                request.timeframe_days
            )
            results['collections'][strategy.value] = collection
        
        # Perform deduplication if requested
        if request.deduplication:
            dedup_results = self._deduplicate_collections(results['collections'])
            results['deduplication_stats'] = dedup_results
        
        # Analyze coverage
        results['coverage_analysis'] = self._analyze_coverage(
            results['collections'],
            request.timeframe_days
        )
        
        # Execute backfill if needed
        if request.backfill_months > 0:
            backfill = await self._execute_backfill(
                request.backfill_months,
                results['coverage_analysis']
            )
            results['backfill_results'] = backfill
        
        # Save results
        saved_path = self._save_dual_sort_results(results)
        
        return {
            'ok': True,
            'strategies_executed': len(request.sort_strategies),
            'total_posts_collected': sum(c['count'] for c in results['collections'].values()),
            'unique_posts': len(self.dedup_cache),
            'coverage_score': results['coverage_analysis'].get('score', 0),
            'backfill_completed': request.backfill_months > 0,
            'results_saved': saved_path,
            'summary': self._generate_summary(results)
        }
    
    async def _collect_with_strategy(self, strategy: SortStrategy, days: int) -> Dict:
        """Collect posts using specific sort strategy"""
        collection = {
            'strategy': strategy.value,
            'count': 0,
            'date_range': {
                'start': (datetime.utcnow() - timedelta(days=days)).isoformat(),
                'end': datetime.utcnow().isoformat()
            },
            'quality_metrics': {}
        }
        
        # In production, this would call Reddit API with specific sort
        # For now, simulate with existing data
        try:
            posts = []
            for file_path in RAW.glob("*.jsonl"):
                df = pd.read_json(file_path, lines=True)
                
                # Apply sort strategy logic
                if strategy == SortStrategy.NEW:
                    df = df.sort_values('created_utc', ascending=False)
                elif strategy == SortStrategy.RELEVANCE:
                    if 'score' in df.columns:
                        df = df.sort_values('score', ascending=False)
                elif strategy == SortStrategy.TOP:
                    if 'score' in df.columns:
                        df = df.nlargest(100, 'score')
                elif strategy == SortStrategy.HOT:
                    # Hot = recent + high engagement
                    df['hot_score'] = df['score'] / (1 + (datetime.utcnow().timestamp() - df['created_utc']) / 86400)
                    df = df.sort_values('hot_score', ascending=False)
                
                posts.append(df.head(100))  # Limit per file
            
            if posts:
                combined = pd.concat(posts, ignore_index=True)
                collection['count'] = len(combined)
                
                # Calculate quality metrics
                collection['quality_metrics'] = {
                    'avg_score': float(combined['score'].mean()) if 'score' in combined.columns else 0,
                    'avg_comments': float(combined['num_comments'].mean()) if 'num_comments' in combined.columns else 0,
                    'unique_subreddits': combined['subreddit'].nunique() if 'subreddit' in combined.columns else 0
                }
                
                # Save strategy-specific collection
                self._save_strategy_collection(combined, strategy)
                
        except Exception as e:
            logger.warning(f"Error collecting with strategy {strategy}: {e}")
        
        return collection
    
    def _deduplicate_collections(self, collections: Dict) -> Dict:
        """Deduplicate across multiple collections"""
        stats = {
            'total_before': 0,
            'total_after': 0,
            'duplicates_removed': 0,
            'duplicate_pairs': []
        }
        
        all_posts = []
        
        for strategy, collection in collections.items():
            # Load the strategy-specific collection
            strategy_file = PROC / f"dual_sort_{strategy}_latest.jsonl"
            if strategy_file.exists():
                df = pd.read_json(strategy_file, lines=True)
                all_posts.append(df)
                stats['total_before'] += len(df)
        
        if all_posts:
            combined = pd.concat(all_posts, ignore_index=True)
            
            # Track duplicates
            before_dedup = len(combined)
            
            # Remove by ID
            combined = combined.drop_duplicates(subset=['id'], keep='first')
            
            # Remove by URL
            if 'url' in combined.columns:
                combined = combined.drop_duplicates(subset=['url'], keep='first')
            
            # Remove by title similarity (fuzzy)
            combined['title_key'] = combined['title'].fillna('').str.lower().str.strip()
            combined = combined.drop_duplicates(subset=['title_key'], keep='first')
            
            stats['total_after'] = len(combined)
            stats['duplicates_removed'] = before_dedup - stats['total_after']
            
            # Update dedup cache
            self.dedup_cache.update(combined['id'].tolist())
            
            # Save deduplicated collection
            dedup_path = PROC / f"dual_sort_dedup_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
            combined.to_json(dedup_path, orient='records', lines=True)
        
        return stats
    
    def _analyze_coverage(self, collections: Dict, timeframe_days: int) -> Dict:
        """Analyze coverage across time periods and strategies"""
        analysis = {
            'score': 0.0,
            'gaps': [],
            'coverage_by_day': {},
            'coverage_by_strategy': {}
        }
        
        try:
            # Analyze temporal coverage
            date_coverage = defaultdict(set)
            
            for strategy, collection in collections.items():
                strategy_file = PROC / f"dual_sort_{strategy}_latest.jsonl"
                if strategy_file.exists():
                    df = pd.read_json(strategy_file, lines=True)
                    df['date'] = pd.to_datetime(df['created_utc'], unit='s').dt.date
                    
                    for date_val in df['date'].unique():
                        date_coverage[date_val].add(strategy)
                    
                    analysis['coverage_by_strategy'][strategy] = {
                        'posts': len(df),
                        'days_covered': df['date'].nunique(),
                        'completeness': df['date'].nunique() / timeframe_days
                    }
            
            # Identify gaps
            expected_dates = pd.date_range(
                end=datetime.utcnow().date(),
                periods=timeframe_days
            ).date
            
            for expected_date in expected_dates:
                if expected_date not in date_coverage:
                    analysis['gaps'].append(str(expected_date))
                else:
                    analysis['coverage_by_day'][str(expected_date)] = list(date_coverage[expected_date])
            
            # Calculate overall coverage score
            analysis['score'] = len(date_coverage) / len(expected_dates)
            
        except Exception as e:
            logger.warning(f"Error analyzing coverage: {e}")
        
        return analysis
    
    async def _execute_backfill(self, months: int, coverage_analysis: Dict) -> Dict:
        """Execute backfill for gaps in historical data"""
        backfill = {
            'months_processed': 0,
            'posts_added': 0,
            'gaps_filled': []
        }
        
        # Identify periods needing backfill
        gaps = coverage_analysis.get('gaps', [])
        
        if gaps:
            # Group gaps by month
            gap_months = defaultdict(list)
            for gap_date in gaps[:30]:  # Limit to recent gaps
                month_key = gap_date[:7]  # YYYY-MM
                gap_months[month_key].append(gap_date)
            
            # Process each month
            for month, dates in list(gap_months.items())[:months]:
                # In production, would call Reddit API for historical data
                logger.info(f"Backfilling {len(dates)} days in {month}")
                
                backfill['gaps_filled'].extend(dates)
                backfill['months_processed'] += 1
                
                # Simulate backfill (in production, would fetch real data)
                backfill['posts_added'] += len(dates) * 10  # Estimate
        
        return backfill
    
    def _save_strategy_collection(self, df: pd.DataFrame, strategy: SortStrategy):
        """Save collection for specific strategy"""
        path = PROC / f"dual_sort_{strategy.value}_latest.jsonl"
        df.to_json(path, orient='records', lines=True)
    
    def _save_dual_sort_results(self, results: Dict) -> str:
        """Save comprehensive dual-sort results"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = PROC / f"dual_sort_results_{timestamp}.json"
        
        path.write_text(json.dumps(results, indent=2, default=str))
        return str(path)
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate executive summary of dual-sort results"""
        return {
            'total_unique_posts': len(self.dedup_cache),
            'coverage_score': results['coverage_analysis'].get('score', 0),
            'best_performing_strategy': max(
                results['collections'].items(),
                key=lambda x: x[1].get('count', 0)
            )[0] if results['collections'] else None,
            'gaps_identified': len(results['coverage_analysis'].get('gaps', [])),
            'backfill_success': results['backfill_results'].get('months_processed', 0) > 0
        }

# ============================================================================
# API Endpoints
# ============================================================================

# Initialize technique implementations
payload_optimizer = PayloadOptimizer()
phrase_miner = PhraseMiner()
filter_engine = ClientSideFilterEngine()
local_targeter = LocalSubTargeting()
vertical_specializer = VerticalSpecializer()
dual_sort_strategy = DualSortStrategy()

@app.get("/")
async def root():
    """Health check and API information"""
    return {
        "service": "CRE Intelligence MCP Server",
        "version": "1.0.0",
        "status": "operational",
        "techniques": [
            "payload_optimization",
            "phrase_mining",
            "client_side_filtering",
            "local_sub_targeting",
            "vertical_specialization",
            "dual_sort_strategy"
        ]
    }

@app.post("/optimize_payload")
async def optimize_payload(request: PayloadOptimizationRequest):
    """Technique 1: Iterative JSON payload refinement"""
    try:
        result = await payload_optimizer.optimize_payload(request)
        return result
    except Exception as e:
        logger.error(f"Payload optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mine_phrases")
async def mine_phrases(request: PhraseMiningRequest):
    """Technique 2: TF-IDF phrase mining with classification"""
    try:
        result = await phrase_miner.mine_phrases(request)
        return result
    except Exception as e:
        logger.error(f"Phrase mining failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/filter_posts")
async def filter_posts(request: ClientSideFilterRequest):
    """Technique 3: 6-stage client-side filtering"""
    try:
        result = await filter_engine.filter_posts(request)
        return result
    except Exception as e:
        logger.error(f"Post filtering failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/target_local_subs")
async def target_local_subs(request: LocalSubTargetingRequest):
    """Technique 4: Geographic targeting and expansion"""
    try:
        result = await local_targeter.target_local_subs(request)
        return result
    except Exception as e:
        logger.error(f"Local targeting failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/specialize_verticals")
async def specialize_verticals(request: VerticalSpecializationRequest):
    """Technique 5: Vertical market specialization"""
    try:
        result = await vertical_specializer.specialize_verticals(request)
        return result
    except Exception as e:
        logger.error(f"Vertical specialization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute_dual_sort")
async def execute_dual_sort(request: DualSortStrategyRequest):
    """Technique 6: Dual-sort strategy execution"""
    try:
        result = await dual_sort_strategy.execute_dual_sort(request)
        return result
    except Exception as e:
        logger.error(f"Dual-sort execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Composite endpoint for full pipeline execution
@app.post("/execute_full_pipeline")
async def execute_full_pipeline(
    metros: List[str],
    verticals: List[VerticalCategory],
    date_start: str,
    date_end: str
):
    """Execute complete intelligence pipeline with all techniques"""
    try:
        results = {}
        
        # Step 1: Optimize payloads
        payload_req = PayloadOptimizationRequest(
            subreddits=["r/commercialrealestate"] + [f"r/{m}" for m in metros],
            keywords=["lease", "rent", "property", "commercial", "tenant"],
            date_start=date_start,
            date_end=date_end
        )
        results['payload_optimization'] = await payload_optimizer.optimize_payload(payload_req)
        
        # Step 2: Mine phrases
        phrase_req = PhraseMiningRequest()
        results['phrase_mining'] = await phrase_miner.mine_phrases(phrase_req)
        
        # Step 3: Filter posts
        filter_req = ClientSideFilterRequest(
            date_start=date_start,
            date_end=date_end,
            keywords=results['phrase_mining']['top_terms'][:10] if results['phrase_mining']['ok'] else []
        )
        results['filtering'] = await filter_engine.filter_posts(filter_req)
        
        # Step 4: Target local subs
        local_req = LocalSubTargetingRequest(metro_areas=metros)
        results['local_targeting'] = await local_targeter.target_local_subs(local_req)
        
        # Step 5: Specialize verticals
        vertical_req = VerticalSpecializationRequest(verticals=verticals)
        results['vertical_specialization'] = await vertical_specializer.specialize_verticals(vertical_req)
        
        # Step 6: Execute dual-sort
        dual_req = DualSortStrategyRequest()
        results['dual_sort'] = await dual_sort_strategy.execute_dual_sort(dual_req)
        
        return {
            'ok': True,
            'pipeline_complete': True,
            'techniques_executed': 6,
            'results': results,
            'summary': {
                'posts_processed': results['filtering'].get('filtered_count', 0),
                'terms_extracted': len(results['phrase_mining'].get('top_terms', [])),
                'metros_covered': len(metros),
                'verticals_analyzed': len(verticals)
            }
        }
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)