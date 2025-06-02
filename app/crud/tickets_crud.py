from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Ticket
from app.schemas.tickets import TicketOut
from app.schemas.tickets import TicketStatus
from typing import Optional


async def create_ticket(
    db: AsyncSession,
    title: str,
    description: Optional[str] = None,
    status: Optional[TicketStatus] = None,
) -> TicketOut:
    """
    Create a new ticket in the database.

    Args:
        db (AsyncSession): The async SQLAlchemy database session.
        title (str): The title of the ticket.
        description (str): The description of the ticket (Optional).
        status (TicketStatus): The status of the ticket (Optional).

    Returns:
        TicketOut: The created ticket as a Pydantic model.
    """
    new_ticket = Ticket(
        title=title,
        description=description,
        status=status,
    )
    db.add(new_ticket)
    await db.commit()
    await db.refresh(new_ticket)
    return TicketOut.from_orm(new_ticket)
