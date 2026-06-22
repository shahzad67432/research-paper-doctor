# PaperDoctor AI

A research paper analysis platform with PDF parsing, structure analysis, gap detection,
similarity checking, citation verification, improvement suggestions, publication readiness
scoring, journal matching, RAG-based Q&A, and research gap discovery.

## Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy .env.example to .env and add your Google Gemini API key
cp .env.example .env
```

## Running the GUI

```bash
streamlit run gui/app.py
```

Opens in your browser at `http://localhost:8501` with three tabs:
- **🔬 Analyze Paper** — upload a PDF and run the full analysis pipeline
- **💬 Q&A over Papers** — ask questions using RAG over the paper database
- **🔍 Gap Discovery** — find research gaps relevant to your interests

## Running Tests

```bash
pytest -v

# Skip integration tests (live API calls):
pytest -v -m "not integration"
```

## Project Structure

```
paperdoctor-ai/
├── gui/
│   └── app.py              # Streamlit GUI
├── src/
│   ├── parser.py           # parse_paper_pdf(pdf_path) -> dict
│   ├── analyzer.py         # analyze_paper_structure(parsed) -> dict
│   ├── gap_finder.py       # find_research_gaps(structure) -> list
│   ├── similarity_checker.py # check_similar_papers(title, abstract) -> list
│   ├── citation_verifier.py # verify_citations(references) -> dict
│   ├── improvement_suggester.py # generate_improvements(...) -> list
│   ├── readiness_scorer.py # calculate_readiness_score(...) -> dict
│   ├── journal_matcher.py  # match_journals(topic, score) -> list
│   ├── qa_interface.py     # answer_question(query) -> dict
│   ├── discovery_engine.py # find_papers_with_gaps(interest) -> list
│   ├── rag_engine.py       # RAG cache layer (ChromaDB + sentence-transformers)
│   ├── llm_client.py       # Gemini API client
│   ├── database_search.py  # arXiv, PubMed, OpenAlex search
│   ├── cache_manager.py    # API response cache
│   └── graph.py            # LangGraph workflow definition
├── tests/
│   ├── test_parser.py
│   ├── test_graph.py
│   ├── test_rag_engine.py
│   ├── test_readiness_scorer.py
│   ├── test_cache_manager.py
│   ├── test_citation_verifier.py
│   └── test_journal_matcher.py
├── data/
│   └── journal_database.csv
├── examples/
├── requirements.txt
└── .env.example
```
