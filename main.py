# API endpoints and Chat logics here
# Main logic of API and code here

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import mysql.connector

# Loading Modules
from db import fetch_schema, execute_query, get_connection
from prompts import sql_prompt, llm_prompt, intent_prompt, build_where_clause_query
from utils import cleaned_sql, is_safe_sql, parse_vague_time_phrases, clean_llm_json_response
from llm import llm_response, llm_response_stream
from memory import get_history, append_to_history, clear_history
# from brochures import router as brochure_router
from brochures import generate_brochure
from reports import extract_filters_via_llm, generate_excel_report, sales_report_select_clause


# FASTAPI initializing 
app = FastAPI(title="THE BOAT BROKERS ChatBot", description="Smart AI assistant for Boat Brokers website", version="2.0")
# app.include_router(brochure_router)


# Add Cors for get/post security
app.add_middleware(
    
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]

)


# Pydantic base model for two inputs
class ChatRequest(BaseModel):

    session_id : str = 'admin'
    user_input : str


# Root End point
@app.get("/")

def root():

    return {
        "Message": "THE BOAT BROKERS ChatBot Runing ⚡"
    }


# Chat End Point
@app.post("/chat")
async def chat_endpoint(payload : ChatRequest):

    try:
        # Get session ID and User_input from input -> post (chat endpoint)
        session_id = payload.session_id
        user_input = payload.user_input


        # if user executes empty string
        if not user_input:
            return JSONResponse(status_code = 480, content = {"Error": " Missing 'query' field in the request"})



        # Getting the paramaters which we gonna pass to the Necessary functions
        schema = fetch_schema()
        history_list = get_history(session_id)
        history_str = "\n".join(history_list)
        clause_sale = sales_report_select_clause()


        # Lets calculate the intent of User's Message
        intent = llm_response(intent_prompt(user_input)).lower().strip()

        # Chat handling after calculating the intent of User's Message
        if intent == "query":

            # Detect vague time expressions like "last month", "this year"
            time_context = parse_vague_time_phrases(user_input)

            sql = llm_response(sql_prompt(user_input, schema, history_str, time_context))
            sql = cleaned_sql(sql)

            if not sql:
                return {"Response": "I couldn't generate a valid SQL query. Please repharase." }
            
            # This will not allow user to perform any bold operation through chatbot
            if not is_safe_sql(sql):
                return {"Response": "Unsafe command detected ❌ Sorry, I'm not allowed to perform these type of tasks"}
            
            result = execute_query(sql)
            prompt = llm_prompt(user_input=user_input, query_result=result, history=history_str)

            # Streaming Gemini response
            def stream_gen():

                full_response = ""
                for chunk in llm_response_stream(prompt):
                    full_response += chunk
                    yield chunk

                append_to_history(session_id, user_input, full_response)

            return StreamingResponse(stream_gen(), media_type="text/plain")

        elif intent == "conversation":

            def stream_gen():
            
                full_response = ""
                for chunk in llm_response_stream(user_input):
                    full_response += chunk
                    yield chunk
            
                append_to_history(session_id, user_input, full_response)

            return StreamingResponse(stream_gen(), media_type="text/plain")
        
        elif intent == "report":

            filters = extract_filters_via_llm(user_input)

            prompt = build_where_clause_query(filters, clause_sale)
            raw_llm_response = llm_response(prompt)
            parsed = clean_llm_json_response(raw_llm_response)
            query = parsed["query"]
            params = parsed["params"]





            # where_sql, params, table = build_where_clause(filters)

            # query = f"SELECT * FROM {table} {where_sql}"

            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(query, params)
            result = cursor.fetchall()

            if conn.is_connected():
                cursor.close()
                conn.close()
                

            return generate_excel_report(result, filters.get("type"))
        
        elif intent == "brochure":

            boat_name = llm_response(f"""You have given a user input, your job is to detect the name of boat from this input 
                                     and return only its name, nothing else. 

                                     For example:

                                     input: 'generate me a brochuer for alpha'
                                     boat name: alpha
                                     
                                     input: 'generate a brochure for senorita'
                                     boat name: senorita
                                     
                                     input: 'brochure for manaas'
                                     boat name: manaas
                                     
                                     input: 'for clarita generate brochures'
                                     boat name: clarita

                                     user input:
                                     {user_input}

                                     """)
            boat_name = boat_name.lower()

            try:
                conn = get_connection()

                # Use separate cursors for separate queries
                cursor1 = conn.cursor(dictionary=True)
                cursor2 = conn.cursor(dictionary=True)

                cursor1.execute("SELECT id FROM leads WHERE seller_boat_name = %s", (boat_name,))
                result = cursor1.fetchone()

                if not result:
                    raise HTTPException(status_code=404, detail=f"There is no boat named in Database as: {boat_name}")
                
                lead_id = result['id']
                
                # Second query to check brochure availability
                cursor2.execute("SELECT * FROM brochures WHERE name = %s", (boat_name,))
                brochure_avl = cursor2.fetchone()

                if not brochure_avl:
                    raise HTTPException(status_code=404, detail="Brochure data not found. Please fill it from the Admin panel")
                
                else:
                    return f"Here is your Brochure download link: https://admin.theboatbrokers.co.uk/admin/download/brochure/{lead_id} "

            except mysql.connector.Error as err:
                raise HTTPException(status_code=500, detail=str(err))

            finally:
                if conn.is_connected():
                    cursor1.close()
                    cursor2.close()
                    conn.close()            


            # return generate_brochure(boat_name)
        
        else:
            return {"Response": "Sorry I couldn't determine your intent. Try rephrasing"}

    except Exception as e:
        return {"Error": str(e)}
    


# user_input = "generate me a brochure of clarita"

# boat_name = llm_response(f"""You have given a user input, your job is to detect the name of boat from this input 
#                          and return only its name, nothing else. 
#                          For example:
#                          input: 'generate me a brochuer for alpha'
#                          boat name: alpha
#                          input: 'generate a brochure for senorita'
#                          boat name: senorita
#                          input: 'brochure for manaas'
#                          boat name: manaas
#                          input: 'for clarita generate brochures'
#                          boat name: clarita

#              user input: 
#              {user_input}
            
#  """)

# boat_name = boat_name.lower()
# for char in boat_name:
#     print(char)

