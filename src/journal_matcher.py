import os

from difflib import SequenceMatcher

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CSV_PATH = os.path.join(DATA_DIR, "journal_database.csv")


def match_journals(topic: str, readiness_score: int) -> list[dict]:
    if not os.path.exists(CSV_PATH):
        print(f"WARNING: journal_database.csv not found at {CSV_PATH}")
        return []

    df = pd.read_csv(CSV_PATH)
    scored = []

    for _, row in df.iterrows():
        sim = SequenceMatcher(
            None, topic.lower(), str(row["topic"]).lower()
        ).ratio()
        if sim < 0.3:
            continue
        fit_score = round(sim * 0.6 + (readiness_score / 100) * 0.4, 4)
        scored.append({
            "name": row["name"],
            "topic": row["topic"],
            "acceptance_rate": row["acceptance_rate"],
            "prestige": row["prestige"],
            "url": row["url"],
            "fit_score": fit_score,
        })

    scored.sort(key=lambda x: x["fit_score"], reverse=True)
    return scored[:5]
