variable "deployment" {}
variable "filter" {}
variable "project_id" {}

provider "google" {
  project = var.project_id
  region  = "us-central1"
  zone    = "us-central1-c"
}

resource "google_pubsub_topic" "my-topic" {
  name = var.deployment
}

resource "google_logging_project_sink" "my-sink" {
  name = format("sink-%s", var.deployment)
  destination = format("pubsub.googleapis.com/projects/%s/topics/%s", var.project_id, var.deployment)
  filter = var.filter
}

resource "google_logging_metric" "my-metric" {
  name   = format("metric-%s", var.deployment)
  filter = var.filter
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}