terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">=6.17.0"
    }
  }
}
provider "google" {
  credentials = file(var.gcp_credentials)
  project     = var.gcp_project_name
  region      = var.gcp_region
}
