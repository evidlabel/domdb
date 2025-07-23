import pytest
import json
import uuid
import yaml
from click.testing import CliRunner
from domdb.core.converters.json2evid.convert import create_evid_dir, convert_json_to_evid
from domdb.core.model import ModelItem
from domdb.cli.main import cli


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
    dir_path = create_evid_dir(case, str(base_output))
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
        assert info["id"] == "test123"
        assert info["headline"] == "Test Case"
        assert info["date"] == "2023-01-01"
        assert info["case_number"] == "123/2023"

    # Check label.tex
    label_path = expected_dir / "label.tex"
    assert label_path.exists()
    with open(label_path, "r") as f:
        content = f.read()
        assert "\\label{case-test123}" in content
        assert "Test Case" in content
        assert "123/2023" in content
        assert "2023-01-01" in content

    # Check extracted text
    text_path = expected_dir / "verdict_text_doc1.txt"
    assert text_path.exists()
    with open(text_path, "r") as f:
        text_content = f.read()
        assert "Test content" in text_content
        assert "More text" in text_content


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
    assert (expected_dir / "label.tex").exists()
    assert (expected_dir / "verdict_text_doc1.txt").exists()


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


def test_j2e_command_success(tmp_path, sample_case):
    json_dir = tmp_path / "json"
    json_dir.mkdir()
    json_file = json_dir / "cases_1.json"
    with open(json_file, "w") as f:
        json.dump([sample_case], f)

    output_dir = tmp_path / "evid"
    runner = CliRunner()
    result = runner.invoke(cli, ["j2e", "-d", str(json_dir), "-o", str(output_dir)])
    assert result.exit_code == 0
    assert "Converted 1 cases to EVID" in result.output
    expected_uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, "test123"))
    expected_dir = output_dir / expected_uuid
    assert (expected_dir / "case.json").exists()
    assert (expected_dir / "info.yml").exists()
    assert (expected_dir / "label.tex").exists()
    assert (expected_dir / "verdict_text_doc1.txt").exists()


def test_j2e_command_no_files(tmp_path):
    json_dir = tmp_path / "json"
    json_dir.mkdir()
    output_dir = tmp_path / "evid"
    runner = CliRunner()
    result = runner.invoke(cli, ["j2e", "-d", str(json_dir), "-o", str(output_dir)])
    assert result.exit_code == 1
    assert "No JSON files found" in result.exception.args[0]
