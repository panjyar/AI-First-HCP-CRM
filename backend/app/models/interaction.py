from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


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
    """
    Represents the complete interaction form shown in the frontend.

    Nullable text and list fields are intentional because the LLM may return
    null when information was not included in the user's message. The values
    are normalized after validation so the frontend receives empty strings
    and empty lists instead of null for those fields.
    """

    interaction_id: int | None = None
    hcp_id: int | None = None

    hcp_name: str | None = None
    specialty: str | None = None
    organization: str | None = None

    interaction_date: date | None = None
    interaction_type: InteractionType | None = None

    products_discussed: list[str] | str | None = Field(default_factory=list)
    topics_discussed: list[str] | str | None = Field(default_factory=list)

    sentiment: Sentiment | None = None

    materials_shared: list[str] | str | None = Field(default_factory=list)
    notes: str | None = None

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
        """
        Accept null, one string, or a list of strings.

        Examples:
        null                         -> []
        "Product brochure"           -> ["Product brochure"]
        ["Brochure", "Safety study"] -> ["Brochure", "Safety study"]
        """
        if value is None:
            return []

        if isinstance(value, str):
            cleaned_value = value.strip()
            return [cleaned_value] if cleaned_value else []

        if isinstance(value, list):
            normalized_items: list[str] = []

            for item in value:
                if item is None:
                    continue

                cleaned_item = str(item).strip()

                if cleaned_item:
                    normalized_items.append(cleaned_item)

            return normalized_items

        raise ValueError(
            "Expected null, a string, or a list of strings"
        )

    @model_validator(mode="after")
    def normalize_missing_form_values(self) -> "InteractionForm":
        """
        Convert nullable LLM output into frontend-friendly values.
        """
        self.hcp_name = self.hcp_name or ""
        self.specialty = self.specialty or ""
        self.organization = self.organization or ""
        self.notes = self.notes or ""

        self.products_discussed = self.products_discussed or []
        self.topics_discussed = self.topics_discussed or []
        self.materials_shared = self.materials_shared or []

        return self


class InteractionPatch(BaseModel):
    """
    Represents only the fields that should be changed during an edit.

    Fields that are not mentioned by the user should remain unset so the edit
    tool can preserve all existing interaction values.
    """

    hcp_id: int | None = None
    hcp_name: str | None = None
    specialty: str | None = None
    organization: str | None = None

    interaction_date: date | None = None
    interaction_type: InteractionType | None = None

    products_discussed: list[str] | str | None = None
    topics_discussed: list[str] | str | None = None

    sentiment: Sentiment | None = None

    materials_shared: list[str] | str | None = None
    notes: str | None = None

    follow_up_required: bool | None = None
    follow_up_date: date | None = None

    @field_validator(
        "products_discussed",
        "topics_discussed",
        "materials_shared",
        mode="before",
    )
    @classmethod
    def normalize_patch_lists(
        cls,
        value: object,
    ) -> list[str] | None:
        """
        Normalize list fields used by the edit tool.

        An omitted field remains unset. An explicit null remains null.
        """
        if value is None:
            return None

        if isinstance(value, str):
            cleaned_value = value.strip()
            return [cleaned_value] if cleaned_value else []

        if isinstance(value, list):
            normalized_items: list[str] = []

            for item in value:
                if item is None:
                    continue

                cleaned_item = str(item).strip()

                if cleaned_item:
                    normalized_items.append(cleaned_item)

            return normalized_items

        raise ValueError(
            "Expected null, a string, or a list of strings"
        )


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
    interaction_date: date | None = None
    interaction_type: str | None = None

    products_discussed: list[str] = Field(default_factory=list)
    topics_discussed: list[str] = Field(default_factory=list)

    sentiment: str | None = None

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
    def normalize_history_lists(cls, value: object) -> list[str]:
        if value is None:
            return []

        if isinstance(value, str):
            cleaned_value = value.strip()
            return [cleaned_value] if cleaned_value else []

        if isinstance(value, list):
            return [
                str(item).strip()
                for item in value
                if item is not None and str(item).strip()
            ]

        raise ValueError(
            "Expected null, a string, or a list of strings"
        )


class FollowUpData(BaseModel):
    follow_up_id: int
    hcp_id: int | None = None
    interaction_id: int | None = None

    hcp_name: str
    due_date: date
    follow_up_type: str
    purpose: str

    priority: str
    status: str