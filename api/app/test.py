from unittest.mock import AsyncMock
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.mark.asyncio
async def test_login_to_database(mocker):
    mock_response = {
        "message": "Logged into the database, you can now make queries",
        "status_code": 200,
    }
    mocker.patch("models.database_model.DBManager.get_db_connection", new=AsyncMock())

    client = TestClient(app)
    response = client.post(
        "/api/v1/login",
        json={
            "username": "adminuser",
            "password": "adminpassword",
            "host": "db",
            "db_name": "postgresdatabase",
        },
    )
    assert response.status_code == 200
    assert response.json() == mock_response
