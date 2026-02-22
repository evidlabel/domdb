from typing import Optional
import glob
import json
import multiprocessing
from loguru import logger
from pydantic import ValidationError
from .dir_creation import create_evid_dir
from ....core.exceptions import EvidConversionError
from ...model import ModelItem


def process_case(args):
    """Worker function for parallel processing."""
    case, output_dir = args
    return create_evid_dir(case, output_dir) is not None  # Return True if successful


def convert_json_to_evid(
    directory: str, output: str, number: Optional[int] = None
) -> int:
    """Convert JSON case files to EVID directory structure with parallel processing."""
    logger.info(f"Loading verdicts from directory: {directory} for EVID conversion")
    json_files = glob.glob(f"{directory}/*.json")
    logger.info(f"Found {len(json_files)} JSON files")
    if not json_files:
        raise EvidConversionError(f"No JSON files found in {directory}")

    cases = []  # Collect cases first
    total_raw = 0
    for file_path in json_files:
        logger.info(f"Processing file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            cases_data = json.load(f)
            total_raw += len(cases_data)
            logger.info(f"Loaded {len(cases_data)} raw cases from {file_path}")
            for case_data in cases_data:
                try:
                    case = ModelItem.model_validate(case_data)
                    if case.id:
                        cases.append(case)
                        if number and len(cases) >= number:
                            break  # Stop collecting if limit reached
                except ValidationError as e:
                    logger.error(f"Invalid case data: {str(e)}")
                    continue

    logger.info(
        f"Total raw cases loaded: {total_raw}, valid cases collected: {len(cases)}"
    )
    if not cases:
        logger.info("No valid cases to process")
        return 0

    # Limit to number if specified
    cases_to_process = cases[:number] if number else cases
    logger.info(f"Processing {len(cases_to_process)} cases to EVID in {output}")

    with multiprocessing.Pool() as pool:  # Use multiprocessing for parallelization
        results = pool.map(process_case, [(case, output) for case in cases_to_process])
        count = sum(1 for result in results if result)  # Count successful creations

    logger.info(f"Converted {count} cases to EVID in {output}")
    return count
