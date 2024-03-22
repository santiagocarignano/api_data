from models.bigquery_models import query_to_bigquery
from serializers.bigquery_serializer import (
    ResponseSerializer
)
from fastapi import HTTPException
import json

async def bigquery_controller(id):
    try:
        response = await query_to_bigquery(id)
        serialized_response = [ResponseSerializer(id=row['id'], message=row['message'], source=row['source']).dict() for row in response]
        return json.dumps(serialized_response, indent=2)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid Query")