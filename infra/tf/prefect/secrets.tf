resource "prefect_block" "gcp_credentials_key" {
  name = "airquality-gcp-credentials"
  # prefect block type ls
  type_slug = "gcp-credentials"
  data = jsonencode({
  "service_account_info" = jsondecode(file(var.gcp_credentials_path)) })
}
resource "prefect_block" "openaq_api_key" {
  name      = "openaq-api-key"
  type_slug = "secret"
  data      = file(var.openaq_credentials_path)
}
