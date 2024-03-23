# Project GCP
variable "project_id" {
  description = "The project ID to deploy the resources."
  type        = string
}

#PubSub
variable "topic_name" {
  description = "The name of the Pub/Sub topic to create."
  type        = string
}

variable "dataflow_suscriber_name" {
  description = "The name of the Pub/Sub subscription to create."
  type        = string
}

#scheduler
variable "scheduler_job_name" {
  description = "The name of the Cloud Scheduler job to create."
  type        = string
}

variable "scheduler_execution_interval" {
  description = "The execution interval of the Cloud Scheduler job."
  type        = string
}

#BigQuery
variable "dataset_id" {
  description = "The ID of the BigQuery dataset to create."
  type        = string
}

variable "location" {
  description = "The location of the BigQuery dataset to create."
  type        = string
}

variable "table_id" {
  description = "The ID of the BigQuery table to create."
  type        = string
}

# Storage
variable "bucket_name" {
  description = "The name of the Cloud Storage bucket to save temp files of dataflow."
  type        = string
}

# Dataflow
variable "job_name" {
  description = "The name of the Dataflow job to create."
  type        = string
}

variable "template_dataflow" {
  description = "The Dataflow template to use."
  type        = string
}

# Artifact Registry
variable "artifact_registry_repository" {
  description = "The name of the Artifact Registry repository to create."
  type        = string
}