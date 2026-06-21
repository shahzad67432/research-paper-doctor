import os
from pathlib import Path

import pytest

from src.parser import parse_paper_pdf
from src.analyzer import analyze_paper_structure

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"
PDF_FILES = sorted(EXAMPLES_DIR.glob("*.pdf"))


def _get_test_pdfs():
    if not PDF_FILES:
        pytest.skip("No PDFs found in examples/ — place a .pdf there to run tests")
    return PDF_FILES


class TestParser:
    def test_parse_returns_dict_with_all_keys(self):
        pdfs = _get_test_pdfs()
        result = parse_paper_pdf(str(pdfs[0]))
        expected_keys = {
            "title", "abstract", "introduction", "methods",
            "results", "conclusion", "references", "full_text",
        }
        assert expected_keys == set(result.keys()), (
            f"Missing keys: {expected_keys - set(result.keys())}"
        )

    def test_full_text_non_empty(self):
        pdfs = _get_test_pdfs()
        result = parse_paper_pdf(str(pdfs[0]))
        assert len(result["full_text"]) > 0, "full_text should not be empty"

    def test_references_is_list(self):
        pdfs = _get_test_pdfs()
        result = parse_paper_pdf(str(pdfs[0]))
        assert isinstance(result["references"], list)

    def test_title_not_empty(self):
        pdfs = _get_test_pdfs()
        result = parse_paper_pdf(str(pdfs[0]))
        assert len(result["title"]) > 0, "title should not be empty"

    def test_sections_are_strings(self):
        pdfs = _get_test_pdfs()
        result = parse_paper_pdf(str(pdfs[0]))
        for key in ["abstract", "introduction", "methods", "results", "conclusion"]:
            assert isinstance(result[key], str), f"{key} should be a string"

    def test_parse_multiple_pdfs(self):
        pdfs = _get_test_pdfs()
        for pdf in pdfs:
            result = parse_paper_pdf(str(pdf))
            assert len(result["full_text"]) > 0
            assert result["title"] != ""


class TestAnalyzer:
    def test_analyzer_returns_expected_keys(self):
        pdfs = _get_test_pdfs()
        parsed = parse_paper_pdf(str(pdfs[0]))
        analysis = analyze_paper_structure(parsed)
        assert "word_counts" in analysis
        assert "sections_present" in analysis
        assert "topic_guess" in analysis

    def test_word_counts_are_integers(self):
        pdfs = _get_test_pdfs()
        parsed = parse_paper_pdf(str(pdfs[0]))
        analysis = analyze_paper_structure(parsed)
        for section, count in analysis["word_counts"].items():
            assert isinstance(count, int), f"{section} count should be int"

    def test_topic_guess_not_empty_if_title_present(self):
        pdfs = _get_test_pdfs()
        parsed = parse_paper_pdf(str(pdfs[0]))
        analysis = analyze_paper_structure(parsed)
        if parsed["title"]:
            assert len(analysis["topic_guess"]) > 0
