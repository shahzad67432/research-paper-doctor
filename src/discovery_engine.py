from concurrent.futures import ThreadPoolExecutor, as_completed

from src import cache_manager
from src.database_search import search_arxiv, search_openalex
from src.llm_client import call_gemini, parse_json_response
from src.rag_engine import cache_papers, search_rag

DISCOVERY_SYSTEM_PROMPT = """You are a research advisor. Given a list of papers and a researcher's interest, identify papers that have gaps the researcher could fill.

Return JSON only: a list of objects with keys: title, year, url, gap_type, gap_description, why_you_can_fill_it (1 sentence, specific to their stated interest).

Return maximum 5 results."""


def find_papers_with_gaps(user_interest: str) -> list[dict]:
    papers = search_rag(user_interest, top_k=15)

    if len(papers) < 5:
        all_papers = list(papers)
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(search_arxiv, user_interest, 10): "arxiv",
                executor.submit(search_openalex, user_interest, 10): "openalex",
            }
            for future in as_completed(futures):
                try:
                    results = future.result()
                    all_papers.extend(results)
                except Exception:
                    pass

        if all_papers:
            cache_papers(all_papers)
            cache_manager.cache_api_result(user_interest, all_papers)
        papers = all_papers

    if not papers:
        return []

    paper_lines = []
    for p in papers[:15]:
        title = p.get("title", "")[:80]
        year = p.get("year", 0)
        url = p.get("url", "")
        abstract = (p.get("abstract") or "")[:200]
        paper_lines.append(f"- {title} ({year}) — {abstract}")

    user_text = f"""Researcher interest: {user_interest}

Papers:
{chr(10).join(paper_lines)}"""

    try:
        raw = call_gemini(DISCOVERY_SYSTEM_PROMPT, user_text)
        return parse_json_response(raw)
    except Exception:
        return []
