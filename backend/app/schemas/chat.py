from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=5000)
    # None means "load the last form for this session".
    # {} means "start from an explicitly empty form".
    current_form: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    assistant_message: str
    current_form: dict[str, Any]
    active_tool: str | None
    tool_result: dict[str, Any] | None


class SessionResponse(BaseModel):
    session_id: str
    current_form: dict[str, Any]
    messages: list[dict[str, Any]]
