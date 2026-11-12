"""CLI-level regression tests for ``-d/--directory`` (finding H1).

The option used to be accepted only before the subcommand and was then
overwritten by the leaf parser's default, so every documented invocation
silently read ``~/domdatabasen/cases`` and the README form
``domdb output bib -d .`` died with "unrecognized arguments".
"""

import json
import sys

import pytest

from domdb.cli.main import main, normalize_argv


@pytest.fixture
def cache(tmp_path):
    """A cache directory with exactly one valid verdict."""
    case = {
        "id": "abc-1",
        "headline": "Tiltale for overtrædelse af straffelovens § 237",
        "author": "Østre Landsret",
        "courtCaseNumber": "B-1234/2024",
        "documents": [{"verdictDateTime": "2024-05-14T09:30:00.000"}],
    }
    (tmp_path / "cases_1.json").write_text(
        json.dumps([case], ensure_ascii=False), encoding="utf-8"
    )
    return tmp_path


@pytest.mark.parametrize(
    "argv_for",
    [
        lambda cache, out: ["-d", str(cache), "output", "bib", "-o", str(out)],
        lambda cache, out: ["output", "bib", "-d", str(cache), "-o", str(out)],
        lambda cache, out: ["output", "bib", "--directory", str(cache), "-o", str(out)],
        lambda cache, out: [f"--directory={cache}", "output", "bib", "-o", str(out)],
        lambda cache, out: [f"-d{cache}", "output", "bib", "-o", str(out)],
    ],
    ids=["before-command", "after-command", "long-after", "long-eq-before", "attached"],
)
def test_directory_option_reaches_the_command(cache, tmp_path, monkeypatch, argv_for):
    """Both documented call forms must convert the cache named by -d."""
    output = tmp_path / "out.bib"
    monkeypatch.setattr(sys, "argv", ["domdb", *argv_for(cache, output)])

    main()  # exits 1 if the cache named by -d is not used

    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert "@article" in text
    assert "B-1234/2024" in text


def test_directory_option_used_by_query(cache, monkeypatch, capsys):
    """``-d`` must also reach the query subcommands, in either position."""
    for argv in (
        ["domdb", "-d", str(cache), "query", "count"],
        ["domdb", "query", "count", "-d", str(cache)],
    ):
        monkeypatch.setattr(sys, "argv", argv)
        main()
        assert capsys.readouterr().out.strip().endswith("1")


def test_normalize_argv_rewrites_to_trailing_option():
    assert normalize_argv(["-d", "/tmp/x", "output", "bib"]) == [
        "output",
        "bib",
        "--directory=/tmp/x",
    ]
    assert normalize_argv(["output", "bib", "--directory=/tmp/x"]) == [
        "output",
        "bib",
        "--directory=/tmp/x",
    ]
    # No -d at all: argv untouched.
    assert normalize_argv(["query", "list", "-n", "5"]) == ["query", "list", "-n", "5"]
    # A trailing -d without a value is left for argparse to reject.
    assert normalize_argv(["output", "bib", "-d"]) == ["output", "bib", "-d"]
