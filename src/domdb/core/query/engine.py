import json
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


def _needs_body_search(params: QueryParams, paragraph_spec: ParagraphSpec | None) -> bool:
    return bool((params.full_text and params.keywords) or (paragraph_spec and paragraph_spec.section))


def _haystack_matches(
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


def _metadata_matches(
    metadata: str,
    keywords: list[str],
    paragraph_spec: ParagraphSpec | None,
) -> bool:
    if not text_contains_keywords(metadata, keywords):
        return False
    if paragraph_spec and paragraph_spec.section:
        if not text_matches_paragraph(metadata, paragraph_spec):
            return False
    return True


def _case_matches(
    case: ModelItem,
    params: QueryParams,
    keywords: list[str],
    paragraph_spec: ParagraphSpec | None,
    from_d,
    to_d,
) -> bool:
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

    metadata = metadata_search_text(case)
    if _metadata_matches(metadata, keywords, paragraph_spec):
        return True

    if not _needs_body_search(params, paragraph_spec):
        return False

    html_body = html_body_search_text(case)
    if _haystack_matches(metadata + "\n" + html_body, keywords, paragraph_spec):
        return True
    if not params.full_text:
        return False

    body = extract_case_text(case).lower()
    return _haystack_matches(metadata + "\n" + body, keywords, paragraph_spec)


def _indexed_row_matches(
    row: IndexedCase,
    params: QueryParams,
    keywords: list[str],
    paragraph_spec: ParagraphSpec | None,
) -> bool:
    if _metadata_matches(row.metadata_text, keywords, paragraph_spec):
        return True
    if not _needs_body_search(params, paragraph_spec):
        return False

    haystack = row.metadata_text + "\n" + row.body_text
    if _haystack_matches(haystack, keywords, paragraph_spec):
        return True
    if not params.full_text:
        return False

    case = _load_case_from_file(row.source_file, row.id)
    if case is None:
        return False

    body = extract_case_text(case).lower()
    return _haystack_matches(row.metadata_text + "\n" + body, keywords, paragraph_spec)


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
            if _indexed_row_matches(row, params, keywords, paragraph_spec):
                yield _case_hit_from_index(row)
        return

    logger.info("No query index found; scanning JSON cache (run `domdb query index` for speed)")
    from ..converters.fields import parse_case_fields

    for case, _source in iter_cached_cases(directory):
        if _case_matches(case, params, keywords, paragraph_spec, from_d, to_d):
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