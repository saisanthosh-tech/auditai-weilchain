"""
AuditAI - Agent State Schema
==============================

Defines the state schema for the LangGraph agent.
The state is passed between nodes in the agent graph
and tracks the full lifecycle of a query.

Uses TypedDict for LangGraph compatibility.
"""

from __future__ import annotations

from typing import Annotated, Any, TypedDict
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages


class AuditEntry(BaseModel):
    """A single audit log entry for one step of the agent."""

    step_number: int = Field(description="Sequential step number in the workflow")
    step_type: str = Field(
        description="Type of step: 'llm_reasoning', 'tool_selection', "
        "'tool_execution', 'termination_check', 'final_response', 'error'"
    )
    timestamp: str = Field(description="ISO 8601 timestamp of when this step occurred")
    input_data: dict[str, Any] = Field(
        default_factory=dict, description="Input data for this step"
    )
    output_data: dict[str, Any] = Field(
        default_factory=dict, description="Output data from this step"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (model, tokens, latency, etc.)",
    )
    tx_hash: str | None = Field(
        default=None, description="Weilchain transaction hash if logged on-chain"
    )
    success: bool = Field(default=True, description="Whether this step succeeded")
    error_message: str | None = Field(
        default=None, description="Error message if step failed"
    )


class ToolCall(BaseModel):
    """Represents a tool call made by the agent."""

    tool_name: str = Field(description="Name of the tool called")
    tool_input: dict[str, Any] = Field(
        default_factory=dict, description="Input parameters for the tool"
    )
    tool_output: dict[str, Any] = Field(
        default_factory=dict, description="Output returned by the tool"
    )
    success: bool = Field(default=True, description="Whether the tool call succeeded")
    latency_ms: float = Field(default=0.0, description="Tool execution time in milliseconds")


class AgentState(TypedDict, total=False):
    """
    The complete state of the AuditAI agent.

    This state is passed between nodes in the LangGraph graph.
    Uses TypedDict for proper LangGraph compatibility.
    """

    # --- Core Query ---
    query: str

    # --- Conversation Messages ---
    messages: Annotated[list, add_messages]

    # --- Audit Trail ---
    audit_entries: list[dict[str, Any]]
    current_step: int

    # --- Tool Tracking ---
    tools_called: list[dict[str, Any]]
    selected_tool: str | None
    tool_input: dict[str, Any]

    # --- Workflow Control ---
    is_complete: bool
    max_iterations: int
    current_iteration: int
    requires_tool_call: bool

    # --- Final Output ---
    final_response: str | None
    reasoning: str | None

    # --- Error Handling ---
    errors: list[str]