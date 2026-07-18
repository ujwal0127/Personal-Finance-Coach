"""
Utilities for interpreting a financial health score into a human-readable
label and color, for use in the UI.
"""


def score_label(score: int) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 50:
        return "Fair"
    if score >= 30:
        return "Needs Attention"
    return "Critical"


def score_color(score: int) -> str:
    """Returns a hex color suitable for a progress bar / badge in the UI."""
    if score >= 85:
        return "#2e7d32"  # green
    if score >= 70:
        return "#66bb6a"  # light green
    if score >= 50:
        return "#fbc02d"  # yellow
    if score >= 30:
        return "#f57c00"  # orange
    return "#c62828"  # red
