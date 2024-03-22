from fastapi import APIRouter, Request
from controllers.bigquery_controller import bigquery_controller

router = APIRouter()

@router.get("/{id}")
async def router_identifier(request: Request):
    print(id)
    id = await request.json()
    return await bigquery_controller(id)