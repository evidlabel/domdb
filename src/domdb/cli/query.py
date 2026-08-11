import json
import os
from typing import List, Optional

from loguru import logger

from domdb.core.query import QueryParams, build_index, count_cases, list_cases


def _params(
    keywords: List[str],
    paragraph: Optional[str],
    from_date: Optional[str],
    to_date: Optional[str],
    full_text: bool,
    court: Optional[str],
    subject: Optional[str],
    limit: Optional[int] = None,
) -> QueryParams:
    return QueryParams(
        keywords=keywords or [],
        paragraph=paragraph or None,
        from_date=from_date or None,
        to_date=to_date or None,
        full_text=full_text,
        court=court or None,
        subject=subject or None,
        limit=limit,
    )


def query_index(
    directory: str,
    keywords: List[str],
    paragraph: Optional[str],
    from_date: Optional[str],
    to_date: Optional[str],
    full_text: bool,
    court: Optional[str],
    subject: Optional[str],
):
    """Build the metadata query index for a cache directory."""
    directory = os.path.expanduser(directory)
    count = build_index(directory)
    print(f"Indexed {count} cases in {directory}")


def query_count(
    directory: str,
    keywords: List[str],
    paragraph: Optional[str],
    from_date: Optional[str],
    to_date: Optional[str],
    full_text: bool,
    court: Optional[str],
    subject: Optional[str],
):
    """Count verdicts matching the query."""
    directory = os.path.expanduser(directory)
    params = _params(keywords, paragraph, from_date, to_date, full_text, court, subject)
    logger.info(f"Query count: {params}")
    total = count_cases(directory, params)
    print(total)


def query_list(
    directory: str,
    keywords: List[str],
    paragraph: Optional[str],
    from_date: Optional[str],
    to_date: Optional[str],
    full_text: bool,
    court: Optional[str],
    subject: Optional[str],
    number: int,
    format: str,
):
    """List verdicts matching the query."""
    directory = os.path.expanduser(directory)
    params = _params(
        keywords,
        paragraph,
        from_date,
        to_date,
        full_text,
        court,
        subject,
        limit=None if number == -1 else number,
    )
    logger.info(f"Query list: {params}")
    hits = list_cases(directory, params)

    if format == "json":
        print(json.dumps([hit.as_dict() for hit in hits], ensure_ascii=False, indent=2))
        return

    for hit in hits:
        date = hit.verdict_date if hit.verdict_date != "Unknown" else "????-??-??"
        print(f"{date}  {hit.case_number:20}  {hit.headline[:72]}")
        print(f"          {hit.court}")
        print(f"          {hit.url}")
        print()
