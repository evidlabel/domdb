import json

import pytest
import yaml

from domdb.core.converters.json2hay.entry import create_hay_entry
from domdb.core.converters.json2hay.convert import convert_json_to_hay
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
        "profession": {"displayText": "Byret"},
        "instance": {"displayText": "1. instans"},
        "caseType": {"displayText": "Civil"},
    }


def test_create_hay_entry(sample_case):
    case = ModelItem.model_validate(sample_case)
    key, entry = create_hay_entry(case)
    assert key == "1232023"
    assert entry["type"] == "Case"
    assert entry["title"] == "Test Case"
    assert entry["author"] == "Test Author"
    assert entry["date"] == "2023-01-01"
    assert entry["serial-number"] == "123/2023"
    assert entry["url"] == "https://domsdatabasen.dk/#sag/test123"
    assert entry["publisher"] == "Subject1"
    assert entry["organization"] == "Byret, 1. instans, Civil"


def test_convert_json_to_hay_success(tmp_path, sample_case):
    json_file = tmp_path / "cases_1.json"
    with open(json_file, "w") as f:
        json.dump([sample_case], f)

    output_file = tmp_path / "output.yml"
    count = convert_json_to_hay(str(tmp_path), str(output_file))
    assert count == 1
    assert output_file.exists()

    text = output_file.read_text(encoding="utf-8")
    assert text.startswith("# generated-by: domdb output hay")
    data = yaml.safe_load(text)
    assert "1232023" in data
    assert data["1232023"]["type"] == "Case"
    assert data["1232023"]["title"] == "Test Case"


def test_convert_json_to_hay_dedupe_and_sort(tmp_path, sample_case):
    older = dict(sample_case)
    older["id"] = "old1"
    older["courtCaseNumber"] = "1/2020"
    older["documents"] = [{"verdictDateTime": "2020-01-01T00:00:00"}]
    newer = dict(sample_case)
    newer["id"] = "new1"
    newer["courtCaseNumber"] = "2/2024"
    newer["documents"] = [{"verdictDateTime": "2024-06-01T00:00:00"}]
    # Duplicate of newer under same key
    dupe = dict(newer)

    json_file = tmp_path / "cases.json"
    with open(json_file, "w") as f:
        json.dump([older, newer, dupe], f)

    output_file = tmp_path / "out.yml"
    count = convert_json_to_hay(str(tmp_path), str(output_file))
    assert count == 2
    data = yaml.safe_load(output_file.read_text(encoding="utf-8"))
    keys = list(data.keys())
    assert keys == ["22024", "12020"]  # newest first


def test_convert_json_to_hay_no_files(tmp_path):
    output_file = tmp_path / "output.yml"
    with pytest.raises(ConversionError, match="No JSON files found in"):
        convert_json_to_hay(str(tmp_path), str(output_file))
