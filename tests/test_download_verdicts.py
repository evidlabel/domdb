import pytest
import json
import requests
from domdb.core.download.main import load_next_batch
from domdb.core.download.auth import get_access_token
from domdb.core.download.fetch import get_sager
from domdb.core.download.storage import save_cases, get_last_saved_page
from domdb.core.exceptions import DownloadError


@pytest.fixture
def mock_requests(mocker):
    return mocker.patch("requests")


def test_get_access_token_success(mock_requests, mocker):
    mocker.patch("domdb.core.download.auth.USER_ID", "test_user")
    mocker.patch("domdb.core.download.auth.PASSWORD", "test_pass")
    mock_response = mock_requests.post.return_value
    mock_response.json.return_value = {"tokenString": "test_token"}
    mock_response.raise_for_status.return_value = None

    token = get_access_token()
    assert token == "test_token"


def test_get_access_token_missing_credentials(mocker):
    mocker.patch("domdb.core.download.auth.USER_ID", None)
    mocker.patch("domdb.core.download.auth.PASSWORD", None)
    with pytest.raises(DownloadError):
        get_access_token()


def test_get_sager_success(mock_requests):
    mock_response = mock_requests.get.return_value
    mock_response.json.return_value = [{"id": "test"}]
    mock_response.raise_for_status.return_value = None

    cases = get_sager("test_token")
    assert len(cases) == 1
    assert cases[0]["id"] == "test"


def test_get_sager_failure(mock_requests):
    mock_requests.get.side_effect = requests.exceptions.RequestException("API error")
    with pytest.raises(DownloadError):
        get_sager("test_token")


def test_save_cases(tmp_path):
    cases = [{"id": "test"}]
    save_cases(1, cases, directory=tmp_path)
    output_file = tmp_path / "cases_1.json"
    assert output_file.exists()
    with open(output_file, "r") as f:
        saved = json.load(f)
        assert saved == cases


def test_get_last_saved_page_empty(tmp_path):
    assert get_last_saved_page(tmp_path) == 1


def test_get_last_saved_page_existing(tmp_path):
    (tmp_path / "cases_1.json").touch()
    (tmp_path / "cases_3.json").touch()
    assert get_last_saved_page(tmp_path) == 4


def test_load_next_batch_success(mock_requests, mocker, tmp_path):
    mocker.patch("domdb.core.download.auth.USER_ID", "test_user")
    mocker.patch("domdb.core.download.auth.PASSWORD", "test_pass")
    mock_response_post = mock_requests.post.return_value
    mock_response_post.json.return_value = {"tokenString": "test_token"}
    mock_response_post.raise_for_status.return_value = None
    mock_response_get = mock_requests.get.return_value
    mock_response_get.json.return_value = [{"id": "test"}]
    mock_response_get.raise_for_status.return_value = None

    count = load_next_batch(directory=tmp_path)
    assert count == 1
    output_file = tmp_path / "cases_1.json"
    assert output_file.exists()
