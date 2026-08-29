from typing import Optional

from bs4 import BeautifulSoup

from ..model import ModelItem
from ..converters.fields import parse_case_fields


def normalize_keywords(keywords: Optional[list[str]]) -> list[str]:
    if not keywords:
        return []
    return [k.strip().lower() for k in keywords if k.strip()]


def metadata_search_text(case: ModelItem) -> str:
    """Plain-text haystack from case metadata (headline, court, subjects, etc.)."""
    fields = parse_case_fields(case)
    parts = [
        case.headline or "No Title",
        fields["author"],
        fields["court"],
        fields["verdict_date"],
        fields["subjects"],
        fields["case_number"],
        case.id or "",
    ]
    return "\n".join(parts).lower()


def text_contains_keywords(haystack: str, keywords: list[str]) -> bool:
    if not keywords:
        return True
    lower = haystack.lower()
    return all(k in lower for k in keywords)


def html_body_search_text(case: ModelItem) -> str:
    """Fast plain-text extraction from HTML documents only (no PDF)."""
    chunks: list[str] = []
    for doc in case.documents or []:
        if doc.contentHtml:
            soup = BeautifulSoup(doc.contentHtml, "html.parser")
            chunks.append(soup.get_text(separator="\n", strip=True))
    return "\n".join(chunks).lower()
