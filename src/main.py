"""
AuditAI - Application Entry Point
===================================

Usage:
  python -m src.main                           # Interactive mode
  python -m src.main --query "Your question"   # Single query mode
  python -m src.main --verbose                 # With verbose audit logging
  python -m src.main --mock-llm               # Mock LLM (no API key needed)
"""

import argparse
import os
import sys
import json

# Load environment variables before anything else
from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

from src.agent.graph import create_agent
from src.audit.logger import AuditLogger
from src.tools.price_feed import PriceFeedTool
from src.tools.news_feed import NewsFeedTool
from src.tools.onchain_data import OnchainDataTool

console = Console()


def print_banner() -> None:
    banner = """
# 🚀 AuditAI — Transparent AI Agent on Weilchain

**Every step. Every decision. Permanently logged on-chain.**

Type your query below, or type `exit` to quit.
Commands: `audit` (show last audit trail), `exit` (quit)
    """
    console.print(Panel(Markdown(banner), border_style="blue"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AuditAI - Transparent AI Agent on Weilchain",
    )
    parser.add_argument("--query", type=str, default=None, help="Run a single query and exit")
    parser.add_argument("--verbose", action="store_true", default=False, help="Enable verbose audit logging")
    parser.add_argument("--no-onchain", action="store_true", default=False, help="Disable on-chain audit logging")
    parser.add_argument("--mock-llm", action="store_true", default=False, help="Use mock LLM (no API key required)")
    return parser.parse_args()


def create_tools() -> list:
    """Initialize all MCP tools."""
    tools = [
        PriceFeedTool(),
        NewsFeedTool(api_key=os.getenv("NEWS_FEED_API_KEY")),
        OnchainDataTool(rpc_url=os.getenv("WEILCHAIN_RPC_URL")),
    ]
    return tools


def run_single_query(
    query: str,
    verbose: bool = False,
    on_chain: bool = True,
    mock_llm: bool = False,
) -> None:
    """Run a single query through the AuditAI agent."""
    console.print(f"\n[bold cyan]Query:[/bold cyan] {query}")
    console.print("[dim]Processing...[/dim]\n")

    # Set mock LLM flag
    if mock_llm:
        os.environ["AUDITAI_MOCK_LLM"] = "true"

    # Initialize audit logger
    audit_logger = AuditLogger(
        on_chain=on_chain,
        verbose=verbose,
        local_file=True,
    )

    # Start workflow
    workflow_id = audit_logger.start_workflow(query)

    # Initialize tools
    tools = create_tools()

    # Create and run the agent
    agent = create_agent(
        audit_logger=audit_logger,
        available_tools=tools,
        max_iterations=10,
    )

    try:
        # Invoke the agent
        initial_state = {
            "query": query,
            "messages": [],
            "audit_entries": [],
            "current_step": 0,
            "tools_called": [],
            "selected_tool": None,
            "tool_input": {},
            "is_complete": False,
            "max_iterations": 10,
            "current_iteration": 0,
            "requires_tool_call": False,
            "final_response": None,
            "reasoning": None,
            "errors": [],
        }

        result = agent.invoke(initial_state)

        # Process audit entries from agent state
        audit_entries = result.get("audit_entries", [])
        audit_logger.log_from_state(audit_entries)

        # Get final response
        final_response = result.get("final_response", "No response generated.")

        # Complete the workflow
        audit_logger.complete_workflow(final_response)

        # Display the response
        console.print(Panel(
            Markdown(final_response),
            title="🤖 AuditAI Response",
            border_style="green",
        ))

        # Show audit summary
        trail = audit_logger.get_trail()
        if trail:
            _print_audit_trail(trail, verbose)

    except Exception as e:
        error_msg = f"Agent execution error: {str(e)}"
        console.print(f"\n[bold red]❌ {error_msg}[/bold red]")
        audit_logger.complete_workflow(error_msg, success=False)

        if verbose:
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")

    # Store last trail for audit command
    run_single_query._last_trail = audit_logger.get_trail()


# Initialize the trail storage
run_single_query._last_trail = None


def _print_audit_trail(trail, verbose: bool = False) -> None:
    """Print a condensed audit trail summary."""
    summary = trail.to_summary()

    console.print("\n[bold blue]📋 Audit Trail[/bold blue]")

    # Quick stats line
    console.print(
        f"  Steps: [cyan]{summary['total_steps']}[/cyan] | "
        f"Tools: [cyan]{summary['total_tools_called']}[/cyan] | "
        f"Tokens: [cyan]{summary['total_tokens_used']}[/cyan] | "
        f"Status: {'[green]✅[/green]' if summary['success'] else '[red]❌[/red]'}"
    )

    # On-chain proof
    on_chain_entries = [e for e in trail.entries if e.tx_hash]
    if on_chain_entries:
        console.print(
            f"\n  🔗 [bold green]{len(on_chain_entries)} steps logged on Weilchain:[/bold green]"
        )
        for e in on_chain_entries[:5]:
            icon = {
                "llm_reasoning": "🧠",
                "tool_selection": "🔧",
                "tool_execution": "⚡",
                "final_response": "✅",
                "workflow_start": "🚀",
                "workflow_end": "🏁",
            }.get(e.step_type.value, "📋")
            console.print(
                f"     {icon} {e.step_type.value:20} → "
                f"[dim]tx:{e.tx_hash[:20]}... | block:{e.block_number}[/dim]"
            )
        if len(on_chain_entries) > 5:
            console.print(f"     ... and {len(on_chain_entries) - 5} more entries")


def run_interactive(verbose: bool = False, on_chain: bool = True, mock_llm: bool = False) -> None:
    """Run the interactive REPL mode."""
    print_banner()

    while True:
        try:
            user_input = console.input("\n[bold green]You>[/bold green] ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                console.print("\n[bold blue]Goodbye! 👋[/bold blue]")
                break
            if user_input.lower() == "audit":
                if run_single_query._last_trail:
                    _print_audit_trail(run_single_query._last_trail, verbose=True)
                else:
                    console.print("[yellow]No audit trail available yet. Run a query first.[/yellow]")
                continue

            run_single_query(user_input, verbose=verbose, on_chain=on_chain, mock_llm=mock_llm)

        except KeyboardInterrupt:
            console.print("\n\n[bold blue]Interrupted. Goodbye! 👋[/bold blue]")
            break


def main() -> None:
    args = parse_args()
    on_chain = not args.no_onchain

    if args.query:
        run_single_query(
            args.query,
            verbose=args.verbose,
            on_chain=on_chain,
            mock_llm=args.mock_llm,
        )
    else:
        run_interactive(
            verbose=args.verbose,
            on_chain=on_chain,
            mock_llm=args.mock_llm,
        )


if __name__ == "__main__":
    main()