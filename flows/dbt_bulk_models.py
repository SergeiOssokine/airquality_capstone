from prefect import flow
from prefect_dbt import PrefectDbtRunner, PrefectDbtSettings


@flow
def run_dbt():
    PrefectDbtRunner(
        settings=PrefectDbtSettings(
            project_dir="../dbt/airquality",
            profiles_dir="../dbt/airquality",
        )
    ).invoke(["build"])


if __name__ == "__main__":
    run_dbt()
