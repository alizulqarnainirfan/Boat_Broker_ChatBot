# Report related Functions and routing here
# report.py
import pandas as pd
from io import BytesIO
from fastapi.responses import StreamingResponse
from utils import parse_vague_time_phrases
from llm import llm_response
from prompts import build_filter_extraction_prompt, build_where_clause_query
import json
import re


def sales_report_select_clause():
    
    """
    Builds a structure for sales report to show only the specific column with specific Names and proper format
    """

    sales_report_select_clause = """
SELECT
  deals.status AS `Sales Status`,
  deals.sale_price AS `Sale Price`,
  deals.deposit AS `Deposit`,
  deals.balance AS `Balance`,
  deals.commission AS `Commission`,
  deals.balance_date AS `Balance Date`,
  deals.deposit_date AS `Deposit Date`,
  deals.sale_price_date AS `Sale Price Date`,
  deals.survey AS `Survey Status`,
  deals.amendment AS `Amendment Status`,

  seller_lead.first_name_1 AS `Vendor First Name 1`,
  seller_lead.first_name_2 AS `Vendor First Name 2`,
  seller_lead.surname_1 AS `Vendor Surname 1`,
  seller_lead.surname_2 AS `Vendor Surname 2`,
  seller_lead.email_1 AS `Vendor Email 1`,
  seller_lead.email_2 AS `Vendor Email 2`,
  seller_lead.telephone_1 AS `Vendor Phone 1`,
  seller_lead.telephone_2 AS `Vendor Phone 2`,
  seller_lead.address_1 AS `Vendor Address 1`,
  seller_lead.address_2 AS `Vendor Address 2`,
  seller_lead.seller_boat_name AS `Vendor Boat Name`,
  seller_lead.seller_boat_lying_at AS `Vendor Boat Location`,
  seller_lead.seller_preference_boat AS `Vendor Boat Type`,
  seller_lead.seller_boat_length AS `Vendor Boat Length`,
  seller_lead.seller_preference_stern_type AS `Vendor Stern Type`,
  seller_lead.seller_boat_year_built AS `Vendor Year Built`,
  seller_lead.seller_boat_builder AS `Vendor Builder`,
  seller_lead.seller_boat_steel_spec AS `Vendor Steel Spec`,
  seller_lead.seller_boat_fit_out AS `Vendor Fit Out`,
  seller_lead.seller_boat_no_of_berths AS `Vendor Berths`,
  seller_lead.seller_boat_engin AS `Vendor Engine`,
  seller_lead.seller_boat_last_service AS `Vendor Last Service`,
  seller_lead.seller_boat_blacking AS `Vendor Blacking`,
  seller_lead.seller_boat_anodes AS `Vendor Anodes`,
  seller_lead.seller_boat_safety_certificate AS `Vendor Safety Certificate`,
  seller_lead.seller_boat_rcd_compliant AS `Vendor RCD Compliant`,
  seller_lead.seller_boat_recent_survey AS `Vendor Recent Survey`,
  seller_lead.seller_boat_reason_for_sale AS `Vendor Reason for Sale`,
  seller_lead.seller_valuation_low AS `Vendor Valuation Low`,
  seller_lead.seller_valuation_high AS `Vendor Valuation High`,
  seller_lead.seller_commission_rate AS `Vendor Commission Rate`,

  buyer_lead.first_name_1 AS `Buyer First Name 1`,
  buyer_lead.first_name_2 AS `Buyer First Name 2`,
  buyer_lead.surname_1 AS `Buyer Surname 1`,
  buyer_lead.surname_2 AS `Buyer Surname 2`,
  buyer_lead.email_1 AS `Buyer Email 1`,
  buyer_lead.email_2 AS `Buyer Email 2`,
  buyer_lead.telephone_1 AS `Buyer Phone 1`,
  buyer_lead.telephone_2 AS `Buyer Phone 2`,
  buyer_lead.address_1 AS `Buyer Address 1`,
  buyer_lead.address_2 AS `Buyer Address 2`,
  buyer_lead.buyer_preference_boat AS `Buyer Boat Preference`,
  buyer_lead.buyer_preference_stern_type AS `Buyer Stern Type`,
  buyer_lead.buyer_preference_length AS `Buyer Length`,
  buyer_lead.buyer_preference_layout AS `Buyer Layout`,
  buyer_lead.buyer_budget AS `Buyer Budget`

"""

    return sales_report_select_clause


