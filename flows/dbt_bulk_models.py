from prefect import flow
from prefect_dbt import PrefectDbtRunner, PrefectDbtSettings
import os

pth = os.path.dirname(__file__)


@flow
def build_sensors_per_location(flag):
    PrefectDbtRunner(
        settings=PrefectDbtSettings(
            project_dir=os.path.join(pth, "../dbt/airquality"),
            profiles_dir=os.path.join("../dbt/airquality"),
        )
    ).invoke(["build"])


if __name__ == "__main__":
    build_sensors_per_location(True)
