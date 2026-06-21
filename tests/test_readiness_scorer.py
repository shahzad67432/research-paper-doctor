from src.readiness_scorer import calculate_readiness_score


class TestReadinessScorer:
    def test_perfect_paper(self):
        structure = {
            "methods": "some methods",
            "results": "some results",
            "conclusion": "some conclusion",
        }
        gaps = []
        citation_results = {"invalid": []}
        r = calculate_readiness_score(structure, gaps, citation_results)
        assert r["score"] == 100
        for v in r["breakdown"].values():
            assert v == 100

    def test_high_severity_deduction(self):
        structure = {
            "methods": "methods",
            "results": "results",
            "conclusion": "conclusion",
        }
        gaps = [{"severity": "high", "gap_type": "methodology"}]
        citation_results = {"invalid": []}
        r = calculate_readiness_score(structure, gaps, citation_results)
        assert r["score"] == 90

    def test_missing_sections_deduction(self):
        structure = {
            "methods": "",
            "results": "",
            "conclusion": "some conclusion",
        }
        gaps = []
        citation_results = {"invalid": []}
        r = calculate_readiness_score(structure, gaps, citation_results)
        assert r["score"] == 84

    def test_invalid_citations_deduction(self):
        structure = {
            "methods": "methods",
            "results": "results",
            "conclusion": "conclusion",
        }
        gaps = []
        citation_results = {"invalid": ["ref1", "ref2"]}
        r = calculate_readiness_score(structure, gaps, citation_results)
        assert r["score"] == 94

    def test_combined_deductions(self):
        structure = {
            "methods": "",
            "results": "results",
            "conclusion": "",
        }
        gaps = [
            {"severity": "high", "gap_type": "methodology"},
            {"severity": "low", "gap_type": "literature"},
        ]
        citation_results = {"invalid": ["ref1", "ref2", "ref3"]}
        r = calculate_readiness_score(structure, gaps, citation_results)
        expected = 100 - 10 - 2 - 3 * 3 - 2 * 8
        assert r["score"] == expected

    def test_clamp_low(self):
        structure = {
            "methods": "",
            "results": "",
            "conclusion": "",
        }
        gaps = [
            {"severity": "high", "gap_type": "methodology"},
            {"severity": "high", "gap_type": "literature"},
            {"severity": "high", "gap_type": "results"},
            {"severity": "high", "gap_type": "conclusion"},
            {"severity": "high", "gap_type": "analysis"},
        ]
        citation_results = {"invalid": ["ref1"] * 30}
        r = calculate_readiness_score(structure, gaps, citation_results)
        assert r["score"] == 0

    def test_sub_score_methodology(self):
        structure = {
            "methods": "methods",
            "results": "results",
            "conclusion": "conclusion",
        }
        gaps = [
            {"severity": "high", "gap_type": "methodology"},
            {"severity": "high", "gap_type": "literature"},
        ]
        citation_results = {"invalid": []}
        r = calculate_readiness_score(structure, gaps, citation_results)
        assert r["breakdown"]["methodology"] == 90
        assert r["breakdown"]["novelty"] == 90
        assert r["breakdown"]["citations"] == 100
        assert r["breakdown"]["writing"] == 100

    def test_sub_score_citations(self):
        structure = {
            "methods": "methods",
            "results": "results",
            "conclusion": "conclusion",
        }
        gaps = []
        citation_results = {"invalid": ["ref1", "ref2"]}
        r = calculate_readiness_score(structure, gaps, citation_results)
        assert r["breakdown"]["citations"] == 94
        assert r["breakdown"]["methodology"] == 100