def extract_filters_via_llm(user_message: str) -> dict:
    """
    Extract filters/selections for report generation from user input using LLM
    """

    time_context = parse_vague_time_phrases(user_message)

    prompt = build_filter_extraction_prompt(user_message, time_context)
    response = llm_response(prompt)

    match = re.search(r'\{.*\}', response, re.DOTALL)
    if not match:
        raise ValueError("Could not extract JSON from LLM response.")
    
    json_str = match.group(0)

    try:
        filters = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON extracted: {e}")

    # Normalize type
    type_map = {
        "vendors": "seller",
        "vendor": "seller",
        "sellers": "seller",
        "buyers": "buyer",
        "buyer": "buyer",
        "sales": "deals",
        "sale": "deals",
        "deal": "deals",
        "deals": "deals"
    }

    report_type = filters.get("type", "").lower()
    filters["type"] = type_map.get(report_type, report_type)

    return filters


# def build_where_clause(filters: dict) -> tuple[str, list, str]:
#     """
#     Builds SQL WHERE clause, parameter list, and selects the correct table (leads or deals).
#     """
#     where_clauses = []
#     params = []

#     report_type = filters.get("type")  # buyer, seller, or deals

#     # Decide table based on report type
#     if report_type == "deals":
#         table = "deals"
#     else:
#         table = "leads"
#         where_clauses.append("type = %s")
#         params.append(report_type)

#     status = filters.get("status")
#     if status and status.lower() != "all":
#         where_clauses.append("status = %s")
#         params.append(status)

#     date_range = filters.get("date_range")
#     if date_range and date_range.get("start_date") and date_range.get("end_date"):
#         where_clauses.append("created_at BETWEEN %s AND %s")
#         params.extend([date_range["start_date"], date_range["end_date"]])

#     # Optional filters
#     for field in ["boat_type", "stern_type"]:
#         val = filters.get(field)
#         if val and val.lower() != "any":
#             where_clauses.append(f"{field} = %s")
#             params.append(val)

#     # Only for buyers and deals (not sellers)
#     if report_type in ["buyer", "deals"]:
#         for field in ["budget", "layout"]:
#             val = filters.get(field)
#             if val and val.lower() not in ["any", "all"]:
#                 where_clauses.append(f"{field} = %s")
#                 params.append(val)

#     where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
#     return where_sql, params, table





# def build_where_clause(filters: dict) -> tuple[str, list, str]:
#     """
#     Builds WHERE clause + parameters based on filters.
#     Also returns the correct table name.
#     """
#     report_type = filters.get("type")
    
#     if report_type == "deals":
#         table = "deals"
#         date_column = "closed_at"
#     else:
#         table = "leads"
#         date_column = "created_at"

#     where_clauses = []
#     params = []

#     # type condition only for leads table
#     if table == "leads":
#         where_clauses.append("type = %s")
#         params.append(report_type)

#     # status
#     status = filters.get("status")
#     if status and status.lower() != "all":
#         where_clauses.append("status = %s")
#         params.append(status)

#     # date range
#     date_range = filters.get("date_range")
#     if date_range and date_range.get("start_date") and date_range.get("end_date"):
#         where_clauses.append(f"{date_column} BETWEEN %s AND %s")
#         params.extend([date_range["start_date"], date_range["end_date"]])

#     # common filters
#     for field in ["boat_type", "stern_type"]:
#         val = filters.get(field)
#         if val and val.lower() != "any":
#             where_clauses.append(f"{field} = %s")
#             params.append(val)

#     # budget/layout only for buyer and deals
#     if report_type in ["buyer", "deals"]:
#         for field in ["budget", "layout"]:
#             val = filters.get(field)
#             if val and val.lower() not in ["any", "all"]:
#                 where_clauses.append(f"{field} = %s")
#                 params.append(val)

#     where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
#     return where_sql, params, table


