import os
import re
import time
import urllib.parse

import requests
from dotenv import load_dotenv

load_dotenv()

CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "unknown@example.com")
USER_AGENT = f"PaperDoctorAI/1.0 (mailto:{CONTACT_EMAIL})"
CROSSREF_WORKS_URL = "https://api.crossref.org/works"
HEADERS = {"User-Agent": USER_AGENT}

DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)


def _extract_doi(ref: str) -> str | None:
    m = DOI_RE.search(ref)
    return m.group(0) if m else None


def _verify_doi(doi: str) -> bool:
    try:
        resp = requests.get(
            f"{CROSSREF_WORKS_URL}/{urllib.parse.quote(doi, safe='')}",
            headers=HEADERS,
            timeout=10,
        )
        return resp.status_code == 200
    except requests.RequestException:
        return False


def _bibliographic_match(ref: str) -> str | None:
    try:
        params = {
            "query.bibliographic": ref[:300],
            "rows": 1,
        }
        resp = requests.get(
            CROSSREF_WORKS_URL,
            params=params,
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        items = data.get("message", {}).get("items", [])
        if not items:
            return None
        title = items[0].get("title", [None])[0]
        if not title:
            return None
        similarity = _string_similarity(ref.lower(), title.lower())
        if similarity >= 0.6:
            return title
        return None
    except Exception:
        return None


def _string_similarity(a: str, b: str) -> float:
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()


def verify_citations(references: list[str]) -> dict:
    total = len(references)
    verified = 0
    matched = 0
    unmatched = 0
    invalid = []
    details = []

    for i, ref in enumerate(references):
        doi = _extract_doi(ref)
        if doi:
            if _verify_doi(doi):
                status = "verified"
                verified += 1
            else:
                status = "invalid"
                invalid.append(ref)
            details.append({
                "index": i,
                "reference": ref,
                "status": status,
                "doi": doi,
                "matched_title": None,
            })
        else:
            matched_title = _bibliographic_match(ref)
            if matched_title:
                status = "matched"
                matched += 1
            else:
                status = "unmatched"
                unmatched += 1
            details.append({
                "index": i,
                "reference": ref,
                "status": status,
                "doi": None,
                "matched_title": matched_title,
            })

        if i < len(references) - 1:
            time.sleep(1)

    return {
        "total": total,
        "verified": verified,
        "matched": matched,
        "unmatched": unmatched,
        "invalid": invalid,
        "details": details,
    }
