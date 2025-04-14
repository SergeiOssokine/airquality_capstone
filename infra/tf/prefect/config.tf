# We create this block so we can pass information to the dbt_profiles.yml
# dynamically
locals {
  config_values={
    project_name = var.gcp_project_name
    data_warehouse_name = var.data_warehouse_name
    datalake_bucket_name = var.datalake_bucket_name
    location = var.gcp_location
  }
}
resource "prefect_block" "gcp_config" {
  name            = "gcp-config" # Choose a descriptive name
  type_slug = "json"                 # Specify the JSON block type

  # The JSON block expects data in the format: {"value": <your_json_object>}
  # We use jsonencode to create the JSON string representation.
  data = jsonencode({
    value = local.config_values
  })

  # Optional: Connect to a specific workspace if not using the default
  # workspace_id = prefect_workspace.my_workspace.id
}