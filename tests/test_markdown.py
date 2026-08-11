import json
import tempfile
from pathlib import Path
import pytest

from domdb.core.converters.json2md.convert import convert_json_to_md
from domdb.core.exceptions import ConversionError


@pytest.fixture
def sample_cases():
    """Sample case data for testing."""
    return [
        {
            "id": "1",
            "headline": "Case One",
            "author": "Author One",
            "officeName": "Office One",
            "profession": {"displayText": "Profession One"},
            "instance": {"displayText": "Instance One"},
            "caseType": {"displayText": "Type One"},
            "caseSubjects": [{"displayText": "Subject One"}],
            "courtCaseNumber": "123-2023",
            "documents": [{"verdictDateTime": "2023-05-01T10:00:00"}],
        },
        {
            "id": "2",
            "headline": "Case Two",
            "author": "Author Two",
            "officeName": None,
            "profession": None,
            "instance": None,
            "caseType": None,
            "caseSubjects": [],
            "courtCaseNumber": "456-2022",
            "documents": [{"verdictDateTime": "2022-03-15T10:00:00"}],
        },
        {
            "id": "3",
            "headline": "Case Three",
            "author": None,
            "officeName": "Office Three",
            "profession": {"displayText": "Profession Three"},
            "instance": {"displayText": "Instance Three"},
            "caseType": {"displayText": "Type Three"},
            "caseSubjects": [{"displayText": "Subject Three"}],
            "courtCaseNumber": "789-2023",
            "documents": [],  # No date
        },
        {
            "id": "1",  # Duplicate
            "headline": "Case One Duplicate",
            "author": "Author One",
            "officeName": "Office One",
            "profession": {"displayText": "Profession One"},
            "instance": {"displayText": "Instance One"},
            "caseType": {"displayText": "Type One"},
            "caseSubjects": [{"displayText": "Subject One"}],
            "courtCaseNumber": "123-2023",
            "documents": [{"verdictDateTime": "2023-05-01T10:00:00"}],
        },
    ]


@pytest.fixture
def temp_dir_with_json(sample_cases):
    """Create a temporary directory with sample JSON files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = Path(tmpdir) / "cases_1.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(sample_cases, f, ensure_ascii=False, indent=2)
        yield tmpdir


@pytest.fixture
def output_dir():
    """Temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestMarkdownConversion:
    def test_basic_conversion(self, temp_dir_with_json, output_dir):
        """Test basic Markdown conversion without splitting."""
        output_file = Path(output_dir) / "cases.md"
        count = convert_json_to_md(temp_dir_with_json, str(output_file))
        assert count == 3  # Unique cases
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        # Sorted descending: 2023 first, 2022 second, no-date last
        idx_one = content.find("Case One")  # 2023-05-01
        idx_two = content.find("Case Two")  # 2022-03-15
        idx_three = content.find("Case Three")  # no verdict date
        assert idx_one < idx_two < idx_three

    def test_split_by_year(self, temp_dir_with_json, output_dir):
        """Test Markdown conversion with split by year."""
        output_file = Path(output_dir) / "cases.md"
        count = convert_json_to_md(
            temp_dir_with_json, str(output_file), split_by_year=True
        )
        assert count == 3
        # Check files created
        files = list(Path(output_dir).glob("cases_*.md"))
        assert len(files) == 3  # 2022, 2023, unknown
        file_names = {f.name for f in files}
        assert "cases_2022.md" in file_names
        assert "cases_2023.md" in file_names
        assert "cases_unknown.md" in file_names
        # Check content
        content_2022 = (Path(output_dir) / "cases_2022.md").read_text()
        assert "Case Two" in content_2022
        content_2023 = (Path(output_dir) / "cases_2023.md").read_text()
        assert "Case One" in content_2023
        content_unknown = (Path(output_dir) / "cases_unknown.md").read_text()
        assert "Case Three" in content_unknown

    def test_number_limit(self, temp_dir_with_json, output_dir):
        """Test with number limit."""
        output_file = Path(output_dir) / "cases.md"
        count = convert_json_to_md(temp_dir_with_json, str(output_file), number=2)
        assert count == 2
        content = output_file.read_text()
        # Should have 2 cases
        entries_md = content.strip().split("\n\n")
        assert len(entries_md) == 2

    def test_no_json_files(self, output_dir):
        """Test when no JSON files are present."""
        with tempfile.TemporaryDirectory() as empty_dir:
            output_file = Path(output_dir) / "cases.md"
            with pytest.raises(ConversionError):
                convert_json_to_md(empty_dir, str(output_file))


