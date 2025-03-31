from prefect import flow, task
from typing import List
from prefect.logging import get_run_logger
import tempfile
from get_sensors_data import get_sensor_location_info
from get_places_data import get_location_bounding_boxes

from upload_data_to_gcs import upload_many_files, create_table_in_dwh
import os


@task
def get_places_data(staging_area: str):
    logger = get_run_logger()
    logger.info("Downloading location data")
    location_files = get_location_bounding_boxes(staging_area)
    return location_files


@task
def get_sensors_data(staging_area):
    logger = get_run_logger()
    logger.info("Downloading all sensor data")
    sensor_files = get_sensor_location_info(staging_area)
    logger.info(f"Sensor files is {sensor_files}")
    return sensor_files


@task
def upload_places_data(filenames: List[str], bucket_name: str):
    logger = get_run_logger()
    logger.info("Uploading places data to GCS")
    logger.info(f"The file names to upload are {filenames}")
    upload_many_files(bucket_name, "places_data", filenames)
    return f"gs://{bucket_name}/places_data"


@task
def upload_sensors_data(filenames: List[str], bucket_name: str):
    logger = get_run_logger()
    logger.info("Uploading all sensor data to GCS")
    upload_many_files(bucket_name, "sensors_data", filenames)
    return f"gs://{bucket_name}/sensors_data"


@task
def create_sensors_table(project_id=None, dwh=None, sensors_path: str = None):
    create_table_in_dwh(
        project_id=project_id, dwh=dwh, files_path=sensors_path, name="sensors"
    )


@task
def create_places_table(project_id=None, dwh=None, places_path: str = None):
    create_table_in_dwh(
        project_id=project_id, dwh=dwh, files_path=places_path, name="places"
    )


@flow
def get_sensors_per_location(
    project_id: str, data_warehouse: str, datalake_bucket: str
):
    logger = get_run_logger()
    logger.info("Assembling sensor information")
    with tempfile.TemporaryDirectory() as staging_area:
        places_files = get_places_data(staging_area)
        sensors_files = get_sensors_data(staging_area)
        places_path = upload_places_data(places_files, datalake_bucket)
        sensors_path = upload_sensors_data(sensors_files, datalake_bucket)
        create_places_table(
            project_id=project_id, dwh=data_warehouse, places_path=places_path
        )
        create_sensors_table(
            project_id=project_id, dwh=data_warehouse, sensors_path=sensors_path
        )

    logger.info("Done")


if __name__ == "__main__":
    bucket_name = os.getenv("DATALAKE_BUCKET")
    project_id = os.getenv("PROJECT_ID")
    dwh = os.getenv("DWH_NAME")
    get_sensors_per_location(project_id, dwh, bucket_name)
