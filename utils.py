from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"

def str_to_date(s):
    if not s:
        return None
    return datetime.strptime(s, DATE_FORMAT)

def date_to_str(dt):
    if not dt:
        return ""
    return dt.strftime(DATE_FORMAT)

PRIORITY_COLORS = {
    "Low": "#8BC34A",
    "Normal": "#2196F3",
    "High": "#FF9800",
    "Critical": "#F44336"
}

RECURRENCE_OPTIONS = ["None", "Daily", "Weekly", "Monthly"]
STATUS_OPTIONS = ["Pending", "Completed"]
