import json
import tempfile
from pathlib import Path

import pytest

from domdb.core.query import QueryParams, build_index, count_cases, list_cases
from domdb.core.query.engine import CaseHit


@pytest.fixture
def research_cases():
    return [
        {
            "id": "100",
            "headline": "Tiltale for overtrædelse af straffelovens § 237, stk. 1",
            "author": "Retten i Aarhus",
            "officeName": "Retten i Aarhus",
            "profession": {"displayText": "Straffesag"},
            "instance": {"displayText": "1. instans"},
            "caseType": {"displayText": "Domsmandssag"},
            "caseSubjects": [{"displayText": "Straffeproces"}],
            "courtCaseNumber": "SS-1/2020",
            "documents": [{"verdictDateTime": "2020-06-15T10:00:00"}],
        },
        {
            "id": "101",
            "headline": "Civilsag om erstatning",
            "author": "Retten i København",
            "officeName": "Retten i København",
            "profession": {"displayText": "Civilsag"},
            "instance": {"displayText": "1. instans"},
            "caseType": {"displayText": "Erstatning"},
            "caseSubjects": [{"displayText": "Erstatning"}],
            "courtCaseNumber": "BS-2/2022",
            "documents": [
                {
                    "verdictDateTime": "2022-03-01T10:00:00",
                    "contentHtml": "<p>Sagen angik straffelovens § 237 og psykisk vold.</p>",
                }
            ],
        },
        {
            "id": "102",
            "headline": "Ældre sag",
            "author": "Retten i Odense",
            "officeName": "Retten i Odense",
            "profession": {"displayText": "Straffesag"},
            "instance": {"displayText": "1. instans"},
            "caseType": {"displayText": "Domsmandssag"},
            "caseSubjects": [{"displayText": "Straffeproces"}],
            "courtCaseNumber": "SS-3/2015",
            "documents": [{"verdictDateTime": "2015-01-10T10:00:00"}],
        },
    ]


@pytest.fixture
def research_dir(research_cases):
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "cases.json"
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(research_cases, handle, ensure_ascii=False)
        yield tmpdir


class TestQueryEngine:
    def test_count_paragraph_in_headline(self, research_dir):
        params = QueryParams(paragraph="straffeloven § 237")
        assert count_cases(research_dir, params) == 2

    def test_count_paragraph_with_date_range(self, research_dir):
        params = QueryParams(
            paragraph="straffeloven § 237",
            from_date="2020-01-01",
            to_date="2021-12-31",
        )
        assert count_cases(research_dir, params) == 1

    def test_count_keywords_metadata_only(self, research_dir):
        params = QueryParams(keywords=["erstatning"])
        assert count_cases(research_dir, params) == 1

    def test_count_keywords_full_text(self, research_dir):
        params = QueryParams(keywords=["psykisk vold"], full_text=True)
        assert count_cases(research_dir, params) == 1

    def test_list_respects_limit(self, research_dir):
        params = QueryParams(paragraph="straffeloven § 237", limit=1)
        hits = list_cases(research_dir, params)
        assert len(hits) == 1
        assert isinstance(hits[0], CaseHit)
        assert hits[0].url.startswith("https://domsdatabasen.dk/")

    def test_index_speed_path(self, research_dir):
        build_index(research_dir)
        params = QueryParams(
            paragraph="straffeloven § 237",
            from_date="2020-01-01",
            to_date="2022-12-31",
        )
        assert count_cases(research_dir, params) == 2

    def test_court_filter(self, research_dir):
        build_index(research_dir)
        params = QueryParams(keywords=["erstatning"], court="København")
        assert count_cases(research_dir, params) == 1
