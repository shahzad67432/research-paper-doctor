# PaperDoctor AI

A research paper analyzer that parses academic PDFs, extracts structure (title, abstract, sections, references), and scores publication readiness.

**Phase 1** — PDF parsing foundation. No LLM calls, no RAG, no GUI yet.

## Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Drop PDFs to analyze into examples/
#    (Already there by default)
```

## Usage

```python
from src.parser import parse_paper_pdf
from src.analyzer import analyze_paper_structure

parsed = parse_paper_pdf("examples/sample-paper.pdf")
analysis = analyze_paper_structure(parsed)

print(analysis["topic_guess"])
print(analysis["sections_present"])
print(analysis["word_counts"])
```

## Running Tests

```bash
# Activate venv first, then:
pytest -v

# Tests skip gracefully if examples/ is empty.
# Place at least one .pdf in examples/ to run them.
```

## Project Structure

```
paperdoctor-ai/
├── src/
│   ├── __init__.py
│   ├── parser.py          # parse_paper_pdf(pdf_path) -> dict
│   └── analyzer.py        # analyze_paper_structure(parsed) -> dict
├── tests/
│   ├── __init__.py
│   └── test_parser.py     # pytest suite (skips if no PDFs present)
├── examples/              # Drop your PDFs here
├── requirements.txt
└── .env.example
```

## Output Format

`parse_paper_pdf` returns a dict with keys: `title`, `abstract`, `introduction`, `methods`, `results`, `conclusion`, `references` (list of strings), `full_text`.

Missing sections return an empty string rather than crashing.

`analyze_paper_structure` adds: `word_counts` (per section), `sections_present` (bool per section), `topic_guess` (title + first 2 abstract sentences).
