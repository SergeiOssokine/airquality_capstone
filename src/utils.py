from prefect.exceptions import MissingContextError
from prefect.logging import get_logger, get_run_logger


import logging


def fetch_logger():
    try:
        logger = get_run_logger()
    except MissingContextError:
        logging.basicConfig()
        logger = get_logger()
        logger.setLevel("INFO")
    return logger


class ProjectParams:
    bucket_name: str
    dwh: str
    project_id: str
