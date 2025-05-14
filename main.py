## main.py

import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from chat import handle_chat  # Handle conversation with the assistant
from report import generate_csv_report  # Handle report generation logic
from memory import ChatMemory  # In-memory conversation history
from utils import normalize_nl_dates, extract_sql, is_business_query
from db import fetch_schema, get_connection
import google.generativeai as genai
from pydantic import BaseModel
from typing import Optional
from prompts import build_prompt
from utils import is_report_request, extract_report_filters
from report import generate_csv_report

# Configure Gemini (Gemini API for chat and responses)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# FastAPI app setup
app = FastAPI(title="Boat Broker Admin Chatbot", description="Smart assistant for managing sales, vendors, leads, and reports.", version="1.0")

# Enable CORS for frontend testing or integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory conversation history (not backed by DB)
memory = ChatMemory()

# Define Pydantic model for input
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"  # Optional, defaults to 'default'

# Pydantic model for report generation input
class ReportRequest(BaseModel):
    type: str
    start: str
    end: str
    filter: Optional[str] = ""

# Root endpoint
@app.get("/")
def root():
    return {"message": "Boat Admin Chatbot is running."}

# Endpoint to handle chat messages and user queries
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        user_query = request.query
        session_id = request.session_id

        if not user_query:
            return JSONResponse(status_code=400, content={"error": "Missing 'query' field in request."})

        # NEW: Check if it's a report request
        if is_report_request(user_query):
            filters = extract_report_filters(user_query)
            msg, filepath = generate_csv_report(filters, filename="static/reports/auto_report.csv")
            if filepath:
                return FileResponse(
                    path=filepath,
                    media_type="text/csv",
                    filename="auto_report.csv"
                )
            else:
                return JSONResponse(status_code=500, content={"error": msg})

        # Handle the chat request as usual
        response = await handle_chat(user_query, session_id)
        return JSONResponse(content=response)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Internal error: {str(e)}"})


# # Updated: Endpoint to generate reports using model-based input
# @app.post("/generate-report")
# async def generate_report_route(body: ReportRequest):
#     table = body.type
#     start = body.start
#     end = body.end
#     filter_str = body.filter

#     try:
#         file_path = generate_csv_report(table, start, end, filter_str)  # will generate the response from sql
#         return {"download_url": f"/static/reports/{os.path.basename(file_path)}"}
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": f"Report generation failed: {str(e)}"})

# # Endpoint for downloading reports generated
# @app.get("/static/reports/{filename}")
# async def download_report(filename: str):
#     file_path = f"static/reports/{filename}"
#     if not os.path.exists(file_path):
#         return JSONResponse(status_code=404, content={"error": "File not found."})

#     return FileResponse(
#         path=file_path,
#         media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
#         filename=filename
#     )


# Helper functions
async def handle_chat(user_query: str, session_id: str = "default"):
    try:
        schema = fetch_schema()  # Fetch the schema for DB interaction
        history = memory.get(session_id)  # Retrieve conversation history for the session
        user_query_cleaned = normalize_nl_dates(user_query)  # Normalize date references

        # Handle business-related queries by using GPT-4 model (Gemini)
        if is_business_query(user_query_cleaned):
            prompt = build_prompt(user_query_cleaned, schema, history)
            response = model.generate_content(prompt).text.strip()
            sql = extract_sql(response)

            if sql:
                result = run_query(sql)  # Execute SQL query
                result_summary = f"Here's what I found:\n{result}" if isinstance(result, list) else result
                memory.append(session_id, user_query, result_summary)  # Store result in history
                return {
                    "type": "db",
                    "query": sql,
                    "message": response,
                    "result": result
                }
            else:
                memory.append(session_id, user_query, response)  # Store response in history
                return {"type": "chat", "message": response}

        else:
            # Handle casual chat or non-business queries
            casual_response = model.generate_content(user_query_cleaned).text.strip()
            memory.append(session_id, user_query, casual_response)
            return {"type": "chat", "message": casual_response}

    except Exception as e:
        return {"type": "error", "message": str(e)}

