import json
import tempfile
from pathlib import Path
import pytest

from domdb.core.converters.json2md.convert import convert_json_to_md


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
        idx_one = content.find("Case One")    # 2023-05-01
        idx_two = content.find("Case Two")    # 2022-03-15
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
            with pytest.raises(Exception):  # ConversionError
                convert_json_to_md(empty_dir, str(output_file))
