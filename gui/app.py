import json
import os
import sys
import tempfile
from pathlib import Path

# Ensure the project root is on sys.path so src/ can be imported
_proj_root = Path(__file__).resolve().parent.parent
if str(_proj_root) not in sys.path:
    sys.path.insert(0, str(_proj_root))

import streamlit as st

from src.graph import app
from src.llm_client import any_key_available
from src.rag_engine import _get_collection


def get_collection_count() -> int:
    try:
        return _get_collection().count()
    except Exception:
        return 0


def pipeline_status_items(result: dict) -> list[dict]:
    checks = [
        ("PDF Parsing", result.get("parsed_content"), bool(result.get("parsed_content", {}).get("title"))),
        ("Structure Analysis", result.get("structure"), bool(result.get("structure", {}).get("word_counts"))),
        ("Gap Detection", result.get("gaps"), len(result.get("gaps", [])) > 0),
        ("Similarity Check", result.get("similar_papers"), len(result.get("similar_papers", [])) > 0),
        ("Citation Verification", result.get("citation_results"), result.get("citation_results", {}).get("total", 0) > 0),
        ("Improvement Suggestions", result.get("improvements"), len(result.get("improvements", [])) > 0),
        ("Readiness Scoring", result.get("readiness_score"), result.get("readiness_score", {}).get("score", 0) > 0),
        ("Journal Matching", result.get("journal_matches"), len(result.get("journal_matches", [])) > 0),
    ]
    return [
        {"label": label, "exists": exists, "ok": ok}
        for label, exists, ok in checks
    ]


def render_pipeline_card(items: list[dict], sub_steps: list[dict] | None = None) -> None:
    lines = []
    for item in items:
        if not item["exists"]:
            icon = "❌"
        elif item["ok"]:
            icon = "✅"
        else:
            icon = "⚠️"
        lines.append(f"{icon} {item['label']}")
    if sub_steps:
        for s in sub_steps:
            s_icon = "✅" if s["ok"] else "⚠️"
            lines.append(f"&emsp;{s_icon} {s['label']}")
    st.markdown(
        "#### Pipeline Status\n" + "\n".join(lines),
    )
    st.divider()


st.set_page_config(page_title="PaperDoctor AI", page_icon="🔬", layout="wide")

st.markdown(
    """
<style>
    .stApp { background-color: #0F1117; color: #E0E0E0; }
    .stApp header { background-color: #0F1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1A1D27; border-radius: 8px 8px 0 0;
        padding: 8px 20px; color: #E0E0E0; font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4F8EF7; color: #fff;
    }
    .stButton > button {
        background-color: #4F8EF7; color: #fff; border: none;
        border-radius: 8px; padding: 8px 24px; font-weight: 600;
    }
    .stButton > button:hover { background-color: #3A7BD5; }
    .stTextInput > div > div {
        background-color: #1A1D27; border: 1px solid #2A2D37;
        border-radius: 8px; color: #E0E0E0;
    }
    .stTextInput > div > div:focus-within { border-color: #4F8EF7; }
    .stTextInput label { color: #A0A0B0; }
    .stDataFrame { background-color: #1A1D27; border-radius: 8px; }
    .stDataFrame th { background-color: #2A2D37; color: #E0E0E0; }
    .stDataFrame td { color: #C0C0D0; }
    .stMetric { background-color: #1A1D27; border-radius: 8px; padding: 12px; }
    .stMetric label { color: #A0A0B0; }
    .stMetric value { color: #E0E0E0; }
    .stProgress > div > div { background-color: #4F8EF7; }
    .stExpander { background-color: #1A1D27; border-radius: 8px; margin: 8px 0; }
    .stExpander summary { color: #E0E0E0; font-weight: 600; }
    .stAlert { border-radius: 8px; }
    .stSidebar { background-color: #1A1D27; }
    .stSidebar .sidebar-content { color: #E0E0E0; }
    h1, h2, h3, h4, h5, h6 { color: #FFFFFF; }
    p { color: #C0C0D0; }
    .st-bb { color: #E0E0E0; }
    .st-at { background-color: #1A1D27; }
    .card {
        background-color: #1A1D27; border-radius: 8px;
        padding: 16px; margin: 8px 0; border: 1px solid #2A2D37;
    }
    .discovery-card {
        background-color: #1A1D27; border-radius: 8px;
        padding: 16px; margin: 8px 0;
        border-left: 3px solid #4F8EF7;
    }
    .badge {
        display: inline-block; padding: 2px 10px; border-radius: 12px;
        font-size: 0.8em; font-weight: 600; margin: 2px;
    }
    .badge-green { background-color: #1B5E20; color: #A5D6A7; }
    .badge-red { background-color: #B71C1C; color: #EF9A9A; }
    .qa-card {
        background-color: #1A1D27; border: 1px solid #4F8EF7;
        border-radius: 8px; padding: 20px; margin: 12px 0;
    }
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #1A1D27; }
    ::-webkit-scrollbar-thumb { background: #3A3D47; border-radius: 4px; }
</style>
""",
    unsafe_allow_html=True,
)

