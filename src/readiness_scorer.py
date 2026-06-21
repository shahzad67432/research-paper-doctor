MISSING_SECTION_PENALTY = 8
SEVERITY_PENALTIES = {"high": 10, "medium": 5, "low": 2}
INVALID_CITATION_PENALTY = 3

CATEGORY_GAP_MAP = {
    "methodology": {"methodology"},
    "novelty": {"literature", "analysis"},
    "writing": {"results", "conclusion"},
}


def _sub_score(gaps: list[dict], gap_types: set[str], invalid_citations: int) -> int:
    score = 100
    for g in gaps:
        if g.get("gap_type") in gap_types:
            score -= SEVERITY_PENALTIES.get(g.get("severity", "low"), 2)
    score -= invalid_citations * INVALID_CITATION_PENALTY
    return max(score, 0)


def calculate_readiness_score(
    structure: dict,
    gaps: list[dict],
    citation_results: dict,
) -> dict:
    score = 100

    for g in gaps:
        sev = g.get("severity", "low")
        score -= SEVERITY_PENALTIES.get(sev, 2)

    invalid_citations = len(citation_results.get("invalid", []))
    score -= invalid_citations * INVALID_CITATION_PENALTY

    missing_sections = 0
    for key in ["methods", "results", "conclusion"]:
        if not structure.get(key, "").strip():
            missing_sections += 1
    score -= missing_sections * MISSING_SECTION_PENALTY

    score = max(0, min(100, score))

    breakdown = {
        "methodology": _sub_score(gaps, CATEGORY_GAP_MAP["methodology"], 0),
        "novelty": _sub_score(gaps, CATEGORY_GAP_MAP["novelty"], 0),
        "citations": _sub_score([], set(), invalid_citations),
        "writing": _sub_score(gaps, CATEGORY_GAP_MAP["writing"], 0),
    }

    return {"score": score, "breakdown": breakdown}
