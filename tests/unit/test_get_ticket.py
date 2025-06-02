from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.crud.exceptions import NotFoundError
from app.main import app


@pytest.mark.asyncio
async def test_get_ticket_success(fake_created_ticket):
    """
    Test getting a ticket by ID successfully.
    """
    with patch(
        "app.crud.tickets_crud.get_ticket_by_id",
        new=AsyncMock(return_value=fake_created_ticket),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/tickets/get_ticket/12345678-1234-5678-1234-567812345678"
            )

    assert response.status_code == 200
    assert response.json()["id"] == str(fake_created_ticket["id"])
    assert response.json()["description"] == str(fake_created_ticket["description"])


@pytest.mark.asyncio
async def test_get_ticket_invalid_ticket_id():
    """
    Test getting a ticket using invalid UUID.
    """
    invalid_ticket_id = "not-a-uuid"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/tickets/get_ticket/{invalid_ticket_id}")

    assert response.status_code == 422
    assert "Input should be a valid UUID" in response.text


@pytest.mark.asyncio
async def test_get_ticket_not_found():
    """
    Test getting a not existing ticket.
    """
    ticket_id = "8382994b-a643-4c56-85ca-bad267acb0b8"
    with patch(
        "app.crud.tickets_crud.get_ticket_by_id",
        new=AsyncMock(side_effect=NotFoundError("Ticket", ticket_id)),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/tickets/get_ticket/{ticket_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"Ticket with ID {ticket_id} is not found."}


@pytest.mark.asyncio
async def test_get_ticket_server_error(fake_created_ticket):
    """
    Test getting a ticket by ID with server error.
    """
    with patch(
        "app.crud.tickets_crud.get_ticket_by_id",
        new=AsyncMock(side_effect=Exception("DB failure")),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/tickets/get_ticket/12345678-1234-5678-1234-567812345678"
            )

    assert response.status_code == 500
    assert "Cannot get the ticket" in response.json()["detail"]
