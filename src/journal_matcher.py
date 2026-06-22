import os

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CSV_PATH = os.path.join(DATA_DIR, "journal_database.csv")


_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def match_journals(topic: str, readiness_score: int) -> list[dict]:
    if not os.path.exists(CSV_PATH):
        print(f"WARNING: journal_database.csv not found at {CSV_PATH}")
        return []

    df = pd.read_csv(CSV_PATH)
    model = _get_model()
    topic_emb = model.encode([topic])[0]

    scored = []
    for _, row in df.iterrows():
        j_topic = str(row["topic"])
        j_emb = model.encode([j_topic])[0]
        sim = float(np.dot(topic_emb, j_emb) / (np.linalg.norm(topic_emb) * np.linalg.norm(j_emb)))
        if sim < 0.3:
            continue
        fit_score = round(sim * 0.6 + (readiness_score / 100) * 0.4, 4)
        scored.append({
            "name": row["name"],
            "topic": j_topic,
            "acceptance_rate": row["acceptance_rate"],
            "prestige": row["prestige"],
            "url": row["url"],
            "fit_score": fit_score,
        })

    scored.sort(key=lambda x: x["fit_score"], reverse=True)
    return scored[:5]
