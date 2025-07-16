import pytest
import json
from click.testing import CliRunner
from domdb.core.json2bib import create_bib_entry
from domdb.cli.cli import cli


@pytest.fixture
def sample_case():
    return {
        "id": "test123",
        "headline": "Test Case",
        "author": "Test Author",
        "officeName": "Test Office",
        "courtCaseNumber": "123/2023",
        "documents": [{"verdictDateTime": "2023-01-01T12:00:00"}],
        "caseSubjects": [{"displayText": "Subject1"}],
    }


def test_create_bib_entry(sample_case):
    entry = create_bib_entry(sample_case)
    assert entry["ID"] == "1232023"
    assert entry["title"] == "Test Case"
    assert entry["date"] == "2023-01-01"
    assert entry["author"] == "Test Author"


def test_main_success(tmp_path, sample_case):
    json_file = tmp_path / "cases_1.json"
    with open(json_file, "w") as f:
        json.dump([sample_case], f)

    output_file = tmp_path / "output.bib"
    runner = CliRunner()
    result = runner.invoke(cli, ["bib", "-d", str(tmp_path), "-o", str(output_file)])
    assert result.exit_code == 0
    assert output_file.exists()


def test_main_no_files(tmp_path):
    output_file = tmp_path / "output.bib"
    runner = CliRunner()
    result = runner.invoke(cli, ["bib", "-d", str(tmp_path), "-o", str(output_file)])
    assert result.exit_code == 1
    assert not output_file.exists()
