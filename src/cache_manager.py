import hashlib
import json
import os
from datetime import datetime, timezone

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CACHE_FILE = os.path.join(CACHE_DIR, "api_cache.json")


def _ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def _hash_query(query: str) -> str:
    return hashlib.md5(query.encode("utf-8")).hexdigest()


def _read_cache() -> dict:
    _ensure_cache_dir()
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _write_cache(cache: dict):
    _ensure_cache_dir()
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def get_cached_results(query: str) -> dict | None:
    cache = _read_cache()
    key = _hash_query(query)
    entry = cache.get(key)
    if entry is None:
        return None
    return entry


def cache_api_result(query: str, results: list) -> None:
    cache = _read_cache()
    key = _hash_query(query)
    cache[key] = {
        "query": query,
        "results": results,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _write_cache(cache)
