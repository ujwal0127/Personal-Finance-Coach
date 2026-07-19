"""
PDF Export Utility
Creates a professional financial report PDF.
"""

from io import BytesIO
import os
import tempfile

import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Optional: register a Unicode font if available.
# Uncomment and update the path if you want better ₹ support.
# pdfmetrics.registerFont(
#     TTFont("DejaVu", "C:/Windows/Fonts/DejaVuSans.ttf")
# )


def money(value):
    """Format currency."""
    return f"₹{value:,.2f}"

def create_expense_chart(report):
    """
    Creates an expense pie chart and returns the image path.
    """

    labels = []
    values = []

    for category, amount in report.expenses.expense_breakdown.items():
        if amount > 0:
            labels.append(category.replace("_", " ").title())
            values.append(amount)

    if not values:
        return None

    fig, ax = plt.subplots(figsize=(6, 6))

    colors_list = [
        "#4CAF50",
        "#2196F3",
        "#FFC107",
        "#FF5722",
        "#9C27B0",
        "#00BCD4",
        "#795548",
        "#8BC34A",
        "#607D8B",
        "#E91E63",
    ]

    ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors_list[:len(values)],
    )

    ax.set_title(
        "Expense Breakdown",
        fontsize=16,
        fontweight="bold",
    )

    plt.tight_layout()

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".png",
    )

    plt.savefig(
        temp_file.name,
        dpi=220,
        bbox_inches="tight",
    )

    plt.close(fig)

    return temp_file.name

def generate_pdf(report):
    """
    Generate a financial report PDF.

    Returns:
        bytes
    """

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    title = styles["Title"]
    title.alignment = TA_CENTER

    heading = styles["Heading2"]
    normal = styles["BodyText"]

    story = []

    # ----------------------------------------------------
    # Title
    # ----------------------------------------------------

    story.append(Paragraph("Personal Finance Coach", title))
    story.append(
        Paragraph(
            "AI Generated Financial Report",
            normal,
        )
    )

    story.append(Spacer(1, 20))

    # ----------------------------------------------------
    # User
    # ----------------------------------------------------

    story.append(Paragraph("User Details", heading))

    story.append(
        Paragraph(
            f"<b>Name:</b> {report.user_name}",
            normal,
        )
    )

    story.append(Spacer(1, 15))
    # ----------------------------------------------------
    # Financial Summary Table
    # ----------------------------------------------------

    story.append(Paragraph("Financial Summary", heading))
    story.append(Spacer(1, 10))

    savings_rate = (
        report.net_monthly_savings /
        report.income.total_monthly_income
        * 100
    )

    table_data = [

        ["Metric", "Value"],

        ["💰 Monthly Income",
        money(report.income.total_monthly_income)],

        ["💳 Monthly Expenses",
        money(report.expenses.total_monthly_expenses)],

        ["🏦 Monthly Savings",
        money(report.net_monthly_savings)],

        ["📈 Savings Rate",
        f"{savings_rate:.1f}%"],

        ["🏆 Financial Health",
        f"{report.financial_health_score}/100"],

    ]

    table = Table(
        table_data,
        colWidths=[250,180],
    )

    table.setStyle(

        TableStyle([

            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1f4e79")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),

            ("BACKGROUND",(0,1),(-1,-1),colors.whitesmoke),

            ("GRID",(0,0),(-1,-1),1,colors.grey),

            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

            ("FONTNAME",(0,1),(-1,-1),"Helvetica"),

            ("BOTTOMPADDING",(0,0),(-1,0),10),

            ("TOPPADDING",(0,1),(-1,-1),8),

            ("BOTTOMPADDING",(0,1),(-1,-1),8),

            ("ALIGN",(1,1),(-1,-1),"CENTER"),

            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),

        ])

    )

    story.append(table)
    story.append(Spacer(1,20))
    # ----------------------------------------------------
    # Expense Pie Chart
    # ----------------------------------------------------

    chart_path = create_expense_chart(report)

    if chart_path:

        story.append(Paragraph("Expense Breakdown", heading))

        story.append(Spacer(1, 10))

        story.append(
            Image(
                chart_path,
                width=320,
                height=320,
            )
        )

        story.append(Spacer(1, 20))

    # ----------------------------------------------------
    # AI Summary
    # ----------------------------------------------------

    story.append(Paragraph("AI Insights", heading))

    story.append(
        Paragraph(
            report.overall_summary,
            normal,
        )
    )

    story.append(Spacer(1, 15))

    # ----------------------------------------------------
    # Income
    # ----------------------------------------------------

    story.append(Paragraph("Income Analysis", heading))
    story.append(
        Paragraph(
            report.income.summary,
            normal,
        )
    )

    story.append(Spacer(1, 10))

    # ----------------------------------------------------
    # Expense
    # ----------------------------------------------------

    story.append(Paragraph("Expense Analysis", heading))
    story.append(
        Paragraph(
            report.expenses.summary,
            normal,
        )
    )

    story.append(Spacer(1, 10))

    # ----------------------------------------------------
    # Investment
    # ----------------------------------------------------

    if report.investment:

        story.append(Paragraph("Investment Recommendation", heading))

        story.append(
            Paragraph(
                report.investment.summary,
                normal,
            )
        )

        story.append(Spacer(1, 10))

    # ----------------------------------------------------
    # Goal
    # ----------------------------------------------------

    if report.goal:

        story.append(Paragraph("Goal Progress", heading))

        story.append(
            Paragraph(
                report.goal.summary,
                normal,
            )
        )

        story.append(Spacer(1, 10))

    # ----------------------------------------------------
    # Action Plan
    # ----------------------------------------------------

    story.append(Paragraph("Action Plan", heading))

    for item in report.action_plan:
        story.append(
            Paragraph(f"• {item}", normal)
        )

    story.append(Spacer(1, 20))

    # ----------------------------------------------------
    # Footer
    # ----------------------------------------------------

    footer = styles["Italic"]

    footer.textColor = colors.grey

    footer.alignment = TA_CENTER

    story.append(
        Paragraph(
            "Generated by Personal Finance Coach",
            footer,
        )
    )

    doc.build(story)

    if chart_path and os.path.exists(chart_path):
        os.remove(chart_path)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf