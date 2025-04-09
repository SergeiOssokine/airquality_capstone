import logging
from dataclasses import dataclass

from prefect.exceptions import MissingContextError
from prefect.logging import get_logger, get_run_logger


def fetch_logger():
    try:
        logger = get_run_logger()
    except MissingContextError:
        logging.basicConfig()
        logger = get_logger()
        logger.setLevel("INFO")
    return logger


@dataclass
class ProjectParams:
    bucket_name: str
    dwh: str
    project_id: str
