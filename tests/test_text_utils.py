import base64

import domdb.core.converters.text_utils as text_utils
from domdb.core.converters.text_utils import (
    extract_case_page_texts,
    extract_case_text,
)
from domdb.core.model import ModelItem


def _case(documents):
    return ModelItem.model_validate({"id": "x", "documents": documents})


def test_extract_html_text_strips_tags():
    case = _case([{"contentHtml": "<p>Hej <b>verden</b></p><p>krisecenter</p>"}])
    text = extract_case_text(case)
    assert "Hej" in text
    assert "verden" in text
    assert "krisecenter" in text
    assert "<p>" not in text


def test_extract_page_texts_one_entry_per_html_doc():
    case = _case(
        [
            {"contentHtml": "<p>doc one</p>"},
            {"contentHtml": "<p>doc two</p>"},
        ]
    )
    pages = extract_case_page_texts(case)
    assert len(pages) == 2
    assert "doc one" in pages[0]
    assert "doc two" in pages[1]


def test_extract_handles_no_documents():
    case = _case([])
    assert extract_case_text(case) == ""


def test_extract_skips_bad_pdf_gracefully():
    # Invalid base64 / non-PDF content should be logged and skipped, not raise.
    case = _case([{"contentPdf": "bm90LWEtcGRm"}])  # base64 for "not-a-pdf"
    assert extract_case_text(case) == ""


def test_extract_skips_scanned_pdf(monkeypatch):
    class FakePage:
        def extract_text(self):
            return None

    class FakePdf:
        pages = [FakePage(), FakePage(), FakePage()]

    class FakePdfContext:
        def __enter__(self):
            return FakePdf()

        def __exit__(self, *args):
            pass

    warnings: list[str] = []

    monkeypatch.setattr(text_utils.pdfplumber, "open", lambda _: FakePdfContext())
    monkeypatch.setattr(
        text_utils.logger, "warning", lambda msg: warnings.append(str(msg))
    )

    pdf_b64 = base64.b64encode(b"%PDF-1.4 scanned").decode()
    case = _case([{"contentPdf": pdf_b64, "id": "scan-1"}])

    pages = extract_case_page_texts(case)

    assert pages == []
    assert any("scanned" in w.lower() for w in warnings)
