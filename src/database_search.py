import os
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import requests

load_dotenv()

ARXIV_URL = "http://export.arxiv.org/api/query"
PUBMED_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
OPENALEX_URL = "https://api.openalex.org/works"

ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}
PUBMED_NS = {"": "http://www.ncbi.nlm.nih.gov/entrez/eutils"}


def _extract_arxiv_year(published: str) -> int:
    try:
        return int(published[:4])
    except (ValueError, TypeError):
        return 0


def search_arxiv(query: str, max_results: int = 10) -> list[dict]:
    try:
        params = {
            "search_query": f"all:{query}",
            "max_results": max_results,
        }
        resp = requests.get(ARXIV_URL, params=params, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        papers = []
        for entry in root.findall("atom:entry", ARXIV_NS):
            id_el = entry.find("atom:id", ARXIV_NS)
            title_el = entry.find("atom:title", ARXIV_NS)
            summary_el = entry.find("atom:summary", ARXIV_NS)
            published_el = entry.find("atom:published", ARXIV_NS)
            url = id_el.text.strip() if id_el is not None else ""
            title = " ".join(title_el.text.split()) if title_el is not None else ""
            abstract = " ".join(summary_el.text.split()) if summary_el is not None else ""
            year = _extract_arxiv_year(published_el.text) if published_el is not None else 0
            authors = []
            for author in entry.findall("atom:author", ARXIV_NS):
                name_el = author.find("atom:name", ARXIV_NS)
                if name_el is not None:
                    authors.append(name_el.text.strip())
            papers.append({
                "id": url,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "year": year,
                "url": url,
            })
        return papers
    except Exception:
        return []


def search_pubmed(query: str, max_results: int = 10) -> list[dict]:
    ncbi_key = os.getenv("NCBI_API_KEY", "")
    try:
        esearch_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
        }
        if ncbi_key:
            esearch_params["api_key"] = ncbi_key
        resp = requests.get(PUBMED_ESEARCH_URL, params=esearch_params, timeout=10)
        resp.raise_for_status()
        esearch_data = resp.json()
        id_list = esearch_data.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return []

        efetch_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "xml",
        }
        if ncbi_key:
            efetch_params["api_key"] = ncbi_key
        resp2 = requests.get(PUBMED_EFETCH_URL, params=efetch_params, timeout=10)
        resp2.raise_for_status()
        root = ET.fromstring(resp2.content)
        papers = []
        for article in root.findall(".//PubmedArticle"):
            medline = article.find("MedlineCitation")
            if medline is None:
                continue
            art = medline.find("Article")
            if art is None:
                continue
            pmid_el = medline.find("PMID")
            pmid = pmid_el.text.strip() if pmid_el is not None else ""
            title_el = art.find("ArticleTitle")
            title = " ".join(title_el.itertext()) if title_el is not None else ""
            abstract_parts = []
            for abs_text in art.findall(".//AbstractText"):
                label = abs_text.get("Label", "")
                text = " ".join(abs_text.itertext())
                if label:
                    abstract_parts.append(f"{label}: {text}")
                else:
                    abstract_parts.append(text)
            abstract = " ".join(abstract_parts)
            authors = []
            for author in art.findall(".//Author"):
                last = author.find("LastName")
                fore = author.find("ForeName")
                if last is not None:
                    name = last.text.strip()
                    if fore is not None:
                        name = f"{fore.text.strip()} {name}"
                    authors.append(name)
            year = 0
            for year_el in art.findall(".//Journal/JournalIssue/PubDate/Year"):
                try:
                    year = int(year_el.text.strip())
                except (ValueError, AttributeError):
                    pass
            if year == 0:
                for year_el in art.findall(".//ArticleDate/Year"):
                    try:
                        year = int(year_el.text.strip())
                    except (ValueError, AttributeError):
                        pass
            papers.append({
                "id": f"pubmed:{pmid}" if pmid else "",
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "year": year,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
            })
        return papers
    except Exception:
        return []


def _reconstruct_openalex_abstract(inverted_index: dict) -> str:
    if not inverted_index:
        return ""
    word_positions = {}
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions[pos] = word
    if not word_positions:
        return ""
    max_pos = max(word_positions.keys())
    result = []
    for i in range(max_pos + 1):
        word = word_positions.get(i)
        if word:
            result.append(word)
        else:
            result.append("")
    return " ".join(result).strip()


def search_openalex(query: str, max_results: int = 10) -> list[dict]:
    email = os.getenv("CONTACT_EMAIL", "")
    try:
        params = {
            "search": query,
            "per-page": max_results,
        }
        if email:
            params["mailto"] = email
        resp = requests.get(OPENALEX_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        papers = []
        for work in data.get("results", []):
            inverted = work.get("abstract_inverted_index")
            abstract = _reconstruct_openalex_abstract(inverted) if inverted else ""
            authors = [
                auth.get("author", {}).get("display_name", "")
                for auth in work.get("authorships", [])
                if auth.get("author", {}).get("display_name")
            ]
            papers.append({
                "id": work.get("id", ""),
                "title": work.get("title", ""),
                "abstract": abstract,
                "authors": authors,
                "year": work.get("publication_year", 0),
                "url": work.get("doi", work.get("id", "")),
            })
        return papers
    except Exception:
        return []
