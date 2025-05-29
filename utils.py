# Utils functions
import re
import json
from datetime import datetime, timedelta

def cleaned_sql(sql: str) -> str:

    """
    Cleans the raw SQL generated from LLM into executable SQL
    """

    match = re.search(r'```sql\n(.*?)\n```', sql, re.DOTALL)

    if match:
        return match.group(1).strip()
    
    else:
        return ""
    
def is_safe_sql(sql : str) -> bool:
    
    """
    Checks if the SQL Query given to chatbot s safe to execute
    """
    forbidden_keywords = ['delete', 'drop', 'truncate', 'update', 'alter']

    lowered = sql.lower()

    return not any(keyword in lowered for keyword in forbidden_keywords)


from datetime import datetime, timedelta
import calendar

def parse_vague_time_phrases(text: str) -> dict:
    """
    Detects vague time phrases and converts them to start and end dates.
    Returns: {"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"} or {} if not detected.
    """

    text = text.lower().strip()
    now = datetime.now()

    def quarter_date_range(ref_date, offset_quarters=0):
        current_month = ref_date.month
        current_quarter = (current_month - 1) // 3 + 1
        target_quarter = current_quarter + offset_quarters

        # Calculate target year and quarter
        target_year = ref_date.year + ((target_quarter - 1) // 4)
        target_quarter = ((target_quarter - 1) % 4) + 1

        start_month = (target_quarter - 1) * 3 + 1
        end_month = start_month + 2

        start_date = datetime(target_year, start_month, 1)
        last_day = calendar.monthrange(target_year, end_month)[1]
        end_date = datetime(target_year, end_month, last_day)

        return start_date, min(end_date, now)

    phrases = {
        "last month": lambda: (
            (now.replace(day=1) - timedelta(days=1)).replace(day=1),
            (now.replace(day=1) - timedelta(days=1))
        ),
        "this month": lambda: (
            now.replace(day=1),
            now
        ),
        "last year": lambda: (
            datetime(now.year - 1, 1, 1),
            datetime(now.year - 1, 12, 31)
        ),
        "this year": lambda: (
            datetime(now.year, 1, 1),
            now
        ),
        "this week": lambda: (
            now - timedelta(days=now.weekday()),
            now
        ),
        "last week": lambda: (
            (now - timedelta(days=now.weekday() + 7)),
            (now - timedelta(days=now.weekday() + 1))
        ),
        "yesterday": lambda: (
            now - timedelta(days=1),
            now - timedelta(days=1)
        ),
        "today": lambda: (
            now,
            now
        ),
        "this quarter": lambda: quarter_date_range(now),
        "last quarter": lambda: quarter_date_range(now, offset_quarters=-1)
    }

    for phrase, date_func in phrases.items():
        if phrase in text:
            start, end = date_func()
            return {
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d")
            }

    return {}


def clean_llm_json_response(response: str) -> dict:
    """
    Cleans LLM response by removing ```json and ``` wrappers and parses the JSON.
    """
    # Remove code block markers like ```json or ```
    cleaned = re.sub(r"```(?:json)?", "", response).strip("` \n")
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}\nCleaned content:\n{cleaned}")