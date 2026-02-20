"""
AuditAI - LangGraph Agent Graph Definition

Defines the main workflow graph for the AuditAI agent. Wires together reasoning,
tool selection, execution, auditing, and termination/retry logic.
"""

from langgraph.graph import StateGraph

from src.agent.state import AgentState
from src.agent import nodes


def create_agent(audit_logger=None, available_tools=None, max_iterations=10):
    """
    Create the LangGraph-based AuditAI agent.

    Args:
        audit_logger: Optional audit logger for recording steps.
        available_tools: List of tool instances/classes available to the agent.
        max_iterations: Max number of reasoning/tool call cycles.

    Returns:
        An initialized LangGraph StateGraph agent instance.
    """
    # Construct the graph, wiring to node functions from nodes.py
    g = StateGraph(AgentState)

    # Mapping node names to functions
    g.add_node("reasoning", nodes.reasoning_node)
    g.add_node("tool_selection", nodes.tool_selection_node)
    g.add_node("tool_execution", nodes.tool_execution_node)
    g.add_node("termination_check", nodes.termination_check_node)
    g.add_node("final_response", nodes.final_response_node)
    g.add_node("error_handling", nodes.error_handling_node)

    # Entry point
    g.set_entry("reasoning")

    # Graph transitions
    g.add_transition("reasoning", "tool_selection")
    g.add_transition("tool_selection", "tool_execution")
    g.add_transition("tool_execution", "termination_check")
    g.add_transition("termination_check", {
        "continue": "reasoning",
        "done": "final_response",
        "error": "error_handling"
    })
    g.add_transition("error_handling", "final_response")
    g.add_transition("final_response", None)  # Terminal

    # Context
    g.set_context(audit_logger=audit_logger,
                  available_tools=available_tools or [],
                  max_iterations=max_iterations)

    return g.compile()


# Optionally, easy shortcut for fast tests/imports
def load_default_agent():
    """Returns the default AuditAI agent with no-op logger and default tools."""
    from src.audit.logger import AuditLogger
    # from src.tools.[...] import PriceFeedTool, etc.
    return create_agent(audit_logger=AuditLogger(on_chain=False), available_tools=[], max_iterations=10)
