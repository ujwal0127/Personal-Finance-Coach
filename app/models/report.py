"""
Helpers for rendering a FinancialReport as human-readable text or a dict
suitable for the Streamlit UI / JSON export.
"""

from __future__ import annotations
from app.models.schemas import FinancialReport


def report_to_markdown(report: FinancialReport) -> str:
    """Render a FinancialReport as a markdown string for display or export."""

    lines = [
        f"# Financial Report for {report.user_name}",
        "",
        f"**Financial Health Score:** {report.financial_health_score}/100",
        "",
        "## Income",
        f"- Total monthly income: {report.income.total_monthly_income:,.2f}",
        f"- Stable income: {report.income.stable_income:,.2f}",
        f"- Variable income: {report.income.variable_income:,.2f}",
        f"- {report.income.summary}",
        "",
        "## Expenses",
        f"- Total monthly expenses: {report.expenses.total_monthly_expenses:,.2f}",
        f"- Largest category: {report.expenses.largest_category} "
        f"({report.expenses.largest_category_amount:,.2f})",
        f"- Savings potential: {report.expenses.savings_potential:,.2f}",
        f"- {report.expenses.summary}",
        "",
        "## Investment Recommendation",
        f"- Monthly investable amount: {report.investment.monthly_investable_amount:,.2f}",
        f"- Emergency fund target: {report.investment.emergency_fund_target:,.2f}",
        f"- Suggested allocation: {report.investment.suggested_allocation}",
        f"- {report.investment.summary}",
        "",
    ]

    if report.goal:
        lines += [
            "## Goal Tracking",
            f"- Goal: {report.goal.goal_name}",
            f"- Progress: {report.goal.completion_percentage:.1f}% "
            f"({report.goal.current_amount:,.2f} / {report.goal.target_amount:,.2f})",
            f"- Monthly savings needed: {report.goal.monthly_savings_needed}",
            f"- Estimated months to complete: {report.goal.estimated_months_to_complete}",
            f"- {report.goal.summary}",
            "",
        ]

    lines += [
        "## Net Monthly Savings",
        f"{report.net_monthly_savings:,.2f}",
        "",
        "## Action Plan",
    ]
    lines += [f"- {item}" for item in report.action_plan]
    lines += ["", "## Overall Summary", report.overall_summary]

    return "\n".join(lines)
