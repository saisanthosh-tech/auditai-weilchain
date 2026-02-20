"""
AuditAI - Agent Nodes

Defines all node functions for the LangGraph agent:
- reasoning
- tool_selection
- tool_execution
- termination_check
- final_response
- error_handling
"""

from datetime import datetime
from src.agent.state import AgentState
from src.agent.prompts import (
    SYSTEM_PROMPT,
    USER_QUERY_PROMPT,
    REASONING_PROMPT,
    TOOL_SELECTION_PROMPT,
    FINAL_RESPONSE_PROMPT,
    ERROR_RECOVERY_PROMPT,
)

def reasoning_node(state: AgentState, **context):
    """
    Run the agent's reasoning step (using LLM).
    """
    # Placeholder: In production, call LLM with SYSTEM_PROMPT, history, etc.
    # Example: Use OpenAI, langchain, etc.
    step_result = {
        "text": "Reasoned about the task and identified the next information needed.",
        "timestamp": datetime.utcnow().isoformat(),
    }
    state.current_iteration += 1
    state.audit_entries.append({
        "step_type": "llm_reasoning",
        "timestamp": step_result["timestamp"],
        "input_data": {"prompt": SYSTEM_PROMPT},
        "output_data": {"thought": step_result["text"]},
    })
    return state

def tool_selection_node(state: AgentState, **context):
    """
    Decide which tool to use (could use LLM or rule-based decision).
    """
    # Placeholder: select the first available tool
    available_tools = context.get('available_tools', [])
    chosen_tool = available_tools[0].name if available_tools else "none"
    state.audit_entries.append({
        "step_type": "tool_selection",
        "timestamp": datetime.utcnow().isoformat(),
        "input_data": {},
        "output_data": {"chosen_tool": chosen_tool},
    })
    state.requires_tool_call = chosen_tool != "none"
    return state

def tool_execution_node(state: AgentState, **context):
    """
    Execute selected tool.
    """
    # Placeholder: Run the selected tool with mock output
    tool_result = {
        "output": "Sample tool output.",
        "latency_ms": 42.0,
        "success": True,
    }
    state.audit_entries.append({
        "step_type": "tool_execution",
        "timestamp": datetime.utcnow().isoformat(),
        "input_data": {},
        "output_data": {"tool_result": tool_result},
    })
    state.tools_called.append({"name": "sample_tool", "result": tool_result})
    return state

def termination_check_node(state: AgentState, **context):
    """
    Decide whether to keep looping or finish.
    """
    # For demo: finish after first iteration
    done = state.current_iteration > 0
    state.is_complete = done
    state.audit_entries.append({
        "step_type": "termination_check",
        "timestamp": datetime.utcnow().isoformat(),
        "input_data": {},
        "output_data": {"done": done},
    })
    if done:
        return {"result":"done"}
    else:
        return {"result":"continue"}

def final_response_node(state: AgentState, **context):
    """
    Produce the agent's final response.
    """
    state.final_response = "This is your answer! (Demo response — integrate LLM here.)"
    state.audit_entries.append({
        "step_type": "final_response",
        "timestamp": datetime.utcnow().isoformat(),
        "input_data": {},
        "output_data": {"final_response": state.final_response},
    })
    state.is_complete = True
    return state

def error_handling_node(state: AgentState, **context):
    """
    Handle errors and produce an error message in the audit log.
    """
    state.errors.append("An error occurred during processing.")
    state.audit_entries.append({
        "step_type": "error",
        "timestamp": datetime.utcnow().isoformat(),
        "input_data": {},
        "output_data": {"error_message": "An error occurred during processing."},
    })
    state.is_complete = True
    return state
