#######################
# PubSub
#######################

resource "google_pubsub_topic" "topic" {
  name = var.topic_name
}

resource "google_pubsub_subscription" "suscriber" {
  name  = var.dataflow_suscriber_name
  topic = google_pubsub_topic.topic.name

  depends_on = [ google_cloud_scheduler_job.scheduler_job]
}

#######################
# Scheduler
#######################

resource "google_cloud_scheduler_job" "scheduler_job" {
  name     = var.scheduler_job_name
  schedule = var.scheduler_execution_interval
  pubsub_target {
    topic_name = google_pubsub_topic.topic.id
    data = base64encode(jsonencode({"id":1,"user": "Elon Musk","role":"CEO of Tesla"}))
  }

}

#######################
# BigQuery
#######################

resource "google_bigquery_dataset" "dataset" {
  dataset_id                  = var.dataset_id
  location                    = var.location
  delete_contents_on_destroy  = false
}

resource "google_bigquery_table" "bigquery_table" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = var.table_id
  deletion_protection=false
    schema = <<EOF
    [
    {
      "name": "id",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
        "name": "user",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "role",
        "type": "STRING",
        "mode": "NULLABLE"
    }
    ]
    EOF
}

#######################
# Storage to save temporary dataflow files
#######################

resource "google_storage_bucket" "dataflow_temp_bucket" {
  name          = var.bucket_name
  location      = "US"
  force_destroy = true

  storage_class = "STANDARD"
}

#######################
# Dataflow
#######################

resource "google_dataflow_job" "dataflow" {
  name              = var.job_name
  template_gcs_path = var.template_dataflow
  temp_gcs_location = google_storage_bucket.dataflow_temp_bucket.url
  parameters = {
    inputSubscription         = "projects/${var.project_id}/subscriptions/${var.dataflow_suscriber_name}"
    outputTableSpec    = "${google_bigquery_dataset.dataset.project}.${google_bigquery_dataset.dataset.dataset_id}.${google_bigquery_table.bigquery_table.table_id}"
  }

  depends_on = [google_pubsub_subscription.suscriber]
}