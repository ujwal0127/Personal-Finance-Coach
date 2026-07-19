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

        prompt = f"""
            You are a personal finance advisor for users in India.

            All monetary values are in Indian Rupees (INR).
            Never use the dollar ($) symbol.
            Always use the ₹ symbol when mentioning money.

            User: {data.name}

            Financial Goal: {data.goal_name}

            Target Amount: ₹{data.goal_target_amount:,.2f}
            Current Savings: ₹{current:,.2f}
            Goal Completion: {completion_pct:.1f}%
            Remaining Amount: ₹{remaining:,.2f}
            Monthly Investable Amount: ₹{monthly_investable:,.2f}
            Estimated Time to Reach Goal: {est_months} months

            Write a motivating and professional summary in 1–2 sentences about the user's progress and encourage them to continue saving. Always display monetary values using ₹.
            """
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
