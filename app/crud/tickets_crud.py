from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.models import Ticket
from app.schemas.tickets import TicketOut, TicketStatus, TicketsResponseList
from typing import Optional
from app.crud.exceptions import DuplicateTitleException, InvalidUUIDError, NotFoundError
from uuid import UUID


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


async def get_all_tickets(
    db: AsyncSession, skip: int = 0, limit: int = 10
) -> TicketsResponseList:
    """
    Retrieve a paginated list of tickets from the database.

    Args:
        db (AsyncSession): The async SQLAlchemy database session.
        skip (int): Number of tickets to skip (for pagination). Default is 0.
        limit (int): Maximum number of tickets to return. Default is 10.

    Returns:
        TicketsResponseList: A Pydantic object containing the total count, pagination info, and tickets list.
    """
    # Get the total number of tickets
    total = await db.scalar(select(func.count()).select_from(Ticket))

    # Get paginated tickets
    result = await db.execute(select(Ticket).offset(skip).limit(limit))
    rows = result.fetchall()
    tickets = [row[0] for row in rows]

    return TicketsResponseList(
        total=total,
        skip=skip,
        limit=limit,
        results=[TicketOut.from_orm(ticket) for ticket in tickets],
    )


def validate_uuid(ticket_id):
    """
    :param ticket_id: the ticket ID that we want to validate.
    :return: ticket_uuid
    """
    try:
        ticket_uuid = UUID(ticket_id)
        return ticket_uuid
    except ValueError:
        raise InvalidUUIDError(f"Invalid UUID format of ticket_id: {ticket_id}")


async def get_ticket_by_id(db: AsyncSession, ticket_id: str) -> TicketOut:
    """
    Get a ticket by its ID if it exists.

    Args:
        db (AsyncSession): The async SQLAlchemy database session.
        ticket_id (str): The ticket ID.

    Returns:
        TicketOut: The ticket as a Pydantic model.
    """
    ticket_uuid = validate_uuid(ticket_id)
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_uuid))
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise NotFoundError("Ticket", ticket_id)

    return TicketOut.from_orm(ticket)
