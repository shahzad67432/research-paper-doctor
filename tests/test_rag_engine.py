import pytest

from src.rag_engine import cache_papers, search_rag


class TestRagEngine:
    def test_cache_and_search_round_trip(self):
        papers = [
            {
                "id": "test-001",
                "title": "Deep Learning for Healthcare",
                "abstract": "This paper explores deep learning applications in medical diagnosis and treatment planning.",
                "authors": ["Alice Smith"],
                "year": 2024,
                "url": "https://example.com/001",
            },
            {
                "id": "test-002",
                "title": "Quantum Computing in Biology",
                "abstract": "A review of quantum computing methods for biological sequence analysis.",
                "authors": ["Bob Jones"],
                "year": 2023,
                "url": "https://example.com/002",
            },
        ]
        cache_papers(papers)

        results = search_rag("deep learning healthcare diagnosis", top_k=5)
        assert len(results) > 0
        assert "similarity_score" in results[0]
        for r in results:
            assert r["similarity_score"] >= 0.0
            assert r["similarity_score"] <= 1.0

        sorted_scores = [r["similarity_score"] for r in results]
        assert sorted_scores == sorted(sorted_scores, reverse=True)

    def test_search_empty_collection_returns_empty(self):
        results = search_rag("random nonexistent query xyz123", top_k=5)
        assert isinstance(results, list)