st.sidebar.markdown("## 🔬 PaperDoctor AI")
st.sidebar.markdown(
    "Analyze research papers, find gaps, check similarity, "
    "and score publication readiness."
)
if not any_key_available():
    st.sidebar.warning(
        "No LLM API keys configured — gap discovery and Q&A "
        "will be limited. Set GEMINI_API_KEY or OPENROUTER_API_KEY in .env",
    )
st.sidebar.divider()
st.sidebar.metric("Papers in RAG Cache", get_collection_count())
st.sidebar.divider()
st.sidebar.markdown(
    "[View on GitHub](https://github.com/shahzad67432)"
)

tab_analyze, tab_qa, tab_discover = st.tabs([
    "🔬 Analyze Paper",
    "💬 Q&A over Papers",
    "🔍 Gap Discovery",
])

with tab_analyze:
    uploaded = st.file_uploader(
        "Upload a research paper (PDF)",
        type=["pdf"],
        help="Accepted format: PDF",
    )

    if uploaded:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded.read())
            st.session_state["paper_path"] = tmp.name
        st.success(f"Uploaded: {uploaded.name}")

    if st.button("Analyze Paper", width="stretch"):
        paper_path = st.session_state.get("paper_path")
        if not paper_path:
            st.error("Please upload a PDF first.")
        else:
            with st.spinner("Running full pipeline... this may take 30–60 seconds"):
                try:
                    state = {
                        "mode": "analyze",
                        "paper_path": paper_path,
                        "query": None,
                    }
                    result = app.invoke(state)
                    st.session_state["analyze_result"] = result
                    st.success("Analysis complete!")
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    if "analyze_result" in st.session_state:
        result = st.session_state["analyze_result"]
        parsed = result.get("parsed_content", {})
        structure = result.get("structure", {})
        gaps = result.get("gaps", [])
        similar = result.get("similar_papers", [])
        citations = result.get("citation_results", {})
        improvements = result.get("improvements", [])
        score = result.get("readiness_score", {})
        journals = result.get("journal_matches", [])

        render_pipeline_card(pipeline_status_items(result))

        with st.expander("Paper Structure", expanded=True):
            title = parsed.get("title", structure.get("topic_guess", "Untitled"))
            st.subheader(title)

            wc = structure.get("word_counts", {})
            if wc:
                st.bar_chart(wc, width="stretch")

            sections = structure.get("sections_present", {})
            if sections:
                cols = st.columns(len(sections))
                for col, (sec, present) in zip(cols, sections.items()):
                    label = sec.replace("_", " ").title()
                    badge = (
                        f'<span class="badge badge-green">✅ {label}</span>'
                        if present
                        else f'<span class="badge badge-red">❌ {label}</span>'
                    )
                    col.markdown(badge, unsafe_allow_html=True)

        with st.expander("Research Gaps", expanded=True):
            if gaps:
                st.metric("Gaps Found", len(gaps))
                for g in gaps:
                    sev = g.get("severity", "low")
                    desc = g.get("description", "")
                    suggestion = g.get("suggestion", "")
                    gap_type = g.get("gap_type", "").title()
                    box = st.error if sev == "high" else (
                        st.warning if sev == "medium" else st.info
                    )
                    box(
                        f"**{gap_type}** — {desc}\n\n"
                        f"💡 *Suggestion:* {suggestion}"
                    )
            else:
                st.info("No research gaps identified.")

        with st.expander("Publication Readiness Score", expanded=True):
            score_val = score.get("score", 0)
            mid = st.columns([1, 2, 1])
            mid[1].metric("Readiness Score", f"{score_val}/100")
            st.progress(score_val / 100.0)

            breakdown = score.get("breakdown", {})
            if breakdown:
                cols = st.columns(4)
                for col, (cat, val) in zip(cols, breakdown.items()):
                    col.metric(cat.title(), f"{val}/100")

        with st.expander("Similar Papers", expanded=False):
            if similar:
                df_data = []
                for p in similar[:5]:
                    sim_pct = f"{p.get('similarity_score', 0) * 100:.1f}%"
                    df_data.append({
                        "Title": p.get("title", ""),
                        "Year": p.get("year", ""),
                        "Journal": (p.get("journal") or p.get("source") or ""),
                        "Similarity": sim_pct,
                        "URL": p.get("url", ""),
                    })
                if df_data:
                    st.data_editor(
                        df_data,
                        column_config={
                            "URL": st.column_config.LinkColumn("URL"),
                        },
                        width="stretch",
                        hide_index=True,
                    )
            else:
                st.info("No similar papers found.")

        with st.expander("Citation Verification", expanded=False):
            total = citations.get("total", 0)
            verified = citations.get("verified", 0)
            matched = citations.get("matched", 0)
            unmatched = citations.get("unmatched", 0)
            invalid = citations.get("invalid", [])

            if total:
                cols = st.columns(3)
                cols[0].metric("Verified", verified)
                cols[1].metric("Matched", matched)
                cols[2].metric("Unmatched", unmatched)

                if invalid:
                    for ref in invalid:
                        st.error(f"Invalid citation: {ref[:100]}…")

                st.caption(f"Total references checked: {total}")
            else:
                st.info("No references to verify.")

        with st.expander("Improvement Suggestions", expanded=False):
            if improvements:
                priority_order = {"high": 0, "medium": 1, "low": 2}
                sorted_imps = sorted(
                    improvements,
                    key=lambda x: priority_order.get(x.get("priority", "low"), 3),
                )
                for s in sorted_imps:
                    action = s.get("action", "")
                    effort = s.get("estimated_effort", "")
                    impact = s.get("expected_impact", "")
                    st.markdown(
                        f"**{action}**  \n"
                        f'<span style="color: #888; font-size: 0.85em;">'
                        f"Effort: {effort} — Impact: {impact}</span>",
                        unsafe_allow_html=True,
                    )
                    st.divider()
            else:
                st.info("No improvement suggestions generated.")

        with st.expander("Journal Recommendations", expanded=False):
            if journals:
                jf_data = []
                for j in journals:
                    jf_data.append({
                        "Journal": j.get("name", ""),
                        "Topic": j.get("topic", ""),
                        "Acceptance Rate": j.get("acceptance_rate", ""),
                        "Prestige": j.get("prestige", ""),
                        "Submit": j.get("url", ""),
                    })
                st.data_editor(
                    jf_data,
                    column_config={
                        "Submit": st.column_config.LinkColumn("Submit"),
                    },
                    width="stretch",
                    hide_index=True,
                )
            else:
                st.info("No journal matches found.")

        with st.expander("Export"):
            st.download_button(
                "Download Report (JSON)",
                data=json.dumps(result, indent=2, default=str),
                file_name="paperdoctor_report.json",
                mime="application/json",
                width="stretch",
            )

