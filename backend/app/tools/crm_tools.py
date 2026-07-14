from __future__ import annotations

import json
from datetime import date
from typing import Annotated, Any, Literal

from langchain_core.tools import InjectedToolArg, tool
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, or_, select

from app.database.models import FollowUp, HCP, Interaction
from app.database.session import AsyncSessionFactory
from app.models.interaction import (
    FollowUpData,
    HCPProfile,
    InteractionForm,
    InteractionHistoryItem,
    InteractionPatch,
    InteractionType,
    Sentiment,
)


def _json(data: dict[str, Any]) -> str:
    return json.dumps(data, default=str)


class SearchHCPInput(BaseModel):
    name: str | None = Field(default=None, description="HCP name or partial name")
    specialty: str | None = Field(default=None, description="Medical specialty")
    organization: str | None = Field(default=None, description="Hospital or clinic")
    city: str | None = Field(default=None, description="City")
    limit: int = Field(default=5, ge=1, le=10)


class InteractionHistoryInput(BaseModel):
    hcp_id: int | None = Field(default=None, description="Known CRM HCP ID")
    hcp_name: str | None = Field(default=None, description="HCP name")
    limit: int = Field(default=5, ge=1, le=10)


class ScheduleFollowUpInput(BaseModel):
    due_date: date
    follow_up_type: Literal["Call", "Email", "Meeting", "Send material", "Other"]
    purpose: str = Field(min_length=3, max_length=1000)
    priority: Literal["Low", "Medium", "High"] = "Medium"


@tool
async def log_interaction(
    hcp_name: str = "",
    hcp_id: int | None = None,
    specialty: str = "",
    organization: str = "",
    interaction_date: date | None = None,
    interaction_type: InteractionType | None = None,
    products_discussed: list[str] | None = None,
    topics_discussed: list[str] | None = None,
    sentiment: Sentiment | None = None,
    materials_shared: list[str] | None = None,
    notes: str = "",
    follow_up_required: bool = False,
    follow_up_date: date | None = None,
    session_id: Annotated[str, InjectedToolArg] = "",
) -> str:
    """Create and persist a new HCP interaction from natural-language details.

    Use this for a new meeting, call, email, conference discussion, or other
    interaction. Extract only information stated or clearly implied by the user.
    """
    form = InteractionForm(
        hcp_id=hcp_id,
        hcp_name=hcp_name,
        specialty=specialty,
        organization=organization,
        interaction_date=interaction_date,
        interaction_type=interaction_type,
        products_discussed=products_discussed or [],
        topics_discussed=topics_discussed or [],
        sentiment=sentiment,
        materials_shared=materials_shared or [],
        notes=notes,
        follow_up_required=follow_up_required,
        follow_up_date=follow_up_date,
    )

    async with AsyncSessionFactory() as db:
        matched_hcp: HCP | None = None

        if form.hcp_name:
            statement = select(HCP).where(
                func.lower(HCP.full_name) == form.hcp_name.strip().lower()
            )
            if form.organization:
                statement = statement.where(
                    func.lower(HCP.organization) == form.organization.strip().lower()
                )
            matched_hcp = (await db.execute(statement.limit(1))).scalar_one_or_none()

        if matched_hcp is not None:
            form.hcp_id = matched_hcp.id
            if not form.specialty:
                form.specialty = matched_hcp.specialty
            if not form.organization:
                form.organization = matched_hcp.organization

        row = Interaction(
            session_id=session_id,
            hcp_id=form.hcp_id,
            hcp_name=form.hcp_name,
            specialty=form.specialty,
            organization=form.organization,
            interaction_date=form.interaction_date,
            interaction_type=form.interaction_type,
            products_discussed=form.products_discussed,
            topics_discussed=form.topics_discussed,
            sentiment=form.sentiment,
            materials_shared=form.materials_shared,
            notes=form.notes,
            follow_up_required=form.follow_up_required,
            follow_up_date=form.follow_up_date,
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)

        form.interaction_id = row.id

    return _json(
        {
            "operation": "replace",
            "form": form.model_dump(mode="json"),
            "message": "The interaction details have been added to the form and saved.",
        }
    )


