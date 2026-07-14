from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class HCP(Base, TimestampMixin):
    __tablename__ = "hcps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    specialty: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    organization: Mapped[str] = mapped_column(String(180), default="", nullable=False)
    city: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    interactions: Mapped[list[Interaction]] = relationship(
        back_populates="hcp",
        cascade="all, delete-orphan",
    )
    follow_ups: Mapped[list[FollowUp]] = relationship(
        back_populates="hcp",
        cascade="all, delete-orphan",
    )


class Interaction(Base, TimestampMixin):
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(120), index=True, nullable=False)

    hcp_id: Mapped[int | None] = mapped_column(
        ForeignKey("hcps.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    hcp_name: Mapped[str] = mapped_column(String(180), default="", nullable=False)
    specialty: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    organization: Mapped[str] = mapped_column(String(180), default="", nullable=False)

    interaction_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    interaction_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    products_discussed: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    topics_discussed: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    sentiment: Mapped[str | None] = mapped_column(String(20), nullable=True)
    materials_shared: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    follow_up_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    follow_up_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    hcp: Mapped[HCP | None] = relationship(back_populates="interactions")
    follow_ups: Mapped[list[FollowUp]] = relationship(
        back_populates="interaction",
        cascade="all, delete-orphan",
    )


class FollowUp(Base, TimestampMixin):
    __tablename__ = "follow_ups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(120), index=True, nullable=False)

    hcp_id: Mapped[int | None] = mapped_column(
        ForeignKey("hcps.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    interaction_id: Mapped[int | None] = mapped_column(
        ForeignKey("interactions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    hcp_name: Mapped[str] = mapped_column(String(180), default="", nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    follow_up_type: Mapped[str] = mapped_column(String(60), nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="Medium", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Pending", nullable=False)

    hcp: Mapped[HCP | None] = relationship(back_populates="follow_ups")
    interaction: Mapped[Interaction | None] = relationship(back_populates="follow_ups")


class AgentSession(Base, TimestampMixin):
    __tablename__ = "agent_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    current_form: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    active_tool: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
