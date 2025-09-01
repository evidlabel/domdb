import pytest
import json
from domdb.core.converters.json2bib.entry import create_bib_entry
from domdb.core.converters.json2bib.convert import convert_json_to_bib
from domdb.core.model import ModelItem
from domdb.core.exceptions import ConversionError


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
    case = ModelItem.model_validate(sample_case)
    entry = create_bib_entry(case)
    assert entry["ID"] == "1232023"
    assert entry["title"] == "Test Case"
    assert entry["date"] == "2023-01-01"
    assert entry["author"] == "Test Author"


def test_convert_json_to_bib_success(tmp_path, sample_case):
    json_file = tmp_path / "cases_1.json"
    with open(json_file, "w") as f:
        json.dump([sample_case], f)

    output_file = tmp_path / "output.bib"
    count = convert_json_to_bib(str(tmp_path), str(output_file))
    assert count == 1
    assert output_file.exists()


def test_convert_json_to_bib_no_files(tmp_path):
    output_file = tmp_path / "output.bib"
    with pytest.raises(ConversionError, match="No JSON files found in"):
        convert_json_to_bib(str(tmp_path), str(output_file))
