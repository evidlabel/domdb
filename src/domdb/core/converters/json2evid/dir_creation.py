from typing import Optional
import json
import os
import uuid
import base64
import io
import yaml
from bs4 import BeautifulSoup
import pdfplumber
from loguru import logger
from .info_utils import create_info_yml
from ...model import ModelItem
from evid.core.label_setup import clean_text_for_typst
from evid.core.models import InfoModel

TYPST_TEMPLATE = """#import \"@local/labtyp:0.1.0\": lablist, lab, mset

#mset(values: (
  title: \"{title}\",
  date: \"{date}\"))

= {title}

{body}

= List of Labels
#lablist()
"""


def create_evid_dir(case: ModelItem, base_output: str) -> Optional[str]:
    """Create EVID directory for a single case."""
    case_id = case.id
    if not case_id:
        logger.error("Case missing 'id'")
        return None

    # Deterministic UUID based on case ID
    ns_uuid = uuid.uuid5(uuid.NAMESPACE_OID, case_id)
    dir_path = os.path.join(base_output, str(ns_uuid))

    if os.path.exists(dir_path):
        logger.info(f"Skipping existing EVID directory: {dir_path}")
        return None

    os.makedirs(dir_path, exist_ok=True)

    # Save case.json
    json_path = os.path.join(dir_path, "case.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(case.model_dump(), f, ensure_ascii=False, indent=2)

    # Save info.yml
    info_dict = create_info_yml(case)
    try:
        validated_info = InfoModel(**info_dict)
        info = validated_info.model_dump()
    except ValueError as e:
        logger.warning(f"Validation error for info: {e}. Using defaults.")
        info = info_dict
    info_path = os.path.join(dir_path, "info.yml")
    with open(info_path, "w", encoding="utf-8") as f:
        yaml.dump(info, f, default_flow_style=False)

    # Collect all page texts from documents
    all_page_texts = []
    for doc in case.documents or []:
        if doc.contentHtml:
            soup = BeautifulSoup(doc.contentHtml, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            all_page_texts.append(text)
        elif doc.contentPdf:
            try:
                pdf_bytes = base64.b64decode(doc.contentPdf)
                with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                    page_texts = [page.extract_text() or "" for page in pdf.pages]
                    all_page_texts.extend(page_texts)
            except Exception as e:
                logger.warning(
                    f"Failed to extract text from PDF for doc {doc.id or 'unknown'}: {e}"
                )

    # Generate body for Typst
    if not all_page_texts:
        body = "#mset(values: (opage: 1))\n== Page 1\nNo content available\n\n"
    else:
        body = "".join(
            f"#mset(values: (opage: {i + 1}))\n== Page {i + 1}\n{clean_text_for_typst(page_text)}\n\n"
            for i, page_text in enumerate(all_page_texts)
        )

    # Prepare date and name
    date = info.get("dates", "DATE")
    if isinstance(date, list):
        date = date[0] if date else "DATE"
    date = str(date)
    name = info.get("label", "NAME")
    title = name.replace("_", " ")

    # Generate label.typ using Typst template
    label_content = TYPST_TEMPLATE.format(title=title, date=date, body=body)
    label_path = os.path.join(dir_path, "label.typ")
    with open(label_path, "w", encoding="utf-8") as f:
        f.write(label_content)

    logger.info(f"Created EVID directory: {dir_path}")
    return dir_path
