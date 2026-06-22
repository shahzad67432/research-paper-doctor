import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
from sentence_transformers import SentenceTransformer

from src.database_search import search_arxiv, search_openalex
from src.llm_client import call_gemini
from src.rag_engine import cache_papers, search_rag

QA_SYSTEM_PROMPT = """You are a research assistant. Answer the user's question using only the provided papers as context. Be specific, cite paper titles inline, and end with a 'Recommended Reading' list of the most relevant papers. Return plain text, not JSON."""


_embedder = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


def _relevance_filter(query: str, papers: list[dict], threshold: float = 0.2) -> list[dict]:
    if not papers:
        return []
    model = _get_embedder()
    query_vec = model.encode(query)
    scored: list[tuple[float, dict]] = []
    for p in papers:
        text = f"{p.get('title', '')} {p.get('abstract', '')}"
        if not text.strip():
            text = p.get("title", "")
        p_vec = model.encode(text)
        sim = float(np.dot(query_vec, p_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(p_vec)))
        if sim >= threshold:
            scored.append((sim, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored]


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


def answer_question(
    query: str,
    step_callback: callable | None = None,
) -> dict:
    cached = search_rag(query, top_k=8)
    _cb(step_callback, "RAG cache search", len(cached) >= 3)

    all_papers: list[dict] = list(cached)
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(search_arxiv, query, 5): "arxiv",
            executor.submit(search_openalex, query, 5): "openalex",
        }
        for future in as_completed(futures):
            try:
                results = future.result()
                all_papers.extend(results)
            except Exception:
                pass

    papers = _merge_papers([all_papers, cached])
    papers = _relevance_filter(query, papers)
    live_ok = any(f.done() and not f.exception() for f in futures)
    _cb(step_callback, "Live search (arXiv + OpenAlex)", live_ok)

    api_calls_saved = len(cached) if live_ok else 0

    if papers:
        cache_papers(papers)

    if not papers:
        _cb(step_callback, "Papers found", False)
        return {"answer": "No relevant papers found.", "papers_used": [], "api_calls_saved": 0}

    _cb(step_callback, "Papers found", True)

    context_parts = []
    papers_used = []
    char_count = 0
    for p in papers[:8]:
        title = p.get("title", "")
        year = p.get("year", 0)
        abstract = (p.get("abstract") or "")[:300]
        entry = f"TITLE: {title} ({year})\nABSTRACT: {abstract}\n"
        if char_count + len(entry) > 1500:
            break
        context_parts.append(entry)
        char_count += len(entry)
        papers_used.append({
            "title": title,
            "year": year,
            "url": p.get("url", ""),
        })

    context = "\n".join(context_parts)
    user_text = f"""Question: {query}

Context papers:
{context}"""

    llm_ok = True
    try:
        answer = call_gemini(QA_SYSTEM_PROMPT, user_text)
    except Exception as e:
        print(f"qa_interface LLM error: {e}", file=sys.stderr)
        answer = "Unable to generate answer due to a service error."
        llm_ok = False

    _cb(step_callback, "LLM answer generation", llm_ok)
    if api_calls_saved > 0:
        _cb(step_callback, f"API calls saved by RAG cache: {api_calls_saved}", True)

    return {
        "answer": answer,
        "papers_used": papers_used,
        "api_calls_saved": api_calls_saved,
    }


def _cb(callback: callable | None, label: str, ok: bool) -> None:
    if callback:
        callback(label, ok)
