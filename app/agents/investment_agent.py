"""
Investment Suggestion Agent — recommends an allocation strategy based on
income, savings potential, age, and risk tolerance.
"""

from app.models.schemas import (
    UserFinancialInput, ExpenseAnalysis, InvestmentRecommendation,
)
from app.utils.calculators import emergency_fund_target
from app.services.llm_client import llm_client


# Simple allocation templates by risk tolerance (percent of investable amount)
ALLOCATION_TEMPLATES = {
    "low": {"Emergency Fund": 40, "Fixed Deposits": 35, "SIP/Mutual Funds": 15, "Gold": 10},
    "moderate": {"Emergency Fund": 25, "SIP/Mutual Funds": 40, "Fixed Deposits": 20, "Gold": 15},
    "high": {"Emergency Fund": 15, "SIP/Mutual Funds": 60, "Fixed Deposits": 10, "Gold": 15},
}


class InvestmentAgent:
    name = "investment_agent"

    def run(self, data: UserFinancialInput, expenses: ExpenseAnalysis) -> InvestmentRecommendation:
        investable = max(expenses.savings_potential, 0)
        template = ALLOCATION_TEMPLATES.get(data.risk_tolerance, ALLOCATION_TEMPLATES["moderate"])
        target_fund = emergency_fund_target(expenses.total_monthly_expenses)

        emergency_fund_gap = max(target_fund - data.current_savings, 0)
        if emergency_fund_gap > 0:
            # Keep the recommendation consistent with the action plan: build
            # the emergency reserve before allocating money to market assets.
            allocation = {"Emergency Fund": round(investable, 2)}
        else:
            allocation = {
                label: round(investable * (pct / 100), 2)
                for label, pct in template.items()
            }

        risk_note = {
            "low": "capital preservation is prioritized over growth",
            "moderate": "a balanced mix of growth and safety is used",
            "high": "growth-oriented instruments are favored given higher risk tolerance",
        }.get(data.risk_tolerance, "a balanced approach is used")
        if emergency_fund_gap > 0:
            risk_note = (
                f"building the emergency fund is prioritized; approximately "
                f"{emergency_fund_gap:.2f} remains to reach the target"
            )

        prompt = f"""
            You are a personal finance advisor for users in India.

            All monetary values are in Indian Rupees (INR).
            Never use the dollar ($) symbol.
            Always use the ₹ symbol when mentioning money.

            User: {data.name}
            Age: {data.age}
            Risk Tolerance: {data.risk_tolerance}
            Investment Experience: {data.investment_experience}

            Monthly Investable Amount: ₹{investable:,.2f}
            Recommended Emergency Fund: ₹{target_fund:,.2f}

            Suggested Investment Allocation:
            {allocation}

            Risk Note:
            {risk_note}

            Write a professional investment summary in 1–2 sentences. Explain whether the investment allocation is suitable for the user's risk profile and always display monetary values using the ₹ symbol.
            """
        summary = llm_client.complete(prompt)

        return InvestmentRecommendation(
            monthly_investable_amount=round(investable, 2),
            emergency_fund_target=round(target_fund, 2),
            suggested_allocation=allocation,
            risk_analysis=risk_note,
            summary=summary,
        )
