import re

from domdb.core.query.paragraph import (
    parse_paragraph_query,
    paragraph_pattern,
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