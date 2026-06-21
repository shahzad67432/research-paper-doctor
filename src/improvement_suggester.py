from src.llm_client import call_gemini, parse_json_response

IMPROVEMENT_SYSTEM_PROMPT = """You are a research paper editor. Based on the paper summary, identified gaps, similar papers, and citation verification results, suggest specific actionable improvements.

Respond with ONLY valid JSON. No markdown fences, no code blocks, no preamble.

Return a JSON array of objects. Each object has these fields:
- "action": a specific, actionable improvement (e.g. "Add a control group of at least 30 samples")
- "priority": "high", "medium", or "low"
- "estimated_effort": a short string like "2-3 days" or "1 week" (not a precise hours estimate)
- "expected_impact": a short string describing the benefit

Return 3 to 6 suggestions. If the paper is already strong, return fewer high-impact suggestions."""


def generate_improvements(
    structure: dict,
    gaps: list,
    similar_papers: list,
    citation_results: dict,
) -> list[dict]:
    sections = []
    for key in ["abstract", "introduction", "methods", "results", "conclusion"]:
        if structure.get(key, "").strip():
            sections.append(key)

    gap_summary = {
        "total": len(gaps),
        "high": sum(1 for g in gaps if g.get("severity") == "high"),
        "medium": sum(1 for g in gaps if g.get("severity") == "medium"),
        "low": sum(1 for g in gaps if g.get("severity") == "low"),
    }

    similar_summary = []
    for p in similar_papers[:3]:
        similar_summary.append({
            "title": p.get("title", "")[:80],
            "similarity": p.get("similarity_score", 0),
        })

    user_text = f"""PAPER STRUCTURE
Title: {structure.get('title', '')[:100]}
Sections present: {', '.join(sections)}

GAPS FOUND: {gap_summary}

CITATION VERIFICATION:
Total: {citation_results.get('total', 0)}
Verified (exact DOI): {citation_results.get('verified', 0)}
Matched (fuzzy): {citation_results.get('matched', 0)}
Unmatched: {citation_results.get('unmatched', 0)}
Invalid (bad DOI): {len(citation_results.get('invalid', []))}

TOP SIMILAR PAPERS:
{similar_summary}"""

    try:
        raw = call_gemini(IMPROVEMENT_SYSTEM_PROMPT, user_text)
        return parse_json_response(raw)
    except Exception:
        return []
