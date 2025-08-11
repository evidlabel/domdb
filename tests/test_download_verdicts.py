import pytest
import json
import requests
from domdb.core.download.main import load_next_batch
from domdb.core.download.auth import get_access_token, API_BASE_URL
from domdb.core.download.fetch import get_sager
from domdb.core.download.storage import save_cases, get_last_saved_page
from domdb.core.exceptions import DownloadError


@pytest.fixture
def mock_env(mocker):
    mocker.patch(
        "os.getenv",
        side_effect=lambda k, d=None: {
            "DOMDB_USER_ID": "test_user",
            "DOMDB_PASSWORD": "test_pass",
        }.get(k, d),
    )


def test_get_access_token_success(mock_env, mocker):
    mock_post = mocker.patch("requests.post")
    mock_response = mock_post.return_value
    mock_response.json.return_value = {"tokenString": "test_token"}
    mock_response.raise_for_status.return_value = None

    token = get_access_token()
    assert token == "test_token"
    mock_post.assert_called_once_with(
        f"{API_BASE_URL}/autoriser",
        json={"Email": "test_user", "Password": "test_pass"},
        headers={"Content-Type": "application/json"},
        timeout=10,
    )


def test_get_access_token_missing_credentials(mocker):
    mocker.patch("os.getenv", return_value=None)
    with pytest.raises(DownloadError, match="Missing USER_ID or PASSWORD environment variables"):
        get_access_token()


def test_get_sager_success(mocker):
    mock_get = mocker.patch("requests.get")
    mock_response = mock_get.return_value
    mock_response.json.return_value = [{"id": "test"}]
    mock_response.raise_for_status.return_value = None

    cases = get_sager("test_token")
    assert len(cases) == 1
    assert cases[0]["id"] == "test"
    mock_get.assert_called_once_with(
        f"{API_BASE_URL}/sager",
        headers={"Authorization": "Bearer test_token"},
        params={"sideNr": 1, "perSide": 100},
        timeout=10,
    )


def test_get_sager_failure(mocker):
    mock_get = mocker.patch("requests.get")
    mock_get.side_effect = requests.exceptions.RequestException("API error")
    with pytest.raises(DownloadError, match="Failed to fetch cases: API error"):
        get_sager("test_token")


def test_save_cases(tmp_path):
    cases = [{"id": "test"}]
    save_cases(1, cases, directory=str(tmp_path))
    output_file = tmp_path / "cases_1.json"
    assert output_file.exists()
    with open(output_file, "r") as f:
        saved = json.load(f)
        assert saved == cases


def test_get_last_saved_page_empty(tmp_path):
    assert get_last_saved_page(str(tmp_path)) == 1


def test_get_last_saved_page_existing(tmp_path):
    (tmp_path / "cases_1.json").touch()
    (tmp_path / "cases_3.json").touch()
    assert get_last_saved_page(str(tmp_path)) == 4


def test_load_next_batch_success(mock_env, mocker, tmp_path):
    mock_post = mocker.patch("requests.post")
    mock_get = mocker.patch("requests.get")
    mock_post_response = mock_post.return_value
    mock_post_response.json.return_value = {"tokenString": "test_token"}
    mock_post_response.raise_for_status.return_value = None
    mock_get_response = mock_get.return_value
    mock_get_response.json.return_value = [{"id": "test"}]
    mock_get_response.raise_for_status.return_value = None
    mocker.patch("domdb.core.config.load_config", return_value={"batch_size": 100})

    count = load_next_batch(directory=str(tmp_path))
    assert count == 1
    output_file = tmp_path / "cases_1.json"
    assert output_file.exists()
