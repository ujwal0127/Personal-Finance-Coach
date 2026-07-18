"""
High-level service that ties together input validation, the agent
pipeline (via LangGraph), and optional DB persistence.
"""

from app.models.schemas import UserFinancialInput, FinancialReport
from app.graph.builder import run_pipeline
from app.db.database import SessionLocal, init_db
from app.db import crud
from app.utils.logger import get_logger

logger = get_logger(__name__)


def generate_report(user_input: UserFinancialInput, persist: bool = True) -> FinancialReport:
    """
    Run the full multi-agent pipeline for a user and optionally persist
    the resulting report to the database.
    """
    report = run_pipeline(user_input)

    if persist:
        try:
            init_db()
            session = SessionLocal()
            try:
                user = crud.get_or_create_user(session, user_input.name, user_input.age)
                crud.save_report(session, user, report)
                logger.info("Report persisted for user=%s", user_input.name)
            finally:
                session.close()
        except Exception as e:  # pragma: no cover - persistence is best-effort
            logger.warning("Could not persist report: %s", e)

    return report
