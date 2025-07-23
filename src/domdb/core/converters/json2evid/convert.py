import glob
import json
import os
import uuid
from typing import Optional
import logging
import base64
import io
import yaml
from bs4 import BeautifulSoup
import pdfplumber
from pydantic import ValidationError

from .utils import create_info_yml, create_label_tex
from ....core.exceptions import EvidConversionError
from ...model import ModelItem

logger = logging.getLogger(__name__)


def create_evid_dir(case: ModelItem, base_output: str) -> Optional[str]:
    """Create EVID directory with case.json, info.yml, label.tex, and extracted text files."""
    case_id = case.id
    if not case_id:
        raise EvidConversionError("Case missing 'id'")

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
    info_path = os.path.join(dir_path, "info.yml")
    with open(info_path, "w", encoding="utf-8") as f:
        yaml.dump(create_info_yml(case), f, default_flow_style=False)

    # Save label.tex
    label_path = os.path.join(dir_path, "label.tex")
    with open(label_path, "w", encoding="utf-8") as f:
        f.write(create_label_tex(case))

    # Extract plain text from documents
    for doc in case.documents:
        text = None
        if doc.contentHtml:
            soup = BeautifulSoup(doc.contentHtml, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
        elif doc.contentPdf:
            try:
                pdf_bytes = base64.b64decode(doc.contentPdf)
                with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                    text_pages = [page.extract_text() for page in pdf.pages if page.extract_text()]
                    text = '\n\n'.join(text_pages)
            except Exception as e:
                logger.warning(f"Failed to extract text from PDF for doc {doc.id}: {e}")

        if text:
            text_path = os.path.join(dir_path, f"verdict_text_{doc.id}.txt")
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(text)

    logger.info(f"Created EVID directory: {dir_path}")
    return dir_path


def convert_json_to_evid(directory: str, output: str, number: Optional[int] = None) -> int:
    """Convert JSON case files to EVID directory structure."""
    json_files = glob.glob(f"{directory}/*.json")
    if not json_files:
        raise EvidConversionError(f"No JSON files found in {directory}")

    count = 0
    for file_path in json_files:
        logger.info(f"Processing file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            cases_data = json.load(f)
            for case_data in cases_data:
                try:
                    case = ModelItem.model_validate(case_data)
                except ValidationError as e:
                    logger.error(f"Invalid case data: {str(e)}")
                    continue
                if number and count >= number:
                    break
                if create_evid_dir(case, output) is not None:
                    count += 1

    logger.info(f"Converted {count} cases to EVID in {output}")
    return count