@pytest.fixture
def body_text_case_dir():
    """A case whose body text (contentHtml) mentions 'psykisk vold' and 'krisecenter',
    but whose metadata does not."""
    cases = [
        {
            "id": "100",
            "headline": "Straffesag",  # metadata does NOT mention either term
            "author": "Retten",
            "officeName": "Retten i Aarhus",
            "profession": {"displayText": "Straffesag"},
            "instance": {"displayText": "1. instans"},
            "caseType": {"displayText": "Domsmandssag"},
            "caseSubjects": [{"displayText": "Straffeproces"}],
            "courtCaseNumber": "SS-1/2024",
            "documents": [
                {
                    "verdictDateTime": "2024-01-01T10:00:00",
                    "contentHtml": "<p>Tiltalte udsatte forurettede for psykisk vold. "
                    "Forurettede flyttede til et krisecenter.</p>",
                }
            ],
        },
        {
            "id": "101",
            "headline": "Civilsag",  # only one term in body
            "author": "Retten",
            "officeName": "Retten i Aalborg",
            "profession": {"displayText": "Civilsag"},
            "instance": {"displayText": "1. instans"},
            "caseType": {"displayText": "Boligsag"},
            "caseSubjects": [{"displayText": "Lejeret"}],
            "courtCaseNumber": "BS-2/2024",
            "documents": [
                {
                    "verdictDateTime": "2024-02-01T10:00:00",
                    "contentHtml": "<p>Sagen angik psykisk vold uden ophold paa noget center.</p>",
                }
            ],
        },
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = Path(tmpdir) / "cases.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(cases, f, ensure_ascii=False, indent=2)
        yield tmpdir


class TestKeywordFiltering:
    def test_metadata_only_misses_body_term(self, body_text_case_dir, output_dir):
        """Without full_text, a body-only term like 'krisecenter' matches nothing."""
        output_file = Path(output_dir) / "cases.md"
        count = convert_json_to_md(
            body_text_case_dir, str(output_file), keywords=["krisecenter"]
        )
        assert count == 0

    def test_full_text_and_match(self, body_text_case_dir, output_dir):
        """With full_text, requiring BOTH terms matches only the case that has both."""
        output_file = Path(output_dir) / "cases.md"
        count = convert_json_to_md(
            body_text_case_dir,
            str(output_file),
            keywords=["psykisk vold", "krisecenter"],
            full_text=True,
        )
        assert count == 1
        content = output_file.read_text(encoding="utf-8")
        assert "100" in content  # the case id appears in the domsdatabasen URL
        assert "101" not in content

    def test_full_text_single_missing_keyword_excludes(
        self, body_text_case_dir, output_dir
    ):
        """A keyword absent from a case excludes it under AND semantics."""
        output_file = Path(output_dir) / "cases.md"
        count = convert_json_to_md(
            body_text_case_dir,
            str(output_file),
            keywords=["krisecenter", "udlændingeret"],
            full_text=True,
        )
        assert count == 0

    def test_metadata_keyword_still_works(self, temp_dir_with_json, output_dir):
        """Single metadata keyword filtering (backwards compatible) still works."""
        output_file = Path(output_dir) / "cases.md"
        count = convert_json_to_md(
            temp_dir_with_json, str(output_file), keywords=["Subject One"]
        )
        assert count == 1

    def test_metadata_and_requires_both_keywords(self, temp_dir_with_json, output_dir):
        """Multi-keyword AND on metadata only, without full_text."""
        output_file = Path(output_dir) / "cases.md"
        count = convert_json_to_md(
            temp_dir_with_json,
            str(output_file),
            keywords=["Subject One", "Case One"],
        )
        assert count == 1
        content = output_file.read_text(encoding="utf-8")
        assert "Case Two" not in content

    def test_metadata_only_does_not_extract_body(
        self, mocker, body_text_case_dir, output_dir
    ):
        """Without full_text, body extraction is never invoked."""
        mock_extract = mocker.patch(
            "domdb.core.converters.json2md.filter.extract_case_text"
        )
        output_file = Path(output_dir) / "cases.md"
        convert_json_to_md(
            body_text_case_dir, str(output_file), keywords=["krisecenter"]
        )
        mock_extract.assert_not_called()

    def test_full_text_skips_extraction_when_metadata_matches(
        self, mocker, temp_dir_with_json, output_dir
    ):
        """With full_text, body extraction is skipped for cases metadata already matches."""
        mock_extract = mocker.patch(
            "domdb.core.converters.json2md.filter.extract_case_text",
            return_value="",
        )
        output_file = Path(output_dir) / "cases.md"
        convert_json_to_md(
            temp_dir_with_json,
            str(output_file),
            keywords=["Subject One"],
            full_text=True,
        )
        extracted_ids = {call.args[0].id for call in mock_extract.call_args_list}
        assert "1" not in extracted_ids

    def test_empty_keyword_strings_treated_as_no_filter(
        self, temp_dir_with_json, output_dir
    ):
        output_file = Path(output_dir) / "cases.md"
        count = convert_json_to_md(
            temp_dir_with_json, str(output_file), keywords=["", "  "]
        )
        assert count == 3
