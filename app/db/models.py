"""SQLAlchemy ORM models for persisting users and their financial reports."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class UserRecord(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    reports = relationship("ReportRecord", back_populates="user", cascade="all, delete-orphan")


class ReportRecord(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    total_income = Column(Float)
    total_expenses = Column(Float)
    net_savings = Column(Float)
    financial_health_score = Column(Integer)

    # Full report payload (income/expense/investment/goal breakdowns, action plan, etc.)
    report_json = Column(JSON)

    user = relationship("UserRecord", back_populates="reports")
