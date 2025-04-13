resource "google_bigquery_dataset" "dwh_dataset" {
  dataset_id = var.data_warehouse_name
  location   = var.location
}
