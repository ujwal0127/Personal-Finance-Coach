"""
Builds the LangGraph workflow wiring together Income, Expense, Investment,
and Goal agent nodes, coordinated by the Supervisor's report-assembly step.

If the `langgraph` package isn't installed, `run_pipeline()` transparently
falls back to calling SupervisorAgent directly (sequential, no graph) so the
project still runs end-to-end without that dependency.
"""

from __future__ import annotations
from app.graph.state import GraphState
from app.graph.routing import has_goal, check_for_errors
from app.agents.income_agent import IncomeAgent
from app.agents.expense_agent import ExpenseAgent
from app.agents.investment_agent import InvestmentAgent
from app.agents.goal_agent import GoalAgent
from app.agents.supervisor_agent import SupervisorAgent
from app.utils.validators import validate_user_input, ValidationError
from app.utils.calculators import financial_health_score
from app.models.schemas import UserFinancialInput, FinancialReport
from app.services.llm_client import llm_client
from app.utils.logger import get_logger

logger = get_logger(__name__)

income_agent = IncomeAgent()
expense_agent = ExpenseAgent()
investment_agent = InvestmentAgent()
goal_agent = GoalAgent()


# ---------------------------------------------------------------------------
# Node functions (each takes and returns a GraphState)
# ---------------------------------------------------------------------------

def validate_node(state: GraphState) -> GraphState:
    try:
        validate_user_input(state["user_input"])
    except ValidationError as e:
        state["error"] = str(e)
    return state


def income_node(state: GraphState) -> GraphState:
    state["income"] = income_agent.run(state["user_input"])
    return state


def expense_node(state: GraphState) -> GraphState:
    state["expenses"] = expense_agent.run(state["user_input"])
    return state


def investment_node(state: GraphState) -> GraphState:
    state["investment"] = investment_agent.run(state["user_input"], state["expenses"])
    return state


def goal_node(state: GraphState) -> GraphState:
    state["goal"] = goal_agent.run(state["user_input"], state["investment"].monthly_investable_amount)
    return state


def assemble_report_node(state: GraphState) -> GraphState:
    data: UserFinancialInput = state["user_input"]
    income = state["income"]
    expenses = state["expenses"]
    investment = state["investment"]
    goal = state.get("goal")

    net_savings = round(income.total_monthly_income - expenses.total_monthly_expenses, 2)
    has_emergency_fund = data.current_savings >= investment.emergency_fund_target
    savings_rate = (
        net_savings / income.total_monthly_income if income.total_monthly_income > 0 else 0
    )
    health_score = financial_health_score(
        income.total_monthly_income, expenses.total_monthly_expenses,
        savings_rate, has_emergency_fund,
    )

    action_plan = SupervisorAgent._build_action_plan(
        net_savings, expenses, investment, goal, has_emergency_fund
    )

    prompt = (
        f"Write a concise overall financial summary for {data.name}. "
        f"Monthly income: {income.total_monthly_income:.2f}, "
        f"expenses: {expenses.total_monthly_expenses:.2f}, "
        f"net savings: {net_savings:.2f}, health score: {health_score}/100. "
        f"Keep it to 2-3 encouraging but honest sentences."
    )
    overall_summary = llm_client.complete(prompt)

    state["report"] = FinancialReport(
        user_name=data.name,
        income=income,
        expenses=expenses,
        investment=investment,
        goal=goal,
        net_monthly_savings=net_savings,
        financial_health_score=health_score,
        action_plan=action_plan,
        overall_summary=overall_summary,
    )
    return state


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_graph():
    """
    Build and compile the LangGraph StateGraph. Raises ImportError if
    langgraph isn't installed (caller should fall back to run_pipeline()).
    """
    from langgraph.graph import StateGraph, END

    graph = StateGraph(GraphState)

    graph.add_node("validate", validate_node)
    graph.add_node("income_agent", income_node)
    graph.add_node("expense_agent", expense_node)
    graph.add_node("investment_agent", investment_node)
    graph.add_node("goal_agent", goal_node)
    graph.add_node("assemble_report", assemble_report_node)

    graph.set_entry_point("validate")

    # income + expenses run after validation (conceptually parallel;
    # LangGraph will execute sequentially here for simplicity)
    graph.add_conditional_edges(
        "validate",
        check_for_errors,
        {"error": END, "continue": "income_agent"},
    )
    graph.add_edge("income_agent", "expense_agent")
    graph.add_edge("expense_agent", "investment_agent")

    # conditionally route to goal_agent or skip straight to report assembly
    graph.add_conditional_edges(
        "investment_agent",
        has_goal,
        {"goal_agent": "goal_agent", "assemble_report": "assemble_report"},
    )
    graph.add_edge("goal_agent", "assemble_report")
    graph.add_edge("assemble_report", END)

    return graph.compile()


def run_pipeline(user_input: UserFinancialInput) -> FinancialReport:
    """
    Entry point used by main.py / the Streamlit UI. Tries the compiled
    LangGraph workflow first; falls back to direct sequential execution via
    SupervisorAgent if langgraph isn't installed.
    """
    try:
        compiled_graph = build_graph()
        result_state = compiled_graph.invoke({"user_input": user_input})
        if result_state.get("error"):
            raise ValidationError(result_state["error"])
        return result_state["report"]
    except ImportError:
        logger.warning("langgraph not installed — falling back to direct SupervisorAgent call.")
        return SupervisorAgent().run(user_input)
