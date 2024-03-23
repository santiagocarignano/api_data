project_id = "fourth-ability-324823"

# Pub/Sub
topic_name = "api_dataflow_topic"
dataflow_suscriber_name = "dataflow_suscriber"

# Scheduler
scheduler_job_name = "insert-data-to-bigquery"
scheduler_execution_interval = "0/3 * * * *"

# BigQuery
dataset_id = "data_ingested"
location = "us-east1"
table_id = "api_data_table"

# Cloud Storage
bucket_name = "dataflow_temp_files_api_data"

# Dataflow
job_name = "api-dataflow-job"
template_dataflow =  "gs://dataflow-templates-us-east1/latest/PubSub_Subscription_to_BigQuery"

# Artifact Registry
artifact_registry_repository = "api-data-repo"