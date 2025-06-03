from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_create_ticket_success(ticket_input, fake_created_ticket):
    """
    Test creating a ticket with valid data.
    """
    with patch(
        "app.crud.tickets_crud.create_ticket",
        new=AsyncMock(return_value=fake_created_ticket),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/tickets/", json=ticket_input)
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == ticket_input["title"]
            assert data["description"] == ticket_input["description"]
            assert "id" in data
            assert "created_at" in data
            assert "updated_at" in data


@pytest.mark.asyncio
async def test_add_ticket_title_too_short(short_title_ticket):
    """
    Test creating a ticket with a title shorter than 3 characters.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/tickets/", json=short_title_ticket)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_ticket_different_status(bad_status_ticket):
    """
    Test creating a ticket with a different status (status=running)
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/tickets/", json=bad_status_ticket)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_ticket_title_too_long(long_title_ticket):
    """
    Test creating a ticket with a title longer than 100 characters.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/tickets/", json=long_title_ticket)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_ticket_description_too_long(long_description_ticket):
    """
    Test creating a ticket with a description longer than 500.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/tickets/", json=long_description_ticket)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_ticket_missing_title(missing_title_ticket):
    """
    Test creating a ticket without the required title field.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/tickets/", json=missing_title_ticket)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_ticket_server_side_error(ticket_input):
    """
    Test creating a ticket with server error.
    """
    with patch(
        "app.crud.tickets_crud.create_ticket",
        new=AsyncMock(side_effect=Exception("DB failure")),
    ) as mocked_get:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/tickets/", json=ticket_input)

    assert response.status_code == 500
    assert "Cannot create new ticket" in response.json()["detail"]
    mocked_get.assert_awaited_once()
