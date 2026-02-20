"""
AuditAI - Application Entry Point
===================================

Usage:
  python -m src.main                          # Interactive mode
  python -m src.main --query "Your question"   # Single query mode
  python -m src.main --verbose                 # With verbose logging
"""

import argparse
import sys

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

def print_banner() -> None:
    banner = """
# AuditAI - Transparent AI Agent on Weilchain

**Every step. Every decision. Permanently logged on-chain.**

Type your query below, or type `exit` to quit.
    """
    console.print(Panel(Markdown(banner), border_style="blue"))

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AuditAI - Transparent AI Agent on Weilchain",
    )
    parser.add_argument("--query", type=str, default=None, help="Run a single query and exit")
    parser.add_argument("--verbose", action="store_true", default=False, help="Enable verbose audit logging")
    parser.add_argument("--no-onchain", action="store_true", default=False, help="Disable on-chain audit logging")
    return parser.parse_args()

def run_single_query(query: str, verbose: bool = False, on_chain: bool = True) -> None:
    console.print(f"\n[bold cyan]Query:[/bold cyan] {query}")
    console.print("[dim]Processing...[/dim]\n")

    # TODO: Initialize agent and audit logger
    # from src.agent.graph import create_agent
    # from src.audit.logger import AuditLogger
    # audit_logger = AuditLogger(on_chain=on_chain, verbose=verbose)
    # agent = create_agent(audit_logger=audit_logger)
    # result = agent.invoke({"query": query})

    console.print(
        Panel(
            "[yellow]Agent not yet initialized. Implement src/agent/graph.py to get started.[/yellow]",
            title="Setup Required",
            border_style="yellow",
        )
    )

def run_interactive(verbose: bool = False, on_chain: bool = True) -> None:
    print_banner()

    while True:
        try:
            user_input = console.input("\n[bold green]You>[/bold green] ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                console.print("\n[bold blue]Goodbye![/bold blue]")
                break
            if user_input.lower() == "audit":
                console.print("[yellow]Audit trail not yet available.[/yellow]")
                continue
            run_single_query(user_input, verbose=verbose, on_chain=on_chain)
        except KeyboardInterrupt:
            console.print("\n\n[bold blue]Interrupted. Goodbye![/bold blue]")
            break

def main() -> None:
    args = parse_args()
    on_chain = not args.no_onchain
    if args.query:
        run_single_query(args.query, verbose=args.verbose, on_chain=on_chain)
    else:
        run_interactive(verbose=args.verbose, on_chain=on_chain)

if __name__ == "__main__":
    main()