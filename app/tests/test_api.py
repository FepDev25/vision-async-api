import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    # Prueba un endpoint de salud (health check)
    response = await client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
