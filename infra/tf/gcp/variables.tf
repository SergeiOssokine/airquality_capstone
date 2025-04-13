variable "gcp_project_name" {
  type = string
  description = "The name of the project"
}
variable "gcp_region" {
    type = string
    description = "The region where to store data and perform computation"
}
variable "location" {
  type = string
  description = "Location of the datalake and DWH"
}
variable "datalake_bucket_name" {
  type = string
  description = "Name of the bucket for the datalake"
}
variable "data_warehouse_name" {
  type = string
  description = "The name of the BigQuery dataset to create"
}
variable "gcp_credentials" {
    type = string
    description = "Path to the service account GCP credentials json file"
}