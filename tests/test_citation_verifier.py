import pytest

from src.citation_verifier import _extract_doi, _string_similarity


class TestCitationVerifier:
    def test_doi_extraction_found(self):
        ref = "J. Smith, \"A Study,\" Nature, vol. 10, doi:10.1234/test.5678, 2023."
        doi = _extract_doi(ref)
        assert doi == "10.1234/test.5678"

    def test_doi_extraction_complex(self):
        ref = "doi:10.1001/jama.2020.12345"
        doi = _extract_doi(ref)
        assert doi == "10.1001/jama.2020.12345"

    def test_doi_extraction_missing(self):
        ref = "J. Smith, \"A Study,\" Nature, vol. 10, pp. 1-5, 2023."
        doi = _extract_doi(ref)
        assert doi is None

    def test_string_similarity_match(self):
        sim = _string_similarity(
            "deep learning for healthcare diagnosis",
            "deep learning in healthcare diagnosis",
        )
        assert sim >= 0.6

    def test_string_similarity_no_match(self):
        sim = _string_similarity(
            "quantum computing in biology",
            "machine learning for image segmentation",
        )
        assert sim < 0.6

    @pytest.mark.integration
    def test_live_doi_verification(self):
        from src.citation_verifier import _verify_doi
        result = _verify_doi("10.1038/s41586-021-03819-2")
        assert result is True

    @pytest.mark.integration
    def test_live_bibliographic_match(self):
        from src.citation_verifier import _bibliographic_match
        title = _bibliographic_match(
            "Attention is all you need, NeurIPS, 2017"
        )
        assert title is not None
        assert len(title) > 0
