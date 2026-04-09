"""Disk-based JSON cache with per-query-type TTL."""

import json
import time
from pathlib import Path
from typing import Any

from src.shared.config import CACHE_DIR


class DiskCache:
    """Simple disk cache that stores JSON data with timestamps."""

    def __init__(self, cache_dir: Path = CACHE_DIR) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def get(self, key: str, ttl: int) -> dict | None:
        """Read cached data if it exists and hasn't expired."""
        path = self._cache_path(key)
        if not path.exists():
            return None
        try:
            with open(path) as f:
                cached = json.load(f)
            if time.time() - cached.get("fetched_at", 0) < ttl:
                return cached["data"]
        except (json.JSONDecodeError, KeyError):
            pass
        return None

    def set(self, key: str, data: Any) -> None:
        """Write data to cache with current timestamp."""
        path = self._cache_path(key)
        with open(path, "w") as f:
            json.dump({"fetched_at": time.time(), "data": data}, f)

    def clear(self, key: str | None = None) -> None:
        """Remove a specific cache entry, or all entries if key is None."""
        if key is not None:
            path = self._cache_path(key)
            if path.exists():
                path.unlink()
        else:
            for path in self.cache_dir.glob("*.json"):
                path.unlink()
