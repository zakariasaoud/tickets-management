from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Ticket
from app.schemas.tickets import TicketOut
from app.schemas.tickets import TicketStatus
from typing import Optional
from app.crud.exceptions import DuplicateTitleException


async def create_ticket(
    db: AsyncSession,
    title: str,
    description: Optional[str] = None,
    status: Optional[TicketStatus] = None,
    reject_duplicates: Optional[bool] = False,
) -> TicketOut:
    """
    Create a new ticket in the database.

    Args:
        db (AsyncSession): The async SQLAlchemy database session.
        title (str): The title of the ticket.
        description (str): The description of the ticket (Optional).
        status (TicketStatus): The status of the ticket (Optional).
        reject_duplicates (bool) : This parameter is used to avoid creating duplicate tickets (with the same title).

    Returns:
        TicketOut: The created ticket as a Pydantic model.
    """
    new_ticket = Ticket(
        title=title,
        description=description,
        status=status,
    )
    existing_tickets = await db.execute(select(Ticket).where(Ticket.title == title))
    duplicate = existing_tickets.scalars().first()
    if reject_duplicates and duplicate:
        raise DuplicateTitleException("ticket", title)
    db.add(new_ticket)
    await db.commit()
    await db.refresh(new_ticket)
    return TicketOut.from_orm(new_ticket)
