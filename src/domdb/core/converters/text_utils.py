"""Shared helpers for extracting plain text from case documents.

Used by the EVID converter (per-page Typst body) and the Markdown converter
(full-text keyword search). HTML via BeautifulSoup; PDF via base64 + pdfplumber.

Compared to the old inline json2evid logic, scanned (image-only) PDFs are now
detected from a short page sample and skipped instead of iterating every page.
"""

import base64
import io

import pdfplumber
from bs4 import BeautifulSoup
from loguru import logger

from ..model import ModelItem

# Scanned (image-only) PDFs in the corpus have no extractable text yet make
# pdfplumber run for many minutes and consume gigabytes of RAM. We detect them
# by sampling the first few pages: if those yield no text, the PDF is treated as
# scanned and skipped (logged — no silent skip) before processing every page.
SCAN_SAMPLE_PAGES = 3


def extract_case_page_texts(case: ModelItem) -> list[str]:
    """Extract plain text from a case's documents as a list of page texts.

    For HTML documents a single entry holds the whole document's text; for PDF
    documents each page contributes one entry. Scanned (image-only) PDFs yield no
    text on their first pages and are skipped (logged). Failures to read a PDF
    are logged and skipped.
    """
    page_texts: list[str] = []
    for doc in case.documents or []:
        if doc.contentHtml:
            soup = BeautifulSoup(doc.contentHtml, "html.parser")
            page_texts.append(soup.get_text(separator="\n", strip=True))
        elif doc.contentPdf:
            doc_id = doc.id or "unknown"
            try:
                pdf_bytes = base64.b64decode(doc.contentPdf)
                with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                    sample = "".join(
                        page.extract_text() or ""
                        for page in pdf.pages[:SCAN_SAMPLE_PAGES]
                    )
                    if not sample.strip():
                        logger.warning(
                            f"Skipping scanned (no extractable text) PDF for doc {doc_id}"
                        )
                        continue
                    page_texts.extend(
                        page.extract_text() or "" for page in pdf.pages
                    )
            except Exception as e:
                logger.warning(
                    f"Failed to extract text from PDF for doc {doc_id}: {e}"
                )
    return page_texts


def extract_case_text(case: ModelItem) -> str:
    """Return the full plain text of a case (all documents joined)."""
    return "\n".join(extract_case_page_texts(case))