# Function to run SQL query in the database
def run_query(sql: str):
    try:
        conn = get_connection()  # Get database connection
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        return {"error": str(e)}















# # Loading the necessary libraries
# import os
# from dotenv import load_dotenv
# import google.generativeai as google_ai
# from typing import TypedDict, List, Dict, Any
# from typing_extensions import Annotated

# from db_connection import get_connection, show_database

# load_dotenv(override = True)
# print("Environment variables loaded.")

# gemini_key = os.getenv("GEMINI_API_KEY")

# if not gemini_key:
#     raise ValueError("Gemini API key not found in environment variables.")

# google_ai.configure(api_key=gemini_key)

# model = google_ai.GenerativeModel('gemini-2.0-flash')
# print("Gemini model configured.")

# tables = [

#     'boat_buyers', 'boat_sellers', 'deals', 'failed_jobs', 'job_batches', 'jobs', 
#     'leads', 'marketings', 'reports', 'users'

# ]

# for table in tables:
#     print(table)


# prompt = """
# You are a database expert. You have to write a query to show the databases in the MySQL server from user input.
# You have to write the query in a way that it will not show any error.
# Maintain the context of the user input and remeber the previous conversation and queries.
# Start conversation with the user from greetings and then ask the user what he wants to do with the database.
# Then write the query according to the user input.



# input: {user_input}
# EXAMPLE: How many sales have been made in the last month? -> query
# output: SELECT COUNT(*) FROM sales WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH); 
# EXAMPLE: what is the total revenue generated from the sales in the last month? ->query
# output: SELECT SUM(revenue) FROM sales WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH);
# Example: Hello, whats up? -> conversation
# output: Hello! I'm here to help you with your database queries. So, how can I assist you today?


# user: {user_input}
# output: {response}

# """

# # Cache schemas after the first retrieval
# schema_cache = {}

# # @tool
# def get_schema_tool(table_name: str) -> str:
#     """Get the schema and sample data for a specific table"""
#     if table_name in schema_cache:
#         return schema_cache[table_name]
    
#     print(f"[Tool Log] get_schema_tool called with table_name={table_name}")
    
#     try:
#         connection = get_connection()
#         cursor = connection.cursor(dictionary=True)
        
#         # Get schema
#         cursor.execute(f"SHOW CREATE TABLE {table_name}")
#         schema_result = cursor.fetchone()
#         schema = schema_result['Create Table']
        
#         # Get sample data (first 5 rows)
#         cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
#         sample_data = cursor.fetchall()
        
#         # Format the response
#         response = f"Table: {table_name}\n\nSCHEMA:\n{schema}\n\nSAMPLE DATA:"
#         for row in sample_data:
#             response += f"\n{row}"
            
#         cursor.close()
#         connection.close()
        
#         # Cache the schema
#         schema_cache[table_name] = response
#         return response
        
#     except Exception as e:
#         return f"Error retrieving schema and data: {str(e)}"

# # @tool
# def execute_query_tool(query: str) -> list[dict[str, any]]:
#     """Execute a SQL query using a connection from the pool"""
#     connection = None
#     try:
#         print(f"[Tool Log] Attempting to get a connection from the pool...")
#         connection = get_connection()
#         if not connection:
#             print("[Tool Log] Failed to get a connection from the pool")
#             return []
        
#         print(f"[Tool Log] Executing query: {query}")
#         cursor = connection.cursor(dictionary=True)
#         cursor.execute(query)
#         results = cursor.fetchall()
#         print(f"[Tool Log] Query executed successfully. Results: {results}")
        
#         return results
#     except Exception as e:
#         print(f"[Tool Log] Error executing query: {str(e)}")
#         return {
#             "error": str(e)
#         }
#     finally:
#         if connection:
#             print("[Tool Log] Closing connection...")
#             connection.close()


