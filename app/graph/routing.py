"""
Conditional routing logic for the LangGraph workflow.
"""

from app.graph.state import GraphState


def has_goal(state: GraphState) -> str:
    """
    Route to the goal_agent node only if the user actually specified a goal;
    otherwise skip straight to the supervisor's final report assembly.
    """
    user_input = state.get("user_input")
    if user_input and user_input.goal_name and user_input.goal_target_amount:
        return "goal_agent"
    return "assemble_report"


def check_for_errors(state: GraphState) -> str:
    """Route to an error-handling end state if validation failed upstream."""
    if state.get("error"):
        return "error"
    return "continue"
