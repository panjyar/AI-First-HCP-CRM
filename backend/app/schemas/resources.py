from datetime import date, datetime

from pydantic import BaseModel


class HCPResponse(BaseModel):
    id: int
    full_name: str
    specialty: str
    organization: str
    city: str
    email: str | None
    phone: str | None


class InteractionResponse(BaseModel):
    id: int
    session_id: str
    hcp_id: int | None
    hcp_name: str
    specialty: str
    organization: str
    interaction_date: date | None
    interaction_type: str | None
    products_discussed: list[str]
    topics_discussed: list[str]
    sentiment: str | None
    materials_shared: list[str]
    notes: str
    follow_up_required: bool
    follow_up_date: date | None
    created_at: datetime
    updated_at: datetime


class FollowUpResponse(BaseModel):
    id: int
    session_id: str
    hcp_id: int | None
    interaction_id: int | None
    hcp_name: str
    due_date: date
    follow_up_type: str
    purpose: str
    priority: str
    status: str
    created_at: datetime
