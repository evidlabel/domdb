from domdb.core.query.paragraph import (
    parse_paragraph_query,
    text_matches_paragraph,
)


def test_parse_law_and_section():
    spec = parse_paragraph_query("straffeloven § 237")
    assert spec.law == "straffeloven"
    assert spec.section == "237"


def test_parse_section_with_subsection():
    spec = parse_paragraph_query("§ 117 stk. 1")
    assert spec.law is None
    assert spec.section == "117"
    assert spec.subsection == "1"


def test_parse_full_citation():
    spec = parse_paragraph_query("færdselslovens § 117, stk. 1, nr. 3")
    assert spec.law == "færdselsloven"
    assert spec.section == "117"
    assert spec.subsection == "1"
    assert spec.item == "3"


def test_matches_headline_citation():
    spec = parse_paragraph_query("straffeloven § 237")
    text = "Tiltale for overtrædelse af straffelovens § 237, stk. 1"
    assert text_matches_paragraph(text, spec)


def test_matches_without_law_when_unspecified():
    spec = parse_paragraph_query("§ 117 stk. 1")
    text = "efter færdselslovens § 117, stk. 1, nr. 3"
    assert text_matches_paragraph(text, spec)


def test_requires_subsection_when_specified():
    spec = parse_paragraph_query("§ 117 stk. 1")
    text = "efter færdselslovens § 117"
    assert not text_matches_paragraph(text, spec)


# --- H5: section/subsection/item numbers need a right-hand boundary ---


def test_section_does_not_match_longer_number():
    spec = parse_paragraph_query("straffeloven § 237")
    assert text_matches_paragraph("straffelovens § 237", spec)
    assert text_matches_paragraph("straffelovens § 237, stk. 1", spec)
    assert not text_matches_paragraph("straffelovens § 2370", spec)
    assert not text_matches_paragraph("straffelovens § 2371, stk. 2", spec)


def test_section_without_law_does_not_match_longer_number():
    spec = parse_paragraph_query("§ 117")
    assert text_matches_paragraph("færdselslovens § 117", spec)
    assert not text_matches_paragraph("færdselslovens § 1170", spec)


def test_letter_section_does_not_match_digit_suffix():
    spec = parse_paragraph_query("straffeloven § 237a")
    assert text_matches_paragraph("straffelovens § 237 a", spec)
    assert not text_matches_paragraph("straffelovens § 237a1", spec)


def test_subsection_does_not_match_longer_number():
    spec = parse_paragraph_query("§ 117 stk. 1")
    assert text_matches_paragraph("færdselslovens § 117, stk. 1", spec)
    assert not text_matches_paragraph("færdselslovens § 117, stk. 10", spec)


def test_item_does_not_match_longer_number():
    spec = parse_paragraph_query("§ 117 stk. 1 nr. 3")
    assert text_matches_paragraph("færdselslovens § 117, stk. 1, nr. 3", spec)
    assert not text_matches_paragraph("færdselslovens § 117, stk. 1, nr. 30", spec)


def test_paragraph_count_not_inflated_by_prefix_numbers(tmp_path):
    """A case citing only § 2370 must not be counted for § 237."""
    import json

    from domdb.core.query import QueryParams, count_cases

    cases = [
        {
            "id": "c1",
            "headline": "Sag om straffelovens § 2370",
            "documents": [{"verdictDateTime": "2024-01-01T10:00:00"}],
        },
        {
            "id": "c2",
            "headline": "Sag om straffelovens § 237",
            "documents": [{"verdictDateTime": "2024-01-01T10:00:00"}],
        },
    ]
    (tmp_path / "cases.json").write_text(json.dumps(cases), encoding="utf-8")

    assert count_cases(str(tmp_path), QueryParams(paragraph="straffeloven § 237")) == 1
