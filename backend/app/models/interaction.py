from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


Sentiment = Literal["Positive", "Neutral", "Negative"]
InteractionType = Literal[
    "In-person",
    "Phone",
    "Video call",
    "Email",
    "Conference",
    "Other",
]


class InteractionForm(BaseModel):
    interaction_id: int | None = None
    hcp_id: int | None = None
    hcp_name: str = ""
    specialty: str = ""
    organization: str = ""
    interaction_date: date | None = None
    interaction_type: InteractionType | None = None
    products_discussed: list[str] = Field(default_factory=list)
    topics_discussed: list[str] = Field(default_factory=list)
    sentiment: Sentiment | None = None
    materials_shared: list[str] = Field(default_factory=list)
    notes: str = ""
    follow_up_required: bool = False
    follow_up_date: date | None = None

    @field_validator(
        "products_discussed",
        "topics_discussed",
        "materials_shared",
        mode="before",
    )
    @classmethod
    def normalize_string_lists(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        raise ValueError("Expected a string or list of strings")


class InteractionPatch(BaseModel):
    hcp_id: int | None = None
    hcp_name: str | None = None
    specialty: str | None = None
    organization: str | None = None
    interaction_date: date | None = None
    interaction_type: InteractionType | None = None
    products_discussed: list[str] | None = None
    topics_discussed: list[str] | None = None
    sentiment: Sentiment | None = None
    materials_shared: list[str] | None = None
    notes: str | None = None
    follow_up_required: bool | None = None
    follow_up_date: date | None = None


class HCPProfile(BaseModel):
    hcp_id: int
    hcp_name: str
    specialty: str
    organization: str
    city: str
    email: str | None = None
    phone: str | None = None


class InteractionHistoryItem(BaseModel):
    interaction_id: int
    interaction_date: date | None
    interaction_type: str | None
    products_discussed: list[str]
    topics_discussed: list[str]
    sentiment: str | None
    materials_shared: list[str]
    notes: str
    follow_up_required: bool
    follow_up_date: date | None


class FollowUpData(BaseModel):
    follow_up_id: int
    hcp_id: int | None
    interaction_id: int | None
    hcp_name: str
    due_date: date
    follow_up_type: str
    purpose: str
    priority: str
    status: str
