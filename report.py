import pandas as pd
from db import run_sql_query

def build_report_query(filters: dict) -> str:
    base_table = {
        "vendors": "leads",
        "sellers": "leads",
        "buyers": "leads",
        "sales": "deals"
    }.get(filters["type"], "vendors")

    query = f"SELECT * FROM {base_table}"

    conditions = []
    if filters.get("category") == "new":
        conditions.append("created_at IS NOT NULL")  # adjust based on your schema
    if filters.get("start_date") and filters.get("end_date"):
        conditions.append(f"created_at BETWEEN '{filters['start_date']}' AND '{filters['end_date']}'")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    return query

# def generate_csv_report(filters: dict, filename: str = "report.csv"):
#     query = build_report_query(filters)
#     result = run_sql_query(query)
#     if isinstance(result, str):  # it's an error
#         return result, None

#     if isinstance(result, dict):
#         df = pd.DataFrame([result])
#         df.to_csv(filename, index=False)
#         return "Report generated successfully", filename
#     else:
#         df = pd.DataFrame(result)
#         df.to_csv(filename, index=False)
#         return "Report generated successfully", filename


def generate_csv_report(sql_or_filters, filename: str = "report.csv"):
    # Determine if a raw SQL string or filters dictionary was passed
    if isinstance(sql_or_filters, str):
        query = sql_or_filters
    else:
        query = build_report_query(sql_or_filters)

    result = run_sql_query(query)

    if isinstance(result, str):  # it's an error
        return result, None

    # Normalize result to DataFrame
    if isinstance(result, dict):
        df = pd.DataFrame([result])
    else:
        df = pd.DataFrame(result)

    df.to_csv(filename, index=False)
    return "Report generated successfully", filename
    



    
