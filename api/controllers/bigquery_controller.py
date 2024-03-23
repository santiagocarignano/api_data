from models.bigquery_models import query_to_bigquery
from serializers.bigquery_serializer import ResponseSerializer
from fastapi import HTTPException
import json


def bigquery_controller(id):
    try:
        return [ResponseSerializer(**row).model_dump() for row in query_to_bigquery(id)]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Query")
