# -*- coding: utf-8 -*-
"""
VibeDoMuse · history_manager.py
In-memory history management for generated music and follow-up conversations.

Features:
- Stores generation history in memory (no disk I/O)
- Tracks relationships between initial generations and follow-ups
- Thread-safe for UI usage
"""
import json
import logging
import time
import threading
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

log = logging.getLogger(__name__)

# Maximum number of history items to keep in memory
MAX_HISTORY_ITEMS = 100


@dataclass
class HistoryItem:
    """Represents a single generation or follow-up entry in history."""
    id: str  # Unique identifier
    timestamp: float  # Unix timestamp
    user_text: str  # Original user request
    analysis: Optional[str] = None  # AI's understanding (if available)
    score: Optional[Dict] = None  # Generated JSON score
    seed: Optional[int] = None  # Generation seed
    method: str = "unknown"  # Generation method (rule, llm, llm_v2, followup, etc.)
    feedback: Optional[str] = None  # User feedback for follow-ups
    parent_id: Optional[str] = None  # ID of parent generation (for follow-ups)
    summary: str = ""  # Brief summary for display


class HistoryManager:
    """Thread-safe in-memory history manager for VibeDoMuse."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the history manager."""
        if not self._initialized:
            self._history: List[HistoryItem] = []
            self._id_counter = 0
            self._initialized = True
            log.info("HistoryManager initialized")

    def add_generation(self, user_text: str, result: Dict[str, Any],
                      analysis: Optional[str] = None, parent_id: Optional[str] = None) -> str:
        """Add a generation result to history.

        Args:
            user_text: The user's natural language request
            result: The generation result from agent.run() or similar
            analysis: Optional AI understanding of the request
            parent_id: Optional ID of parent generation (for follow-ups)

        Returns:
            The ID of the added history item
        """
        with self._lock:
            self._id_counter += 1
            item_id = f"gen_{int(time.time())}_{self._id_counter}"

            # Extract summary from result
            summary = result.get("summary", result.get("text", "")[:100])

            item = HistoryItem(
                id=item_id,
                timestamp=time.time(),
                user_text=user_text,
                analysis=analysis,
                score=result.get("score"),
                seed=result.get("seed"),
                method=result.get("method", "unknown"),
                parent_id=parent_id,
                summary=summary
            )

            # Add to beginning of list (newest first)
            self._history.insert(0, item)

            # Keep only MAX_HISTORY_ITEMS
            if len(self._history) > MAX_HISTORY_ITEMS:
                self._history = self._history[:MAX_HISTORY_ITEMS]

            log.debug(f"Added history item {item_id}: {summary[:50]}...")
            return item_id

    def get_history(self) -> List[HistoryItem]:
        """Get all history items sorted by timestamp (newest first)."""
        with self._lock:
            return list(self._history)

    def get_item(self, item_id: str) -> Optional[HistoryItem]:
        """Get a specific history item by ID."""
        with self._lock:
            for item in self._history:
                if item.id == item_id:
                    return item
            return None

    def get_followups(self, parent_id: str) -> List[HistoryItem]:
        """Get all follow-up items for a given parent ID."""
        with self._lock:
            return [item for item in self._history if item.parent_id == parent_id]

    def clear(self):
        """Clear all history."""
        with self._lock:
            self._history.clear()
            self._id_counter = 0
            log.info("History cleared")

    def get_conversation_thread(self, item_id: str) -> List[HistoryItem]:
        """Get the full conversation thread (parent and all follow-ups) for an item.

        Returns items in chronological order (oldest first).
        """
        with self._lock:
            # Find the root item (first item in the thread without a parent)
            root_item = self.get_item(item_id)
            if not root_item:
                return []

            # Find the root of the thread
            current = root_item
            while current.parent_id:
                parent = self.get_item(current.parent_id)
                if parent:
                    current = parent
                else:
                    break

            # Collect all items in this thread
            thread = [current]
            followups = self.get_followups(current.id)
            thread.extend(followups)

            return thread


# Global instance
history_manager = HistoryManager()
