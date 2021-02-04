variable "deployment" {}
variable "project_id" {}

provider "google" {
  project = var.project_id
  region  = "us-central1"
  zone    = "us-central1-c"
}

locals{
    DATASET = replace(format("%sdataset", var.deployment), "-", "_")
    TABLE = replace(format("%stable", var.deployment), "-", "_")
}

resource "google_bigquery_dataset" "default" {
  dataset_id = local.DATASET
  labels = {
    goog-dm = var.deployment
  }
}

resource "google_bigquery_table" "default" {
  dataset_id = google_bigquery_dataset.default.dataset_id
  table_id   = local.TABLE
  labels = {
    goog-dm = var.deployment
  }
}

