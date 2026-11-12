"""Unicode-aware folding shared by the index writer and the query builders.

SQLite's built-in ``LIKE`` and ``lower()`` only fold ASCII, so ``Østre``
never matched ``østre`` once an index existed (the JSON-scan path folded both
sides in Python and did match). Every value written to a ``*_folded`` index
column and every needle bound into a query goes through :func:`fold_text`, so
the comparison is a plain case-sensitive comparison of already-folded text.
"""

import unicodedata


def fold_text(value: str | None) -> str:
    """Return ``value`` normalised (NFC) and case-folded for comparison."""
    if not value:
        return ""
    return unicodedata.normalize("NFC", value).casefold() or ""
