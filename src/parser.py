import re

import fitz


SECTION_PATTERNS = {
    "abstract": re.compile(r"^\s*(?:abstract)\b", re.IGNORECASE),
    "introduction": re.compile(
        r"^\s*(?:[A-Z\d]+\.\s*)?introduction\b", re.IGNORECASE
    ),
    "methods": re.compile(
        r"^\s*(?:[A-Z\d]+\.\s+)(?:methods?|methodology|system\s*model)\b",
        re.IGNORECASE,
    ),
    "results": re.compile(
        r"^\s*(?:[A-Z\d]+\.\s+)(?:results?|experimental?\s+evaluation)\b",
        re.IGNORECASE,
    ),
    "discussion": re.compile(
        r"^\s*(?:[A-Z\d]+\.\s+)(?:discussion|conclusion)\b", re.IGNORECASE
    ),
    "references": re.compile(r"^\s*(?:references|bibliography)\b", re.IGNORECASE),
}


def _extract_title_from_blocks(page) -> str:
    d = page.get_text("dict")
    candidates = []
    for block in d["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                if text:
                    candidates.append((span["size"], text))
    if not candidates:
        return ""
    max_size = max(c[0] for c in candidates)
    title_parts = [c[1] for c in candidates if c[0] == max_size]
    return " ".join(title_parts) if title_parts else ""


def _extract_title_fallback(full_text: str) -> str:
    lines = [l.strip() for l in full_text.split("\n") if l.strip()]
    return lines[0] if lines else ""


def _extract_text_pymupdf_columns(page) -> str:
    page_width = page.rect.width
    col_mid = page_width / 2
    left = []
    right = []
    for b in page.get_text("blocks"):
        if b[6] != 0:
            continue
        x0, y0, x1, y1, text = b[0], b[1], b[2], b[3], b[4]
        text = text.strip()
        if not text:
            continue
        if x0 < col_mid:
            left.append((y0, text, x0))
        else:
            right.append((y0, text, x0))
    left.sort(key=lambda e: (e[0], e[2]))
    right.sort(key=lambda e: (e[0], e[2]))
    result = [t for _, t, _ in left] + [t for _, t, _ in right]
    return "\n".join(result)


def _extract_texts(pdf_path: str) -> tuple[str, list[str]]:
    doc = fitz.open(pdf_path)
    page_texts = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = _extract_text_pymupdf_columns(page)
        page_texts.append(text)
    doc.close()
    return "\n".join(page_texts), page_texts


def _find_section_boundaries(text: str) -> list[tuple[str, int]]:
    lines = text.split("\n")
    sections = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        for key, pattern in SECTION_PATTERNS.items():
            if pattern.search(stripped):
                sections.append((key, i, stripped))
                break
    sections.sort(key=lambda x: x[1])
    merged = []
    seen = set()
    for key, line_num, header_text in sections:
        if key in seen:
            continue
        seen.add(key)
        merged.append((key, line_num, header_text))
    return merged


def _extract_abstract_without_header(page1_text: str, intro_line_num: int) -> str:
    lines = page1_text.split("\n")
    if intro_line_num < 0 or intro_line_num >= len(lines):
        return ""

    author_indicators = [
        "@", "department", "university", "ieee", " member",
        "professor", "lecturer", "faculty", "laboratory", "lab",
        "institute", "school of", "college of", "assistant",
        "principal lecturer",
    ]

    pre_intro = []
    for i in range(intro_line_num):
        line = lines[i].strip()
        if not line:
            continue
        if line.lower().startswith("keywords") or line.lower().startswith(
            "index terms"
        ):
            break
        pre_intro.append(line)

    last_author_idx = -1
    for i, line in enumerate(pre_intro):
        line_lower = line.lower()
        if any(indicator in line_lower for indicator in author_indicators):
            last_author_idx = i

    abstract_lines = pre_intro[last_author_idx + 1 :]
    return " ".join(abstract_lines) if abstract_lines else ""


def _extract_section_text(text: str, boundaries: list[tuple[str, int]], section_key: str) -> str:
    lines = text.split("\n")
    start = None
    end = None
    for i, (key, line_num, _) in enumerate(boundaries):
        if key == section_key:
            start = line_num
            end = boundaries[i + 1][1] if i + 1 < len(boundaries) else len(lines)
            break
    if start is None:
        return ""
    section_lines = []
    for i in range(start + 1, end):
        l = lines[i].strip()
        if l:
            section_lines.append(l)
    return "\n".join(section_lines)


def _split_references(ref_text: str) -> list[str]:
    if not ref_text:
        return []
    refs = re.split(r"\n\s*(?=\[\d+\]|\d+\.\s+[A-Z])", ref_text)
    refs = [r.strip() for r in refs if r.strip()]
    if not refs:
        refs = [ref_text.strip()]
    return refs


def parse_paper_pdf(pdf_path: str) -> dict:
    result = {
        "title": "",
        "abstract": "",
        "introduction": "",
        "methods": "",
        "results": "",
        "conclusion": "",
        "references": [],
        "full_text": "",
    }

    doc = fitz.open(pdf_path)
    title = _extract_title_from_blocks(doc[0])
    if not title:
        title = _extract_title_fallback(doc[0].get_text())
    result["title"] = title
    doc.close()

    full_text, page_texts = _extract_texts(pdf_path)
    page1_text = page_texts[0] if page_texts else full_text

    boundaries = _find_section_boundaries(full_text)

    has_abstract_header = any(key == "abstract" for key, _, _ in boundaries)
    if has_abstract_header:
        result["abstract"] = _extract_section_text(full_text, boundaries, "abstract")
    else:
        page1_lines = page1_text.split("\n")
        intro_line_page1 = -1
        for i, line in enumerate(page1_lines):
            if SECTION_PATTERNS["introduction"].search(line.strip()):
                intro_line_page1 = i
                break
        result["abstract"] = _extract_abstract_without_header(
            page1_text, intro_line_page1
        )

    result["introduction"] = _extract_section_text(full_text, boundaries, "introduction")
    result["methods"] = _extract_section_text(full_text, boundaries, "methods")
    result["results"] = _extract_section_text(full_text, boundaries, "results")
    result["conclusion"] = _extract_section_text(full_text, boundaries, "discussion")

    ref_text = _extract_section_text(full_text, boundaries, "references")
    result["references"] = _split_references(ref_text)
    result["full_text"] = full_text

    return result
