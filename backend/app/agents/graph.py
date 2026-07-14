from __future__ import annotations

import json
from typing import Any, Literal

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph

from app.agents.prompts import build_system_prompt
from app.agents.state import CRMState
from app.config import get_settings
from app.tools import CRM_TOOLS, TOOLS_BY_NAME


settings = get_settings()

llm = ChatGroq(
    api_key=settings.groq_api_key,
    model=settings.groq_model,
    temperature=0,
    max_retries=2,
)
llm_with_tools = llm.bind_tools(CRM_TOOLS)


async def assistant_node(state: CRMState) -> dict[str, Any]:
    system_message = SystemMessage(
        content=build_system_prompt(state.get("current_form", {}))
    )
    response = await llm_with_tools.ainvoke(
        [system_message, *state.get("messages", [])]
    )
    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def route_after_assistant(
    state: CRMState,
) -> Literal["execute_tools", "__end__"]:
    latest_message = state["messages"][-1]

    if state.get("llm_calls", 0) >= 5:
        return END

    if isinstance(latest_message, AIMessage) and latest_message.tool_calls:
        return "execute_tools"

    return END


def _apply_tool_result(
    current_form: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    operation = result.get("operation")

    if operation == "replace":
        return dict(result.get("form") or {})

    if operation == "patch":
        updated = dict(current_form)
        updated.update(result.get("changes") or {})
        return updated

    return current_form


async def execute_tools_node(state: CRMState) -> dict[str, Any]:
    latest_message = state["messages"][-1]
    current_form = dict(state.get("current_form", {}))
    session_id = state.get("session_id", "")

    tool_messages: list[ToolMessage] = []
    active_tool: str | None = None
    latest_result: dict[str, Any] | None = None
    latest_error: str | None = None

    for tool_call in latest_message.tool_calls:
        tool_name = tool_call["name"]
        active_tool = tool_name
        crm_tool = TOOLS_BY_NAME.get(tool_name)

        if crm_tool is None:
            raw_result = json.dumps(
                {
                    "operation": "informational",
                    "message": f"Unknown tool requested: {tool_name}",
                }
            )
            latest_error = f"Unknown tool: {tool_name}"
        else:
            tool_args = dict(tool_call.get("args") or {})

            # Runtime-only values are hidden from the LLM schema and injected here.
            if tool_name in {"log_interaction", "schedule_follow_up"}:
                tool_args["session_id"] = session_id
            if tool_name in {
                "edit_interaction",
                "get_interaction_history",
                "schedule_follow_up",
            }:
                tool_args["current_form"] = current_form

            try:
                raw_result = await crm_tool.ainvoke(tool_args)
            except Exception as exc:  # Keep the graph alive and give the LLM an error result.
                latest_error = str(exc)
                raw_result = json.dumps(
                    {
                        "operation": "informational",
                        "message": f"The {tool_name} tool failed: {exc}",
                        "error": str(exc),
                    }
                )

        try:
            parsed_result = json.loads(raw_result)
        except (TypeError, json.JSONDecodeError):
            parsed_result = {
                "operation": "informational",
                "message": str(raw_result),
            }

        current_form = _apply_tool_result(current_form, parsed_result)
        latest_result = parsed_result

        tool_messages.append(
            ToolMessage(
                content=json.dumps(parsed_result, default=str),
                tool_call_id=tool_call["id"],
                name=tool_name,
            )
        )

    return {
        "messages": tool_messages,
        "current_form": current_form,
        "active_tool": active_tool,
        "tool_result": latest_result,
        "error": latest_error,
    }


builder = StateGraph(CRMState)
builder.add_node("assistant", assistant_node)
builder.add_node("execute_tools", execute_tools_node)
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    route_after_assistant,
    {
        "execute_tools": "execute_tools",
        END: END,
    },
)
builder.add_edge("execute_tools", "assistant")

crm_graph = builder.compile()
