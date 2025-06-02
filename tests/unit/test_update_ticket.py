from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.crud.exceptions import (
    AlreadyClosedError,
    InvalidCloseTransitionError,
    NotFoundError,
)
from app.main import app


@pytest.mark.asyncio
async def test_update_ticket_success(
    ticket_id, ticket_update_data, fake_updated_ticket
):
    """
    Testing updating an existing ticket.
    """
    with patch(
        "app.crud.tickets_crud.update_ticket_by_id",
        new=AsyncMock(return_value=fake_updated_ticket),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put(
                f"/tickets/update_ticket/{ticket_id}", json=ticket_update_data
            )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ticket_id
    assert data["title"] == ticket_update_data["title"]
    assert data["description"] == ticket_update_data["description"]
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_update_ticket_not_found(ticket_id, ticket_update_data):
    """
    Testing updating not an existing ticket.
    """
    with patch(
        "app.crud.tickets_crud.update_ticket_by_id",
        new=AsyncMock(side_effect=NotFoundError("Ticket", ticket_id)),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put(
                f"/tickets/update_ticket/{ticket_id}", json=ticket_update_data
            )

    assert response.status_code == 404
    assert f"Ticket with ID {ticket_id} is not found." in response.text


@pytest.mark.asyncio
async def test_update_ticket_server_error(ticket_id, ticket_update_data):
    """
    Testing updating with server error
    """
    with patch(
        "app.crud.tickets_crud.update_ticket_by_id",
        new=AsyncMock(side_effect=Exception("DB failure")),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put(
                f"/tickets/update_ticket/{ticket_id}", json=ticket_update_data
            )

    assert response.status_code == 500
    assert "Cannot update the ticket" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_ticket_unexpected_error(ticket_id, ticket_update_data):
    """
    Test server error during updating ticket
    """
    with patch(
        "app.crud.tickets_crud.update_ticket_by_id",
        new=AsyncMock(side_effect=Exception("Something went wrong")),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put(
                f"/tickets/update_ticket/{ticket_id}", json=ticket_update_data
            )

    assert response.status_code == 500
    assert f"Cannot update the ticket with id {ticket_id}" in response.text


@pytest.mark.asyncio
async def test_update_ticket_with_title_too_long(long_title_ticket):
    """
    Test updating a ticket with a too long title.
    """
    valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            f"/tickets/update_ticket/{valid_uuid}", json=long_title_ticket
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_ticket_with_bad_status(bad_status_ticket):
    """
    Test updating a ticket with a wrong status
    """
    valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            f"/tickets/update_ticket/{valid_uuid}", json=bad_status_ticket
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_ticket_empty_data(
    ticket_id, ticket_update_empty_data, fake_updated_ticket
):
    """
    Test updating a ticket with an empty data.
    """
    with patch(
        "app.crud.tickets_crud.update_ticket_by_id",
        new=AsyncMock(return_value=fake_updated_ticket),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put(
                f"/tickets/update_ticket/{ticket_id}", json=ticket_update_empty_data
            )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == fake_updated_ticket["id"]
    assert data["title"] == fake_updated_ticket["title"]
    assert data["description"] == fake_updated_ticket["description"]
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_close_ticket_success(ticket_id, fake_updated_closed_ticket):
    """
    Test closing a ticket.
    """
    with patch(
        "app.crud.tickets_crud.close_ticket_by_id",
        new=AsyncMock(return_value=fake_updated_closed_ticket),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.patch(f"/tickets/{ticket_id}/close")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(fake_updated_closed_ticket["id"])
    assert data["title"] == fake_updated_closed_ticket["title"]
    assert data["status"] == "closed"


@pytest.mark.asyncio
async def test_close_ticket_already_closed(ticket_id):
    """
    Test closing an already closed ticket.
    """
    with patch(
        "app.crud.tickets_crud.close_ticket_by_id",
        new=AsyncMock(side_effect=AlreadyClosedError("Ticket is already closed")),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.patch(f"/tickets/{ticket_id}/close")

    assert response.status_code == 400
    assert "already closed" in response.text


@pytest.mark.asyncio
async def test_close_ticket_invalid_transition(ticket_id):
    """
    Test closing a ticket with status = "stalled"
    """
    with patch(
        "app.crud.tickets_crud.close_ticket_by_id",
        new=AsyncMock(side_effect=InvalidCloseTransitionError("Invalid status change")),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.patch(f"/tickets/{ticket_id}/close")

    assert response.status_code == 400
    assert "Invalid status change" in response.text


@pytest.mark.asyncio
async def test_close_ticket_server_error(ticket_id):
    """
    Test closing a ticket with server error.
    """
    with patch(
        "app.crud.tickets_crud.close_ticket_by_id",
        new=AsyncMock(side_effect=Exception("DB failure")),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.patch(f"/tickets/{ticket_id}/close")

    assert response.status_code == 500
    assert "Cannot close the ticket" in response.json()["detail"]
