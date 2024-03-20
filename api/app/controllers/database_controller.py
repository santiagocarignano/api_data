from models import database_model
from serializers.database_serializer import (
    TableNameSerializer,
    DatabaseCredentialSerializer
)
from pydantic import ValidationError
from fastapi import HTTPException


async def login(login_credentials):
    try:
        login_data = DatabaseCredentialSerializer(**login_credentials)
    except ValidationError as e:
        raise HTTPException(
            status_code=422, detail="Unvalid data, please check the documentation."
        )
    try:
        username = login_data.username
        password = login_data.password
        host = login_data.host
        db_name = login_data.db_name
        response = await database_model.login_to_database(
            username, password, host, db_name
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid credentials")


async def schema():
    return await database_model.get_db_schema()


async def table(table_name):
    try:
        return await database_model.get_table(
            TableNameSerializer(table_name=table_name).table_name
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
