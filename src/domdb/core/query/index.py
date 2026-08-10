import sqlite3
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from ..converters.fields import parse_case_fields
from .loader import iter_cached_cases
from .search import html_body_search_text, metadata_search_text

INDEX_FILENAME = ".domdb-query.sqlite"
SCHEMA_VERSION = 2


@dataclass(frozen=True)
class IndexedCase:
    id: str
    verdict_date: str | None
    headline: str
    author: str
    court: str
    subjects: str
    case_number: str
    metadata_text: str
    body_text: str
    has_pdf: bool
    source_file: str


def index_path(directory: str) -> Path:
    return Path(directory).expanduser() / INDEX_FILENAME


def index_exists(directory: str) -> bool:
    return index_path(directory).is_file()


def _connect(directory: str) -> sqlite3.Connection:
    path = index_path(directory)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY,
            verdict_date TEXT,
            headline TEXT NOT NULL,
            author TEXT NOT NULL,
            court TEXT NOT NULL,
            subjects TEXT NOT NULL,
            case_number TEXT NOT NULL,
            metadata_text TEXT NOT NULL,
            body_text TEXT NOT NULL,
            has_pdf INTEGER NOT NULL,
            source_file TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_cases_verdict_date ON cases(verdict_date);
        """
    )


def build_index(directory: str) -> int:
    """Build or rebuild the metadata index for a cache directory."""
    directory = str(Path(directory).expanduser())
    path = index_path(directory)
    if path.exists():
        path.unlink()

    conn = _connect(directory)
    try:
        _init_schema(conn)
        conn.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?)",
            ("schema_version", str(SCHEMA_VERSION)),
        )

        rows: list[tuple] = []
        seen_ids: set[str] = set()
        for case, source_file in iter_cached_cases(directory):
            if case.id in seen_ids:
                continue
            seen_ids.add(case.id)
            fields = parse_case_fields(case)
            verdict_date = fields["verdict_date"]
            if verdict_date == "Unknown":
                verdict_date = None
            has_pdf = any(doc.contentPdf for doc in case.documents or [])
            rows.append(
                (
                    case.id,
                    verdict_date,
                    case.headline or "",
                    fields["author"],
                    fields["court"],
                    fields["subjects"],
                    fields["case_number"],
                    metadata_search_text(case),
                    html_body_search_text(case),
                    int(has_pdf),
                    source_file,
                )
            )

        conn.executemany(
            """
            INSERT INTO cases (
                id, verdict_date, headline, author, court, subjects,
                case_number, metadata_text, body_text, has_pdf, source_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
        logger.info(f"Indexed {len(rows)} cases at {path}")
        return len(rows)
    finally:
        conn.close()


def fetch_indexed_cases(
    directory: str,
    *,
    from_date: str | None = None,
    to_date: str | None = None,
    court: str | None = None,
    subject: str | None = None,
) -> list[IndexedCase]:
    """Return index rows pre-filtered by date, court, and subject."""
    if not index_exists(directory):
        return []

    clauses: list[str] = []
    params: list[str] = []

    if from_date:
        clauses.append("verdict_date >= ?")
        params.append(from_date)
    if to_date:
        clauses.append("verdict_date <= ?")
        params.append(to_date)
    if court:
        clauses.append("(court LIKE ? OR author LIKE ?)")
        needle = f"%{court.lower()}%"
        params.extend([needle, needle])
    if subject:
        clauses.append("subjects LIKE ?")
        params.append(f"%{subject.lower()}%")

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"""
        SELECT id, verdict_date, headline, author, court, subjects,
               case_number, metadata_text, body_text, has_pdf, source_file
        FROM cases
        {where}
        ORDER BY verdict_date DESC, headline
    """

    conn = _connect(directory)
    try:
        cur = conn.execute(sql, params)
        return [
            IndexedCase(
                id=row["id"],
                verdict_date=row["verdict_date"],
                headline=row["headline"],
                author=row["author"],
                court=row["court"],
                subjects=row["subjects"],
                case_number=row["case_number"],
                metadata_text=row["metadata_text"],
                body_text=row["body_text"],
                has_pdf=bool(row["has_pdf"]),
                source_file=row["source_file"],
            )
            for row in cur.fetchall()
        ]
    finally:
        conn.close()