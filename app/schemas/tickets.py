from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TicketStatus(str, Enum):
    open = "open"
    stalled = "stalled"
    closed = "closed"


class TicketCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="the ticket title",
        examples=["ticket1"],
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="The ticket description",
        examples=["This ticket is a backend ticket"],
    )
    status: Optional[TicketStatus] = Field(
        TicketStatus.open,
        description="The ticket status (=open by default)",
        examples=["open", "stalled", "closed"],
    )

    model_config = {"from_attributes": True}


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="the ticket updated title",
        examples=["new_title1"],
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="The ticket description",
        examples=["This ticket is updated"],
    )
    status: Optional[TicketStatus] = Field(
        None,
        description="The updated ticket status",
        examples=["open", "stalled", "closed"],
    )


class TicketOut(TicketCreate):
    id: UUID = Field(
        ...,
        description="The ticket ID",
        examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
    )
    created_at: datetime = Field(
        ..., description="The ticket creation date", examples=["2025-05-01"]
    )
    updated_at: datetime = Field(
        ..., description="The ticket update date", examples=["2025-06-01"]
    )


# This model is used to return a list of tickets
class TicketsResponseList(BaseModel):
    total: int
    skip: int
    limit: int
    results: List[TicketOut]
