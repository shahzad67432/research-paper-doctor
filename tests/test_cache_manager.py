import json
import os
import tempfile

import pytest

from src.cache_manager import get_cached_results, cache_api_result, _hash_query


class TestCacheManager:
    def test_cache_round_trip(self):
        query = "test query for cache"
        results = [{"id": "123", "title": "Test Paper"}]
        cache_api_result(query, results)
        cached = get_cached_results(query)
        assert cached is not None
        assert cached["query"] == query
        assert cached["results"] == results
        assert "timestamp" in cached

    def test_cache_miss_returns_none(self):
        result = get_cached_results("nonexistent-query-12345")
        assert result is None

    def test_hash_is_deterministic(self):
        h1 = _hash_query("hello world")
        h2 = _hash_query("hello world")
        assert h1 == h2

    def test_different_queries_different_hashes(self):
        h1 = _hash_query("query one")
        h2 = _hash_query("query two")
        assert h1 != h2

    def test_cache_overwrites_same_query(self):
        query = "overwrite-test"
        results1 = [{"id": "1"}]
        results2 = [{"id": "2"}]
        cache_api_result(query, results1)
        cache_api_result(query, results2)
        cached = get_cached_results(query)
        assert cached["results"] == results2
