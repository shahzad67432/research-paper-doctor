import hashlib
import os

import chromadb
from sentence_transformers import SentenceTransformer

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma_db")
COLLECTION_NAME = "research_papers"


_client = None
_collection = None
_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _get_collection():
    global _client, _collection
    if _collection is None:
        os.makedirs(CHROMA_DIR, exist_ok=True)
        _client = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = _client.get_or_create_collection(name=COLLECTION_NAME)
    return _collection


def _paper_id(paper: dict) -> str:
    if paper.get("id"):
        return hashlib.md5(paper["id"].encode("utf-8")).hexdigest()
    raw = f"{paper.get('title', '')}{paper.get('year', 0)}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def cache_papers(papers: list[dict]) -> None:
    if not papers:
        return
    collection = _get_collection()
    model = _get_model()
    ids = []
    documents = []
    metadatas = []
    for paper in papers:
        pid = _paper_id(paper)
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
        ids.append(pid)
        documents.append(text)
        metadatas.append({
            "title": paper.get("title", ""),
            "year": str(paper.get("year", 0)),
            "authors": ", ".join(paper.get("authors", [])),
            "url": paper.get("url", ""),
        })
    embeddings = model.encode(documents).tolist()
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def search_rag(query: str, top_k: int = 5) -> list[dict]:
    try:
        collection = _get_collection()
    except Exception:
        return []
    try:
        count = collection.count()
        if count == 0:
            return []
    except Exception:
        return []

    model = _get_model()
    query_emb = model.encode([query]).tolist()
    try:
        results = collection.query(
            query_embeddings=query_emb,
            n_results=min(top_k, count),
        )
    except Exception:
        return []

    output = []
    ids_list = results.get("ids", [[]])[0]
    distances_list = results.get("distances", [[]])[0]
    metadatas_list = results.get("metadatas", [[]])[0]

    for idx, doc_id in enumerate(ids_list):
        dist = distances_list[idx] if idx < len(distances_list) else 1.0
        sim_score = max(0.0, 1.0 - dist)
        meta = metadatas_list[idx] if idx < len(metadatas_list) else {}
        output.append({
            "id": doc_id,
            "title": meta.get("title", ""),
            "year": int(meta.get("year", 0)) if meta.get("year", "").isdigit() else 0,
            "authors": [a.strip() for a in meta.get("authors", "").split(",") if a.strip()],
            "url": meta.get("url", ""),
            "similarity_score": round(sim_score, 4),
        })
    output.sort(key=lambda x: x["similarity_score"], reverse=True)
    return output
