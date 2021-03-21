variable "deployment" {}
variable "filter" {}
variable "project_id" {}

resource "google_pubsub_topic" "my-topic" {
  name = var.deployment
  project = var.project_id
}

resource "google_logging_project_sink" "my-sink" {
  name = format("sink-%s", var.deployment)
  destination = format("pubsub.googleapis.com/projects/%s/topics/%s", var.project_id, var.deployment)
  filter = var.filter
  project = var.project_id
}

resource "google_logging_metric" "my-metric" {
  name   = format("metric-%s", var.deployment)
  filter = var.filter
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
  project = var.project_id
}