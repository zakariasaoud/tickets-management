from unittest.mock import ANY, AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.crud.exceptions import InvalidCloseTransitionError, NotFoundError
from app.main import app


@pytest.mark.asyncio
async def test_delete_ticket_success(ticket_id):
    """
    Testing successful deletion of a ticket.
    """
    with patch(
        "app.crud.tickets_crud.delete_ticket_by_id", new=AsyncMock(return_value=None)
    ) as mock_delete:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete(f"/tickets/{ticket_id}")

    assert response.status_code == 204
    mock_delete.assert_awaited_once_with(
        db=ANY, ticket_id=ticket_id, force_delete=False
    )


@pytest.mark.asyncio
async def test_delete_ticket_force_success(ticket_id):
    """
    Testing successful deletion of a ticket with force_delete=True.
    """
    with patch(
        "app.crud.tickets_crud.delete_ticket_by_id", new=AsyncMock(return_value=None)
    ) as mock_delete:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete(f"/tickets/{ticket_id}?force_delete=true")

    assert response.status_code == 204
    mock_delete.assert_awaited_once_with(db=ANY, ticket_id=ticket_id, force_delete=True)


@pytest.mark.asyncio
async def test_delete_ticket_not_found(ticket_id):
    """
    Testing deleting a not existing ticket.
    """
    with patch(
        "app.crud.tickets_crud.delete_ticket_by_id",
        new=AsyncMock(side_effect=NotFoundError("Ticket", ticket_id)),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete(f"/tickets/{ticket_id}")

    assert response.status_code == 404
    assert f"Ticket with ID {ticket_id} is not found." in response.text


@pytest.mark.asyncio
async def test_delete_ticket_not_closed_error(ticket_id):
    """
    Testing deleting not closed ticket and force_delete=False.
    """
    with patch(
        "app.crud.tickets_crud.delete_ticket_by_id",
        new=AsyncMock(
            side_effect=InvalidCloseTransitionError("Cannot delete an open ticket")
        ),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete(f"/tickets/{ticket_id}")

    assert response.status_code == 400
    assert "Cannot delete an open ticket" in response.text


@pytest.mark.asyncio
async def test_delete_ticket_server_error(ticket_id):
    """
    Testing deleting ticket with server error
    """
    with patch(
        "app.crud.tickets_crud.delete_ticket_by_id",
        new=AsyncMock(side_effect=Exception("DB failure")),
    ) as mock_delete:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete(f"/tickets/{ticket_id}")

    assert response.status_code == 500
    assert "Cannot delete the ticket" in response.json()["detail"]
    mock_delete.assert_awaited_once_with(
        db=ANY, ticket_id=ticket_id, force_delete=False
    )


@pytest.mark.asyncio
async def test_delete_all_tickets_success():
    """
    Testing delete_all_tickets success.
    """
    message = {"delete_count": 3, "total_count": 0}
    with patch(
        "app.crud.tickets_crud.delete_tickets",
        new=AsyncMock(return_value=message),
    ) as mock_delete:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete("/tickets/")

    assert response.status_code == 200
    assert response.json() == {"message": "3 tickets deleted. 0 remaining tickets."}
    mock_delete.assert_awaited_once_with(db=ANY, force_delete=False)


@pytest.mark.asyncio
async def test_delete_all_tickets_server_error():
    """
    Testing delete_all_tickets with server error.
    """
    with patch(
        "app.crud.tickets_crud.delete_tickets",
        new=AsyncMock(side_effect=Exception("DB failure")),
    ) as mock_delete:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete("/tickets/")

    assert response.status_code == 500
    assert "Cannot delete tickets" in response.json()["detail"]
    mock_delete.assert_awaited_once_with(db=ANY, force_delete=False)
