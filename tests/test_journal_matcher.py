import os
import tempfile

import pytest

from src.journal_matcher import match_journals


@pytest.fixture
def fake_csv():
    content = (
        "name,topic,acceptance_rate,prestige,url\n"
        "Journal A,NLP machine learning,30,high,https://a.com\n"
        "Journal B,healthcare AI,40,medium,https://b.com\n"
        "Journal C,quantum computing,25,top,https://c.com\n"
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(content)
        path = f.name
    yield path
    os.unlink(path)


def test_match_journals_top_result(monkeypatch, fake_csv):
    import src.journal_matcher as jm
    monkeypatch.setattr(jm, "CSV_PATH", fake_csv)
    results = match_journals("NLP deep learning", 80)
    assert len(results) <= 5
    assert len(results) > 0
    scores = [r["fit_score"] for r in results]
    assert scores == sorted(scores, reverse=True)
    assert results[0]["fit_score"] >= results[-1]["fit_score"]


def test_match_journals_returns_empty_for_missing_file(monkeypatch):
    import src.journal_matcher as jm
    monkeypatch.setattr(jm, "CSV_PATH", "/nonexistent/path.csv")
    results = match_journals("NLP", 50)
    assert results == []


def test_match_journals_orders_by_fit_score(monkeypatch, fake_csv):
    import src.journal_matcher as jm
    monkeypatch.setattr(jm, "CSV_PATH", fake_csv)
    results = match_journals("NLP machine learning", 100)
    assert len(results) >= 1
    assert results[0]["name"] == "Journal A"
    assert results[0]["fit_score"] > 0.3
