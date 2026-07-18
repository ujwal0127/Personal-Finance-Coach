"""
Goal Tracking Agent — monitors progress toward a user-defined financial goal
(house, car, education, retirement, vacation, emergency fund, gadgets, etc).
"""

from typing import Optional
from app.models.schemas import UserFinancialInput, GoalStatus
from app.utils.calculators import (
    goal_completion_percentage, months_to_goal, monthly_savings_needed,
)
from app.services.llm_client import llm_client


class GoalAgent:
    name = "goal_agent"

    def run(self, data: UserFinancialInput, monthly_investable: float) -> Optional[GoalStatus]:
        if not data.goal_name or not data.goal_target_amount:
            return None

        current = data.goal_current_amount or 0
        remaining = max(data.goal_target_amount - current, 0)
        completion_pct = goal_completion_percentage(current, data.goal_target_amount)

        est_months = months_to_goal(remaining, monthly_investable)
        needed = monthly_savings_needed(remaining, data.goal_target_months)

        prompt = (
            f"User {data.name} is saving for '{data.goal_name}', target "
            f"{data.goal_target_amount:.2f}, currently at {current:.2f} "
            f"({completion_pct:.1f}% complete). Remaining: {remaining:.2f}. "
            f"At current investable rate of {monthly_investable:.2f}/month, "
            f"estimated months to complete: {est_months}. "
            f"Summarize progress and encouragement in 1-2 sentences."
        )
        summary = llm_client.complete(prompt)

        return GoalStatus(
            goal_name=data.goal_name,
            target_amount=data.goal_target_amount,
            current_amount=current,
            remaining_amount=round(remaining, 2),
            completion_percentage=completion_pct,
            monthly_savings_needed=needed,
            estimated_months_to_complete=est_months,
            summary=summary,
        )
