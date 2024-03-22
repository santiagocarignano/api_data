from httpx import AsyncClient
import pytest
from main import app
from unittest.mock import patch


@pytest.mark.asyncio
async def test_bigquery_route():
    test_id = "1"
    expected_response = [
        {"id": "1", "message": "Hello World From Source", "source": "cloud_scheduler"}
    ]
    with patch(
        "controllers.bigquery_controller.query_to_bigquery",
        return_value=expected_response,
    ) as mock_query:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/api/v1/{test_id}")
            assert response.status_code == 200
            assert response.json() == expected_response


@pytest.mark.asyncio
async def test_bigquery_route_invalid_query():
    test_id = "invalid"
    with patch(
        "controllers.bigquery_controller.query_to_bigquery",
        side_effect=Exception("Invalid Query"),
    ):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/api/v1/{test_id}")
            assert response.status_code == 400
            assert response.json().get("detail") == "Invalid Query"
