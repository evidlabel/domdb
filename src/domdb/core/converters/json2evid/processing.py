import multiprocessing
from typing import Optional

from loguru import logger

from .dir_creation import create_evid_dir
from ....core.exceptions import EvidConversionError
from ..case_load import load_cases


def process_case(args):
    """Worker function for parallel processing."""
    case, output_dir = args
    return create_evid_dir(case, output_dir) is not None  # Return True if successful


def convert_json_to_evid(
    directory: str, output: str, number: Optional[int] = None
) -> int:
    """Convert JSON case files to EVID directory structure with parallel processing."""
    cases = load_cases(directory, number, error_cls=EvidConversionError)
    if not cases:
        logger.info("No valid cases to process")
        return 0

    logger.info(f"Processing {len(cases)} cases to EVID in {output}")

    with multiprocessing.Pool() as pool:  # Use multiprocessing for parallelization
        results = pool.map(process_case, [(case, output) for case in cases])
        count = sum(1 for result in results if result)  # Count successful creations

    logger.info(f"Converted {count} cases to EVID in {output}")
    return count
