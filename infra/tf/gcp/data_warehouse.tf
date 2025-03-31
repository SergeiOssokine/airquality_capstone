resource "google_bigquery_dataset" "dwh_dataset" {
  dataset_id = var.dwh_name
  location   = var.location
}