@tool
async def edit_interaction(
    hcp_id: int | None = None,
    hcp_name: str | None = None,
    specialty: str | None = None,
    organization: str | None = None,
    interaction_date: date | None = None,
    interaction_type: InteractionType | None = None,
    products_discussed: list[str] | None = None,
    topics_discussed: list[str] | None = None,
    sentiment: Sentiment | None = None,
    materials_shared: list[str] | None = None,
    notes: str | None = None,
    follow_up_required: bool | None = None,
    follow_up_date: date | None = None,
    current_form: Annotated[dict[str, Any], InjectedToolArg] = None,
) -> str:
    """Update only the HCP interaction fields explicitly corrected by the user.

    Preserve every existing field that the user did not mention. Use this when
    the user says something was wrong, changed, or needs correction.
    Pass only the fields that changed; omit everything else.
    """
    patch = InteractionPatch(
        hcp_id=hcp_id,
        hcp_name=hcp_name,
        specialty=specialty,
        organization=organization,
        interaction_date=interaction_date,
        interaction_type=interaction_type,
        products_discussed=products_discussed,
        topics_discussed=topics_discussed,
        sentiment=sentiment,
        materials_shared=materials_shared,
        notes=notes,
        follow_up_required=follow_up_required,
        follow_up_date=follow_up_date,
    ).model_dump(
        mode="json",
        exclude_unset=True,
        exclude_none=True,
    )

    if not patch:
        return _json(
            {
                "operation": "informational",
                "message": "No explicit field changes were detected.",
                "changes": {},
            }
        )

    existing = InteractionForm.model_validate(current_form or {})
    merged_data = existing.model_dump(mode="json")
    merged_data.update(patch)
    updated_form = InteractionForm.model_validate(merged_data)

    if updated_form.interaction_id is not None:
        async with AsyncSessionFactory() as db:
            row = await db.get(Interaction, updated_form.interaction_id)
            if row is not None:
                editable_fields = {
                    "hcp_id",
                    "hcp_name",
                    "specialty",
                    "organization",
                    "interaction_date",
                    "interaction_type",
                    "products_discussed",
                    "topics_discussed",
                    "sentiment",
                    "materials_shared",
                    "notes",
                    "follow_up_required",
                    "follow_up_date",
                }
                for field_name, value in patch.items():
                    if field_name in editable_fields:
                        setattr(row, field_name, value)
                await db.commit()

    return _json(
        {
            "operation": "replace",
            "form": updated_form.model_dump(mode="json"),
            "changes": patch,
            "message": "Only the requested interaction fields were updated.",
        }
    )


@tool(args_schema=SearchHCPInput)
async def search_hcp(
    name: str | None = None,
    specialty: str | None = None,
    organization: str | None = None,
    city: str | None = None,
    limit: int = 5,
) -> str:
    """Search CRM HCP records by name, specialty, organization, or city.

    Use this when the representative asks to find, identify, or select an HCP.
    When exactly one result is found, its profile can populate the form.
    """
    filters = []
    if name:
        filters.append(HCP.full_name.ilike(f"%{name.strip()}%"))
    if specialty:
        filters.append(HCP.specialty.ilike(f"%{specialty.strip()}%"))
    if organization:
        filters.append(HCP.organization.ilike(f"%{organization.strip()}%"))
    if city:
        filters.append(HCP.city.ilike(f"%{city.strip()}%"))

    if not filters:
        return _json(
            {
                "operation": "informational",
                "matches": [],
                "message": "Provide at least one HCP search criterion.",
            }
        )

    async with AsyncSessionFactory() as db:
        statement = select(HCP).where(*filters).order_by(HCP.full_name).limit(limit)
        rows = list((await db.execute(statement)).scalars().all())

    matches = [
        HCPProfile(
            hcp_id=row.id,
            hcp_name=row.full_name,
            specialty=row.specialty,
            organization=row.organization,
            city=row.city,
            email=row.email,
            phone=row.phone,
        ).model_dump(mode="json")
        for row in rows
    ]

    if len(matches) == 1:
        match = matches[0]
        return _json(
            {
                "operation": "patch",
                "changes": {
                    "hcp_id": match["hcp_id"],
                    "hcp_name": match["hcp_name"],
                    "specialty": match["specialty"],
                    "organization": match["organization"],
                },
                "matches": matches,
                "message": f"Selected {match['hcp_name']} from the CRM.",
            }
        )

    if not matches:
        message = "No matching HCP was found."
    else:
        message = f"Found {len(matches)} matching HCPs. Ask the user which one to select."

    return _json(
        {
            "operation": "informational",
            "matches": matches,
            "message": message,
        }
    )


