"""
AuditAI - Tools Tests

Unit tests for the MCP tool components.
"""

import pytest
from src.tools.base import BaseTool, ToolResult

class MockTool(BaseTool):
    """A mock tool for testing."""

    name = "mock_tool"
    description = "A mock tool for testing purposes"

    def execute(self, input_data: dict) -> dict:
        if input_data.get("fail"):
            raise RuntimeError("Mock failure")
        return {"result": f"Processed: {input_data.get('input', '')}"}

class TestBaseTool:
    """Tests for the BaseTool class."""

    def test_tool_success(self):
        """Test successful tool execution."""
        tool = MockTool()
        result = tool.run({"input": "test"})
        assert result.success is True
        assert result.data["result"] == "Processed: test"
        assert result.error is None
        assert result.latency_ms > 0

    def test_tool_failure(self):
        """Test tool execution failure."""
        tool = MockTool()
        result = tool.run({"fail": True})
        assert result.success is False
        assert result.error == "Mock failure"
        assert result.data == {}

    def test_tool_schema(self):
        """Test tool schema generation."""
        tool = MockTool()
        schema = tool.get_schema()
        assert schema["name"] == "mock_tool"
        assert "mock tool" in schema["description"].lower()
