"""
AuditAI - Base Tool Class

Abstract base class for all MCP tools used by the AuditAI agent.
"""

from __future__ import annotations
import time
from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    success: bool = Field(description="Whether the tool execution succeeded")
    data: dict[str, Any] = Field(default_factory=dict, description="The tool output data")
    error: str | None = Field(default=None, description="Error message if failed")
    latency_ms: float = Field(default=0.0, description="Execution time in ms")


class BaseTool(ABC):
    name: str = "base_tool"
    description: str = "Base tool - override in subclass"

    def run(self, input_data: dict[str, Any]) -> ToolResult:
        start_time = time.perf_counter()
        try:
            result_data = self.execute(input_data)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return ToolResult(success=True, data=result_data, latency_ms=elapsed_ms)
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return ToolResult(success=False, data={}, error=str(e), latency_ms=elapsed_ms)

    @abstractmethod
    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        ...

    def get_schema(self) -> dict[str, str]:
        return {"name": self.name, "description": self.description}