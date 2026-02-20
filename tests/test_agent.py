"""
AuditAI - Agent Tests

Unit tests for the LangGraph agent components.
"""

import pytest
from src.agent.state import AgentState, AuditEntry, ToolCall

class TestAgentState:
    """Tests for the AgentState schema."""

    def test_create_default_state(self):
        """Test creating a state with default values."""
        state = AgentState(query="Test query")
        assert state.query == "Test query"
        assert state.is_complete is False
        assert state.current_step == 0
        assert state.current_iteration == 0
        assert state.max_iterations == 10
        assert state.final_response is None
        assert state.errors == []
        assert state.audit_entries == []
        assert state.tools_called == []

    def test_audit_entry_creation(self):
        """Test creating an audit entry."""
        entry = AuditEntry(
            step_number=1,
            step_type="llm_reasoning",
            timestamp="2026-02-20T10:00:00Z",
            input_data={"query": "test"},
            output_data={"reasoning": "test reasoning"},
        )
        assert entry.step_number == 1
        assert entry.step_type == "llm_reasoning"
        assert entry.success is True
        assert entry.tx_hash is None

    def test_tool_call_creation(self):
        """Test creating a tool call record."""
        tool_call = ToolCall(
            tool_name="price_feed",
            tool_input={"token": "bitcoin"},
            tool_output={"price": 50000},
            success=True,
            latency_ms=150.5,
        )
        assert tool_call.tool_name == "price_feed"
        assert tool_call.success is True
        assert tool_call.latency_ms == 150.5
