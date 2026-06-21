import re

SECTION_KEYS = [
    "abstract",
    "introduction",
    "methods",
    "results",
    "conclusion",
]


def _word_count(text: str) -> int:
    return len(text.split()) if text.strip() else 0


def _first_two_sentences(text: str) -> str:
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", text.strip(), maxsplit=2)
    return " ".join(parts[:2]).strip()


def analyze_paper_structure(parsed: dict) -> dict:
    word_counts = {}
    sections_present = {}

    for key in SECTION_KEYS:
        text = parsed.get(key, "")
        wc = _word_count(text)
        word_counts[key] = wc
        sections_present[key] = wc > 0

    word_counts["references"] = len(parsed.get("references", []))
    sections_present["references"] = word_counts["references"] > 0

    title = parsed.get("title", "")
    abstract = parsed.get("abstract", "")
    topic_guess = f"{title} {_first_two_sentences(abstract)}".strip()

    return {
        "word_counts": word_counts,
        "sections_present": sections_present,
        "topic_guess": topic_guess,
    }
