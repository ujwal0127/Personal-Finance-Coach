"""
Income Agent — analyzes all sources of income and produces a monthly
income summary.
"""

from app.models.schemas import UserFinancialInput, IncomeAnalysis
from app.utils.calculators import total_income, stable_vs_variable
from app.services.llm_client import llm_client


class IncomeAgent:
    name = "income_agent"

    def run(self, data: UserFinancialInput) -> IncomeAnalysis:
        income = total_income(
            data.monthly_salary,
            data.freelance_income,
            data.rental_income,
            data.passive_income,
            data.annual_bonus,
        )
        stable, variable = stable_vs_variable(
            data.monthly_salary, data.rental_income,
            data.freelance_income, data.passive_income,
        )

        breakdown = {
            "salary": data.monthly_salary,
            "freelance": data.freelance_income,
            "rental": data.rental_income,
            "passive": data.passive_income,
            "bonus_monthly_equivalent": round(data.annual_bonus / 12, 2),
        }

        prompt = (
            f"User {data.name} has a total monthly income of ₹{income:,.2f} INR, "
            f"with ₹{stable:,.2f} stable income and ₹{variable:,.2f} variable income. "
            f"Income breakdown (all values in Indian Rupees): {breakdown}. "
            "Summarize this income situation in 1-2 sentences. "
            "IMPORTANT: All monetary values are in Indian Rupees (INR). "
            "Always use the ₹ symbol instead of the $ symbol in your response."
        )
        summary = llm_client.complete(prompt)

        return IncomeAnalysis(
            total_monthly_income=round(income, 2),
            stable_income=round(stable, 2),
            variable_income=round(variable, 2),
            income_breakdown=breakdown,
            summary=summary,
        )
