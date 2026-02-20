# AuditAI - Architecture Documentation

## Overview

This document describes the detailed architecture of the AuditAI system.

## Components

### 1. LangGraph Agent
The core agentic framework that handles reasoning, tool selection, and response generation using configurable workflows and explicit state transitions.

### 2. Audit Logger
Captures every step of the agent's workflow and persists it both locally and on-chain using the Weilliptic Python SDK. This ensures transparency, accountability, and immutability for all agent actions.

### 3. MCP Tools
Modular, external service integrations that the agent can invoke to gather information (such as token prices, news, or on-chain blockchain data).

### 4. Weilchain Integration
On-chain audit trail storage via the Weilliptic Python SDK and Weilchain blockchain.

## Data Flow

1. **User submits a query** via Icarus chatbot.
2. The query enters the **LangGraph agent** reasoning loop.
3. Each step is processed (reasoning, tool call, response).
4. Each step and decision is captured by the **AuditLogger**.
5. **Tools** are called as needed with full input/output logging.
6. **Audit entries are pushed to the Weilchain blockchain**.
7. Final response is returned to the user with an audit trail link.

## Design Decisions

- **LangGraph over vanilla LangChain:** Provides clear control flow, fine-grained step-level auditing, and predictable state transitions.
- **Audit-first approach:** Every LLM thought, tool call, and decision is auditable and stored immutably.
- **Modular tools:** All external/world-interaction logic is isolated, making it easy to extend or swap out APIs.
- **Separation of concerns:** Reasoning, tool selection, tool execution, and auditing are all distinct code modules and logic paths.
- **Support for Local + On-Chain Audit:** Dual logging ensures robustness, easy debugging, and verifiability.

## Sequence Diagram

```
User -> Icarus Chatbot -> LangGraph Agent
         |         |
         |--(query)-> [Reasoning Node]
         |             |
         |      [Tool Selection Node]
         |             |
         |      [Tool Execution Node] --> [MCP Tool(s)]
         |             |
         |      [Termination Check Node]
         |             |
         |         [Audit Logger]
         |             |
         |      [Weilchain Blockchain]
         |
<--[Final Response]<--|
```

## Extending the Architecture

- **Add new tools:** Implement a new class inheriting from `BaseTool` and register it.
- **Audit more events:** Add new step types
