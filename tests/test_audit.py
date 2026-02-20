"""
AuditAI - Audit Logger Tests

Unit tests for the audit logging components.
"""

import pytest
from src.audit.schemas import AuditLogEntry, AuditStepType, AuditTrail

class TestAuditSchemas:
    """Tests for audit log schemas."""

    def test_create_audit_entry(self):
        """Test creating an audit log entry."""
        entry = AuditLogEntry(
            workflow_id="test-workflow-123",
            step_number=1,
            step_type=AuditStepType.LLM_REASONING,
            input_data={"query": "test"},
            output_data={"reasoning": "thinking..."},
        )
        assert entry.workflow_id == "test-workflow-123"
        assert entry.step_type == AuditStepType.LLM_REASONING
        assert entry.success is True

    def test_audit_trail_add_entry(self):
        """Test adding entries to an audit trail."""
        trail = AuditTrail(
            workflow_id="test-trail",
            query="Test query",
        )
        assert trail.total_steps == 0

        entry = AuditLogEntry(
            workflow_id="test-trail",
            step_number=1,
            step_type=AuditStepType.WORKFLOW_START,
        )
        trail.add_entry(entry)
        assert trail.total_steps == 1

    def test_audit_trail_complete(self):
        """Test completing an audit trail."""
        trail = AuditTrail(
            workflow_id="test-trail",
            query="Test query",
        )
        trail.complete(final_response="Done!", success=True)
        assert trail.completed_at is not None
        assert trail.final_response == "Done!"
        assert trail.success is True

    def test_audit_trail_summary(self):
        """Test generating audit trail summary."""
        trail = AuditTrail(
            workflow_id="test-trail",
            query="Test query",
        )
        entry = AuditLogEntry(
            workflow_id="test-trail",
            step_number=1,
            step_type=AuditStepType.TOOL_EXECUTION,
            tool_name="price_feed",
            total_tokens=100,
        )
        trail.add_entry(entry)

        summary = trail.to_summary()
        assert summary["total_steps"] == 1
        assert summary["total_tokens_used"] == 100
        assert summary["total_tools_called"] == 1
