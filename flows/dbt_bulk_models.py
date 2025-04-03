from prefect import flow
from prefect_dbt import PrefectDbtRunner, PrefectDbtSettings


@flow
def build_sensors_per_location(flag):
    PrefectDbtRunner(
        settings=PrefectDbtSettings(
            project_dir="../dbt/airquality",
            profiles_dir="../dbt/airquality",
        )
    ).invoke(["build"])


if __name__ == "__main__":
    build_sensors_per_location(True)
