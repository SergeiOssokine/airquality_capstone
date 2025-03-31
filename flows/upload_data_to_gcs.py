import logging
import os
from typing import List

from prefect_gcp import GcpCredentials
from rich.logging import RichHandler
from rich.traceback import install
from prefect.logging import get_run_logger

# Sets up the logger to work with rich
logger = logging.getLogger(__name__)
logger.addHandler(RichHandler(rich_tracebacks=True, markup=True))
logger.setLevel("INFO")
# Setup rich to get nice tracebacks
install()


def upload_many_files(bucket_name: str, dataset_prefix: str, filenames: List[str]):
    """Upload every file in a list to a bucket, concurrently in a process pool.

    Each blob name is derived from the filename, not including the
    `source_directory` parameter. For complete control of the blob name for each
    file (and other aspects of individual blob metadata), use
    transfer_manager.upload_many() instead.
    """

    storage_client = GcpCredentials.load(
        "airquality-gcp-credentials"
    ).get_cloud_storage_client()
    bucket = storage_client.bucket(bucket_name)
    for fname in filenames:
        source_name = os.path.basename(fname)
        destination_name = f"{dataset_prefix}/{source_name}"
        logger.info(f"Uploading {fname} to {destination_name}")
        blob = bucket.blob(destination_name)
        blob.upload_from_filename(
            fname,
        )
        logger.info("Done")


def create_table_in_dwh(
    project_id: str = None, dwh: str = None, files_path: str = None, name: str = None
):
    logger = get_run_logger()

    logger.info(f"Creating raw {name} table")
    # Construct a BigQuery client object.
    client = GcpCredentials.load("airquality-gcp-credentials").get_bigquery_client(
        location="EU"
    )
    query = f"""
LOAD DATA OVERWRITE `{project_id}.{dwh}.{name}`
FROM FILES (
  format = 'PARQUET',
  uris = ['{files_path}/*.parquet']
);
"""
    logger.info(query)
    client.query_and_wait(query)
