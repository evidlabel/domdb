"""Regression tests for citation-key derivation (finding H3).

Keys used to be derived from ``courtCaseNumber`` alone, so ``B-1234/2024`` and
``B 1234-2024`` both became ``b12342024`` and the de-duplicator dropped one of
two distinct judgments.
"""

import json

from domdb.core.converters.fields import (
    entry_id_for,
    slugify_identifier,
    unique_entry_id,
)
from domdb.core.converters.json2bib.convert import convert_json_to_bib
from domdb.core.model import ModelItem


def _case(case_id, case_number, date="2024-05-14T09:30:00"):
    return {
        "id": case_id,
        "headline": f"Sag {case_id}",
        "author": "Retten i Aarhus",
        "courtCaseNumber": case_number,
        "documents": [{"verdictDateTime": date}],
    }


def test_entry_id_prefers_source_id():
    case = ModelItem.model_validate(_case("abc-1", "B-1234/2024"))
    assert entry_id_for(case) == "abc1"


def test_entry_id_falls_back_to_case_number():
    case = ModelItem.model_validate(_case(None, "B-1234/2024"))
    assert case.id is None
    assert entry_id_for(case) == "b12342024"


def test_entry_id_falls_back_to_unknown():
    case = ModelItem.model_validate(_case(None, None))
    assert entry_id_for(case) == "unknown"


def test_unique_entry_id_disambiguates_collisions():
    used: set[str] = set()
    assert unique_entry_id("b12342024", used) == "b12342024"
    assert unique_entry_id("b12342024", used) == "b12342024-2"
    assert unique_entry_id("b12342024", used) == "b12342024-3"
    assert used == {"b12342024", "b12342024-2", "b12342024-3"}


def test_slugify_is_unchanged_for_existing_keys():
    assert slugify_identifier("123/2023") == "1232023"


def test_colliding_case_numbers_keep_both_judgments(tmp_path):
    """Two distinct verdicts whose case numbers normalise alike both survive."""
    cases = [
        _case("abc-1", "B-1234/2024", "2024-05-14T09:30:00"),
        _case("abc-2", "B 1234-2024", "2024-06-01T09:30:00"),
    ]
    (tmp_path / "cases_1.json").write_text(
        json.dumps(cases, ensure_ascii=False), encoding="utf-8"
    )

    count = convert_json_to_bib(str(tmp_path), str(tmp_path / "out.bib"))

    assert count == 2
    text = (tmp_path / "out.bib").read_text(encoding="utf-8")
    assert "@article{abc1," in text
    assert "@article{abc2," in text


def test_missing_case_numbers_do_not_collapse(tmp_path):
    """Records without a case number still get distinct, stable keys."""
    cases = [
        _case("id-one", None, "2024-01-01T10:00:00"),
        _case("id-two", None, "2024-02-01T10:00:00"),
    ]
    (tmp_path / "cases_1.json").write_text(json.dumps(cases), encoding="utf-8")

    count = convert_json_to_bib(str(tmp_path), str(tmp_path / "out.bib"))

    assert count == 2
    text = (tmp_path / "out.bib").read_text(encoding="utf-8")
    assert "@article{idone," in text
    assert "@article{idtwo," in text


def test_genuine_duplicate_record_is_still_dropped(tmp_path):
    """The same source id appearing twice (e.g. a re-fetched page) is a dupe."""
    case = _case("abc-1", "B-1234/2024")
    (tmp_path / "cases_1.json").write_text(json.dumps([case, dict(case)]), encoding="utf-8")

    count = convert_json_to_bib(str(tmp_path), str(tmp_path / "out.bib"))

    assert count == 1
