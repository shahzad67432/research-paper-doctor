from concurrent.futures import ThreadPoolExecutor, as_completed

from sentence_transformers import SentenceTransformer
import numpy as np

from src.database_search import search_arxiv, search_pubmed, search_openalex
from src import cache_manager
from src.rag_engine import cache_papers, search_rag


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def _search_query(title: str, abstract: str) -> str:
    combined = f"{title} {abstract}"
    if len(combined) <= 300:
        return combined
    return f"{title} {abstract[:150]}"


def check_similar_papers(title: str, abstract: str) -> list[dict]:
    full_query = f"{title} {abstract}"
    api_query = _search_query(title, abstract)

    cached = cache_manager.get_cached_results(full_query)
    if cached:
        rag_results = search_rag(full_query, top_k=10)
        good_results = [r for r in rag_results if r.get("similarity_score", 0) > 0.5]
        if len(good_results) >= 3:
            return good_results[:5]

    all_papers = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(search_arxiv, api_query): "arxiv",
            executor.submit(search_pubmed, api_query): "pubmed",
            executor.submit(search_openalex, api_query): "openalex",
        }
        for future in as_completed(futures):
            try:
                results = future.result()
                all_papers.extend(results)
            except Exception:
                pass

    if all_papers:
        cache_manager.cache_api_result(full_query, all_papers)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    input_emb = model.encode([full_query])[0]

    scored = []
    for paper in all_papers:
        paper_text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
        if not paper_text.strip():
            continue
        paper_emb = model.encode([paper_text])[0]
        sim = _cosine_similarity(input_emb, paper_emb)
        paper["similarity_score"] = round(sim, 4)
        scored.append(paper)

    scored.sort(key=lambda x: x["similarity_score"], reverse=True)

    top = scored[:5]

    if top:
        cache_papers(top)

    return top