def generate_excel_report(query_result: list[dict], report_type: str) -> StreamingResponse:
    """
    Generate downloadable Excel report from query result with proper formatting
    """
    df = pd.DataFrame(query_result)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        sheet_name = report_type.capitalize()
        df.to_excel(writer, index=False, sheet_name=sheet_name)

        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        # Format for date columns
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        for idx, column in enumerate(df.columns):
            col_width = max(len(str(column)), df[column].astype(str).map(len).max()) + 2
            worksheet.set_column(idx, idx, col_width)

            if 'date' in column.lower() or 'created_at' in column.lower() or 'closed_at' in column.lower():
                worksheet.set_column(idx, idx, col_width, date_format)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={report_type}_report.xlsx"
        }
    )


# inp = "generate me a report of buyers where status is won from 1st april 2025 to 30 april 2025 ,boat type is narrow boat,  stern type is semi traditional, budget is £75k-£100k and layout is reverse"
# fil = extract_filters_via_llm(inp)
# from prompts import build_where_clause_query

# prom = build_where_clause_query(fil)

# res = llm_response(prom)

# import json
# import re

# def clean_llm_json_response(response: str) -> dict:
#     """
#     Cleans LLM response by removing ```json and ``` wrappers and parses the JSON.
#     """
#     # Remove code block markers like ```json or ```
#     cleaned = re.sub(r"```(?:json)?", "", response).strip("` \n")
    
#     try:
#         return json.loads(cleaned)
#     except json.JSONDecodeError as e:
#         raise ValueError(f"Failed to parse JSON: {e}\nCleaned content:\n{cleaned}")

# sql_clean = clean_llm_json_response(res)
# print(sql_clean)

# parsed = clean_llm_json_response(res)

# query = parsed["query"]
# params = parsed["params"]

# print(query, params)





















# import pandas as pd
# from io import BytesIO
# from fastapi.responses import StreamingResponse

# from llm import llm_response
# from prompts import build_filter_extraction_prompt
# import json
# import re


# def extract_filters_via_llm(user_message: str) -> dict:
#     """
#     Extract filters/selections for report generation from user input using LLM
#     """
#     prompt = build_filter_extraction_prompt(user_message)
#     response = llm_response(prompt)

#     # Extract JSON from LLM response using regex
#     match = re.search(r'\{.*\}', response, re.DOTALL)
#     if not match:
#         raise ValueError("Could not extract JSON from LLM response.")
    
#     json_str = match.group(0)

#     try:
#         filters = json.loads(json_str)
#     except json.JSONDecodeError as e:
#         raise ValueError(f"Invalid JSON extracted: {e}")

#     # Normalize 'type' for DB compatibility
#     type_map = {
#         "vendors": "seller",
#         "vendor": "seller",
#         "sellers": "seller",
#         "buyers": "buyer",
#         "buyer": "buyer",
#         "sales": "deals",
#         "sale": "deals",
#         "deal": "deals",
#         "deals": "deals"
#     }

#     report_type = filters.get("type", "").lower()
#     filters["type"] = type_map.get(report_type, report_type)

#     return filters


# def build_where_clause(filters: dict) -> tuple[str, list]:
#     """
#     Builds SQL WHERE clause and parameter list from filter dict
#     """
#     where_clauses = []
#     params = []

#     report_type = filters.get("type")
#     if report_type:
#         where_clauses.append("type = %s")
#         params.append(report_type)

#     status = filters.get("status")
#     if status and status.lower() != "all":
#         where_clauses.append("status = %s")
#         params.append(status)

#     date_range = filters.get("date_range")
#     if date_range and date_range.get("start_date") and date_range.get("end_date"):
#         where_clauses.append("created_at BETWEEN %s AND %s")
#         params.extend([date_range["start_date"], date_range["end_date"]])

#     # Optional filters
#     for field in ["boat_type", "stern_type"]:
#         val = filters.get(field)
#         if val and val.lower() != "any":
#             where_clauses.append(f"{field} = %s")
#             params.append(val)

