import glob
import json
from collections.abc import Iterator
from pathlib import Path

from loguru import logger
from pydantic import ValidationError

from ..model import ModelItem


def iter_cached_cases(directory: str) -> Iterator[tuple[ModelItem, str]]:
    """Yield (case, source_json_path) from all JSON files in the cache directory."""
    pattern = str(Path(directory) / "*.json")
    for path in sorted(glob.glob(pattern)):
        with open(path, encoding="utf-8") as handle:
            cases_data = json.load(handle)
        for case_data in cases_data:
            try:
                case = ModelItem.model_validate(case_data)
            except ValidationError as exc:
                logger.debug(f"Skipping invalid case in {path}: {exc}")
                continue
            if case.id:
                yield case, path