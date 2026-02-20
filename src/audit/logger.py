"""
AuditAI - Audit Logger
========================

Central audit logging system that captures every agent step.
Supports dual logging: local file + Weilchain blockchain.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.audit.schemas import AuditLogEntry, AuditStepType, AuditTrail
from src.audit.weilchain import WeilchainBridge

console = Console()


class AuditLogger:
    """
    Comprehensive audit logger that records every step of the agent workflow.

    Features:
      - Local JSON Lines file logging
      - Console output with rich formatting
      - Weilchain blockchain submission (via WeilchainBridge)
      - Full workflow trail management
    """

    def __init__(
        self,
        on_chain: bool = True,
        verbose: bool = False,
        local_file: bool = True,
        local_file_path: str = "./logs/audit.jsonl",
    ) -> None:
        self.on_chain = on_chain
        self.verbose = verbose
        self.local_file = local_file
        self.local_file_path = local_file_path

        self._trail: AuditTrail | None = None
        self._bridge: WeilchainBridge | None = None

        # Initialize Weilchain bridge if on-chain logging is enabled
        if self.on_chain:
            self._bridge = WeilchainBridge(
                rpc_url=os.getenv("WEILCHAIN_RPC_URL", "https://rpc.weilchain.io"),
                wallet_key=os.getenv("WEILCHAIN_WALLET_KEY", ""),
                applet_id=os.getenv("WEILLIPTIC_APPLET_ID", ""),
            )
            self._bridge.connect()

        # Ensure log directory exists
        if self.local_file:
            Path(self.local_file_path).parent.mkdir(parents=True, exist_ok=True)

    def start_workflow(self, query: str) -> str:
        """
        Start a new audit workflow for a query.

        Args:
            query: The user's original query.

        Returns:
            The unique workflow ID.
        """
        workflow_id = str(uuid.uuid4())
        self._trail = AuditTrail(
            workflow_id=workflow_id,
            query=query,
        )

        # Log workflow start
        self.log_step(
            step_type=AuditStepType.WORKFLOW_START,
            input_data={"query": query},
            output_data={"workflow_id": workflow_id},
        )

        if self.verbose:
            console.print(
                Panel(
                    f"[bold cyan]Workflow Started[/bold cyan]\n"
                    f"ID: [dim]{workflow_id}[/dim]\n"
                    f"Query: {query}",
                    border_style="cyan",
                    title="🔍 AuditAI",
                )
            )

        return workflow_id

    def log_step(
        self,
        step_type: AuditStepType | str,
        input_data: dict[str, Any] | None = None,
        output_data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        tool_name: str | None = None,
        tool_success: bool | None = None,
        model_name: str | None = None,
        tokens: dict[str, Any] | None = None,
        success: bool = True,
        error_message: str | None = None,
    ) -> AuditLogEntry | None:
        """
        Log a single step in the audit trail.
        """
        if self._trail is None:
            return None

        # Convert string step_type to enum if needed
        if isinstance(step_type, str):
            try:
                step_type = AuditStepType(step_type)
            except ValueError:
                step_type = AuditStepType.LLM_REASONING

        step_number = self._trail.total_steps + 1

        entry = AuditLogEntry(
            workflow_id=self._trail.workflow_id,
            step_number=step_number,
            step_type=step_type,
            input_data=input_data or {},
            output_data=output_data or {},
            model_name=model_name,
            prompt_tokens=tokens.get("prompt_tokens") if tokens else None,
            completion_tokens=tokens.get("completion_tokens") if tokens else None,
            total_tokens=tokens.get("total_tokens") if tokens else None,
            tool_name=tool_name,
            tool_success=tool_success,
            success=success,
            error_message=error_message,
            metadata=metadata or {},
        )

        # Submit to Weilchain if enabled
        if self.on_chain and self._bridge:
            try:
                result = self._bridge.submit_audit_entry(
                    entry.model_dump(mode="json")
                )
                entry.tx_hash = result.get("tx_hash")
                entry.block_number = result.get("block_number")
            except Exception as e:
                if self.verbose:
                    console.print(f"[yellow]⚠ On-chain submission failed: {e}[/yellow]")

        # Add to trail
        self._trail.add_entry(entry)

        # Write to local file
        if self.local_file:
            self._write_local(entry)

        # Verbose console output
        if self.verbose:
            self._print_step(entry)

        return entry

    def log_from_state(self, audit_entries: list[dict[str, Any]]) -> None:
        """
        Log multiple audit entries from agent state (batch processing).
        Called after the agent finishes to process all accumulated entries.
        """
        for entry_data in audit_entries:
            step_type = entry_data.get("step_type", "llm_reasoning")
            metadata = entry_data.get("metadata", {})

            self.log_step(
                step_type=step_type,
                input_data=entry_data.get("input_data", {}),
                output_data=entry_data.get("output_data", {}),
                metadata=metadata,
                model_name=metadata.get("model"),
                tokens=metadata.get("tokens") if isinstance(metadata.get("tokens"), dict) else None,
            )

    def complete_workflow(self, final_response: str, success: bool = True) -> None:
        """Complete the current workflow."""
        if self._trail is None:
            return

        self._trail.complete(final_response=final_response, success=success)

        self.log_step(
            step_type=AuditStepType.WORKFLOW_END,
            input_data={},
            output_data={
                "final_response_length": len(final_response),
                "total_steps": self._trail.total_steps,
                "total_tools_called": self._trail.total_tools_called,
            },
        )

        if self.verbose:
            self._print_summary()

    def get_trail(self) -> AuditTrail | None:
        """Get the current audit trail."""
        return self._trail

    def _write_local(self, entry: AuditLogEntry) -> None:
        """Write an entry to the local log file."""
        try:
            with open(self.local_file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry.model_dump(mode="json"), default=str) + "\n")
        except Exception:
            pass  # Don't crash on file write failure

    def _print_step(self, entry: AuditLogEntry) -> None:
        """Print a formatted step to the console."""
        step_icons = {
            AuditStepType.LLM_REASONING: "🧠",
            AuditStepType.TOOL_SELECTION: "🔧",
            AuditStepType.TOOL_EXECUTION: "⚡",
            AuditStepType.TERMINATION_CHECK: "🔄",
            AuditStepType.FINAL_RESPONSE: "✅",
            AuditStepType.ERROR: "❌",
            AuditStepType.ERROR_RECOVERY: "🔄",
            AuditStepType.WORKFLOW_START: "🚀",
            AuditStepType.WORKFLOW_END: "🏁",
        }
        icon = step_icons.get(entry.step_type, "📋")
        tx_info = f" | tx: [dim]{entry.tx_hash[:16]}...[/dim]" if entry.tx_hash else ""

        console.print(
            f"  {icon} [bold]Step {entry.step_number}[/bold] "
            f"[cyan]{entry.step_type.value}[/cyan]{tx_info}"
        )

    def _print_summary(self) -> None:
        """Print a formatted audit trail summary."""
        if self._trail is None:
            return

        summary = self._trail.to_summary()

        table = Table(title="📋 Audit Trail Summary", border_style="blue")
        table.add_column("Field", style="bold cyan")
        table.add_column("Value", style="white")

        table.add_row("Workflow ID", summary["workflow_id"][:16] + "...")
        table.add_row("Query", summary["query"][:60] + ("..." if len(summary["query"]) > 60 else ""))
        table.add_row("Total Steps", str(summary["total_steps"]))
        table.add_row("Tools Called", str(summary["total_tools_called"]))
        table.add_row("Total Tokens", str(summary["total_tokens_used"]))
        table.add_row("Success", "✅" if summary["success"] else "❌")

        if summary.get("duration_ms"):
            table.add_row("Duration", f"{summary['duration_ms']:.0f}ms")

        console.print(table)

        # Print on-chain proof
        on_chain_entries = [
            e for e in (self._trail.entries if self._trail else []) if e.tx_hash
        ]
        if on_chain_entries:
            console.print(
                f"\n  🔗 [bold green]{len(on_chain_entries)} steps logged on Weilchain[/bold green]"
            )
            for e in on_chain_entries[:3]:
                console.print(f"     tx: [dim]{e.tx_hash}[/dim]")
            if len(on_chain_entries) > 3:
                console.print(f"     ... and {len(on_chain_entries) - 3} more")
