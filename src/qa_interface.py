from concurrent.futures import ThreadPoolExecutor, as_completed

from src.database_search import search_arxiv, search_openalex
from src.llm_client import call_gemini
from src.rag_engine import cache_papers, search_rag

QA_SYSTEM_PROMPT = """You are a research assistant. Answer the user's question using only the provided papers as context. Be specific, cite paper titles inline, and end with a 'Recommended Reading' list of the most relevant papers. Return plain text, not JSON."""


def answer_question(query: str) -> dict:
    papers = search_rag(query, top_k=8)
    api_calls_saved = len(papers)

    if len(papers) < 3:
        all_papers = list(papers)
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

        if all_papers:
            cache_papers(all_papers)
        papers = all_papers
        api_calls_saved = 0

    if not papers:
        return {"answer": "No relevant papers found.", "papers_used": [], "api_calls_saved": 0}

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

    try:
        answer = call_gemini(QA_SYSTEM_PROMPT, user_text)
    except Exception:
        answer = "Unable to generate answer due to a service error."

    return {
        "answer": answer,
        "papers_used": papers_used,
        "api_calls_saved": api_calls_saved,
    }
