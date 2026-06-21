import pytest

from src.database_search import search_arxiv, search_pubmed, search_openalex


EXPECTED_KEYS = {"id", "title", "abstract", "authors", "year", "url"}


class TestArxiv:
    @pytest.mark.integration
    def test_arxiv_returns_results(self):
        results = search_arxiv("transformer attention", max_results=3)
        assert len(results) > 0, "arXiv should return results"
        assert EXPECTED_KEYS == set(results[0].keys()), (
            f"arXiv keys mismatch: {set(results[0].keys())}"
        )

    @pytest.mark.integration
    def test_arxiv_results_have_content(self):
        results = search_arxiv("transformer attention", max_results=3)
        first = results[0]
        assert first["title"], "Title should not be empty"
        assert first["abstract"], "Abstract should not be empty"
        assert len(first["authors"]) > 0, "Should have at least one author"
        assert first["year"] > 0, "Year should be valid"

    @pytest.mark.integration
    def test_arxiv_max_results(self):
        results = search_arxiv("machine learning", max_results=5)
        assert len(results) <= 5

    @pytest.mark.integration
    def test_arxiv_authors_is_list_of_strings(self):
        results = search_arxiv("transformer attention", max_results=2)
        for author in results[0]["authors"]:
            assert isinstance(author, str)


class TestPubmed:
    @pytest.mark.integration
    def test_pubmed_returns_results(self):
        results = search_pubmed("cancer", max_results=3)
        assert len(results) > 0, "PubMed should return results"
        assert EXPECTED_KEYS == set(results[0].keys()), (
            f"PubMed keys mismatch: {set(results[0].keys())}"
        )

    @pytest.mark.integration
    def test_pubmed_results_have_content(self):
        results = search_pubmed("cancer", max_results=3)
        first = results[0]
        assert first["title"], "Title should not be empty"
        assert len(first["authors"]) > 0, "Should have at least one author"
        assert first["year"] > 0, "Year should be valid"


class TestOpenAlex:
    @pytest.mark.integration
    def test_openalex_returns_results(self):
        results = search_openalex("transformer attention", max_results=3)
        assert len(results) > 0, "OpenAlex should return results"
        assert EXPECTED_KEYS == set(results[0].keys()), (
            f"OpenAlex keys mismatch: {set(results[0].keys())}"
        )

    @pytest.mark.integration
    def test_openalex_results_have_content(self):
        results = search_openalex("transformer attention", max_results=3)
        first = results[0]
        assert first["title"], "Title should not be empty"
        assert first["abstract"], "Abstract should not be empty"
        assert len(first["authors"]) > 0, "Should have at least one author"
        assert first["year"] > 0, "Year should be valid"
        assert first["url"], "URL should not be empty"
