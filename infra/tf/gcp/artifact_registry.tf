resource "google_artifact_registry_repository" "prefect-images" {
  location = var.gcp_region
  repository_id = "prefect-images"
  description = "Contains images used for prefect CloudRun jobs"
  format = "DOCKER"
}