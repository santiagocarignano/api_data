from fastapi import APIRouter, Request
from controllers import database_controller

router = APIRouter()


@router.post("/login")
async def router_login(request: Request):
    credentials = await request.json()
    return await database_controller.login(credentials)


@router.get("/retrieve-schema")
async def router_schema():
    return await database_controller.schema()


@router.get("/tables/{table_name}")
async def router_table(table_name):
    return await database_controller.table(table_name)
