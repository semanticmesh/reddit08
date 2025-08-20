"""
Sliding Window Context Manager
Manages context with intelligent pruning to prevent overflow
"""
import logging
from collections import deque
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ContextConfig:
    """Configuration for Context Manager"""
    max_tokens: int = 100000
    max_context_items: int = 1000
    priority_retention: bool = True

class SlidingWindowContextManager:
    """Manages context with sliding window and intelligent pruning"""
    
    def __init__(self, config: Optional[ContextConfig] = None):
        self.config = config or ContextConfig()
        self.context_window = deque(maxlen=self.config.max_context_items)
        self.priority_context: Dict[str, Any] = {}  # Always retained
        self.token_count = 0
        self.logger = logging.getLogger(__name__)
        
    def add_context(self, content: Union[str, Dict[str, Any]], priority: str = "normal") -> None:
        """Add context with intelligent pruning"""
        # Convert content to string for token estimation
        content_str = str(content) if not isinstance(content, str) else content
        content_tokens = len(content_str) // 4  # Rough token estimation
        
        if priority == "critical":
            # Add to priority context (never pruned)
            content_hash = hash(content_str)
            self.priority_context[content_hash] = {
                "content": content,
                "tokens": content_tokens,
                "added_at": self.token_count
            }
        else:
            # Add to sliding window
            self.context_window.append({
                "content": content,
                "tokens": content_tokens,
                "priority": priority,
                "added_at": self.token_count
            })
        
        # Update token count
        self.token_count += content_tokens
        
        # Prune if exceeding limits
        self._prune_context()
        
        self.logger.debug(f"Added context: {content_tokens} tokens, total: {self.get_total_tokens()}")
    
    def _prune_context(self) -> None:
        """Prune context when exceeding token limits"""
        while self.get_total_tokens() > self.config.max_tokens:
            if self.context_window:
                # Remove oldest non-critical item
                removed = self.context_window.popleft()
                self.token_count -= removed["tokens"]
                self.logger.debug(f"Pruned context item: {removed['tokens']} tokens")
            else:
                # No more items to prune
                self.logger.warning("Context limit exceeded but no items to prune")
                break
    
    def get_total_tokens(self) -> int:
        """Get total token count including priority context"""
        # Count tokens in sliding window
        window_tokens = sum(item["tokens"] for item in self.context_window)
        
        # Count tokens in priority context
        priority_tokens = sum(item["tokens"] for item in self.priority_context.values())
        
        return window_tokens + priority_tokens
    
    def get_context_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of current context"""
        return {
            "total_tokens": self.get_total_tokens(),
            "window_items": len(self.context_window),
            "priority_items": len(self.priority_context),
            "priority_context": list(self.priority_context.values()),
            "recent_context": list(self.context_window)[-10:] if self.context_window else []
        }
    
    def clear_context(self) -> None:
        """Clear all context"""
        self.context_window.clear()
        self.priority_context.clear()
        self.token_count = 0
        self.logger.info("Context cleared")
    
    def get_relevant_context(self, query: str = "", max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Get context relevant to a query, up to max_tokens"""
        max_tokens = max_tokens or self.config.max_tokens
        
        # Start with priority context (always included)
        relevant_context = {
            "priority": list(self.priority_context.values()),
            "window": []
        }
        
        current_tokens = sum(item["tokens"] for item in self.priority_context.values())
        
        # Add window context items until we reach the limit
        for item in reversed(self.context_window):  # Most recent first
            if current_tokens + item["tokens"] <= max_tokens:
                relevant_context["window"].append(item)
                current_tokens += item["tokens"]
            else:
                break
        
        return relevant_context
    
    def remove_old_context(self, max_age: int) -> int:
        """Remove context items older than max_age token positions"""
        cutoff = self.token_count - max_age
        removed_count = 0
        
        # Remove from sliding window
        new_window = deque()
        for item in self.context_window:
            if item["added_at"] >= cutoff:
                new_window.append(item)
            else:
                removed_count += 1
                self.token_count -= item["tokens"]
        
        self.context_window = new_window
        return removed_count