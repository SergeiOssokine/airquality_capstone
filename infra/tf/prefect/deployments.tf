locals {
  repository_url = "https://github.com/SergeiOssokine/airquality_capstone.git"
  branch         = "main"
}

resource "prefect_flow" "prepare_location_data_flow" {
  name = "prepare-location-data-flow"
}

resource "prefect_flow" "airquality_analysis_flow" {
  name = "airquality-analysis-flow"
}

resource "prefect_deployment" "prepare_location_data" {
  name            = "prepare-location-data"
  flow_id         = prefect_flow.prepare_location_data_flow.id
  work_pool_name  = prefect_work_pool.airquality_gcp.name
  work_queue_name = "default"
  entrypoint      = "flows/sensors_per_location.py:sensors_per_location"

  parameters = jsonencode({})
  job_variables = jsonencode({
    env = {
      DATALAKE_BUCKET = "${var.datalake_bucket_name}",
      PROJECT_ID      = "${var.gcp_project_name}",
      DWH_NAME        = "${var.data_warehouse_name}"
    }
  })
  paused = true
  pull_steps = [{
    type       = "git_clone"
    repository = "${local.repository_url}"
    branch     = "${local.branch}"
  }]
}

resource "prefect_deployment" "air_quality_analysis" {
  name            = "airquality-analysis"
  flow_id         = prefect_flow.airquality_analysis_flow.id
  work_pool_name  = prefect_work_pool.airquality_gcp.name
  work_queue_name = "default"
  entrypoint      = "flows/dbt_location_analysis.py:air_quality_analysis"

  parameters = jsonencode({})
  job_variables = jsonencode({
    env = {
      DATALAKE_BUCKET = "${var.datalake_bucket_name}",
      PROJECT_ID      = "${var.gcp_project_name}",
      DWH_NAME        = "${var.data_warehouse_name}"
    }
  })
  paused = true
  pull_steps = [{
    type       = "git_clone"
    repository = "${local.repository_url}"
    branch     = "${local.branch}"
  }]
}
