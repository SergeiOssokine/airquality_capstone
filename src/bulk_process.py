import glob
import gzip
import os
import tempfile
from multiprocessing.pool import ThreadPool

import boto3
import pandas as pd
from botocore import UNSIGNED
from botocore.config import Config
from prefect_gcp import GcpCredentials

from src.upload_data_to_gcs import upload_many_files
from src.utils import fetch_logger

s3_client = boto3.client("s3", config=Config(signature_version=UNSIGNED))


def _fetch(p):
    local_file_path, object_key, bucket_name = p
    with open(local_file_path, "wb") as data:
        print(f"Downloading {object_key} to {local_file_path}")
        s3_client.download_fileobj(bucket_name, object_key, data)


class BulkProcessor:
    def __init__(
        self,
        location_name: str,
        datalake_bucket: str,
        data_warehouse: str,
        project_id: str,
        dataset_name: str = "sensor_measurements",
    ):
        self.project_bucket = datalake_bucket
        self.data_warehouse = data_warehouse
        self.project_id = project_id
        self.location_name = location_name
        self.dataset_name = dataset_name

    def get_location_list(self):
        logger = fetch_logger()

        logger.info(f"Locating all sensors in {self.location_name}")
        client = GcpCredentials.load("airquality-gcp-credentials").get_bigquery_client(
            location="EU"
        )
        query = f"""
    select location_id
    from {self.project_id}.{self.data_warehouse}.stg_sensors_per_location
    where location_name="{self.location_name}"
    """
        logger.info(query)
        self.locations = client.query_and_wait(query).to_dataframe()["location_id"]

    def _download_data(
        self,
        year: int,
        bucket_name: str = "openaq-data-archive",
        location_path: str = ".",
    ):
        logger = fetch_logger()
        paginator = s3_client.get_paginator("list_objects_v2")
        local_destination_dir = os.path.join(location_path, f"year={year}")
        base_path = "records/csv.gz"
        pool = ThreadPool(8)
        for loc in self.locations:
            logger.info(f"Downloading data for location {loc}")
            prefix = f"{base_path}/locationid={loc}/year={year}"
            pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
            data_paths = []
            for page in pages:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        object_key = obj["Key"]
                        # Skip if the key is just the prefix itself (like an empty folder object)
                        if object_key == prefix:
                            continue
                        # Construct the local file path, preserving the structure relative to the prefix
                        relative_path = os.path.relpath(object_key, prefix)
                        local_file_path = os.path.join(
                            local_destination_dir, relative_path
                        )

                        # Create necessary subdirectories locally if they don't exist
                        local_file_dir = os.path.dirname(local_file_path)
                        if (
                            local_file_dir
                        ):  # Check if dirname is not empty (i.e., not in the root)
                            os.makedirs(local_file_dir, exist_ok=True)

                        data_paths.append([local_file_path, object_key, bucket_name])

            pool.map(_fetch, data_paths)
            logger.info("Done downloading")

    def _load_one_month(self, month: int, year_path: str):
        pth = os.path.join(year_path, f"month={str(month).zfill(2)}")
        day_list = glob.glob(f"{pth}/*.csv.gz")
        monthly_results = []
        for day in day_list:
            with gzip.open(day, "rb") as fp:
                df = pd.read_csv(fp)
                # df["datetime"] = pd.to_datetime(
                #     df["datetime"], utc=True, yearfirst=True, format="ISO8601"
                # )
                monthly_results.append(df)

        if monthly_results:
            monthly_results = pd.concat(monthly_results)
            return monthly_results
        return pd.DataFrame()

    def _process_one_year(self, year: int, location_path: str):
        logger = fetch_logger()
        tmp = []
        year_path = os.path.join(location_path, f"year={year}")
        logger.info(f"Processing all data in {year_path}")
        for month in range(1, 13):
            try:
                tmp.append(self._load_one_month(month, year_path))
            except OSError:
                continue
        combined_data = pd.concat(tmp)
        return combined_data

    def process_location(self, year: int, location_path: str = "."):
        with tempfile.TemporaryDirectory() as location_path:
            self.get_location_list()
            self._download_data(year, location_path=location_path)
            data = self._process_one_year(year, location_path)
            fname = f"data_{self.location_name}_{year}.parquet"
            output_name = os.path.join(location_path, fname)
            data.to_parquet(output_name, index=False, compression="snappy")
            upload_many_files(self.project_bucket, self.dataset_name, [output_name])
            gs_path = f"gs://{self.project_bucket}/{self.dataset_name}/{fname}"
            return gs_path


if __name__ == "__main__":
    year = 2024
    bucket_name = os.getenv("DATALAKE_BUCKET")
    project_id = os.getenv("PROJECT_ID")
    dwh = os.getenv("DWH_NAME")
    proc = BulkProcessor("Berlin", bucket_name, dwh, project_id)
    proc.process_location(year)
