terraform {
  required_providers {
    prefect = {
      source = "prefecthq/prefect"
    }
  }
}

# By default, the provider points to Prefect Cloud
# and you can pass in your API key and account ID
# via variables or static inputs.
provider "prefect" {
  account_id = var.account_id
  workspace_id = var.workspace_id
}
