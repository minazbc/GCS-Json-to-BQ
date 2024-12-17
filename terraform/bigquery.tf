# dataset creation (dataflow setup)
resource "google_bigquery_dataset" "dataflow_assignment" {
    dataset_id = var.dataset_id
    location = var.location
}

# table creation (dataflow setup)
resource "google_bigquery_table" "dataflow_data" {
    table_id = "dataflow_data"
    dataset_id = google_bigquery_dataset.dataflow_assignment.dataset_id
    project = google_bigquery_dataset.dataflow_assignment.project
    schema = file("${path.module}/table_schema.json")
}