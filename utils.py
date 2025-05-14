## utils.py

from datetime import datetime, timedelta
import re

def normalize_nl_dates(text: str) -> str:
    """
    Replace vague natural language dates like "last month", "this year" with specific SQL-compatible date expressions.
    """
    now = datetime.now()
    replacements = {
        r"last month": _range_last_month(now),
        r"this month": _range_this_month(now),
        r"last year": _range_last_year(now),
        r"this year": _range_this_year(now),
        r"last quarter": _range_last_quarter(now),
        r"this quarter": _range_this_quarter(now),
    }

    for pattern, (start, end) in replacements.items():
        if re.search(pattern, text, re.IGNORECASE):
            text = re.sub(pattern, f"between '{start}' and '{end}'", text, flags=re.IGNORECASE)
    return text

def _range_last_month(now):
    first = now.replace(day=1)
    last_month_end = first - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    return (last_month_start.strftime("%Y-%m-%d"), last_month_end.strftime("%Y-%m-%d"))

def _range_this_month(now):
    start = now.replace(day=1)
    end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

def _range_last_year(now):
    start = now.replace(year=now.year - 1, month=1, day=1)
    end = now.replace(year=now.year - 1, month=12, day=31)
    return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

def _range_this_year(now):
    start = now.replace(month=1, day=1)
    end = now.replace(month=12, day=31)
    return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

def _range_last_quarter(now):
    current_q = (now.month - 1) // 3 + 1
    last_q = current_q - 1 if current_q > 1 else 4
    year = now.year if current_q > 1 else now.year - 1
    return _quarter_range(year, last_q)

def _range_this_quarter(now):
    current_q = (now.month - 1) // 3 + 1
    return _quarter_range(now.year, current_q)

def _quarter_range(year, quarter):
    start_month = 3 * (quarter - 1) + 1
    start = datetime(year, start_month, 1)
    end_month = start_month + 2
    last_day = (datetime(year, end_month + 1, 1) - timedelta(days=1)).day
    end = datetime(year, end_month, last_day)
    return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

# Helper function to check if a query is related to business
def is_business_query(user_input: str) -> bool:
    """
    Checks if the user input contains business-related terms that indicate a query related to metrics.
    """
    business_keywords = [
        "sales", "revenue", "leads", "vendors", "marketing", "commission", "buyers", 
        "clients", "orders", "profit", "monthly", "total", "generated", "deals", "vendor", "buyer"
    ]
    
    return any(keyword in user_input.lower() for keyword in business_keywords)

# Helper function to extract SQL query from the assistant's response
def extract_sql(response: str) -> str:
    """
    Extracts an SQL query from the response if it's enclosed in markdown (e.g., ```sql`...`).
    """
    match = re.search(r'```sql\n(.*?)\n```', response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

import re
from datetime import datetime, timedelta

# Simple report detection
def is_report_request(user_input: str) -> bool:
    report_keywords = ["report", "download", "export", "summary", "csv", "xlsx", "generate"]
    return any(word in user_input.lower() for word in report_keywords)

# Extract keywords from user query
def extract_report_filters(user_input: str) -> dict:
    filters = {}

    # Basic type detection
    for key in ["vendors", "buyers", "sellers", "sales", "marketing"]:
        if key in user_input.lower():
            filters["type"] = key
            break

    # Detect category (all, new, won)
    for cat in ["new", "all", "won"]:
        if cat in user_input.lower():
            filters["category"] = cat
            break

    # Detect time ranges
    now = datetime.now()
    if "last month" in user_input.lower():
        start = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
        end = start.replace(day=28) + timedelta(days=4)  # end of month trick
        filters["start_date"] = start.strftime("%Y-%m-%d")
        filters["end_date"] = (end - timedelta(days=end.day)).strftime("%Y-%m-%d")

    # Fallback: no date
    return filters

