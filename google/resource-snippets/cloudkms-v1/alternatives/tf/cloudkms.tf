variable "project_id" {}
variable "deployment" {}
variable "user" {}

provider "google" {
  project = var.project_id
  region  = "us-central1"
  zone    = "us-central1-c"
}

resource "google_kms_key_ring" "default" {
  name     = "test-keyring"
  location = "us-central1"
}

resource "google_kms_crypto_key" "default" {
  name     = format("%s-cryptoKey", var.deployment)
  key_ring = google_kms_key_ring.default.id
  purpose  = "ENCRYPT_DECRYPT"
  labels = {
    foo = var.deployment
  }
}

data "google_iam_policy" "admin" {
  binding {
    role = "roles/cloudkms.admin"

    members = [
      var.user,
    ]
  }
}

resource "google_kms_crypto_key_iam_policy" "crypto_key" {
  crypto_key_id = google_kms_crypto_key.default.id
  policy_data   = data.google_iam_policy.admin.policy_data
}

data "google_kms_crypto_key_version" "crypto-key-version" {
  crypto_key = google_kms_crypto_key.default.self_link
}
