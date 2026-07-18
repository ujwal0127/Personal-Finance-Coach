# Architecture

## Overview

```
                    User
                      |
                      v
            Supervisor Agent
                      |
     +--------+--------+--------+---------+
     v        v        v        v
 Income   Expense   Investment   Goal
 Agent     Agent      Agent      Agent
     +--------+--------+--------+---------+
                      |
                      v
        Personalized Financial Report
```

## Module Breakdown

| Path | Responsibility |
|---|---|
| `app/main.py` | CLI entry point; loads a sample user and prints the generated report. |
| `app/config.py` | Loads settings from `.env` (API keys, DB URL, provider choice). |
| `app/agents/` | One file per agent: `income_agent.py`, `expense_agent.py`, `investment_agent.py`, `goal_agent.py`, `supervisor_agent.py`. Each agent takes structured Pydantic input and returns structured Pydantic output. |
| `app/graph/` | LangGraph wiring. `state.py` defines the shared `GraphState`, `builder.py` builds/compiles the `StateGraph` (with a sequential-fallback if `langgraph` isn't installed), `routing.py` holds conditional edge logic (e.g. skip the Goal Agent if no goal was provided). |
| `app/models/` | Pydantic schemas (`schemas.py`) for all agent inputs/outputs, plus `report.py` for markdown rendering. |
| `app/db/` | SQLAlchemy models and CRUD helpers for persisting users and report history (SQLite by default, Postgres via `DATABASE_URL`). |
| `app/vectorstore/` | Optional FAISS-backed (or keyword-fallback) store of finance tips, for future retrieval-augmented summaries. |
| `app/services/` | `llm_client.py` (OpenAI/Gemini wrapper with an offline mock fallback), `report_generator.py` (orchestrates pipeline + persistence), `financial_health.py` (score → label/color helpers). |
| `app/utils/` | Pure helper functions: `calculators.py` (financial math), `validators.py` (input sanity checks), `logger.py`. |
| `app/ui/` | `streamlit_app.py` dashboard plus one rendering component per agent output in `components/`. |
| `tests/` | Unit tests per agent plus an end-to-end supervisor test. |
| `data/sample_users.json` | Sample financial profiles used by `main.py` and for manual testing. |

## Data Flow

1. User submits financial data (CLI sample file or Streamlit form) → validated into `UserFinancialInput`.
2. `SupervisorAgent` / LangGraph pipeline validates the input, then runs:
   - `IncomeAgent` → `IncomeAnalysis`
   - `ExpenseAgent` → `ExpenseAnalysis`
   - `InvestmentAgent` (needs `ExpenseAnalysis`) → `InvestmentRecommendation`
   - `GoalAgent` (needs investable amount from Investment agent; skipped if no goal given) → `GoalStatus | None`
3. Supervisor computes `net_monthly_savings`, `financial_health_score`, and an `action_plan`, then asks the LLM client for a short overall summary.
4. The combined `FinancialReport` is returned, optionally persisted to the DB, and rendered (markdown for CLI, Streamlit widgets for UI).

## Why LangGraph over plain function calls?

The graph formalizes the same workflow shown in the architecture diagram: it
gives explicit nodes and edges (so the flow is inspectable/visualizable),
supports conditional routing (skipping the Goal Agent), and is the natural
place to later add features like agent retries, parallel execution, or
human-in-the-loop checkpoints — without restructuring the underlying agent
logic, which stays in plain, independently testable Python classes.