@tool
async def get_interaction_history(
    hcp_id: int | None = None,
    hcp_name: str | None = None,
    limit: int = 5,
    current_form: Annotated[dict[str, Any], InjectedToolArg] = None,
) -> str:
    """Retrieve recent CRM interactions for an HCP.

    Use this when the representative asks what happened previously, what was
    discussed last time, or requests interaction history.
    """
    current = current_form or {}
    resolved_hcp_id = hcp_id or current.get("hcp_id")
    resolved_hcp_name = hcp_name or current.get("hcp_name")

    if not resolved_hcp_id and not resolved_hcp_name:
        return _json(
            {
                "operation": "informational",
                "history": [],
                "message": "Select or name an HCP before requesting history.",
            }
        )

    async with AsyncSessionFactory() as db:
        statement = select(Interaction)
        if resolved_hcp_id:
            statement = statement.where(Interaction.hcp_id == resolved_hcp_id)
        else:
            statement = statement.where(
                Interaction.hcp_name.ilike(f"%{str(resolved_hcp_name).strip()}%")
            )

        statement = statement.order_by(
            desc(Interaction.interaction_date),
            desc(Interaction.created_at),
        ).limit(limit)
        rows = list((await db.execute(statement)).scalars().all())

    history = [
        InteractionHistoryItem(
            interaction_id=row.id,
            interaction_date=row.interaction_date,
            interaction_type=row.interaction_type,
            products_discussed=row.products_discussed or [],
            topics_discussed=row.topics_discussed or [],
            sentiment=row.sentiment,
            materials_shared=row.materials_shared or [],
            notes=row.notes,
            follow_up_required=row.follow_up_required,
            follow_up_date=row.follow_up_date,
        ).model_dump(mode="json")
        for row in rows
    ]

    return _json(
        {
            "operation": "informational",
            "history": history,
            "message": (
                f"Found {len(history)} recent interaction(s)."
                if history
                else "No previous interactions were found for this HCP."
            ),
        }
    )


@tool
async def schedule_follow_up(
    due_date: date,
    follow_up_type: str,
    purpose: str,
    priority: str = "Medium",
    session_id: Annotated[str, InjectedToolArg] = "",
    current_form: Annotated[dict[str, Any], InjectedToolArg] = None,
) -> str:
    """Create a follow-up activity for the HCP in the current interaction.

    Use this for requests to schedule a call, email, meeting, material delivery,
    or another next action. Also mark the current interaction as requiring follow-up.
    """
    current = InteractionForm.model_validate(current_form or {})

    if not current.hcp_id and not current.hcp_name:
        return _json(
            {
                "operation": "informational",
                "message": "An HCP must be selected before scheduling a follow-up.",
            }
        )

    async with AsyncSessionFactory() as db:
        row = FollowUp(
            session_id=session_id,
            hcp_id=current.hcp_id,
            interaction_id=current.interaction_id,
            hcp_name=current.hcp_name,
            due_date=due_date,
            follow_up_type=follow_up_type,
            purpose=purpose,
            priority=priority,
            status="Pending",
        )
        db.add(row)

        if current.interaction_id is not None:
            interaction_row = await db.get(Interaction, current.interaction_id)
            if interaction_row is not None:
                interaction_row.follow_up_required = True
                interaction_row.follow_up_date = due_date

        await db.commit()
        await db.refresh(row)

    follow_up = FollowUpData(
        follow_up_id=row.id,
        hcp_id=row.hcp_id,
        interaction_id=row.interaction_id,
        hcp_name=row.hcp_name,
        due_date=row.due_date,
        follow_up_type=row.follow_up_type,
        purpose=row.purpose,
        priority=row.priority,
        status=row.status,
    )

    return _json(
        {
            "operation": "patch",
            "changes": {
                "follow_up_required": True,
                "follow_up_date": due_date.isoformat(),
            },
            "follow_up": follow_up.model_dump(mode="json"),
            "message": f"Follow-up scheduled for {due_date.isoformat()}.",
        }
    )


CRM_TOOLS = [
    log_interaction,
    edit_interaction,
    search_hcp,
    get_interaction_history,
    schedule_follow_up,
]

TOOLS_BY_NAME = {crm_tool.name: crm_tool for crm_tool in CRM_TOOLS}
