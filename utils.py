"""
Utils Module - Helper functions for display and data formatting.
"""

from collections import Counter


def format_schedule_text(schedule):
    """Return a formatted string of the schedule."""
    lines = ["─" * 30, f"{'Time':<12} {'Subject'}", "─" * 30]
    for slot, subject in schedule:
        icon = "☕" if subject == "Break" else "📖"
        lines.append(f"{slot:<12} {icon} {subject}")
    lines.append("─" * 30)
    return "\n".join(lines)


def schedule_to_dict_list(schedule):
    """Convert schedule tuples to list of dicts for table display."""
    rows = []
    for slot, subject in schedule:
        rows.append({"Time": slot, "Subject": subject})
    return rows


def get_subject_summary(schedule, subjects_data):
    """Return per-subject hour count vs allocated."""
    counts = Counter(s for _, s in schedule if s != "Break")
    rows = []
    for s in subjects_data:
        name = s["name"]
        allocated = s["hours"]
        scheduled = counts.get(name, 0)
        rows.append({
            "Subject": name,
            "Allocated": allocated,
            "Scheduled": scheduled,
            "Status": "✅" if scheduled >= 1 else "⚠️ Missing"
        })
    return rows


def priority_label(val):
    return {1: "Low", 2: "Medium", 3: "High"}.get(val, "Medium")