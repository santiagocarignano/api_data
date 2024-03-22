#######################
# PubSub
#######################

resource "google_pubsub_topic" "topic" {
  name = "api_dataflow_topic"
}

resource "google_pubsub_subscription" "suscriber" {
  name  = "dataflow_suscriber"
  topic = google_pubsub_topic.topic.name

  depends_on = [ google_cloud_scheduler_job.scheduler_job]
}

#######################
# Scheduler
#######################

resource "google_cloud_scheduler_job" "scheduler_job" {
  name     = "insert-data-to-bigquery"
  schedule = "0/3 * * * *"

  pubsub_target {
    topic_name = google_pubsub_topic.topic.id
    data = base64encode(jsonencode({"id":1,"message": "Hello World From Source","source":"cloud_scheduler"}))
  }

}

#######################
# BigQuery
#######################

resource "google_bigquery_dataset" "dataset" {
  dataset_id                  = "data_ingested"
  location                    = "us-east1"
  delete_contents_on_destroy  = false
}

resource "google_bigquery_table" "bigquery_table" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "api_data_table"
  deletion_protection=false
    schema = <<EOF
    [
    {
      "name": "id",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
        "name": "message",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "source",
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
  name          = "dataflow_temp_files_api_data"
  location      = "US"
  force_destroy = true

  storage_class = "STANDARD"
}

#######################
# Dataflow
#######################

resource "google_dataflow_job" "dataflow" {
  name              = "dataflow-job"
  template_gcs_path = "gs://dataflow-templates-us-east1/latest/PubSub_Subscription_to_BigQuery"
  temp_gcs_location = google_storage_bucket.dataflow_temp_bucket.url
  parameters = {
    inputSubscription         = "projects/fourth-ability-324823/subscriptions/dataflow_suscriber"
    outputTableSpec    = "${google_bigquery_dataset.dataset.project}.${google_bigquery_dataset.dataset.dataset_id}.${google_bigquery_table.bigquery_table.table_id}"
  }

  depends_on = [google_pubsub_subscription.suscriber]
}

#######################
# Artifact Registry
#######################

resource "google_artifact_registry_repository" "api_data_registry" {
  repository_id = "api-data-repo"
  description   = "Docker repository"
  format        = "DOCKER"
}