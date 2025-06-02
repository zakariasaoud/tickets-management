import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from app.main import app
import json


@pytest.mark.asyncio
async def test_list_tickets_success(mock_session, fake_tickets_list):
    """
    Test listing tickets successfully.
    """
    # Patch the tickets_crud.get_all_tickets to return fake data
    with patch(
        "app.crud.tickets_crud.get_all_tickets",
        new=AsyncMock(return_value=fake_tickets_list),
    ) as mocked_get:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/tickets/list_tickets", params={"skip": 0, "limit": 10}
            )

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert response.json() == json.loads(fake_tickets_list.json())
    mocked_get.assert_awaited_once_with(db=mock_session, skip=0, limit=10)


@pytest.mark.asyncio
async def test_list_tickets_empty(mock_session, fake_empty_tickets_list):
    """
    Test listing tickets when there is no tickets.
    """
    with patch(
        "app.crud.tickets_crud.get_all_tickets",
        new=AsyncMock(return_value=fake_empty_tickets_list),
    ) as mocked_get:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/tickets/list_tickets", params={"skip": 0, "limit": 10}
            )

    assert response.status_code == 200
    assert response.json()["results"] == []
    assert response.json()["total"] == 0
    mocked_get.assert_awaited_once_with(db=mock_session, skip=0, limit=10)


@pytest.mark.asyncio
async def test_list_tickets_invalid_params():
    """
    Test listing tickets with invalid query parameters.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/tickets/list_tickets", params={"skip": -2, "limit": 10}
        )

    assert response.status_code == 422
    assert "detail" in response.json()
    assert (
        "Input should be greater than or equal to 0"
        in response.json()["detail"][0]["msg"]
    )


@pytest.mark.asyncio
async def test_list_tickets_server_side_error(mock_session):
    """
    Test server error during ticket listing.
    """
    with patch(
        "app.crud.tickets_crud.get_all_tickets",
        new=AsyncMock(side_effect=Exception("DB failure")),
    ) as mocked_get:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/tickets/list_tickets", params={"skip": 0, "limit": 10}
            )

    assert response.status_code == 500
    assert "Cannot get the tickets list" in response.json()["detail"]
    mocked_get.assert_awaited_once()
