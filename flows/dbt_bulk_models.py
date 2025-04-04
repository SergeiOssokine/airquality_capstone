from prefect import flow
from prefect_dbt import PrefectDbtRunner, PrefectDbtSettings
import os
from prefect.logging import get_run_logger

pth = os.path.dirname(__file__)


@flow
def build_sensors_per_location(flag):
    logger = get_run_logger()
    logger.info(f"I am in {os.getcwd()}")
    PrefectDbtRunner(
        settings=PrefectDbtSettings(
            project_dir=os.path.join(pth, "../dbt/airquality"),
            profiles_dir=os.path.join(pth, "../dbt/airquality"),
        )
    ).invoke(["build"])


if __name__ == "__main__":
    build_sensors_per_location(True)
