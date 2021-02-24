provider "google" {
  project = var.project_id
  region  = "{REGION}"
  zone    = "{ZONE}"
}

variable "deployment" {
  type        = string
  description = "Deployment name used to label the resources created."
  default     = {}

}

variable "project_id" {
  type        = string
  description = "Project id used to create resources in that project."
  default     = {}

}

resource "google_pubsub_topic" "my-topic" {
  name = "{TOPIC_NAME}"
  labels = {
    goog-dm = var.deployment
  }
}

resource "google_pubsub_subscription" "my-subscription" {
  name = "{SUBSCRIPTION_NAME}"
  labels = {
    goog-dm = var.deployment
  }
  topic                      = google_pubsub_topic.my-topic.name
  message_retention_duration = "{MESSAGE_RETENTION_DURATION}"
  retain_acked_messages      = {TRUE,FALSE}
  ack_deadline_seconds       = {ACK_DEADLINE_SECONDS}
  expiration_policy {
    ttl = {TTL}
  }
}