# class State(TypedDict):
#     messages: Annotated[List[AnyMessage], add_messages]
#     intent: str | None
#     schema: str | None  
#     chosen_table: str | None
#     sql_query: str | None
#     query_results: List[Dict] | None
#     performance_metrics: Dict[str, str]
#     thread_id: str | None

# def print_performance_metrics(state: Dict) -> None:
#     """Helper function to print performance metrics"""
#     if "performance_metrics" in state:
#         print("\nPerformance Metrics:")
#         for metric, value in state["performance_metrics"].items():
#             print(f"{metric.replace('_', ' ').title()}: {value}")
#         print("This is the performance metrics of the query.")
#     else:
#         print("No performance metrics available for this query.")

    
# @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
# def call_model_with_retry(messages):
#     print("Retrying to get the response")
#     return model.generate_content(messages)

# def conversational_agent_node(state: State) -> Dict[str, List[AIMessage]]:
#     start_time = time.time()
#     print("NODE: conversational_agent_node - RUNNING")
    
#     try:
#         # Get all messages from state
#         messages = state["messages"]
        
#         # Convert messages to Gemini format, filtering out SQL-related messages
#         conversation_history = []
#         for msg in messages:
#             # Skip debug messages, SQL queries, and query results
#             if (isinstance(msg, AIMessage) and isinstance(msg.content, str) and 
#                 (msg.content.startswith("(Debug)") or 
#                  msg.content.startswith("Generated SQL:") or 
#                  msg.content.startswith("Retrieved schemas"))):
#                 continue
#             if isinstance(msg, ToolMessage):
#                 continue
                
#             # Convert to Gemini format
#             conversation_history.append({
#                 "parts": [{"text": msg.content}],
#                 "role": "user" if isinstance(msg, HumanMessage) else "model"
#             })
        
#         # Add system message at the beginning
#         conversation_history.insert(0, {
#             "parts": [{"text": """You are Chatbot for Boat Brokers specializing in Company Database Queries. 
#             Maintain context of the conversation and remember important details.
#             If asked about previous questions or information, recall them from the conversation history.
#             """}],
#             "role": "user"
#         })

#         # Generate response with proper error handling
#         try:
#             response = model.generate_content(conversation_history)
#             content = response.text
#         except Exception as e:
#             print(f"Gemini API error: {str(e)}")
#             content = "Sorry, I'm having trouble generating a response right now."

#         return {
#             "messages": [AIMessage(content=content)],
#             "performance_metrics": {
#                 **state.get("performance_metrics", {}),
#                 "conversational_response_time": f"{(time.time()-start_time):.2f}s"
#             }
#         }
        
#     except Exception as e:
#         print(f"Conversational Error: {str(e)}")
#         return {
#             "messages": [AIMessage(content="Error in conversation")],
#             "performance_metrics": {
#                 **state.get("performance_metrics", {}),
#                 "error": str(e)[:100]  # Truncate long errors
#             }
#         }


# def refine_query_node(state: State) -> Dict[str, Any]:
#     """Refine the user query into a SQL query"""
#     start_time = time.time()
#     print("NODE: refine_query_node - RUNNING")
#     try:
#         user_msg = next((msg.content for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)), "")
        
#         combined_prompt = f"""As an SQL expert, convert this user request into a valid SQL query using EXACT field names from these schemas:

# USER REQUEST: "{user_msg}" """

# SCHEMA = state.get("schema", None)

# def get_schema_from_state(state: State) -> str:
#     '''
#     Get the schema from the state.
#     '''
#     if state.get('schema') is not None:
#         return state['schema']
#     else:
#         return "No schema found in state."
    
# def run_after_finding_intent(intent: str) -> str:
#     """
#     This function will continue the conversation after finding the intent.
#     """
#     if intent == "query":
#         continue_conversation = "Yes, I can help you with that. Please provide the details of your query."

#     elif intent == "conversation":
#         continue_conversation = "Sure, let's continue our conversation. What would you like to discuss about?"
        
#     return 





    
