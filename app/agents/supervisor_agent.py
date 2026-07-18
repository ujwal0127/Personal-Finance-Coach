"""
Supervisor Agent — coordinates Income, Expense, Investment, and Goal agents
and merges their outputs into one FinancialReport.
"""

from app.models.schemas import UserFinancialInput, FinancialReport
from app.agents.income_agent import IncomeAgent
from app.agents.expense_agent import ExpenseAgent
from app.agents.investment_agent import InvestmentAgent
from app.agents.goal_agent import GoalAgent
from app.utils.calculators import financial_health_score
from app.utils.validators import validate_user_input
from app.services.llm_client import llm_client
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SupervisorAgent:
    name = "supervisor_agent"

    def __init__(self):
        self.income_agent = IncomeAgent()
        self.expense_agent = ExpenseAgent()
        self.investment_agent = InvestmentAgent()
        self.goal_agent = GoalAgent()

    def run(self, data: UserFinancialInput) -> FinancialReport:
        # 1. Validate input
        validate_user_input(data)
        logger.info("Input validated for user=%s", data.name)

        # 2. Run each specialized agent (income + expenses independent,
        #    investment depends on expenses, goal depends on investment)
        income = self.income_agent.run(data)
        logger.info("Income agent complete: total=%.2f", income.total_monthly_income)

        expenses = self.expense_agent.run(data)
        logger.info("Expense agent complete: total=%.2f", expenses.total_monthly_expenses)

        investment = self.investment_agent.run(data, expenses)
        logger.info("Investment agent complete: investable=%.2f",
                    investment.monthly_investable_amount)

        goal = self.goal_agent.run(data, investment.monthly_investable_amount)
        if goal:
            logger.info("Goal agent complete: %.1f%% toward %s",
                        goal.completion_percentage, goal.goal_name)

        # 3. Derive summary metrics
        net_savings = round(income.total_monthly_income - expenses.total_monthly_expenses, 2)
        has_emergency_fund = data.current_savings >= investment.emergency_fund_target
        savings_rate = (
            net_savings / income.total_monthly_income
            if income.total_monthly_income > 0 else 0
        )
        health_score = financial_health_score(
            income.total_monthly_income, expenses.total_monthly_expenses,
            savings_rate, has_emergency_fund,
        )

        # 4. Build an action plan
        action_plan = self._build_action_plan(
            net_savings, expenses, investment, goal, has_emergency_fund
        )

        # 5. Final LLM-generated overall summary (resolves/synthesizes agent outputs)
        prompt = (
            f"Write a concise overall financial summary for {data.name}. "
            f"Monthly income: {income.total_monthly_income:.2f}, "
            f"expenses: {expenses.total_monthly_expenses:.2f}, "
            f"net savings: {net_savings:.2f}, health score: {health_score}/100. "
            f"Keep it to 2-3 encouraging but honest sentences."
        )
        overall_summary = llm_client.complete(prompt)

        return FinancialReport(
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

    @staticmethod
    def _build_action_plan(net_savings, expenses, investment, goal, has_emergency_fund) -> list[str]:
        plan = []

        if net_savings < 0:
            plan.append("Your expenses exceed your income — review discretionary spending immediately.")
        elif net_savings == 0:
            plan.append("You're breaking even — look for at least one category to trim.")

        if not has_emergency_fund:
            plan.append(
                f"Build your emergency fund up to {investment.emergency_fund_target:,.2f} "
                f"before increasing market investments."
            )

        plan.append(
            f"Review your {expenses.largest_category} spending "
            f"({expenses.largest_category_amount:,.2f}/month) for potential savings."
        )

        if investment.monthly_investable_amount > 0:
            plan.append(
                f"Invest approximately {investment.monthly_investable_amount:,.2f}/month "
                f"per the suggested allocation."
            )

        if goal:
            if goal.monthly_savings_needed:
                plan.append(
                    f"Save {goal.monthly_savings_needed:,.2f}/month to hit your "
                    f"'{goal.goal_name}' goal on schedule."
                )
            elif goal.estimated_months_to_complete:
                plan.append(
                    f"At the current rate, '{goal.goal_name}' will be reached in "
                    f"about {goal.estimated_months_to_complete} months."
                )

        return plan
