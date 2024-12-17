variable "project_id" {
    description = "Project ID."
    type = string
}

variable "dataset_id" {
    description = "Dataset ID."
    type = string
}

variable "location" {
    description = "Project location."
    type = string
}

variable "region" {
    description = "Region used in project."
    type = string
}

variable "service_account_key_path" {
    description = "Local path to service account key."
    type = string
}

variable "dataflow_template_path" {
    description = "Dataflow template."
    type = string
}

variable "cloud_functions_path" {
    description = "Source code to deploy cloud functions."
    type = string
}