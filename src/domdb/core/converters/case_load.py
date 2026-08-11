"""Shared case loading for converter modules."""

import glob
import json
from typing import Type

from loguru import logger
from pydantic import ValidationError

from ..exceptions import ConversionError
from ..model import ModelItem


def load_cases(
    directory: str,
    number: int | None = None,
    *,
    error_cls: Type[Exception] = ConversionError,
) -> list[ModelItem]:
    """Glob directory/*.json → validate ModelItem → optional cap.

    Raises error_cls (default ConversionError; use EvidConversionError for evid)
    if no JSON files are found. Skips invalid cases and cases without id.
    """
    logger.info(f"Loading verdicts from directory: {directory}")
    json_files = glob.glob(f"{directory}/*.json")
    logger.info(f"Found {len(json_files)} JSON files")
    if not json_files:
        raise error_cls(f"No JSON files found in {directory}")

    cases: list[ModelItem] = []
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
                    if not case.id:
                        logger.error("Skipping case without id")
                        continue
                    cases.append(case)
                    if number is not None and len(cases) >= number:
                        logger.info(
                            f"Total raw cases loaded: {total_raw}, "
                            f"valid cases collected: {len(cases)}"
                        )
                        return cases
                except ValidationError as e:
                    logger.error(f"Invalid case data: {e!s}")
                    continue

    logger.info(
        f"Total raw cases loaded: {total_raw}, valid cases collected: {len(cases)}"
    )
    return cases
