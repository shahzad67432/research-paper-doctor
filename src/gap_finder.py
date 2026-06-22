from src.llm_client import call_gemini, parse_json_response

GAP_SYSTEM_PROMPT = """You are a research paper reviewer. Analyze the given paper structure and identify research gaps in 5 categories: methodology, analysis, literature, results, conclusion.

Respond with ONLY valid JSON. No markdown fences, no code blocks, no preamble. The response must be parseable by json.loads() directly.

Return a JSON array of objects. Each object has these fields:
- "gap_type": one of "methodology", "analysis", "literature", "results", "conclusion"
- "description": a concise sentence describing the gap
- "severity": "high", "medium", or "low"
- "suggestion": a concrete suggestion to address the gap

Return at least 2 gaps, up to 8 max. If you cannot find any meaningful gaps, return an empty array []."""


def find_research_gaps(structure: dict) -> list[dict]:
    title = structure.get("title", "")
    abstract = structure.get("abstract", "")
    intro = structure.get("introduction", "")
    methods = structure.get("methods", "")
    results = structure.get("results", "")
    conclusion = structure.get("conclusion", "")
    refs = structure.get("references", [])

    user_text = f"""TITLE: {title}

ABSTRACT: {abstract[:2000]}

INTRODUCTION (first 1500 chars): {intro[:1500]}

METHODS (first 1500 chars): {methods[:1500]}

RESULTS (first 1500 chars): {results[:1500]}

CONCLUSION: {conclusion[:1500]}

NUMBER OF REFERENCES: {len(refs)}"""

    try:
        raw = call_gemini(GAP_SYSTEM_PROMPT, user_text)
        return parse_json_response(raw)
    except Exception as e:
        print(f"gap_finder LLM error: {e}", file=sys.stderr)
        return []
