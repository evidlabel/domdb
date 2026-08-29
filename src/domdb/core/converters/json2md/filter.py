from ...model import ModelItem
from ...query.search import (
    metadata_search_text,
    normalize_keywords,
    text_contains_keywords,
)

__all__ = ["case_matches_keywords", "normalize_keywords", "metadata_search_text"]
from ..text_utils import extract_case_text


def case_matches_keywords(
    case: ModelItem,
    keywords: list[str],
    *,
    full_text: bool = False,
) -> bool:
    """Return True if all normalized keywords match metadata and/or body text."""
    if not keywords:
        return True
    metadata = metadata_search_text(case)
    if text_contains_keywords(metadata, keywords):
        return True
    if not full_text:
        return False
    body = extract_case_text(case).lower()
    return text_contains_keywords(metadata + "\n" + body, keywords)
