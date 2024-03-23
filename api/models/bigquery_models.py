from google.cloud import bigquery
from constants import GCP_PROJECT, BIGQUERY_DATASET, BIGQUERY_TABLE


def query_to_bigquery(id):
    try:
        client = bigquery.Client()
        sql_query = f"""select * from `{GCP_PROJECT}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}` where id='{id}' LIMIT 10"""
        query_job = client.query(sql_query)
        rows_list = [dict(row) for row in query_job.result()]
        return rows_list
    except Exception as e:
        return e
