variable "gcp_credentials" {
  type        = string
  description = "The path to the GCP service credentials"
}
variable "openaq_credentials" {
  type        = string
  description = "The path the OpenAQ API key"
}
variable "account_id" {
  type        = string
  description = "The account ID for Prefect Cloud account"
  sensitive   = true
}
variable "workspace_id" {
  type        = string
  description = "The workspace ID for the project"
  sensitive   = true
}
variable "docker_image" {
  type        = string
  description = "The image to use for running Prefect jobs in Google CloudRun"

}
variable "datalake_bucket_name" {
  type        = string
  description = "The name of the datalake bucket"
}
variable "data_warehouse_name" {
  type        = string
  description = "The name of the data warehouse"
}
variable "gcp_project_name" {
  type        = string
  description = "The name of the GCP project"
}
variable "gcp_region" {
  type        = string
  description = "The region in which all the GCP resources are"
}
variable "gcp_location" {
  type        = string
  description = "The location of the GCP project (e.g EU, US)"
}
