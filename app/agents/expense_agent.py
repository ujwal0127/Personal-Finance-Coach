"""
Expense Analysis Agent — categorizes spending, flags the largest category,
and estimates savings potential.
"""

from app.models.schemas import UserFinancialInput, ExpenseAnalysis
from app.utils.calculators import total_income, savings_potential
from app.services.llm_client import llm_client


class ExpenseAgent:
    name = "expense_agent"

    def run(self, data: UserFinancialInput) -> ExpenseAnalysis:
        breakdown = {
            "food": data.expense_food,
            "rent": data.expense_rent,
            "shopping": data.expense_shopping,
            "entertainment": data.expense_entertainment,
            "transportation": data.expense_transportation,
            "utilities": data.expense_utilities,
            "healthcare": data.expense_healthcare,
            "education": data.expense_education,
            "emi": data.expense_emi,
            "miscellaneous": data.expense_miscellaneous,
        }

        total_expenses = sum(breakdown.values())
        largest_category, largest_amount = max(breakdown.items(), key=lambda kv: kv[1])

        income = total_income(
            data.monthly_salary, data.freelance_income,
            data.rental_income, data.passive_income, data.annual_bonus,
        )
        potential = savings_potential(income, total_expenses)

        prompt = (
            f"User {data.name} spends {total_expenses:.2f} per month. "
            f"Largest category: {largest_category} ({largest_amount:.2f}). "
            f"Breakdown: {breakdown}. Estimated savings potential: {potential:.2f}. "
            f"Summarize spending behavior and one area to cut back, in 1-2 sentences."
        )
        summary = llm_client.complete(prompt)

        return ExpenseAnalysis(
            total_monthly_expenses=round(total_expenses, 2),
            expense_breakdown=breakdown,
            largest_category=largest_category,
            largest_category_amount=round(largest_amount, 2),
            savings_potential=round(potential, 2),
            summary=summary,
        )
