"""
AuditAI - Agent State Schema
==============================

Defines the state schema for the LangGraph agent.
The state is passed between nodes in the agent graph
and tracks the full lifecycle of a query.
"""

from __future__ import annotations

from typing import Annotated, Any
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


class AgentState(BaseModel):
    """
    The complete state of the AuditAI agent.

    This state is passed between nodes in the LangGraph graph.
    It tracks the user query, conversation messages, audit trail,
    tool calls, and workflow control flags.
    """

    # --- Core Query ---
    query: str = Field(description="The original user query")

    # --- Conversation Messages ---
    messages: Annotated[list, add_messages] = Field(
        default_factory=list,
        description="Conversation messages (LangGraph message format)",
    )

    # --- Audit Trail ---
    audit_entries: list[AuditEntry] = Field(
        default_factory=list,
        description="Ordered list of audit entries for this workflow",
    )
    current_step: int = Field(
        default=0, description="Current step number in the workflow"
    )

    # --- Tool Tracking ---
    tools_called: list[ToolCall] = Field(
        default_factory=list,
        description="List of all tool calls made during this workflow",
    )
    available_tools: list[str] = Field(
        default_factory=list,
        description="Names of tools available to the agent",
    )

    # --- Workflow Control ---
    is_complete: bool = Field(
        default=False, description="Whether the agent has finished processing"
    )
    max_iterations: int = Field(
        default=10, description="Maximum number of reasoning iterations"
    )
    current_iteration: int = Field(
        default=0, description="Current reasoning iteration"
    )
    requires_tool_call: bool = Field(
        default=False, description="Whether the agent needs to call a tool next"
    )

    # --- Final Output ---
    final_response: str | None = Field(
        default=None, description="The agent's final response to the user"
    )

    # --- Error Handling ---
    errors: list[str] = Field(
        default_factory=list, description="Any errors encountered during processing"
    )