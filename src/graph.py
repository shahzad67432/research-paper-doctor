import sys
from typing import TypedDict

from langgraph.graph import END, StateGraph

from src.analyzer import analyze_paper_structure
from src.citation_verifier import verify_citations
from src.discovery_engine import find_papers_with_gaps
from src.gap_finder import find_research_gaps
from src.improvement_suggester import generate_improvements
from src.journal_matcher import match_journals
from src.parser import parse_paper_pdf
from src.qa_interface import answer_question
from src.readiness_scorer import calculate_readiness_score
from src.similarity_checker import check_similar_papers


class AgentState(TypedDict):
    mode: str
    paper_path: str | None
    query: str | None
    parsed_content: dict
    structure: dict
    gaps: list
    similar_papers: list
    citation_results: dict
    improvements: list
    readiness_score: dict
    journal_matches: list
    qa_result: dict
    discovery_results: list
    _steps: list


def router_node(state: AgentState) -> dict:
    state.setdefault("_steps", [])
    return state


def parse_node(state: AgentState) -> dict:
    try:
        path = state.get("paper_path")
        if not path:
            return {"parsed_content": {}}
        result = parse_paper_pdf(path)
        return {"parsed_content": result}
    except Exception as e:
        print(f"parse_node error: {e}", file=sys.stderr)
        return {"parsed_content": {}}


def analyze_node(state: AgentState) -> dict:
    try:
        parsed = state.get("parsed_content", {})
        if not parsed:
            return {"structure": {}}
        result = analyze_paper_structure(parsed)
        return {"structure": result}
    except Exception as e:
        print(f"analyze_node error: {e}", file=sys.stderr)
        return {"structure": {}}


def find_gaps_node(state: AgentState) -> dict:
    try:
        parsed = state.get("parsed_content", {})
        gaps = find_research_gaps(parsed)
        return {"gaps": gaps}
    except Exception as e:
        print(f"find_gaps_node error: {e}", file=sys.stderr)
        return {"gaps": []}


def check_similarity_node(state: AgentState) -> dict:
    try:
        parsed = state.get("parsed_content", {})
        title = parsed.get("title", "")
        abstract = parsed.get("abstract", "")
        if not title and not abstract:
            return {"similar_papers": []}
        results = check_similar_papers(title, abstract)
        return {"similar_papers": results}
    except Exception as e:
        print(f"check_similarity_node error: {e}", file=sys.stderr)
        return {"similar_papers": []}


def verify_citations_node(state: AgentState) -> dict:
    try:
        parsed = state.get("parsed_content", {})
        refs = parsed.get("references", [])
        results = verify_citations(refs)
        return {"citation_results": results}
    except Exception as e:
        print(f"verify_citations_node error: {e}", file=sys.stderr)
        return {"citation_results": {"total": 0, "verified": 0, "matched": 0, "unmatched": 0, "invalid": [], "details": []}}


def suggest_improvements_node(state: AgentState) -> dict:
    try:
        parsed = state.get("parsed_content", {})
        gaps = state.get("gaps", [])
        similar = state.get("similar_papers", [])
        citations = state.get("citation_results", {})
        results = generate_improvements(parsed, gaps, similar, citations)
        return {"improvements": results}
    except Exception as e:
        print(f"suggest_improvements_node error: {e}", file=sys.stderr)
        return {"improvements": []}


def calculate_score_node(state: AgentState) -> dict:
    try:
        parsed = state.get("parsed_content", {})
        gaps = state.get("gaps", [])
        citations = state.get("citation_results", {})
        score = calculate_readiness_score(parsed, gaps, citations)
        return {"readiness_score": score}
    except Exception as e:
        print(f"calculate_score_node error: {e}", file=sys.stderr)
        return {"readiness_score": {"score": 0, "breakdown": {}}}


def match_journals_node(state: AgentState) -> dict:
    try:
        structure = state.get("structure", {})
        topic = structure.get("topic_guess", "")
        score_dict = state.get("readiness_score", {})
        score = score_dict.get("score", 0)
        matches = match_journals(topic, score)
        return {"journal_matches": matches}
    except Exception as e:
        print(f"match_journals_node error: {e}", file=sys.stderr)
        return {"journal_matches": []}


def answer_question_node(state: AgentState) -> dict:
    try:
        query = state.get("query", "")
        if not query:
            return {"qa_result": {"answer": "No query provided.", "papers_used": [], "api_calls_saved": 0}}
        steps: list[dict] = []
        def _steps(label, ok):
            steps.append({"label": label, "ok": ok})
        result = answer_question(query, step_callback=_steps)
        return {"qa_result": result, "_steps": steps}
    except Exception as e:
        print(f"answer_question_node error: {e}", file=sys.stderr)
        return {"qa_result": {"answer": "Error processing query.", "papers_used": [], "api_calls_saved": 0}, "_steps": []}


def find_gaps_in_db_node(state: AgentState) -> dict:
    try:
        query = state.get("query", "")
        if not query:
            return {"discovery_results": []}
        steps: list[dict] = []
        def _steps(label, ok):
            steps.append({"label": label, "ok": ok})
        results = find_papers_with_gaps(query, step_callback=_steps)
        return {"discovery_results": results, "_steps": steps}
    except Exception as e:
        print(f"find_gaps_in_db_node error: {e}", file=sys.stderr)
        return {"discovery_results": [], "_steps": []}


def route_fn(state: AgentState) -> str:
    return state.get("mode", "analyze")


builder = StateGraph(AgentState)

builder.add_node("router", router_node)
builder.add_node("parse_node", parse_node)
builder.add_node("analyze_node", analyze_node)
builder.add_node("find_gaps_node", find_gaps_node)
builder.add_node("check_similarity_node", check_similarity_node)
builder.add_node("verify_citations_node", verify_citations_node)
builder.add_node("suggest_improvements_node", suggest_improvements_node)
builder.add_node("calculate_score_node", calculate_score_node)
builder.add_node("match_journals_node", match_journals_node)
builder.add_node("answer_question_node", answer_question_node)
builder.add_node("find_gaps_in_db_node", find_gaps_in_db_node)

builder.set_entry_point("router")

builder.add_conditional_edges(
    "router",
    route_fn,
    {
        "analyze": "parse_node",
        "qa": "answer_question_node",
        "discover": "find_gaps_in_db_node",
    },
)

builder.add_edge("parse_node", "analyze_node")
builder.add_edge("analyze_node", "find_gaps_node")
builder.add_edge("find_gaps_node", "check_similarity_node")
builder.add_edge("check_similarity_node", "verify_citations_node")
builder.add_edge("verify_citations_node", "suggest_improvements_node")
builder.add_edge("suggest_improvements_node", "calculate_score_node")
builder.add_edge("calculate_score_node", "match_journals_node")
builder.add_edge("match_journals_node", END)
builder.add_edge("answer_question_node", END)
builder.add_edge("find_gaps_in_db_node", END)

app = builder.compile()
