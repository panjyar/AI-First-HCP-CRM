from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import crm_graph
from app.database.models import AgentSession, ChatMessage
from app.database.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse, SessionResponse


router = APIRouter(tags=["AI Assistant"])


def _message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("text"):
                parts.append(str(item["text"]))
        return "\n".join(parts).strip()
    return str(content or "").strip()




async def _load_recent_messages(
    db: AsyncSession,
    session_id: str,
    limit: int = 12,
) -> list[HumanMessage | AIMessage]:
    statement = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
        .limit(limit)
    )
    rows = list((await db.execute(statement)).scalars().all())
    rows.reverse()

    messages: list[HumanMessage | AIMessage] = []
    for row in rows:
        if row.role == "user":
            messages.append(HumanMessage(content=row.content))
        elif row.role == "assistant":
            messages.append(AIMessage(content=row.content))
    return messages


async def _load_session_form(db: AsyncSession, session_id: str) -> dict[str, Any]:
    statement = select(AgentSession).where(AgentSession.session_id == session_id)
    row = (await db.execute(statement)).scalar_one_or_none()
    return dict(row.current_form) if row is not None else {}


async def _save_session_form(
    db: AsyncSession,
    session_id: str,
    current_form: dict[str, Any],
) -> None:
    statement = select(AgentSession).where(AgentSession.session_id == session_id)
    row = (await db.execute(statement)).scalar_one_or_none()

    if row is None:
        db.add(AgentSession(session_id=session_id, current_form=current_form))
    else:
        row.current_form = current_form


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    # Preserve the contract you already tested:
    # an explicit {} starts with an empty form; None restores session state.
    current_form = (
        request.current_form
        if request.current_form is not None
        else await _load_session_form(db, request.session_id)
    )

    previous_messages = await _load_recent_messages(db, request.session_id)

    db.add(
        ChatMessage(
            session_id=request.session_id,
            role="user",
            content=request.message,
        )
    )
    await db.commit()

    try:
        result = await crm_graph.ainvoke(
            {
                "messages": [*previous_messages, HumanMessage(content=request.message)],
                "session_id": request.session_id,
                "current_form": current_form,
                "active_tool": None,
                "tool_result": None,
                "error": None,
                "llm_calls": 0,
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {exc}",
        ) from exc

    assistant_message = ""
    for message in reversed(result.get("messages", [])):
        if isinstance(message, AIMessage) and message.content:
            assistant_message = _message_text(message.content)
            if assistant_message:
                break

    tool_result = result.get("tool_result")
    if not assistant_message and tool_result:
        assistant_message = str(tool_result.get("message") or "Action completed.")
    if not assistant_message:
        assistant_message = "I could not determine the requested CRM action."

    result_form = dict(result.get("current_form") or {})

    await _save_session_form(db, request.session_id, result_form)
    db.add(
        ChatMessage(
            session_id=request.session_id,
            role="assistant",
            content=assistant_message,
            active_tool=result.get("active_tool"),
        )
    )
    await db.commit()

    return ChatResponse(
        assistant_message=assistant_message,
        current_form=result_form,
        active_tool=result.get("active_tool"),
        tool_result=tool_result,
    )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> SessionResponse:
    current_form = await _load_session_form(db, session_id)
    statement = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at, ChatMessage.id)
    )
    rows = list((await db.execute(statement)).scalars().all())

    return SessionResponse(
        session_id=session_id,
        current_form=current_form,
        messages=[
            {
                "role": row.role,
                "content": row.content,
                "active_tool": row.active_tool,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ],
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def reset_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    await db.execute(delete(ChatMessage).where(ChatMessage.session_id == session_id))
    await db.execute(delete(AgentSession).where(AgentSession.session_id == session_id))
    await db.commit()
