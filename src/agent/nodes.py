"""
AuditAI - Agent Nodes
======================

Defines all node functions for the LangGraph agent.
Each node returns a dict of state updates (LangGraph pattern).

Nodes:
- reasoning: LLM thinks about the query
- tool_selection: LLM picks the right tool
- tool_execution: Runs the selected tool
- termination_check: Decides continue or stop
- final_response: Produces final answer
- error_handling: Handles errors gracefully
"""

import os
import json
from datetime import datetime, timezone

from src.agent.prompts import (
    SYSTEM_PROMPT,
    USER_QUERY_PROMPT,
    REASONING_PROMPT,
    TOOL_SELECTION_PROMPT,
    FINAL_RESPONSE_PROMPT,
    ERROR_RECOVERY_PROMPT,
)


def _get_llm():
    """Get the LLM instance (OpenAI GPT-4 or mock)."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    use_mock = os.getenv("AUDITAI_MOCK_LLM", "false").lower() == "true"

    if use_mock or not api_key or api_key.startswith("sk-your"):
        return None  # Will use mock responses

    try:
        from langchain_openai import ChatOpenAI
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
        base_url = os.getenv("OPENAI_API_BASE", None)
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            base_url=base_url,
        )
    except Exception:
        return None


def _llm_call(llm, prompt: str, fallback: str = "Mock LLM response.") -> tuple[str, dict]:
    """
    Call the LLM with a prompt. Returns (response_text, metadata).
    Falls back to mock if LLM is None.
    """
    if llm is None:
        return fallback, {"model": "mock", "tokens": 0}

    try:
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        metadata = {
            "model": getattr(response, 'response_metadata', {}).get('model_name', 'gpt-4o-mini'),
            "tokens": getattr(response, 'response_metadata', {}).get('token_usage', {}),
        }
        return content, metadata
    except Exception:
        # On any LLM error (quota, network, etc.), use the fallback gracefully
        return fallback, {"model": "fallback", "tokens": 0}


def _now() -> str:
    """Current UTC timestamp in ISO 8601."""
    return datetime.now(timezone.utc).isoformat()


def _build_tools_description(tools: list) -> str:
    """Build a formatted string describing available tools."""
    if not tools:
        return "No tools available."
    lines = []
    for t in tools:
        lines.append(f"- **{t.name}**: {t.description}")
    return "\n".join(lines)


# =============================================================================
# NODE FUNCTIONS — Each returns a dict of state updates
# =============================================================================

def reasoning_node(state: dict) -> dict:
    """
    Run the agent's reasoning step using the LLM.
    Analyzes the query and decides what to do next.
    """
    llm = _get_llm()
    query = state.get("query", "")
    iteration = state.get("current_iteration", 0) + 1
    tools_called = state.get("tools_called", [])

    # Build gathered info from previous tool calls
    gathered_info = "None yet."
    if tools_called:
        info_lines = []
        for tc in tools_called:
            info_lines.append(f"- Tool '{tc['name']}': {json.dumps(tc.get('result', {}), indent=2)[:500]}")
        gathered_info = "\n".join(info_lines)

    if iteration == 1:
        prompt = f"{SYSTEM_PROMPT}\n\n{USER_QUERY_PROMPT.format(query=query)}"
        fallback = (
            f"I need to analyze the query: '{query}'. "
            f"Let me determine what information I need and which tools to use."
        )
    else:
        prompt = REASONING_PROMPT.format(
            query=query,
            steps_completed=iteration - 1,
            gathered_info=gathered_info,
        )
        fallback = (
            f"After reviewing the gathered information, I now have enough data to formulate a response."
        )

    reasoning_text, metadata = _llm_call(llm, prompt, fallback)

    audit_entry = {
        "step_type": "llm_reasoning",
        "timestamp": _now(),
        "input_data": {"query": query, "iteration": iteration},
        "output_data": {"reasoning": reasoning_text[:500]},
        "metadata": metadata,
    }

    existing_entries = state.get("audit_entries", [])

    return {
        "reasoning": reasoning_text,
        "current_iteration": iteration,
        "current_step": state.get("current_step", 0) + 1,
        "audit_entries": existing_entries + [audit_entry],
    }


def tool_selection_node(state: dict) -> dict:
    """
    Decide which tool to use based on reasoning.
    Uses LLM to intelligently select the most appropriate tool.
    """
    llm = _get_llm()
    reasoning = state.get("reasoning", "")
    query = state.get("query", "")
    iteration = state.get("current_iteration", 0)

    # Import tools to get their descriptions
    from src.tools.price_feed import PriceFeedTool
    from src.tools.news_feed import NewsFeedTool
    from src.tools.onchain_data import OnchainDataTool

    available_tools = [PriceFeedTool(), NewsFeedTool(), OnchainDataTool()]
    tools_desc = _build_tools_description(available_tools)

    # If already called tools or second+ iteration, might be done
    tools_called = state.get("tools_called", [])
    if iteration > 1 and len(tools_called) > 0:
        audit_entry = {
            "step_type": "tool_selection",
            "timestamp": _now(),
            "input_data": {"reasoning": reasoning[:200]},
            "output_data": {"chosen_tool": "none", "reason": "Sufficient information gathered."},
        }
        return {
            "selected_tool": None,
            "requires_tool_call": False,
            "audit_entries": state.get("audit_entries", []) + [audit_entry],
            "current_step": state.get("current_step", 0) + 1,
        }

    # Ask LLM which tool to use
    prompt = TOOL_SELECTION_PROMPT.format(
        available_tools=tools_desc,
        reasoning=reasoning,
    )
    prompt += (
        "\n\nRespond in this exact JSON format:\n"
        '{"tool": "tool_name_or_none", "input": {"key": "value"}, "reason": "why"}\n'
        "Tool names: price_feed, news_feed, onchain_data, or none."
    )

    fallback_tool = "none"
    fallback_input = {}

    # Simple keyword-based fallback for mock mode
    query_lower = query.lower()
    if any(w in query_lower for w in ["price", "cost", "worth", "value", "bitcoin", "ethereum", "token"]):
        # Extract token name
        token = "bitcoin"
        for t in ["bitcoin", "ethereum", "solana", "cardano", "dogecoin", "bnb", "xrp"]:
            if t in query_lower:
                token = t
                break
        fallback_tool = "price_feed"
        fallback_input = {"token": token}
    elif any(w in query_lower for w in ["news", "latest", "update", "happening"]):
        topic = "cryptocurrency"
        for t in ["bitcoin", "ethereum", "defi", "nft", "blockchain"]:
            if t in query_lower:
                topic = t
                break
        fallback_tool = "news_feed"
        fallback_input = {"topic": topic}
    elif any(w in query_lower for w in ["balance", "transaction", "block", "onchain", "wallet", "address"]):
        fallback_tool = "onchain_data"
        fallback_input = {"query_type": "balance", "address": "0x0000000000000000000000000000000000000000"}

    fallback_response = json.dumps({
        "tool": fallback_tool,
        "input": fallback_input,
        "reason": f"Selected {fallback_tool} based on query analysis.",
    })

    response_text, metadata = _llm_call(llm, prompt, fallback_response)

    # Parse the LLM response
    chosen_tool = "none"
    tool_input = {}
    reason = "No tool needed."

    try:
        # Try to extract JSON from response
        text = response_text.strip()
        # Find JSON in response
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            parsed = json.loads(text[start:end])
            chosen_tool = parsed.get("tool", "none")
            tool_input = parsed.get("input", {})
            reason = parsed.get("reason", "")
    except (json.JSONDecodeError, KeyError):
        chosen_tool = fallback_tool
        tool_input = fallback_input
        reason = "Fallback selection due to parse error."

    needs_tool = chosen_tool not in ("none", "None", "", None)

    audit_entry = {
        "step_type": "tool_selection",
        "timestamp": _now(),
        "input_data": {"reasoning": reasoning[:200]},
        "output_data": {"chosen_tool": chosen_tool, "tool_input": tool_input, "reason": reason},
        "metadata": metadata,
    }

    return {
        "selected_tool": chosen_tool if needs_tool else None,
        "tool_input": tool_input if needs_tool else {},
        "requires_tool_call": needs_tool,
        "audit_entries": state.get("audit_entries", []) + [audit_entry],
        "current_step": state.get("current_step", 0) + 1,
    }


def tool_execution_node(state: dict) -> dict:
    """
    Execute the selected tool and capture the result.
    """
    selected_tool = state.get("selected_tool", "")
    tool_input = state.get("tool_input", {})

    # Import tools
    from src.tools.price_feed import PriceFeedTool
    from src.tools.news_feed import NewsFeedTool
    from src.tools.onchain_data import OnchainDataTool

    tool_map = {
        "price_feed": PriceFeedTool(),
        "news_feed": NewsFeedTool(),
        "onchain_data": OnchainDataTool(),
    }

    tool = tool_map.get(selected_tool)
    if tool is None:
        audit_entry = {
            "step_type": "tool_execution",
            "timestamp": _now(),
            "input_data": {"tool": selected_tool},
            "output_data": {"error": f"Tool '{selected_tool}' not found."},
        }
        return {
            "audit_entries": state.get("audit_entries", []) + [audit_entry],
            "errors": state.get("errors", []) + [f"Tool '{selected_tool}' not found."],
            "current_step": state.get("current_step", 0) + 1,
        }

    # Run the tool
    result = tool.run(tool_input)

    tool_record = {
        "name": selected_tool,
        "input": tool_input,
        "result": result.data if result.success else {"error": result.error},
        "success": result.success,
        "latency_ms": result.latency_ms,
    }

    audit_entry = {
        "step_type": "tool_execution",
        "timestamp": _now(),
        "input_data": {"tool": selected_tool, "input": tool_input},
        "output_data": {
            "success": result.success,
            "data": result.data if result.success else {},
            "error": result.error,
            "latency_ms": result.latency_ms,
        },
    }

    return {
        "tools_called": state.get("tools_called", []) + [tool_record],
        "requires_tool_call": False,
        "audit_entries": state.get("audit_entries", []) + [audit_entry],
        "current_step": state.get("current_step", 0) + 1,
    }


def termination_check_node(state: dict) -> dict:
    """
    Decide whether the agent should continue or finish.
    Checks: max iterations, tool results, completion signals.
    """
    iteration = state.get("current_iteration", 0)
    max_iter = state.get("max_iterations", 10)
    tools_called = state.get("tools_called", [])
    errors = state.get("errors", [])

    # Terminate if: max iterations reached, or we have tool results and reasoning done
    done = False
    reason = ""

    if errors:
        done = True
        reason = "Errors encountered."
    elif iteration >= max_iter:
        done = True
        reason = f"Max iterations ({max_iter}) reached."
    elif len(tools_called) > 0 and not state.get("requires_tool_call", False):
        done = True
        reason = "Tool results gathered, ready to respond."
    elif iteration > 1:
        done = True
        reason = "Sufficient reasoning iterations completed."

    audit_entry = {
        "step_type": "termination_check",
        "timestamp": _now(),
        "input_data": {"iteration": iteration, "tools_called_count": len(tools_called)},
        "output_data": {"is_complete": done, "reason": reason},
    }

    return {
        "is_complete": done,
        "audit_entries": state.get("audit_entries", []) + [audit_entry],
        "current_step": state.get("current_step", 0) + 1,
    }


def final_response_node(state: dict) -> dict:
    """
    Produce the agent's final response using the LLM.
    Synthesizes all gathered information into a comprehensive answer.
    """
    llm = _get_llm()
    query = state.get("query", "")
    tools_called = state.get("tools_called", [])
    reasoning = state.get("reasoning", "")
    audit_entries = state.get("audit_entries", [])

    # Build audit summary
    audit_summary_lines = []
    for i, entry in enumerate(audit_entries):
        step_type = entry.get("step_type", "unknown")
        output = entry.get("output_data", {})
        audit_summary_lines.append(f"Step {i+1} [{step_type}]: {json.dumps(output, default=str)[:200]}")
    audit_summary = "\n".join(audit_summary_lines)

    prompt = FINAL_RESPONSE_PROMPT.format(
        query=query,
        audit_summary=audit_summary,
    )

    # Build a fallback that uses actual tool data
    fallback = f"Based on my analysis of your query: '{query}'\n\n"
    if tools_called:
        for tc in tools_called:
            tool_name = tc.get("name", "unknown")
            tool_data = tc.get("result", {})
            if tool_name == "price_feed" and tc.get("success"):
                token = tool_data.get("token", "")
                price = tool_data.get("price", "N/A")
                change = tool_data.get("price_change_24h_pct", "N/A")
                market_cap = tool_data.get("market_cap", "N/A")
                fallback += f"📊 **{token.title()} Price Data:**\n"
                fallback += f"  - Current Price: ${price:,.2f}\n" if isinstance(price, (int, float)) else f"  - Current Price: {price}\n"
                fallback += f"  - 24h Change: {change:.2f}%\n" if isinstance(change, (int, float)) else f"  - 24h Change: {change}\n"
                fallback += f"  - Market Cap: ${market_cap:,.0f}\n\n" if isinstance(market_cap, (int, float)) else f"  - Market Cap: {market_cap}\n\n"
            elif tool_name == "news_feed" and tc.get("success"):
                articles = tool_data.get("articles", [])
                fallback += f"📰 **Latest News on '{tool_data.get('topic', '')}' ({len(articles)} articles):**\n"
                for a in articles[:3]:
                    fallback += f"  - {a.get('title', 'N/A')} ({a.get('source', 'Unknown')})\n"
                fallback += "\n"
            elif tool_name == "onchain_data" and tc.get("success"):
                fallback += f"🔗 **On-Chain Data:** {json.dumps(tool_data, indent=2)[:300]}\n\n"
    else:
        fallback += reasoning[:500] if reasoning else "I processed your query but no specific tools were needed."

    fallback += "\n\n*Every step of this analysis has been logged to the audit trail for transparency.*"

    response_text, metadata = _llm_call(llm, prompt, fallback)

    audit_entry = {
        "step_type": "final_response",
        "timestamp": _now(),
        "input_data": {"query": query},
        "output_data": {"response_length": len(response_text)},
        "metadata": metadata,
    }

    return {
        "final_response": response_text,
        "is_complete": True,
        "audit_entries": state.get("audit_entries", []) + [audit_entry],
        "current_step": state.get("current_step", 0) + 1,
    }


def error_handling_node(state: dict) -> dict:
    """
    Handle errors and produce an error message in the audit log.
    """
    errors = state.get("errors", [])
    error_msg = "; ".join(errors) if errors else "An unknown error occurred."

    audit_entry = {
        "step_type": "error",
        "timestamp": _now(),
        "input_data": {},
        "output_data": {"error_message": error_msg},
    }

    return {
        "final_response": f"⚠️ An error occurred during processing: {error_msg}",
        "is_complete": True,
        "audit_entries": state.get("audit_entries", []) + [audit_entry],
        "current_step": state.get("current_step", 0) + 1,
    }
