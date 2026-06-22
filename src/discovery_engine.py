import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
from sentence_transformers import SentenceTransformer

from src import cache_manager
from src.database_search import search_arxiv, search_openalex
from src.llm_client import call_gemini, parse_json_response
from src.rag_engine import cache_papers, search_rag

_embedder = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


def _relevance_filter(interest: str, papers: list[dict], threshold: float = 0.2) -> list[dict]:
    if not papers:
        return []
    model = _get_embedder()
    interest_vec = model.encode(interest)
    scored: list[tuple[float, dict]] = []
    for p in papers:
        text = f"{p.get('title', '')} {p.get('abstract', '')}"
        if not text.strip():
            text = p.get("title", "")
        p_vec = model.encode(text)
        sim = float(np.dot(interest_vec, p_vec) / (np.linalg.norm(interest_vec) * np.linalg.norm(p_vec)))
        if sim >= threshold:
            scored.append((sim, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored]

DISCOVERY_SYSTEM_PROMPT = """You are a research advisor. Given a list of papers and a researcher's interest, identify papers that have gaps the researcher could fill.

Return JSON only: a list of objects with keys:
- title (exact title from the paper list)
- year (exact year from the paper list)
- url (exact URL from the paper list — never fabricate a URL)
- gap_type (one of: methodology, analysis, literature, results, conclusion)
- gap_description (2-3 sentences explaining what is missing and why it matters)
- why_you_can_fill_it (1-2 sentences specific to their stated interest)

Return maximum 5 results. Never fabricate URLs — use the exact URL from the paper list."""


def _merge_papers(lists: list[list[dict]]) -> list[dict]:
    seen_titles: set[str] = set()
    merged: list[dict] = []
    for lst in lists:
        for p in lst:
            t = (p.get("title") or "").strip().lower()
            if t and t not in seen_titles:
                seen_titles.add(t)
                merged.append(p)
    return merged


def find_papers_with_gaps(
    user_interest: str,
    step_callback: callable | None = None,
) -> list[dict]:
    papers = search_rag(user_interest, top_k=15)
    _cb(step_callback, "RAG cache search", len(papers) >= 5)

    all_papers: list[dict] = list(papers)
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

    papers = _merge_papers([all_papers, papers])
    papers = _relevance_filter(user_interest, papers)
    live_ok = any(f.done() and not f.exception() for f in futures)
    _cb(step_callback, "Live search (arXiv + OpenAlex)", live_ok)

    if papers:
        cache_papers(papers)
        cache_manager.cache_api_result(user_interest, papers)

    if not papers:
        _cb(step_callback, "Papers found", False)
        return []

    _cb(step_callback, "Papers found", True)

    paper_lines = []
    for p in papers[:15]:
        title = p.get("title", "")[:80]
        year = p.get("year", 0)
        url = p.get("url", "")
        abstract = (p.get("abstract") or "")[:200]
        paper_lines.append(f"- {title} ({year}) | URL: {url} | {abstract}")

    user_text = f"""Researcher interest: {user_interest}

Papers:
{chr(10).join(paper_lines)}"""

    llm_ok = False
    try:
        raw = call_gemini(DISCOVERY_SYSTEM_PROMPT, user_text)
        results = parse_json_response(raw)
        if results:
            llm_ok = True
            _cb(step_callback, "LLM gap analysis", True)
            return results
    except Exception as e:
        print(f"discovery LLM error: {e}", file=sys.stderr)

    if not llm_ok:
        _cb(step_callback, "LLM gap analysis — unavailable, using fallback", False)

    return [
        {
            "title": p.get("title", "")[:80],
            "year": p.get("year", 0),
            "url": p.get("url", ""),
            "gap_type": "literature",
            "gap_description": (
                "This paper may contain research gaps relevant to your interest. "
                "Review it to identify specific open problems."
            ),
            "why_you_can_fill_it": (
                f"Your expertise in this area positions you to extend or "
                f"challenge the findings presented in this paper."
            ),
            "_note": "LLM unavailable — showing papers without gap analysis",
        }
        for p in papers[:5]
    ]


def _cb(callback: callable | None, label: str, ok: bool) -> None:
    if callback:
        callback(label, ok)
