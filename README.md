# 🚀 AuditAI — Transparent AI Agent on Weilchain

[![Weilliptic Hackathon](https://img.shields.io/badge/Weilliptic-Hackathon%202026-blueviolet)]()
[![Built with LangGraph](https://img.shields.io/badge/Built%20with-LangGraph-green)]()
[![Weilchain](https://img.shields.io/badge/Deployed%20on-Weilchain-orange)]()

> **An intelligent AI agent that thinks, decides, and acts autonomously — with every step permanently audit-logged on the Weilchain blockchain.**

---

## 📖 Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Usage](#usage)
- [Audit Logging](#audit-logging)
- [MCP Tools](#mcp-tools)
- [Evaluation Criteria](#evaluation-criteria)
- [Timeline](#timeline)
- [Team](#team)
- [References](#references)

---

## Overview

**AuditAI** is a transparent, accountable AI agent built for the **Weilliptic Hackathon 2026**. It leverages the **LangGraph** agentic framework and the **Weilliptic Python SDK** to create an autonomous AI system where every reasoning step, tool call, and decision is permanently recorded on the **Weilchain blockchain**.

Users don't just get answers — they get **proof** of how the AI arrived at those answers.

> _"We're building an AI agent that can think, decide, and act on its own — and every single step it takes is permanently recorded on the blockchain so anyone can verify what it did and why."_

---

## Problem Statement

**Hackathon Problem Statement #2:** Use an external agentic framework like LangChain or Google ADK and add Weilliptic audit logging into the mix.

We use the **Python SDK for Weilchain** applets to build an agentic application with **comprehensive audit logging** at every step of the agentic workflow, including:

- Custom agentic loop with explicit control logic
- Detailed auditing of LLM interactions
- Predicting and handling tool calls
- Executing tools via the Weilchain MCP applet framework
- Defining clear termination conditions

---

## Architecture

```
👤 User Query
      │
      ▼
┌─────────────────────┐
│   Icarus Chatbot     │  ← User Interface
│   (Weilchain)        │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│   LangGraph Agent    │  ← Agentic Framework
│   (Reasoning Loop)   │
└──────────┬──────────┘
           ▼
    ┌──────┴──────┐
    ▼             ▼
┌────────┐  ┌──────────┐
│  LLM   │  │  MCP     │  ← Tools & Intelligence
│ (GPT)  │  │  Tools   │
└───┬────┘  └────┬─────┘
    │            │
    ▼            ▼
┌─────────────────────┐
│  Weilliptic Audit   │  ← Every step logged
│  Logger (SDK)       │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Weilchain          │  ← Immutable on-chain
│  Blockchain         │     audit trail
└─────────────────────┘
```

---

## Tech Stack

| Component         | Technology               | Purpose                              |
|-------------------|-------------------------|--------------------------------------|
| **Language**      | Python 3.11+            | Core development                     |
| **Agentic Framework** | LangChain / LangGraph | Agent reasoning & orchestration      |
| **LLM Provider**  | OpenAI GPT-4            | AI reasoning engine                  |
| **Blockchain**    | Weilchain               | Decentralized infrastructure         |
| **Audit Logging** | Weilliptic Python SDK   | On-chain audit trail                 |
| **Tool Framework**| Weilchain MCP Applets   | External service integration         |
| **Chatbot**       | Icarus (Weilliptic)     | User-facing interface                |

---

## Project Structure

```
auditai-weilchain/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   ├── state.py
│   │   └── prompts.py
│   ├── audit/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── schemas.py
│   │   └── weilchain.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── price_feed.py
│   │   ├── news_feed.py
│   │   └── onchain_data.py
│   └── utils/
│       ├── __init__.py
│       └── config.py
│
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_audit.py
│   └── test_tools.py
│
├── docs/
│   ├── architecture.md
│   ├── audit-logging.md
│   └── deployment.md
│
└── scripts/
    ├── setup.sh
    └── deploy.sh
```

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- A Weilchain wallet
- OpenAI API key (or any supported LLM provider)
- Weilliptic SDK access

### Installation

```bash
git clone https://github.com/saisanthosh-tech/auditai-weilchain.git
cd auditai-weilchain

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your API keys
```

### Quick Start

```bash
python -m src.main                          # Interactive mode
python -m src.main --query "Your question"  # Single query
python -m src.main --verbose                # Verbose logging
pytest tests/                               # Run tests
```

---

## Configuration

Copy `.env.example` to `.env` and fill in your values. See the `.env.example` file for all available options.

---

## Usage

```python
from src.agent.graph import create_agent
from src.audit.logger import AuditLogger

audit_logger = AuditLogger(on_chain=True)
agent = create_agent(audit_logger=audit_logger)

result = agent.invoke({"query": "Analyze the risk profile of Token X"})

for entry in audit_logger.get_trail().entries:
    print(f"[{entry.step_type.value}] tx: {entry.tx_hash}")
```

---

## Audit Logging

Every step is logged with:

| Field         | Description                                                   |
|---------------|--------------------------------------------------------------|
| `timestamp`   | When the step occurred                                       |
| `step_type`   | `llm_reasoning`, `tool_selection`, `tool_execution`, `termination_check`, `final_response` |
| `input_data`  | What went into this step                                     |
| `output_data` | What came out of this step                                   |
| `metadata`    | Model, tokens used, latency                                  |
| `tx_hash`     | Weilchain transaction hash (proof of logging)                |

---

## MCP Tools

| Tool           | Description                         |
|----------------|-------------------------------------|
| `price_feed`   | Fetches real-time token prices      |
| `news_feed`    | Aggregates crypto/DeFi news         |
| `onchain_data` | Queries on-chain data from Weilchain|

---

## Evaluation Criteria

| Criteria                     | Our Approach                                     |
|------------------------------|--------------------------------------------------|
| **Innovation**               | AI + blockchain audit trail = unique transparency|
| **Technical Implementation** | Clean LangGraph architecture with modular design |
| **Weilliptic SDK Usage**     | Deep integration — audit logging at every step   |
| **On-Chain Integration**     | Real audit data stored immutably on Weilchain    |
| **User Experience**          | Icarus chatbot interface + audit trail viewer    |
| **Documentation**            | Comprehensive docs, clear architecture           |

---

## Timeline

| Phase               | Dates             | Deliverable                |
|---------------------|-------------------|----------------------------|
| 💡 Idea Submission  | Feb 25, 2026      | Slides + basic prototype   |
| 🛠️ Core Development | Feb 26 — Mar 13   | Agent + audit logging      |
| 📝 Midterm Review   | Mar 14, 2026      | Working demo + mentor feedback |
| 🏆 Final Submission | Mar 16, 2026      | Complete project           |

---

## Team

| Name | Role              | Responsibilities                        |
|------|-------------------|------------------------------------------|
| TBD  | AI/Backend Dev    | LangGraph agent, agentic loop            |
| TBD  | Blockchain Dev    | Weilliptic SDK, audit logging            |
| TBD  | Tool/API Dev      | MCP tools, external integrations         |
| TBD  | Frontend/UX Dev   | Chat UI, audit trail viewer              |
| TBD  | Docs/Presentation | Documentation, slides, demo              |

---

## References

- [Weilliptic Documentation](https://docs.weilliptic.ai/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Cerebrum Agents Tutorial](https://docs.weilliptic.ai/docs/tutorials/cerebrum-agents)

---

**Built with ❤️ for the Weilliptic Hackathon 2026**