with tab_qa:
    query = st.text_input(
        "Ask a question about research papers",
        placeholder="e.g. What methods work best for NLP in healthcare?",
    )

    if st.button("Search", width="stretch"):
        if not query.strip():
            st.error("Please enter a question.")
        else:
            with st.spinner("Searching papers and generating answer..."):
                try:
                    state = {
                        "mode": "qa",
                        "query": query,
                        "paper_path": None,
                    }
                    result = app.invoke(state)
                    qa = result.get("qa_result", {})
                    st.session_state["qa_result"] = qa
                    st.session_state["qa_state"] = result
                except Exception as e:
                    st.error(f"Search failed: {e}")

    if "qa_result" in st.session_state:
        qa = st.session_state["qa_result"]
        qa_full = st.session_state.get("qa_state", {})
        qa_steps = qa_full.get("_steps", [])
        render_pipeline_card([
            {
                "label": "Q&A Search",
                "exists": True,
                "ok": bool(qa.get("answer")) and "Unable to generate" not in qa.get("answer", ""),
            },
        ], sub_steps=qa_steps)
        st.markdown(
            f'<div class="qa-card">{qa.get("answer", "")}</div>',
            unsafe_allow_html=True,
        )

        papers = qa.get("papers_used", [])
        if papers:
            st.subheader("Papers Used")
            pu_data = []
            for p in papers:
                pu_data.append({
                    "Title": p.get("title", ""),
                    "Year": p.get("year", ""),
                })
            st.dataframe(pu_data, width="stretch", hide_index=True)

        saved = qa.get("api_calls_saved", 0)
        if saved:
            st.success(f"✅ API calls saved by RAG cache: {saved}")

with tab_discover:
    interest = st.text_input(
        "Your research interest",
        placeholder="e.g. transformer models for low-resource Urdu NLP",
    )

    if st.button("Find Opportunities", width="stretch"):
        if not interest.strip():
            st.error("Please enter a research interest.")
        else:
            with st.spinner("Discovering research gaps..."):
                try:
                    state = {
                        "mode": "discover",
                        "query": interest,
                        "paper_path": None,
                    }
                    result = app.invoke(state)
                    st.session_state["discover_result"] = result.get(
                        "discovery_results", []
                    )
                    st.session_state["discover_state"] = result
                except Exception as e:
                    st.error(f"Discovery failed: {e}")

    if "discover_result" in st.session_state:
        discoveries = st.session_state["discover_result"]
        result = st.session_state.get("discover_state", {})
        steps = result.get("_steps", [])
        has_note = bool(discoveries and discoveries[0].get("_note"))
        render_pipeline_card([
            {
                "label": "Gap Discovery",
                "exists": True,
                "ok": bool(discoveries) and not has_note,
            },
        ], sub_steps=steps)
        if has_note:
            st.warning(discoveries[0]["_note"])
        if discoveries:
            for d in discoveries:
                st.markdown(
                    f'<div class="discovery-card">'
                    f"<h4>{d.get('title', '')} ({d.get('year', '')})</h4>"
                    f'<span class="badge badge-green">{d.get("gap_type", "")}</span>'
                    f"<p>{d.get('gap_description', '')}</p>"
                    f"<p><em>💡 {d.get('why_you_can_fill_it', '')}</em></p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                url = d.get("url", "")
                if url:
                    st.link_button("View Paper", url, width="stretch")
        else:
            st.info("No research gaps discovered.")
