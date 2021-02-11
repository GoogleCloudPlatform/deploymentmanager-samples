provider "google" {
  project = "{PROJECT_ID}"
  region  = "{REGION}"
  zone    = "{ZONE}"
}

variable "deployment" {
 default={}

}

variable "project_id" {
 default={}

}

resource "google_pubsub_topic" "{TOPIC_REF}" {
  name = "{TOPIC_NAME}"
}

resource "google_pubsub_topic" "{BACKUP_TOPIC_REF}" {
  name="{BACKUP_TOPIC_NAME}"
}

resource "google_pubsub_subscription" "{SUBSCRIPTION_REF}" {
  name = "{SUBSCRIPTION_NAME}"
  topic = google_pubsub_topic.{TOPIC_REF}.name
  message_retention_duration="{MESSAGE_RETENTION_DURATION}"
  retain_acked_messages={TRUE,FALSE}
  ack_deadline_seconds = {ACK_DEADLINE_SECONDS}
  dead_letter_policy {
    dead_letter_topic = google_pubsub_topic.{BACKUP_TOPIC_REF}.id
    max_delivery_attempts={MAX_DELIVERY_ATTEMPTS}

  }
  expiration_policy {
    ttl="{TTL}"
  }
  retry_policy {
    minimum_backoff="{MINIMUM_BACKOFF}"
    maximum_backoff= "{MAXIMUM_BACKOFF}"

  }
  
  resource "google_pubsub_subscription" "deadletter_sub" {
    name = "my-backup-subscription"
    topic = google_pubsub_topic.sample_dead_letter.name

  }

}

