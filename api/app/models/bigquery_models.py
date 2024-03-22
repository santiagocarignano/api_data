from google.cloud import bigquery

async def query_to_bigquery(id):
    client = bigquery.Client()
    GCP_PROJECT = 'fourth-ability-324823'
    BIGQUERY_DATASET = 'data_ingested'
    BIGQUERY_TABLE = 'api_data_table'
    sqlQuery = f"""select * from `{GCP_PROJECT}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}` where id='{id}' LIMIT 10"""
    query_job = await client.query(sqlQuery)
    rows = query_job.result()
    return rows

