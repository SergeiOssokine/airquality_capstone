variable "project_id" {
  type = string
  description = "The ID of the project"
}
variable "region" {
    type = string
    description = "The region where to store data and perform computation"
}
variable "location" {
  type = string
  description = "Location of the datalake and DWH"
}
variable "datalake_bucket" {
  type = string
  description = "Name of the bucket for the datalake"
}
variable "dwh_name" {
  type = string
  description = "The name of the BigQuery dataset to create"
}
variable "credentials" {
    type = string
    description = "My Credentials"
}