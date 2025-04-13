resource "google_storage_bucket" "datalake_bucket" {
  name     = var.datalake_bucket_name
  location = var.location

  # Allow bucket destruction even when it's not empty
  # Important for cleanup
  force_destroy = true
}
