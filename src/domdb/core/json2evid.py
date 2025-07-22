import glob
import json
import os
import uuid
from typing import Optional
from datetime import datetime
import yaml
import logging
from pydantic import ValidationError
from .model import ModelItem

logger = logging.getLogger(__name__)


class EvidConversionError(Exception):
    """Custom exception for EVID conversion errors."""
    pass


def extract_verdict_date(case: ModelItem) -> Optional[str]:
    """Extract verdict date from case documents."""
    for doc in case.documents:
        if doc.verdictDateTime and isinstance(doc.verdictDateTime, str):
            try:
                return datetime.strptime(
                    doc.verdictDateTime, "%Y-%m-%dT%H:%M:%S"
                ).strftime("%Y-%m-%d")
            except ValueError:
                continue
    return None


def create_info_yml(case: ModelItem) -> dict:
    """Create info.yml content from case."""
    verdict_date = extract_verdict_date(case) or "Unknown"
    profession = case.profession.displayText or "Unknown"
    instance = case.instance.displayText or "Unknown"
    case_type = case.caseType.displayText or "Unknown"
    court = f"{profession}, {instance}, {case_type}"
    subjects = ", ".join(
        s.displayText for s in case.caseSubjects
    ) or "Unknown"
    return {
        "id": case.id,
        "headline": case.headline or "No Title",
        "court": court,
        "date": verdict_date,
        "subjects": subjects,
        "case_number": case.courtCaseNumber or "Unknown",
        "url": f"https://domsdatabasen.dk/#sag/{case.id or 'unknown'}",
    }


def create_label_tex(case: ModelItem) -> str:
    """Create label.tex content for LaTeX citation."""
    headline = case.headline or "No Title"
    case_number = case.courtCaseNumber or "Unknown"
    verdict_date = extract_verdict_date(case) or "Unknown"
    return f"""\\label{{case-{case.id or 'unknown'}}}

\\textbf{{{headline}}}\\\\
Case Number: {case_number}\\\\
Date: {verdict_date}
"""


def create_evid_dir(case: ModelItem, base_output: str) -> Optional[str]:
    """Create EVID directory with case.json, info.yml, and label.tex."""
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
