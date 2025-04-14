import os

from prefect import flow
from prefect.logging import get_run_logger
from prefect_dbt import PrefectDbtRunner


pth = os.path.dirname(__file__)


@flow(description="Combine sensor and geographical location data")
def build_sensors_per_location(flag):
    logger = get_run_logger()
    logger.info(f"I am in {os.getcwd()}")
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
    runner.invoke(["run", "--select", "tag:setup"])


if __name__ == "__main__":
    build_sensors_per_location(True)
