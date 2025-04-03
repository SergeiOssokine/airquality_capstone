import os
from prefect import flow
from get_sensors_per_location import get_sensors_per_location
from dbt_bulk_models import build_sensors_per_location


@flow
def sensors_per_location():
    bucket_name = os.getenv("DATALAKE_BUCKET")
    project_id = os.getenv("PROJECT_ID")
    dwh = os.getenv("DWH_NAME")

    flag = get_sensors_per_location(project_id, dwh, bucket_name)
    build_sensors_per_location(flag)


if __name__ == "__main__":
    sensors_per_location()
