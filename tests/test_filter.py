from domdb.core.converters.json2md.filter import case_matches_keywords
from domdb.core.query.search import metadata_search_text, normalize_keywords
from domdb.core.model import ModelItem


def test_normalize_keywords_strips_and_drops_empty():
    assert normalize_keywords([" Foo ", "", "  ", "bar"]) == ["foo", "bar"]
    assert normalize_keywords(None) == []
    assert normalize_keywords([]) == []


def test_metadata_search_text_includes_headline_and_subjects():
    case = ModelItem.model_validate(
        {
            "id": "42",
            "headline": "Straffesag",
            "caseSubjects": [{"displayText": "Subject One"}],
        }
    )
    text = metadata_search_text(case)
    assert "straffesag" in text
    assert "subject one" in text
    assert "42" in text


def test_case_matches_keywords_metadata_only():
    case = ModelItem.model_validate(
        {
            "id": "1",
            "headline": "Case One",
            "caseSubjects": [{"displayText": "Subject One"}],
        }
    )
    assert case_matches_keywords(case, ["subject one", "case one"])
    assert not case_matches_keywords(case, ["missing"])


def test_case_matches_keywords_uses_body_when_full_text():
    case = ModelItem.model_validate(
        {
            "id": "100",
            "headline": "Straffesag",
            "documents": [{"contentHtml": "<p>krisecenter</p>"}],
        }
    )
    assert not case_matches_keywords(case, ["krisecenter"])
    assert case_matches_keywords(case, ["krisecenter"], full_text=True)
