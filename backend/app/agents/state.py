from typing import Annotated, Any, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class CRMState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    session_id: str
    current_form: dict[str, Any]
    active_tool: str | None
    tool_result: dict[str, Any] | None
    error: str | None
    llm_calls: int
