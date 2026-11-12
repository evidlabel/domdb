"""Regression tests for verdict date parsing (finding H4).

The API returns ``verdictDateTime`` values with fractional seconds
(``2024-05-14T09:30:00.000``); ``strptime("%Y-%m-%dT%H:%M:%S")`` rejected them
and the swallowed ValueError emitted ``date = {Unknown}`` - and excluded the
case from every ``--from``/``--to`` query.
"""

import json

import pytest

from domdb.core.converters.fields import (
    parse_case_fields,
    verdict_date_from_datetime,
)
from domdb.core.converters.json2bib.entry import create_bib_entry
from domdb.core.converters.json2evid.date_utils import extract_verdict_date
from domdb.core.model import ModelItem
from domdb.core.query import QueryParams, count_cases


def _case(dt, case_id="c1"):
    return ModelItem.model_validate(
        {
            "id": case_id,
            "headline": "Sag",
            "courtCaseNumber": "B-1/2024",
            "documents": [{"verdictDateTime": dt}],
        }
    )


@pytest.mark.parametrize(
    "raw",
    [
        "2024-05-14T09:30:00",
        "2024-05-14T09:30:00.000",
        "2024-05-14T09:30:00.123456",
        "2024-05-14T09:30:00+02:00",
        "2024-05-14T09:30:00Z",
    ],
)
def test_fractional_seconds_and_offsets_parse(raw):
    assert verdict_date_from_datetime(raw) == "2024-05-14"


def test_parse_case_fields_keeps_date_with_fractional_seconds():
    fields = parse_case_fields(_case("2024-05-14T09:30:00.000"))
    assert fields["verdict_date"] == "2024-05-14"


def test_bib_entry_no_longer_says_unknown():
    entry = create_bib_entry(_case("2024-05-14T09:30:00.000"))
    assert entry["date"] == "2024-05-14"


def test_evid_date_utility_matches():
    assert extract_verdict_date(_case("2024-05-14T09:30:00.000")) == "2024-05-14"


def test_unparseable_value_is_kept_not_turned_into_unknown():
    """A value we cannot parse is reported verbatim, not replaced by Unknown."""
    fields = parse_case_fields(_case("14. maj 2024 kl. 09:30"))
    assert fields["verdict_date"] == "14. maj 2024 kl. 09:30"


def test_leading_iso_date_is_salvaged_from_noisy_value():
    fields = parse_case_fields(_case("2024-05-14 kl. 09:30"))
    assert fields["verdict_date"] == "2024-05-14"


def test_missing_datetime_is_still_unknown():
    assert parse_case_fields(_case(None))["verdict_date"] == "Unknown"
    assert parse_case_fields(ModelItem.model_validate({"id": "c1"}))[
        "verdict_date"
    ] == "Unknown"


def test_fractional_second_case_is_not_excluded_from_date_range(tmp_path):
    cases = [
        {
            "id": "c1",
            "headline": "Sag",
            "documents": [{"verdictDateTime": "2024-05-14T09:30:00.000"}],
        }
    ]
    (tmp_path / "cases.json").write_text(json.dumps(cases), encoding="utf-8")

    params = QueryParams(from_date="2024-01-01", to_date="2024-12-31")
    assert count_cases(str(tmp_path), params) == 1
