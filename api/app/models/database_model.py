from dotenv import load_dotenv
import asyncpg
from typing import Optional
from fastapi import HTTPException, status
from serializers.database_serializer import (
    ResponseConnectionSerializer,
    DatabaseSchemaSerializer,
    TableSchema,
)

load_dotenv()


class DBManager:
    _DATABASE_URL: Optional[str] = None

    @classmethod
    async def set_db_credentials(
        cls, username: str, password: str, host: str, db_name: str
    ):
        cls._DATABASE_URL = f"postgresql://{username}:{password}@{host}/{db_name}"

    @classmethod
    async def get_db_connection(cls) -> Optional[asyncpg.Connection]:
        if cls._DATABASE_URL is None:
            raise HTTPException(
                status_code=500, detail="Database credentials are not set."
            )
        try:
            return await asyncpg.connect(cls._DATABASE_URL)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Failure to connect to the database."
            )


async def login_to_database(username, password, host, db_name):
    await DBManager.set_db_credentials(username, password, host, db_name)
    try:
        connection = await DBManager.get_db_connection()
        await connection.close()
        return ResponseConnectionSerializer(
            message="Logged into the database, you can now make queries",
            status_code=status.HTTP_200_OK,
        )
    except HTTPException as e:
        raise e


async def get_db_schema():
    db = await DBManager.get_db_connection()
    try:
        database_name = await db.fetchval("SELECT current_database();")
        tables = await db.fetch(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public';
        """
        )
        schema_info = {"database_name": database_name, "tables": {}}
        for table_record in tables:
            table_name = table_record["table_name"]
            columns = await db.fetch(
                f"""
                SELECT *
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = $1;
            """,
                table_name,
            )
            schema_info["tables"][table_name] = [
                {
                    "column_name": column["column_name"],
                    "data_type": column["data_type"],
                    "is_nullable": column["is_nullable"],
                }
                for column in columns
            ]
        return DatabaseSchemaSerializer(**schema_info)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failure to connect to the database."
        )
    finally:
        await db.close()


async def get_table(table_name):
    db = await DBManager.get_db_connection()
    try:
        exists = await db.fetchval(
            """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE  table_schema = 'public'
            AND    table_name   = $1
        );
    """,
            table_name,
        )
        if not exists:
            raise HTTPException(status_code=404, detail="Table not found")
        columns = await db.fetch(
            f"""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = $1;
    """,
            table_name,
        )
        table_info = {
            "table_name": table_name,
            "columns": [
                {
                    "column_name": column["column_name"],
                    "data_type": column["data_type"],
                    "is_nullable": column["is_nullable"],
                }
                for column in columns
            ],
        }
        return TableSchema(**table_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Table does not exists.")
    finally:
        await db.close()
