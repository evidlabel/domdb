import json
from collections.abc import Callable
from dataclasses import dataclass, field

from loguru import logger

from ..converters.text_utils import extract_case_text
from ..model import ModelItem
from .dates import case_verdict_date, date_in_range, parse_query_date
from .index import IndexedCase, fetch_indexed_cases, index_exists
from .loader import iter_cached_cases
from .paragraph import ParagraphSpec, parse_paragraph_query, text_matches_paragraph
from .search import (
    html_body_search_text,
    metadata_search_text,
    normalize_keywords,
    text_contains_keywords,
)


@dataclass
class QueryParams:
    keywords: list[str] = field(default_factory=list)
    paragraph: str | None = None
    from_date: str | None = None
    to_date: str | None = None
    full_text: bool = False
    court: str | None = None
    subject: str | None = None
    limit: int | None = None


@dataclass(frozen=True)
class CaseHit:
    id: str
    headline: str
    verdict_date: str
    court: str
    case_number: str
    url: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "headline": self.headline,
            "verdict_date": self.verdict_date,
            "court": self.court,
            "case_number": self.case_number,
            "url": self.url,
        }


@dataclass(frozen=True)
class SearchableCase:
    """Searchable text surface shared by cache-scan and index match paths.

    ``body_text`` / ``full_text`` are callables so HTML extraction and PDF load
    stay lazy until keyword/paragraph matching actually needs them.
    """

    metadata_text: str
    body_text: Callable[[], str] = field(repr=False, hash=False, compare=False)
    full_text: Callable[[], str | None] = field(repr=False, hash=False, compare=False)


def _case_hit(case: ModelItem, fields: dict[str, str]) -> CaseHit:
    return CaseHit(
        id=case.id or "",
        headline=case.headline or "",
        verdict_date=fields["verdict_date"],
        court=fields["court"],
        case_number=fields["case_number"],
        url=f"https://domsdatabasen.dk/#sag/{case.id}",
    )


def _case_hit_from_index(row: IndexedCase) -> CaseHit:
    return CaseHit(
        id=row.id,
        headline=row.headline,
        verdict_date=row.verdict_date or "Unknown",
        court=row.court,
        case_number=row.case_number,
        url=f"https://domsdatabasen.dk/#sag/{row.id}",
    )


def _load_case_from_file(path: str, case_id: str) -> ModelItem | None:
    with open(path, encoding="utf-8") as handle:
        cases_data = json.load(handle)
    for case_data in cases_data:
        if case_data.get("id") == case_id:
            return ModelItem.model_validate(case_data)
    return None


def _searchable_from_case(case: ModelItem) -> SearchableCase:
    return SearchableCase(
        metadata_text=metadata_search_text(case),
        body_text=lambda: html_body_search_text(case),
        full_text=lambda: extract_case_text(case).lower(),
    )


def _searchable_from_index(row: IndexedCase) -> SearchableCase:
    def full_text() -> str | None:
        case = _load_case_from_file(row.source_file, row.id)
        if case is None:
            return None
        return extract_case_text(case).lower()

    return SearchableCase(
        metadata_text=row.metadata_text,
        body_text=lambda: row.body_text,
        full_text=full_text,
    )


def _needs_body_search(
    params: QueryParams, paragraph_spec: ParagraphSpec | None
) -> bool:
    return bool(
        (params.full_text and params.keywords)
        or (paragraph_spec and paragraph_spec.section)
    )


def _text_matches(
    haystack: str,
    keywords: list[str],
    paragraph_spec: ParagraphSpec | None,
) -> bool:
    if not text_contains_keywords(haystack, keywords):
        return False
    if paragraph_spec and paragraph_spec.section:
        if not text_matches_paragraph(haystack, paragraph_spec):
            return False
    return True


def _matches(
    case: SearchableCase,
    params: QueryParams,
    keywords: list[str],
    paragraph_spec: ParagraphSpec | None,
) -> bool:
    """Keyword / paragraph / full-text match against a searchable case."""
    if _text_matches(case.metadata_text, keywords, paragraph_spec):
        return True
    if not _needs_body_search(params, paragraph_spec):
        return False

    haystack = case.metadata_text + "\n" + case.body_text()
    if _text_matches(haystack, keywords, paragraph_spec):
        return True
    if not params.full_text:
        return False

    body = case.full_text()
    if body is None:
        return False
    return _text_matches(case.metadata_text + "\n" + body, keywords, paragraph_spec)


def _scan_filters_match(
    case: ModelItem,
    params: QueryParams,
    from_d,
    to_d,
) -> bool:
    """Date / court / subject filters for the full JSON cache scan path.

    The index path applies the same filters in SQL via ``fetch_indexed_cases``.
    """
    from ..converters.fields import parse_case_fields

    if not date_in_range(case_verdict_date(case), from_d, to_d):
        return False

    fields = parse_case_fields(case)
    if params.court:
        court_needle = params.court.lower()
        hay = f"{fields['author']} {fields['court']}".lower()
        if court_needle not in hay:
            return False
    if params.subject:
        if params.subject.lower() not in fields["subjects"].lower():
            return False
    return True


def _iter_hits(directory: str, params: QueryParams):
    keywords = normalize_keywords(params.keywords)
    paragraph_spec = (
        parse_paragraph_query(params.paragraph) if params.paragraph else None
    )
    from_d = parse_query_date(params.from_date)
    to_d = parse_query_date(params.to_date)

    if index_exists(directory):
        rows = fetch_indexed_cases(
            directory,
            from_date=params.from_date,
            to_date=params.to_date,
            court=params.court,
            subject=params.subject,
        )
        for row in rows:
            if _matches(_searchable_from_index(row), params, keywords, paragraph_spec):
                yield _case_hit_from_index(row)
        return

    logger.info(
        "No query index found; scanning JSON cache (run `domdb query index` for speed)"
    )
    from ..converters.fields import parse_case_fields

    for case, _source in iter_cached_cases(directory):
        if not _scan_filters_match(case, params, from_d, to_d):
            continue
        if _matches(_searchable_from_case(case), params, keywords, paragraph_spec):
            yield _case_hit(case, parse_case_fields(case))


def count_cases(directory: str, params: QueryParams) -> int:
    total = 0
    for _hit in _iter_hits(directory, params):
        total += 1
    return total


def list_cases(directory: str, params: QueryParams) -> list[CaseHit]:
    hits: list[CaseHit] = []
    for hit in _iter_hits(directory, params):
        hits.append(hit)
        if params.limit and len(hits) >= params.limit:
            break
    return hits
