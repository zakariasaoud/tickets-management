from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.tickets import (
    TicketCreate,
    TicketOut,
)
from app.db.sqlite import get_db
from app.crud import tickets_crud


router = APIRouter()


@router.post(
    "/add_ticket",
    summary="Create a new ticket",
    description="Creating new ticket, by giving the ticket title. The ticket description and the status are optionals",
    response_model=TicketOut,
)
async def create_new_ticket(
    ticket_in: TicketCreate, db: AsyncSession = Depends(get_db)
):
    try:
        new_ticket = await tickets_crud.create_ticket(
            db=db,
            title=ticket_in.title,
            description=ticket_in.description,
            status=ticket_in.status,
        )
        return new_ticket
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Cannot create new ticket because of: {str(e)}"
        )
