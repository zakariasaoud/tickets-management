import pytest
from httpx import AsyncClient, ASGITransport
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.main import app


@pytest.mark.asyncio
async def test_add_ticket():
    ticket_data = {
        "title": "Testing integration ticket",
        "description": "Testing without mock",
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/tickets/add_ticket", json=ticket_data)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == ticket_data["title"]
    assert data["description"] == ticket_data["description"]
    assert "id" in data


@pytest.mark.asyncio
async def test_add_ticket_with_reject_duplicates():
    ticket_data = {
        "title": "Testing integration ticket",
        "description": "Testing without with reject_duplicates = True",
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/tickets/add_ticket?reject_duplicates=True", json=ticket_data
        )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "A ticket with the title: Testing integration ticket, already exists."
    )


@pytest.mark.asyncio
async def test_list_tickets():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/tickets/list_tickets", params={"skip": 0, "limit": 10}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    assert data["results"][0]["title"] == "Testing integration ticket"


@pytest.mark.asyncio
async def test_get_ticket_by_id():
    ticket_data = {"title": "Sample", "description": "Testing get ticket by ID"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created_ticket = await client.post("/tickets/add_ticket", json=ticket_data)
        ticket_id = created_ticket.json()["id"]
        get_ticket = await client.get(f"/tickets/get_ticket/{ticket_id}")

    assert get_ticket.status_code == 200
    data = get_ticket.json()
    assert data["id"] == ticket_id
    assert data["title"] == "Sample"


@pytest.mark.asyncio
async def test_update_ticket():
    ticket_data = {"title": "Old title", "description": "Test Updating ticket."}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        ticket_to_update = await client.post("/tickets/add_ticket", json=ticket_data)
        ticket_id = ticket_to_update.json()["id"]
        update_data = {"title": "Updated title", "description": "Updated desc"}
        updated_ticket = await client.put(
            f"/tickets/update_ticket/{ticket_id}", json=update_data
        )

    assert updated_ticket.status_code == 200
    assert updated_ticket.json()["title"] == "Updated title"
    assert updated_ticket.json()["description"] == "Updated desc"


@pytest.mark.asyncio
async def test_update_ticket_empty_data():
    ticket_data = {"title": "Old title 1", "description": "Test Updating ticket empty."}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        ticket_to_update = await client.post("/tickets/add_ticket", json=ticket_data)
        ticket_id = ticket_to_update.json()["id"]
        update_empty_data = {}
        updated_ticket = await client.put(
            f"/tickets/update_ticket/{ticket_id}", json=update_empty_data
        )

    assert updated_ticket.status_code == 200
    assert updated_ticket.json()["title"] == ticket_data["title"]
    assert updated_ticket.json()["description"] == ticket_data["description"]


@pytest.mark.asyncio
async def test_close_ticket():
    ticket_data = {"title": "To Close ticket", "description": "Closing this ticket"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        ticket_to_close = await client.post("/tickets/add_ticket", json=ticket_data)
        ticket_id = ticket_to_close.json()["id"]
        closed_ticket = await client.patch(f"/tickets/{ticket_id}/close")

    assert ticket_to_close.json()["status"] == "open"
    assert closed_ticket.status_code == 200
    assert closed_ticket.json()["status"] == "closed"


@pytest.mark.asyncio
async def test_close_not_existing_ticket(ticket_id):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        closed_ticket = await client.patch(f"/tickets/{ticket_id}/close")

    assert closed_ticket.status_code == 404
    assert "is not found" in closed_ticket.json()["detail"]


@pytest.mark.asyncio
async def test_close_already_closed_ticket():
    ticket_data = {
        "title": "To Close ticket",
        "description": "Closing this ticket",
        "status": "closed",
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        ticket_to_close = await client.post("/tickets/add_ticket", json=ticket_data)
        ticket_id = ticket_to_close.json()["id"]
        closed_ticket = await client.patch(f"/tickets/{ticket_id}/close")

    assert closed_ticket.json()["detail"] == "Ticket is already closed."
    assert closed_ticket.status_code == 400


@pytest.mark.asyncio
async def test_delete_ticket():
    ticket_data = {"title": "Ticket To delete", "description": "Will be deleted"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        ticket_to_delete = await client.post("/tickets/add_ticket", json=ticket_data)
        ticket_id = ticket_to_delete.json()["id"]
        await client.patch(f"/tickets/{ticket_id}/close")
        deletion = await client.delete(f"/tickets/delete_ticket/{ticket_id}")
    assert deletion.status_code == 204


@pytest.mark.asyncio
async def test_delete_all_tickets_no_force():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(
            "/tickets/delete_all_tickets",
        )
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "2 tickets deleted. 4 remaining tickets."


@pytest.mark.asyncio
async def test_delete_all_tickets_force():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(
            "/tickets/delete_all_tickets", params={"force_delete": True}
        )
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "4 tickets deleted. 0 remaining tickets."


@pytest.mark.asyncio
async def test_delete_all_not_tickets_for_deletion():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/tickets/delete_all_tickets")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "No tickets were deleted. 0 remaining tickets."
