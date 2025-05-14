## chat.py

import os
import google.generativeai as genai
from db import get_connection, fetch_schema
from prompts import build_prompt
from memory import ChatMemory
from utils import extract_sql, normalize_nl_dates, is_business_query

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# In-memory conversation memory (not DB-backed)
memory = ChatMemory()

def run_query(sql: str):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        return {"error": str(e)}

from report import generate_csv_report
from utils import is_report_request, extract_report_filters

def handle_chat(user_input: str, session_id: str = "default"):
    schema = fetch_schema()
    history = memory.get(session_id)
    user_input_cleaned = normalize_nl_dates(user_input)

    try:
        if is_report_request(user_input_cleaned):
            try:
                report_type, start_date, end_date = extract_report_filters(user_input_cleaned)
                table_map = {
                    # "vendors": "boat_vendors",
                    # "buyers": "buyers",
                    # "sales": "deals"
                    "vendors": "leads",   # vendors → sellers → leads
                    "sellers": "leads",
                    "buyers": "leads",
                    "sales": "deals"
                }
                table_name = table_map.get(report_type.lower(), report_type.lower())
                sql = f"SELECT * FROM {table_name} WHERE created_at BETWEEN '{start_date}' AND '{end_date}'"



                # ✅ Add filter by type if leads table is used
                if table_name == "leads" and report_type.lower() in ["buyers", "sellers", "vendors"]:
                    user_type = "seller" if report_type.lower() in ["sellers", "vendors"] else "buyer"
                    sql += f" AND type = '{user_type}'"
         

                file_path = generate_csv_report(sql, report_type)
                download_url = f"/static/reports/{os.path.basename(file_path)}"
                response = f" Your report on {report_type} from {start_date} to {end_date} is ready: [Download Report]({download_url})"

                memory.append(session_id, user_input, response)
                return {
                    "type": "report",
                    "query": sql,
                    "message": response,
                    "download_url": download_url
                }

            except Exception as e:
                return {"type": "error", "message": f"Couldn't generate report: {str(e)}"}

        elif is_business_query(user_input_cleaned):
            prompt = build_prompt(user_input_cleaned, schema, history)
            response = model.generate_content(prompt).text.strip()
            sql = extract_sql(response)

            if sql:
                result = run_query(sql)
                result_summary = f"Here's what I found:\n{result}" if isinstance(result, list) else result
                memory.append(session_id, user_input, result_summary)
                return {
                    "type": "db",
                    "query": sql,
                    "message": response,
                    "result": result
                }
            else:
                memory.append(session_id, user_input, response)
                return {"type": "chat", "message": response}

        else:
            casual_response = model.generate_content(user_input_cleaned).text.strip()
            memory.append(session_id, user_input, casual_response)
            return {"type": "chat", "message": casual_response}

    except Exception as e:
        return {"type": "error", "message": str(e)}
