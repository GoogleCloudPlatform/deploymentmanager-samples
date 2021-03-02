provider "google" {
  project = var.project_id
  region  = "us-central1"
  zone    = "us-central1-c"
}

variable "deployment" {
  type        = string
  description = "Deployment name used to label the resources created."

}

variable "project_id" {
  type        = string
  description = "Project id used to create resources in that project."

}

resource "google_pubsub_topic" "my-topic" {
  name = "my-pubsub-topic"
  labels = {
    goog-dm = var.deployment
  }
}

resource "google_pubsub_subscription" "my-subscription" {
  name = "my-pubsub-subscription"
  labels = {
    goog-dm = var.deployment
  }
  topic                      = google_pubsub_topic.my-topic.name
  message_retention_duration = "1200s"
  retain_acked_messages      = true
  ack_deadline_seconds       = 60
  expiration_policy {
    ttl = "86400s"
  }
}
