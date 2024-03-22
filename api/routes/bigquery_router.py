from fastapi import APIRouter, Request
from controllers.bigquery_controller import bigquery_controller

router = APIRouter()


@router.get("/{id}")
def router_identifier(id):
    return bigquery_controller(id)
