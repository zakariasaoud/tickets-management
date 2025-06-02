from fastapi import APIRouter, Path, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.tickets import (
    TicketCreate,
    TicketOut,
    TicketUpdate,
    TicketsResponseList,
)
from app.db.sqlite import get_db
from app.crud import tickets_crud
from app.crud.exceptions import (
    DuplicateTitleException,
    NotFoundError,
    InvalidCloseTransitionError,
    AlreadyClosedError,
)
from uuid import UUID

router = APIRouter()


@router.post(
    "/add_ticket",
    summary="Create a new ticket",
    description="Creating new ticket, by giving the ticket title. The ticket description and the status are optionals",
    response_model=TicketOut,
)
async def create_new_ticket(
    ticket_in: TicketCreate,
    reject_duplicates: bool = Query(
        False, description="Used to avoid creating tickets with same title."
    ),
    db: AsyncSession = Depends(get_db),
):
    try:
        new_ticket = await tickets_crud.create_ticket(
            db=db,
            title=ticket_in.title,
            description=ticket_in.description,
            status=ticket_in.status,
            reject_duplicates=reject_duplicates,
        )
        return new_ticket

    except DuplicateTitleException as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Cannot create new ticket because of: {str(e)}"
        )


@router.get(
    "/list_tickets",
    summary="List all tickets",
    description="Listing all tickets. To specify how many tickets you would like to get, you can use skip and limit parameters",
    response_model=TicketsResponseList,
)
async def list_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0, le=100),
    db: AsyncSession = Depends(get_db),
):
    try:
        tickets_list_from_db = await tickets_crud.get_all_tickets(
            db=db, skip=skip, limit=limit
        )
        return tickets_list_from_db
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Cannot get the tickets list, because of: {str(e)}"
        )


@router.get(
    "/get_ticket/{ticket_id}",
    summary="Get a ticket from its ID",
    description="Get a ticket by its ID if it exists..",
    response_model=TicketOut,
)
async def get_ticket(ticket_id: UUID = Path(...), db: AsyncSession = Depends(get_db)):
    try:
        ticket = await tickets_crud.get_ticket_by_id(db=db, ticket_id=str(ticket_id))
        return ticket
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cannot get the ticket with id {ticket_id}, because of: {str(e)}",
        )


@router.put(
    "/update_ticket/{ticket_id}",
    summary="Update a ticket from its ID",
    description="Get an existing ticket by its ID.",
    response_model=TicketOut,
)
async def update_ticket(
    update_data: TicketUpdate,
    ticket_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        updated_ticket = await tickets_crud.update_ticket_by_id(
            db=db,
            update_data=update_data,
            ticket_id=str(ticket_id),
        )
        return updated_ticket
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cannot update the ticket with id {ticket_id}, because of: {str(e)}",
        )


@router.patch(
    "/{ticket_id}/close",
    summary="Close a ticket",
    description="Close an existing ticket.",
    response_model=TicketOut,
)
async def close_ticket(ticket_id: UUID = Path(...), db: AsyncSession = Depends(get_db)):
    try:
        updated_ticket = await tickets_crud.close_ticket_by_id(
            db=db,
            ticket_id=str(ticket_id),
        )
        return updated_ticket
    except (InvalidCloseTransitionError, AlreadyClosedError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cannot close the ticket with id {ticket_id}, because of: {str(e)}",
        )


@router.delete(
    "/delete_ticket/{ticket_id}",
    summary="Delete a ticket",
    description="Delete a ticket that is already closed. If force_delete=true, delete the ticket regardless of his status.",
    status_code=204,
)
async def delete_ticket(
    ticket_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    force_delete: bool = Query(False, description="Forcefully remove this ticket"),
):
    try:
        await tickets_crud.delete_ticket_by_id(
            db=db, ticket_id=str(ticket_id), force_delete=force_delete
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidCloseTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cannot delete the ticket with id {ticket_id}, because of: {str(e)}",
        )


@router.delete(
    "/delete_all_tickets",
    summary="Delete all tickets",
    description="Delete all closed tickets. If force_delete=true, delete all tickets regardless of status.",
)
async def delete_all_tickets(
    db: AsyncSession = Depends(get_db),
    force_delete: bool = Query(False, description="Forcefully remove all tickets"),
):
    try:
        result = await tickets_crud.delete_tickets(db=db, force_delete=force_delete)
        if result["delete_count"] == 0:
            return {
                "message": f"No tickets were deleted. {result['total_count']} remaining tickets."
            }
        return {
            "message": f"{result['delete_count']} tickets deleted. {result['total_count']} remaining tickets."
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Cannot delete tickets because of: {str(e)}"
        )
