"""
utils/cache.py
In-memory LRU Cache for resumes, embeddings, and NLP results.
"""

from functools import lru_cache
from typing import Any, Dict

class SimpleLRUCache:
    def __init__(self, maxsize: int = 128):
        self.cache: Dict[str, Any] = {}
        self.maxsize = maxsize

    def get(self, key: str) -> Any:
        return self.cache.get(key)

    def set(self, key: str, value: Any):
        if len(self.cache) >= self.maxsize:
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        self.cache[key] = value

    def clear(self):
        self.cache.clear()

cache = SimpleLRUCache()
