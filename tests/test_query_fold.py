"""Regression tests for Danish-letter court/subject filters (finding H2).

SQLite's ``LIKE`` folds ASCII only, so ``--court "Østre Landsret"`` returned
rows on the JSON-scan path and zero on the index path. The index now stores
Python-folded shadow columns and queries compare folded values on both sides.
"""

import json
import sqlite3

import pytest

from domdb.core.query import QueryParams, build_index, count_cases
from domdb.core.query.fold import fold_text
from domdb.core.query.index import INDEX_FILENAME


def _case(case_id, author, subjects):
    return {
        "id": case_id,
        "headline": f"Sag {case_id}",
        "author": author,
        "officeName": author,
        "profession": {"displayText": "Straffesag"},
        "instance": {"displayText": "1. instans"},
        "caseType": {"displayText": "Domsmandssag"},
        "caseSubjects": [{"displayText": s} for s in subjects],
        "courtCaseNumber": f"SS-{case_id}/2024",
        "documents": [{"verdictDateTime": "2024-01-01T10:00:00"}],
    }


@pytest.fixture
def cache(tmp_path):
    cases = [
        _case("1", "Østre Landsret", ["Økonomisk kriminalitet"]),
        _case("2", "Østre Landsret", ["Økonomisk kriminalitet"]),
        _case("3", "Retten i København", ["Strafferet"]),
    ]
    (tmp_path / "cases.json").write_text(
        json.dumps(cases, ensure_ascii=False), encoding="utf-8"
    )
    return tmp_path


def test_fold_text_folds_danish_letters():
    assert fold_text("Østre Landsret") == fold_text("østre landsret")
    assert fold_text("ØKONOMISK") == "økonomisk"
    # Decomposed input (a + combining ring) folds to the same value.
    assert fold_text("Århus") == fold_text("Århus")


@pytest.mark.parametrize(
    "court", ["østre", "Østre", "ØSTRE", "Østre Landsret", "østre landsret"]
)
def test_index_court_filter_matches_danish_letters(cache, court):
    scan = count_cases(str(cache), QueryParams(court=court))
    build_index(str(cache))
    indexed = count_cases(str(cache), QueryParams(court=court))
    assert scan == 2
    assert indexed == scan


@pytest.mark.parametrize("subject", ["økonomisk", "Økonomisk kriminalitet", "ØKONOMISK"])
def test_index_subject_filter_matches_danish_letters(cache, subject):
    scan = count_cases(str(cache), QueryParams(subject=subject))
    build_index(str(cache))
    indexed = count_cases(str(cache), QueryParams(subject=subject))
    assert scan == 2
    assert indexed == scan


def test_stale_index_schema_falls_back_to_scan(cache):
    """An index written by an older schema lacks the folded columns."""
    build_index(str(cache))
    conn = sqlite3.connect(str(cache / INDEX_FILENAME))
    try:
        conn.execute("UPDATE meta SET value = '2' WHERE key = 'schema_version'")
        conn.commit()
    finally:
        conn.close()

    # The stale index is ignored, so the (correct) scan path answers.
    assert count_cases(str(cache), QueryParams(court="Østre")) == 2
