import os
import sys
from datetime import datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.db.sqlite import get_db
from app.main import app
from app.schemas.tickets import TicketOut, TicketsResponseList


@pytest.fixture
def ticket_id() -> str:
    return "e8a69b44-98dc-4fc1-9f24-b764fd8c89a2"


@pytest.fixture
def ticket_id_2() -> str:
    return "12345678-1234-5678-1234-567812345679"


@pytest.fixture
def ticket_input():
    return {
        "title": "New Ticket",
        "description": "This is a test ticket.",
    }


@pytest.fixture
def bad_status_ticket():
    return {
        "title": "Running Ticket",
        "description": "This is a running ticket.",
        "status": "running",
    }


@pytest.fixture
def short_title_ticket():
    return {"title": "TO", "description": "Short title ..."}


@pytest.fixture
def long_title_ticket():
    return {"title": "T" * 150, "description": "Too long title"}


@pytest.fixture
def long_description_ticket():
    return {"title": "Long description", "description": "D" * 600}


@pytest.fixture
def missing_title_ticket():
    return {"description": "No title provided"}


@pytest.fixture
def fake_created_ticket(ticket_id):
    return {
        "id": UUID(ticket_id),
        "title": "New Ticket",
        "description": "This is a test ticket.",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def mock_session():
    """
    Mocked async SQLAlchemy session.
    """
    session = AsyncMock()
    session.add = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture(autouse=True)
def override_get_db(mock_session):
    """
    Automatically override FastAPI's get_db dependency with the mocked session.
    """
    app.dependency_overrides[get_db] = lambda: mock_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def fake_tickets_list(ticket_id, ticket_id_2):
    return TicketsResponseList(
        total=2,
        skip=0,
        limit=10,
        results=[
            TicketOut(
                id=UUID(ticket_id),
                title="Ticket1",
                description="Add new feature to backend.",
                status="open",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            TicketOut(
                id=UUID(ticket_id_2),
                title="Ticket2",
                description="Correction the integration tests.",
                status="closed",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        ],
    )


@pytest.fixture
def fake_empty_tickets_list():
    return TicketsResponseList(total=0, skip=0, limit=10, results=[])


@pytest.fixture
def ticket_update_data():
    return {"title": "Updated Title", "description": "Updated Description"}


@pytest.fixture
def ticket_update_empty_data():
    return {}


@pytest.fixture
def fake_updated_ticket(ticket_id):
    return {
        "id": ticket_id,
        "title": "Updated Title",
        "description": "Updated Description",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def fake_updated_closed_ticket(fake_created_ticket):
    return {
        "id": fake_created_ticket["id"],
        "title": fake_created_ticket["title"],
        "description": fake_created_ticket["description"],
        "status": "closed",
        "created_at": fake_created_ticket["created_at"],
        "updated_at": fake_created_ticket["updated_at"],
    }
