from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import FollowUp, HCP, Interaction
from app.database.session import get_db
from app.schemas.resources import FollowUpResponse, HCPResponse, InteractionResponse


router = APIRouter(tags=["CRM Data"])


@router.get("/hcps", response_model=list[HCPResponse])
async def list_hcps(
    q: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[HCPResponse]:
    statement = select(HCP)
    if q:
        search = f"%{q.strip()}%"
        statement = statement.where(
            or_(
                HCP.full_name.ilike(search),
                HCP.specialty.ilike(search),
                HCP.organization.ilike(search),
                HCP.city.ilike(search),
            )
        )
    statement = statement.order_by(HCP.full_name).limit(limit)
    rows = list((await db.execute(statement)).scalars().all())
    return [
        HCPResponse(
            id=row.id,
            full_name=row.full_name,
            specialty=row.specialty,
            organization=row.organization,
            city=row.city,
            email=row.email,
            phone=row.phone,
        )
        for row in rows
    ]


@router.get("/interactions", response_model=list[InteractionResponse])
async def list_interactions(
    hcp_id: int | None = None,
    session_id: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[InteractionResponse]:
    statement = select(Interaction)
    if hcp_id is not None:
        statement = statement.where(Interaction.hcp_id == hcp_id)
    if session_id:
        statement = statement.where(Interaction.session_id == session_id)
    statement = statement.order_by(desc(Interaction.created_at)).limit(limit)
    rows = list((await db.execute(statement)).scalars().all())
    return [InteractionResponse(**_interaction_dict(row)) for row in rows]


@router.get("/interactions/{interaction_id}", response_model=InteractionResponse)
async def get_interaction(
    interaction_id: int,
    db: AsyncSession = Depends(get_db),
) -> InteractionResponse:
    row = await db.get(Interaction, interaction_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found",
        )
    return InteractionResponse(**_interaction_dict(row))


@router.get("/follow-ups", response_model=list[FollowUpResponse])
async def list_follow_ups(
    hcp_id: int | None = None,
    status_value: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[FollowUpResponse]:
    statement = select(FollowUp)
    if hcp_id is not None:
        statement = statement.where(FollowUp.hcp_id == hcp_id)
    if status_value:
        statement = statement.where(FollowUp.status.ilike(status_value))
    statement = statement.order_by(FollowUp.due_date, FollowUp.created_at).limit(limit)
    rows = list((await db.execute(statement)).scalars().all())
    return [
        FollowUpResponse(
            id=row.id,
            session_id=row.session_id,
            hcp_id=row.hcp_id,
            interaction_id=row.interaction_id,
            hcp_name=row.hcp_name,
            due_date=row.due_date,
            follow_up_type=row.follow_up_type,
            purpose=row.purpose,
            priority=row.priority,
            status=row.status,
            created_at=row.created_at,
        )
        for row in rows
    ]


def _interaction_dict(row: Interaction) -> dict:
    return {
        "id": row.id,
        "session_id": row.session_id,
        "hcp_id": row.hcp_id,
        "hcp_name": row.hcp_name,
        "specialty": row.specialty,
        "organization": row.organization,
        "interaction_date": row.interaction_date,
        "interaction_type": row.interaction_type,
        "products_discussed": row.products_discussed or [],
        "topics_discussed": row.topics_discussed or [],
        "sentiment": row.sentiment,
        "materials_shared": row.materials_shared or [],
        "notes": row.notes,
        "follow_up_required": row.follow_up_required,
        "follow_up_date": row.follow_up_date,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }
