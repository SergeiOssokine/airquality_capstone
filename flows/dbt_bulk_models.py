from prefect import flow
from prefect_dbt import PrefectDbtRunner, PrefectDbtSettings
import os
from prefect.logging import get_run_logger

pth = os.path.dirname(__file__)


@flow
def build_sensors_per_location(flag):
    logger = get_run_logger()
    logger.info(f"I am in {os.getcwd()}")
    dbt_path = os.path.abspath(os.path.join(pth, "../dbt/airquality"))
    logger.info(f"The dbt_path is {dbt_path}")
    runner = PrefectDbtRunner(
        settings=PrefectDbtSettings(
            project_dir=dbt_path,
            profiles_dir=dbt_path,
        )
    )
    # First parse and compile to generate manifest
    runner.invoke(["parse"])
    runner.invoke(["compile"])
    # Then build
    runner.invoke(["build"])


if __name__ == "__main__":
    build_sensors_per_location(True)
