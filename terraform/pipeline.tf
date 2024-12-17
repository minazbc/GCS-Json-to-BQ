# dataflow files bucket
resource "google_storage_bucket" "df_bucket_files" {
    name = "${var.project_id}_dataflow_files"
    location = var.region
    uniform_bucket_level_access = true
}

# dataflow archive bucket
resource "google_storage_bucket" "df_bucket_archive" {
    name = "${var.project_id}_dataflow_archive"
    location = var.region
    uniform_bucket_level_access = true
}

# dataflow temp bucket
resource "google_storage_bucket" "df_bucket_temp" {
    name = "${var.project_id}_dataflow_temp"
    location = var.region
    uniform_bucket_level_access = true
}

# source assets bucket (dataflow template, cloud functions code)
resource "google_storage_bucket" "bucket_assets" {
    name = "${var.project_id}_assets"
    location = var.region
}

# upload assets
resource "google_storage_bucket_object" "dataflow_template" {
    name = "templates/${basename(var.dataflow_template_path)}"
    bucket = google_storage_bucket.bucket_assets.name
    source = var.dataflow_template_path
    content_type = "application/json"
}

resource "google_storage_bucket_object" "cloud_functions" {
    name = "${basename(var.cloud_functions_path)}"
    bucket = google_storage_bucket.bucket_assets.name
    source = var.cloud_functions_path
}

# pubsub
resource "google_pubsub_topic" "dataflow_pipeline_done" {
    name = "dataflow-pipeline-done"
}

resource "google_pubsub_subscription" "dataflow_pipeline_done_sub" {
    name = "dataflow-pipeline-done-sub"
    topic = google_pubsub_topic.dataflow_pipeline_done.id
}

# cloud function (gen2)
resource "google_cloudfunctions2_function" "archive_json_files" {
    name = "archive-json-files"
    location = var.region

    build_config {
        runtime = "python39"
        entry_point = "run"
        source {
            storage_source {
                bucket = google_storage_bucket.bucket_assets.name
                object = google_storage_bucket_object.cloud_functions.name
            }
        }
    }
    event_trigger {
        trigger_region = var.region
        event_type = "google.cloud.pubsub.topic.v1.messagePublished"
        pubsub_topic   = google_pubsub_topic.dataflow_pipeline_done.id
    }
}

# deploy dataflow pipeline from template
resource "google_data_pipeline_pipeline" "dataflow_pipeline" {
    name = "cloud-storage-json-files-to-bigquery"
    display_name = "Cloud Storage JSON files to BigQuery"
    type = "PIPELINE_TYPE_BATCH"
    state = "STATE_ACTIVE"
    region = var.region

    workload {
        dataflow_launch_template_request {
            location = var.region
            project_id = var.project_id
            gcs_path = "gs://${google_storage_bucket.bucket_assets.name}/${google_storage_bucket_object.dataflow_template.name}"
        }
    }
    schedule_info {
        schedule = "0 7 * * *"
        time_zone = "Etc/UTC"
  }
}

