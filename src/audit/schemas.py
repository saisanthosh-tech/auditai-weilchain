"""
AuditAI - Audit Log Schemas

Defines the data schemas for audit log entries.
"""

from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class AuditStepType(str, Enum):
    LLM_REASONING = "llm_reasoning"
    TOOL_SELECTION = "tool_selection"
    TOOL_EXECUTION = "tool_execution"
    TERMINATION_CHECK = "termination_check"
    FINAL_RESPONSE = "final_response"
    ERROR = "error"
    ERROR_RECOVERY = "error_recovery"
    WORKFLOW_START = "workflow_start"
    WORKFLOW_END = "workflow_end"


class AuditLogEntry(BaseModel):
    workflow_id: str = Field(description="Unique ID for the entire workflow")
    step_number: int = Field(description="Sequential step number")
    step_type: AuditStepType = Field(description="Type of step")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: float = Field(default=0.0)
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] = Field(default_factory=dict)
    model_name: str | None = Field(default=None)
    prompt_tokens: int | None = Field(default=None)
    completion_tokens: int | None = Field(default=None)
    total_tokens: int | None = Field(default=None)
    tool_name: str | None = Field(default=None)
    tool_success: bool | None = Field(default=None)
    tx_hash: str | None = Field(default=None)
    block_number: int | None = Field(default=None)
    success: bool = Field(default=True)
    error_message: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditTrail(BaseModel):
    workflow_id: str = Field(description="Unique workflow ID")
    query: str = Field(description="Original user query")
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = Field(default=None)
    entries: list[AuditLogEntry] = Field(default_factory=list)
    total_steps: int = Field(default=0)
    total_tokens_used: int = Field(default=0)
    total_tools_called: int = Field(default=0)
    success: bool = Field(default=True)
    final_response: str | None = Field(default=None)

    def add_entry(self, entry: AuditLogEntry) -> None:
        self.entries.append(entry)
        self.total_steps = len(self.entries)
        if entry.total_tokens:
            self.total_tokens_used += entry.total_tokens
        if entry.step_type == AuditStepType.TOOL_EXECUTION:
            self.total_tools_called += 1

    def complete(self, final_response: str, success: bool = True) -> None:
        self.completed_at = datetime.now(timezone.utc)
        self.final_response = final_response
        self.success = success

    def to_summary(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "query": self.query,
            "total_steps": self.total_steps,
            "total_tokens_used": self.total_tokens_used,
            "total_tools_called": self.total_tools_called,
            "success": self.success,
            "duration_ms": (
                (self.completed_at - self.started_at).total_seconds() * 1000
                if self.completed_at else None
            ),
            "steps": [
                {
                    "step": e.step_number,
                    "type": e.step_type.value,
                    "success": e.success,
                    "tx_hash": e.tx_hash,
                }
                for e in self.entries
            ],
        }