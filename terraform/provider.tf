provider "google" {
    credentials = file(var.service_account_key_path)
    project = var.project_id
    region = var.region
}