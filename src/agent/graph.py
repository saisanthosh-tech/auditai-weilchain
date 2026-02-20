"""
AuditAI - LangGraph Agent Graph Definition

Defines the main workflow graph for the AuditAI agent. Wires together reasoning,
tool selection, execution, auditing, and termination/retry logic.

Uses the correct LangGraph API:
  - add_edge(START, ...) for entry point
  - add_edge(..., ...) for linear transitions
  - add_conditional_edges(...) for branching
  - END for terminal nodes
"""

from langgraph.graph import StateGraph, START, END

from src.agent.state import AgentState
from src.agent import nodes


def should_continue(state: dict) -> str:
    """
    Routing function for the termination check node.
    Determines whether the agent should continue reasoning or finish.
    """
    if state.get("errors") and len(state["errors"]) > 0:
        return "error"
    if state.get("is_complete", False):
        return "done"
    if state.get("requires_tool_call", False):
        return "use_tool"
    return "done"


def create_agent(audit_logger=None, available_tools=None, max_iterations=10):
    """
    Create the LangGraph-based AuditAI agent.

    Args:
        audit_logger: Optional audit logger for recording steps.
        available_tools: List of tool instances available to the agent.
        max_iterations: Max number of reasoning/tool call cycles.

    Returns:
        A compiled LangGraph agent ready to invoke.
    """
    g = StateGraph(AgentState)

    # Add nodes
    g.add_node("reasoning", nodes.reasoning_node)
    g.add_node("tool_selection", nodes.tool_selection_node)
    g.add_node("tool_execution", nodes.tool_execution_node)
    g.add_node("termination_check", nodes.termination_check_node)
    g.add_node("final_response", nodes.final_response_node)
    g.add_node("error_handling", nodes.error_handling_node)

    # Entry point: start with reasoning
    g.add_edge(START, "reasoning")

    # Reasoning -> Tool Selection
    g.add_edge("reasoning", "tool_selection")

    # Tool Selection -> conditional: either execute tool or go to termination check
    g.add_conditional_edges(
        "tool_selection",
        lambda state: "execute" if state.get("requires_tool_call") else "check",
        {
            "execute": "tool_execution",
            "check": "termination_check",
        },
    )

    # Tool Execution -> Termination Check
    g.add_edge("tool_execution", "termination_check")

    # Termination Check -> conditional: continue, done, or error
    g.add_conditional_edges(
        "termination_check",
        should_continue,
        {
            "use_tool": "reasoning",
            "done": "final_response",
            "error": "error_handling",
        },
    )

    # Error handling -> Final Response
    g.add_edge("error_handling", "final_response")

    # Final Response -> END
    g.add_edge("final_response", END)

    # Store tool and logger config in graph metadata
    config = {
        "audit_logger": audit_logger,
        "available_tools": available_tools or [],
        "max_iterations": max_iterations,
    }

    compiled = g.compile()
    # Attach config so nodes can access it
    compiled._auditai_config = config

    return compiled


def load_default_agent():
    """Returns the default AuditAI agent with no-op logger and default tools."""
    from src.audit.logger import AuditLogger
    from src.tools.price_feed import PriceFeedTool
    from src.tools.news_feed import NewsFeedTool
    from src.tools.onchain_data import OnchainDataTool

    tools = [PriceFeedTool(), NewsFeedTool(), OnchainDataTool()]
    return create_agent(
        audit_logger=AuditLogger(on_chain=False),
        available_tools=tools,
        max_iterations=10,
    )
