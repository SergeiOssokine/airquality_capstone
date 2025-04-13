
# Inject credentials into the base job template
locals {
    base_job_template = templatefile(
    "base-job-template.json",
    {
      block_document_id = prefect_block.gcp_credentials_key.id
      docker_image = var.docker_image
      region = var.gcp_region
    }
  )
}
# Create the work pool
resource "prefect_work_pool" "airquality_gcp" {
  name              = "airquality-gcp"
  type              = "cloud-run:push"
  concurrency_limit = 2
  base_job_template = jsonencode(jsondecode(local.base_job_template))
}
