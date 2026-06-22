from unittest.mock import patch

import pytest

from src.graph import app, AgentState


def test_graph_compiles():
    assert app is not None
    nodes = [n for n in app.get_graph().nodes]
    assert "router" in nodes
    assert "parse_node" in nodes
    assert "answer_question_node" in nodes
    assert "find_gaps_in_db_node" in nodes


def test_analyze_mode_returns_expected_keys():
    state: AgentState = {
        "mode": "analyze",
        "paper_path": "examples/ai-driven-healthcare-research-paper.pdf",
        "query": None,
        "parsed_content": {},
        "structure": {},
        "gaps": [],
        "similar_papers": [],
        "citation_results": {},
        "improvements": [],
        "readiness_score": {},
        "journal_matches": [],
        "qa_result": {},
        "discovery_results": [],
    }

    result = app.invoke(state, {"recursion_limit": 30})
    assert "parsed_content" in result
    assert "structure" in result
    assert "gaps" in result
    assert "similar_papers" in result
    assert "citation_results" in result
    assert "improvements" in result
    assert "readiness_score" in result
    assert "journal_matches" in result


def test_qa_mode_routes_correctly():
    state: AgentState = {
        "mode": "qa",
        "paper_path": None,
        "query": "What is deep learning?",
        "parsed_content": {},
        "structure": {},
        "gaps": [],
        "similar_papers": [],
        "citation_results": {},
        "improvements": [],
        "readiness_score": {},
        "journal_matches": [],
        "qa_result": {},
        "discovery_results": [],
    }

    result = app.invoke(state, {"recursion_limit": 30})
    assert "qa_result" in result


def test_discover_mode_routes_correctly():
    state: AgentState = {
        "mode": "discover",
        "paper_path": None,
        "query": "NLP healthcare",
        "parsed_content": {},
        "structure": {},
        "gaps": [],
        "similar_papers": [],
        "citation_results": {},
        "improvements": [],
        "readiness_score": {},
        "journal_matches": [],
        "qa_result": {},
        "discovery_results": [],
    }

    result = app.invoke(state, {"recursion_limit": 30})
    assert "discovery_results" in result
