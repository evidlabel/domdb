import pytest
import json
import uuid
import yaml
from domdb.core.converters.json2evid.dir_creation import create_evid_dir
from domdb.core.converters.json2evid.processing import convert_json_to_evid
from domdb.core.model import ModelItem
from domdb.core.exceptions import EvidConversionError


@pytest.fixture
def sample_case():
    return {
        "id": "test123",
        "headline": "Test Case",
        "courtCaseNumber": "123/2023",
        "documents": [
            {
                "id": "doc1",
                "verdictDateTime": "2023-01-01T12:00:00",
                "contentHtml": "<p>Test content</p><p>More text</p>",
                "contentPdf": None,
            }
        ],
        "profession": {"displayText": "Test Profession"},
        "instance": {"displayText": "Test Instance"},
        "caseType": {"displayText": "Test Type"},
        "caseSubjects": [{"displayText": "Subject1"}],
    }


def test_create_evid_dir(tmp_path, sample_case):
    base_output = tmp_path / "evid"
    case = ModelItem.model_validate(sample_case)
    create_evid_dir(case, str(base_output))
    expected_uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, "test123"))
    expected_dir = base_output / expected_uuid
    assert expected_dir.exists()

    # Check case.json
    json_path = expected_dir / "case.json"
    assert json_path.exists()
    with open(json_path, "r") as f:
        saved = json.load(f)
        assert saved == case.model_dump()

    # Check info.yml
    info_path = expected_dir / "info.yml"
    assert info_path.exists()
    with open(info_path, "r") as f:
        info = yaml.safe_load(f)
        assert info["uuid"] == expected_uuid
        assert info["dates"] == "2023-01-01"
        assert info["title"] == "Test Case"
        assert info["label"] == "Test Profession, Test Instance, Test Type"
        assert info["tags"] == "Subject1"
        assert info["original_name"] == "123/2023"
        assert info["url"] == "https://domsdatabasen.dk/#sag/test123"

    # Check label.typ
    label_path = expected_dir / "label.typ"
    assert label_path.exists()
    with open(label_path, "r") as f:
        content = f.read()
        assert "#mset(values: (opage: 1))" in content
        assert "Test content" in content
        assert "More text" in content
        assert "2023-01-01" in content
        assert "Test Profession, Test Instance, Test Type" in content


def test_convert_json_to_evid_success(tmp_path, sample_case):
    json_dir = tmp_path / "json"
    json_dir.mkdir()
    json_file = json_dir / "cases_1.json"
    with open(json_file, "w") as f:
        json.dump([sample_case], f)

    output_dir = tmp_path / "evid"
    count = convert_json_to_evid(str(json_dir), str(output_dir))
    assert count == 1
    expected_uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, "test123"))
    expected_dir = output_dir / expected_uuid
    assert (expected_dir / "case.json").exists()
    assert (expected_dir / "info.yml").exists()
    assert (expected_dir / "label.typ").exists()


def test_convert_json_to_evid_skip_existing(tmp_path, sample_case):
    json_dir = tmp_path / "json"
    json_dir.mkdir()
    json_file = json_dir / "cases_1.json"
    with open(json_file, "w") as f:
        json.dump([sample_case], f)

    output_dir = tmp_path / "evid"
    # First conversion
    count1 = convert_json_to_evid(str(json_dir), str(output_dir))
    assert count1 == 1

    # Second conversion
    count2 = convert_json_to_evid(str(json_dir), str(output_dir))
    assert count2 == 0


def test_convert_json_to_evid_no_files(tmp_path):
    json_dir = tmp_path / "json"
    json_dir.mkdir()
    output_dir = tmp_path / "evid"
    with pytest.raises(EvidConversionError, match="No JSON files found"):
        convert_json_to_evid(str(json_dir), str(output_dir))
