"""
CLI entry point for the Personal Finance Coach.

Run with:
    python app/main.py
"""

import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.models.schemas import UserFinancialInput
from app.models.report import report_to_markdown
from app.services.report_generator import generate_report


def load_sample_input() -> UserFinancialInput:
    sample_path = Path(__file__).resolve().parents[1] / "data" / "sample_users.json"
    with open(sample_path) as f:
        samples = json.load(f)
    return UserFinancialInput(**samples[0])


def main():
    print("=" * 60)
    print("Personal Finance Coach — Multi-Agent AI System")
    print("=" * 60)

    user_input = load_sample_input()
    print(f"\nRunning pipeline for sample user: {user_input.name}\n")

    report = generate_report(user_input, persist=True)

    print(report_to_markdown(report))


if __name__ == "__main__":
    main()
