import pytest
import sys
from io import StringIO

from domdb.cli.bib import bib
from domdb.cli.j2e import j2e
from domdb.cli.download import download
from domdb.cli.main import main
from domdb.core.exceptions import ConversionError, EvidConversionError, DownloadError


def test_bib_success(mocker, capsys):
    """Test successful bib conversion."""
    mock_convert = mocker.patch('domdb.cli.bib.convert_json_to_bib', return_value=5)
    bib(-1, 'dir', 'out.bib')
    captured = capsys.readouterr()
    assert "Converted 5 unique cases to out.bib" in captured.out
    mock_convert.assert_called_once_with('dir', 'out.bib', None)


def test_bib_error(mocker, capsys):
    """Test bib conversion error."""
    mock_convert = mocker.patch('domdb.cli.bib.convert_json_to_bib', side_effect=ConversionError('error'))
    with pytest.raises(SystemExit) as excinfo:
        bib(10, 'dir', 'out.bib')
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "error" in captured.err
    mock_convert.assert_called_once_with('dir', 'out.bib', 10)


def test_j2e_success(mocker, capsys):
    """Test successful j2e conversion."""
    mock_convert = mocker.patch('domdb.cli.j2e.convert_json_to_evid', return_value=3)
    j2e(-1, 'dir', 'out')
    captured = capsys.readouterr()
    assert "Converted 3 cases to EVID in out" in captured.out
    mock_convert.assert_called_once_with('dir', 'out', None)


def test_j2e_error(mocker, capsys):
    """Test j2e conversion error."""
    mock_convert = mocker.patch('domdb.cli.j2e.convert_json_to_evid', side_effect=EvidConversionError('error'))
    with pytest.raises(SystemExit) as excinfo:
        j2e(5, 'dir', 'out')
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "error" in captured.err
    mock_convert.assert_called_once_with('dir', 'out', 5)


def test_download_success(mocker, capsys):
    """Test successful download."""
    mock_load = mocker.patch('domdb.cli.download.load_next_batch', return_value=7)
    download('dir')
    captured = capsys.readouterr()
    assert "Successfully fetched 7 cases" in captured.out
    mock_load.assert_called_once_with('dir')


def test_download_error(mocker, capsys):
    """Test download error."""
    mock_load = mocker.patch('domdb.cli.download.load_next_batch', side_effect=DownloadError('error'))
    with pytest.raises(SystemExit) as excinfo:
        download('dir')
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "error" in captured.err
    mock_load.assert_called_once_with('dir')


def test_download_unexpected_error(mocker, capsys):
    """Test unexpected download error."""
    mock_load = mocker.patch('domdb.cli.download.load_next_batch', side_effect=Exception('unexpected'))
    with pytest.raises(SystemExit) as excinfo:
        download('dir')
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Unexpected error: unexpected" in captured.err
    mock_load.assert_called_once_with('dir')


def test_main(mocker):
    """Test main function."""
    mock_app = mocker.patch('domdb.cli.main.app')
    main()
    mock_app.run.assert_called_once()
