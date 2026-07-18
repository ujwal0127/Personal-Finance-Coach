"""Create/read/update/delete helper functions for users and reports."""

from sqlalchemy.orm import Session
from app.db.models import UserRecord, ReportRecord
from app.models.schemas import FinancialReport


def get_or_create_user(session: Session, name: str, age: int) -> UserRecord:
    user = session.query(UserRecord).filter_by(name=name, age=age).first()
    if user:
        return user
    user = UserRecord(name=name, age=age)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def save_report(session: Session, user: UserRecord, report: FinancialReport) -> ReportRecord:
    record = ReportRecord(
        user_id=user.id,
        total_income=report.income.total_monthly_income,
        total_expenses=report.expenses.total_monthly_expenses,
        net_savings=report.net_monthly_savings,
        financial_health_score=report.financial_health_score,
        report_json=report.model_dump(),
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_report_history(session: Session, user_id: int) -> list[ReportRecord]:
    return (
        session.query(ReportRecord)
        .filter_by(user_id=user_id)
        .order_by(ReportRecord.created_at.desc())
        .all()
    )
