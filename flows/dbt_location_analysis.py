import os

from prefect import flow, task
from prefect_dbt import PrefectDbtRunner
from prefect_gcp import GcpCredentials

from src.bulk_process import BulkProcessor
from src.utils import ProjectParams, fetch_logger

pth = os.path.dirname(__file__)


@task(
    description="Download sensor measurements for a given location and year and then upload them to the datalake"
)
def get_sensor_data(location: str, year: int, params: ProjectParams):
    proc = BulkProcessor(location, params.bucket_name, params.dwh, params.project_id)
    return proc.process_location(year)


@task(description="Create the raw data table from the parquet files")
def create_raw_data_table(
    raw_file_path, params: ProjectParams, table: str = "sensors_data"
):
    logger = fetch_logger()

    client = GcpCredentials.load("airquality-gcp-credentials").get_bigquery_client(
        location="EU"
    )
    query = f"""
LOAD DATA OVERWRITE {params.dwh}.{table}
FROM FILES (
format = 'PARQUET',
uris = ['{raw_file_path}']);
"""
    logger.info(query)
    client.query_and_wait(query)


@flow(
    description="Set up all the raw sensor measurements in BigQuery for further analysis"
)
def setup_sensor_data_for_analysis(
    location: str = "Berlin", year: int = 2024, params: ProjectParams = None
):
    raw_file_path = get_sensor_data(location, year, params)
    create_raw_data_table(raw_file_path, params)


@flow(description="Run the dbt models to perform air quality analysis")
def build_air_quality_analysis():
    logger = fetch_logger()
    dbt_path = os.path.abspath(os.path.join(pth, "../dbt/airquality"))
    logger.info(f"The dbt_path is {dbt_path}")
    # Workaround for https://github.com/PrefectHQ/prefect/issues/17555
    os.environ["DBT_PROJECT_DIR"] = dbt_path
    os.environ["DBT_PROFILES_DIR"] = dbt_path
    runner = PrefectDbtRunner()

    # First parse and compile to generate manifest
    runner.invoke(["parse"])
    runner.invoke(["compile"])
    # Then build
    runner.invoke(["run", "--select", "tag:batch_analysis"])


@flow(description="Perform air quality analysis")
def air_quality_analysis():
    bucket_name = os.getenv("DATALAKE_BUCKET")
    project_id = os.getenv("PROJECT_ID")
    dwh = os.getenv("DWH_NAME")
    params = ProjectParams(bucket_name, dwh, project_id)
    setup_sensor_data_for_analysis(params=params)
    build_air_quality_analysis()


if __name__ == "__main__":
    air_quality_analysis()