#     # Only for buyers/sales
#     if report_type in ["buyer", "sale"]:
#         for field in ["budget", "layout"]:
#             val = filters.get(field)
#             if val and val.lower() not in ["any", "all"]:
#                 where_clauses.append(f"{field} = %s")
#                 params.append(val)

#     where_sql = "WHERE " + " AND ".join(where_clauses)
#     return where_sql, params


# def generate_excel_report(query_result: list[dict], report_type: str) -> StreamingResponse:
#     """
#     Generate downloadable Excel report from query result with proper formatting
#     """
#     df = pd.DataFrame(query_result)

#     output = BytesIO()
#     with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#         sheet_name = report_type.capitalize()
#         df.to_excel(writer, index=False, sheet_name=sheet_name)

#         workbook = writer.book
#         worksheet = writer.sheets[sheet_name]

#         # Format for date columns
#         date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

#         for idx, column in enumerate(df.columns):
#             col_width = max(len(str(column)), df[column].astype(str).map(len).max()) + 2
#             worksheet.set_column(idx, idx, col_width)

#             if 'date' in column.lower() or 'created_at' in column.lower():
#                 worksheet.set_column(idx, idx, col_width, date_format)

#     output.seek(0)
#     return StreamingResponse(
#         output,
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         headers={
#             "Content-Disposition": f"attachment; filename={report_type}_report.xlsx"
#         }
#     )






















# import pandas as pd
# from io import BytesIO
# from fastapi.responses import StreamingResponse

# from llm import llm_response
# from prompts import build_filter_extraction_prompt
# import json
# import re

# def extract_filters_via_llm(user_message: str) -> dict:
#     """
#     Extract filters/selections for report generation from user input using LLM
#     """
#     prompt = build_filter_extraction_prompt(user_message)
#     response = llm_response(prompt)
    
#     # Use regex to extract the JSON block
#     match = re.search(r'\{.*\}', response, re.DOTALL)
#     if not match:
#         raise ValueError("Could not extract JSON from LLM response.")
    
#     json_str = match.group(0)

#     try:
#         return json.loads(json_str)
#     except json.JSONDecodeError as e:
#         raise ValueError(f"Invalid JSON extracted: {e}")
    
# fil = extract_filters_via_llm("generate me a report of buyer from 1st april 2025 to 30 april 2025 ,status should be won, boat type any, stern type any, budget all, layout any")

    

# def build_where_clause(filters: dict) -> tuple[str, list]:

#     """
#     Buils SQL query for report generation by changing filters into Where clause for SQL Query
#     """
#     where_clauses = []
#     params = []

#     # Normalize 'type'
#     report_type = filters.get("type")
#     if report_type == "sellers":
#         report_type = "vendors"

#     where_clauses.append("type = %s")
#     params.append(report_type)

#     status = filters.get("status")
#     if status and status.lower() != "all":
#         where_clauses.append("status = %s")
#         params.append(status)

#     date_range = filters.get("date_range")
#     if date_range and date_range.get("start_date") and date_range.get("end_date"):
#         where_clauses.append("created_at BETWEEN %s AND %s")
#         params.extend([date_range["start_date"], date_range["end_date"]])

#     # Optional filters
#     for field in ["boat_type", "stern_type"]:
#         val = filters.get(field)
#         if val and val.lower() != "any":
#             where_clauses.append(f"{field} = %s")
#             params.append(val)

#     # Only for buyers/sales
#     if report_type in ["buyers", "sales"]:
#         for field in ["budget", "layout"]:
#             val = filters.get(field)
#             if val and val.lower() != "all" and val.lower() != "any":
#                 where_clauses.append(f"{field} = %s")
#                 params.append(val)

#     where_sql = "WHERE " + " AND ".join(where_clauses)
#     return where_sql, params

# print(build_where_clause(fil))


# def generate_excel_report(query_result: list[dict], report_type: str) -> StreamingResponse:
#     df = pd.DataFrame(query_result)

#     output = BytesIO()
#     with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#         df.to_excel(writer, index=False, sheet_name=report_type.capitalize())

#     output.seek(0)
#     return StreamingResponse(
#         output,
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         headers={
#             "Content-Disposition": f"attachment; filename={report_type}_report.xlsx"
#         }
#     )

