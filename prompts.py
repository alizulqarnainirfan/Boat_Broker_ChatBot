# Prompts related functions


def sql_prompt(user_input : str, schema :str, history : str, time_context : dict = None) -> str:
    
    """
    Buils an efficient prompt for LLM to convert natural language to SQL Query
    """
    
    time_info = ""
    if time_context:
        time_info = f"""
NOTE:
Based on user's input, the following time context was detected:
Start Date: {time_context['start_date']}
End Date: {time_context['end_date']}

If dates are relevant, use them in your WHERE clause.
"""
        

    prompt = f"""
You are a helpful AI assistant for a Boat Brokers website.

Your job is to convert the given user input into a valid, error-free SQL query based on the database schema provided.
Return only the SQL query. Do not include explanations, comments, markdown, or code blocks. You have the whole database schema, so use it while writing sql query.
You should be smart enough to understand whole database using this schema(provided below).
You have previous messages history as CONVERSATION HISTORY, use that for the context of conversation. Maintain context throughout the whole conversation (first read CONVERSATION HISTORY then USER INPUT and SCHEMA)

IMPORTANT NOTE: 
- vendors or vendor are written 'seller' in database. So, when user asks for vendor make sure you replace vendor with seller
- Data is mainly in the 'leads' table, all the buyers, sellers/vendors are present there, seperated by column 'type' (buyer/seller).
- Sales Data is in 'deals' Table (if you cant find sales data in 'deals' then you can check 'leads' table)
- Here is leads table structure: leads(id,type,source,facebook,instagram,linkedin,twitter,status,date,salutation_1,salutation_2,first_name_1,surname_1,first_name_2,surname_2,address_1,address_2,email_1,email_2,telephone_1,telephone_2,buyer_preference_boat,buyer_preference_stern_type,buyer_preference_length,buyer_preference_layout,buyer_budget,seller_boat_name,seller_boat_lying_at,seller_preference_boat,seller_boat_length,seller_preference_stern_type,seller_boat_year_built,seller_boat_builder,seller_boat_steel_spec,seller_boat_fit_out,seller_boat_no_of_berths,seller_boat_engin,seller_boat_last_service,seller_boat_blacking,seller_boat_anodes,seller_boat_safety_certificate,seller_boat_rcd_compliant,seller_boat_recent_survey,seller_boat_reason_for_sale,seller_valuation_low,seller_valuation_high,seller_commission_rate,seller_sale_price,is_archived,created_at,updated_at,note,buyer_preference_boat_name,won_at,listed,listed_at)
- Here is deals table structure: deals(id,boat_seller_id,boat_buyer_id,status,survey,amendment,buyer_acceptance_letter,vendor_acceptance_letter,brokerage_offer_form_buyer,agreement_for_sale_purchase_both,bill_of_sale_seller,buyer_amendment_letter,vendor_amendment_letter,buyer_completion_letter,vendor_completion_letter,statement_of_account_seller,deposit,deposit_date,balance,balance_date,sale_price,sale_price_date,completed_at,canceled_at,commission,note,created_at,updated_at)
NOTE: 
- Vendors are known as sellers in database
- Sales are known as deals in database
- 'deals' table have column 'status' where contract received is reffered as 'contract_received' and cancelled is reffered as 'canceled' 


CONVERSATION HISTORY:
{history}

USER INPUT:
{user_input}

{time_info}

DATABASE SCHEMA:
{schema}



Important:
- Use only the table and column names from the given schema.
- Write clean and syntactically correct SQL.
- Don't return anything other than sql
- Don't include any explanation, comments, markdown or anything with the SQL


"""
    
    return prompt


def llm_prompt(user_input : str, query_result, history: str) -> str:

    
    """
    Builds an efficient prompt with user input and its correspondes result in database
    to convert raw result into Natural Language for Human
    
    """

    prompt = f"""
You are an intelligent AI assistant for admin of Boat Brokers website names as THE BOAT BROKERS.
You have been provided with user input and its result/response according to website database.
Your job is to convert this raw result into a Human friendly and Natural Language.
Be polite, kind, talk like humans do and always answer intelligently.
You also have previous chat history for conversation context.
You have previous messages history as HISTORY, use that for the context of conversation. Maintain context throughout the whole conversation (first read HISTORY then USER_INPUT and RESPONSE/RESULT)


USER_INPUT : 
{user_input}

RESPONSE/RESULT :
{query_result}

HISTORY :
{history}

"""
    
    return prompt


def intent_prompt(user_input: str):
    """
    Generates a well-structured prompt for an LLM to classify the user's intent
    on a boat broker website.

    The LLM should return one of the following categories:
    - 'query'
    - 'conversation'
    - 'report'
    - 'brochure'
    """

    prompt = f"""
You are an intelligent assistant for a boat broker website called **THE BOAT BROKERS**.
Your job is to classify the user input into **one of the following categories**:

1. **query** - The user is asking for business-related data, often requiring database queries.
   Examples:
   - "Show me all buyers from last month"
   - "How many leads came from California?"
   - "List vendor emails"

2. **conversation** - The user is engaging in casual or non-technical conversation.
   Examples:
   - "Hi, how are you?"
   - "Can you help me?"
   - "Thanks a lot!"

3. **report** - The user wants to generate or download a report (usually in Excel format).
   Look for words like: generate, download, create, excel, xlsx, report.
   Examples:
   - "Download a report of all vendors"
   - "Generate buyer report in Excel"
   - "Create xlsx file for this month’s sales"

4. **brochure** - The user wants a brochure (PDF or summary document) for a vendor or seller.
   Examples:
   - "Generate a brochure for this vendor"
   - "Can you make a seller brochure?"
   - "I need a brochure for boat 123"

Classify the following input into one of these four categories and return only the label:

User Input: `{user_input}`
"""

    return prompt



def build_filter_extraction_prompt(user_message: str, time_context : dict = None) -> str:
    """
    Structured, Efficient prompt for LLM to extract all the filers for report Generation
    from user input to chatbot.
    """

    time_info = ""
    if time_context:
        time_info = f"""
NOTE:
Based on user's input, the following time context was detected:
Start Date: {time_context['start_date']}
End Date: {time_context['end_date']}

If dates are relevant, use them in your WHERE clause.
"""


    prompt = f"""
You are a smart assistant that extracts structured filters from natural language.

Given the user message below, extract the following filters:

- type: one of 'vendors', 'buyers', or 'sales' (synonyms: seller = vendors)
- status:
    - For vendors/buyers: one of 'all', 'new', 'won', 'archived'
    - For sales: one of 'all', 'current', 'completed', 'cancelled'
- date_range: extract as {{"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"}}
- boat_type: one of 'narrow_boat', 'wide_beam', 'any'
- stern_type: one of 'cruiser', 'semi_traditional', 'traditional', 'euro_cruiser', 'other', 'any'
- budget: one of 'Under £25K', '£25k-50k', '£50k-75k', '£75k-£100k', '£100k+', 'All' (only for buyers/sales)
- layout: one of 'traditional', 'reverse', 'engine_room', 'any' (only for buyers/sales)

Return output as a JSON object. If a filter is not specified in the message, set its value to null.

User message:
\"\"\"
{user_message}
\"\"\"

time context:
\"\"\"
{time_info}
\"\"\"
"""

    return prompt


def build_where_clause_query(filters: dict, sales_report_where_clause : str) -> str:
    """
    Generate a clear and safe prompt that instructs an LLM to generate a parameterized SQL query
    and corresponding parameters based on the provided filters and schema.
    """

    prompt = f"""
You are an assistant that generates safe, parameterized SQL queries based on user-provided filters and a known database schema.

### Database Schema

- **leads** table:
  - id, type, source, facebook, instagram, linkedin, twitter, status, date,
  - salutation_1, salutation_2, first_name_1, surname_1, first_name_2, surname_2,
  - address_1, address_2, email_1, email_2, telephone_1, telephone_2,
  - buyer_preference_boat, buyer_preference_stern_type, buyer_preference_length,
  - buyer_preference_layout, buyer_budget,
  - seller_boat_name, seller_boat_lying_at, seller_preference_boat, seller_boat_length,
  - seller_preference_stern_type, seller_boat_year_built, seller_boat_builder,
  - seller_boat_steel_spec, seller_boat_fit_out, seller_boat_no_of_berths,
  - seller_boat_engin, seller_boat_last_service, seller_boat_blacking, seller_boat_anodes,
  - seller_boat_safety_certificate, seller_boat_rcd_compliant, seller_boat_recent_survey,
  - seller_boat_reason_for_sale, seller_valuation_low, seller_valuation_high,
  - seller_commission_rate, seller_sale_price, is_archived, created_at, updated_at,
  - note, buyer_preference_boat_name, won_at, listed, listed_at

- **deals** table:
  - id, boat_seller_id, boat_buyer_id, status, survey, amendment,
  - buyer_acceptance_letter, vendor_acceptance_letter, brokerage_offer_form_buyer,
  - agreement_for_sale_purchase_both, bill_of_sale_seller, buyer_amendment_letter,
  - vendor_amendment_letter, buyer_completion_letter, vendor_completion_letter,
  - statement_of_account_seller, deposit, deposit_date, balance, balance_date,
  - sale_price, sale_price_date, completed_at, canceled_at, commission,
  - note, created_at, updated_at

### Instructions

- You will receive a Python `filters` dictionary next.
- Your job is to generate a **parameterized SQL SELECT query** with `%s` placeholders.
- Also return a list of values to safely bind to those placeholders (`params`).

#### Requirements:

1. Use `leads` table if type is `"buyer"` or `"seller"`.
2. Use `deals` table if type is `"deals"`.
3. When using `leads`, include `type = 'buyer'` or `type = 'seller'` in the WHERE clause.
4. Ignore any filters whose values are `"all"`, `"any"`, `null`, or empty strings.
5. Use `BETWEEN %s AND %s` for `created_at` date range filters.
6. Field mapping rules:
    - For type `"buyer"` (leads):
        - `boat_type` → `buyer_preference_boat`
        - `stern_type` → `buyer_preference_stern_type`
        - `budget` → `buyer_budget`
        - `layout` → `buyer_preference_layout`
    - For type `"seller"` (leads):
        - `boat_type` → `seller_preference_boat`
        - `stern_type` → `seller_preference_stern_type`
        - `budget` and `layout` should be ignored

    - For type `"deals"`:
        - Use the following select clause:
        {sales_report_where_clause}
        ### - Base query on `deals` table.
        - JOIN the `boat_buyers` table ON `deals.boat_buyer_id = buyer.id`.
        - JOIN the `boat_sellers` table ON `deals.boat_seller_id = seller.id`.
        - JOIN `leads` AS `buyer_lead` ON `boat_buyers.lead_id = buyer_lead.id`.
        - JOIN `leads` AS `seller_lead` ON `boat_sellers.lead_id = seller_lead.id`.
        - Apply filters using:
            - Check both `buyer_lead.buyer_preference_boat` and `seller_lead.seller_preference_boat` for `boat_type`. Return results matching buyer or seller boat type preferences, including all if both match.
            - Check both `buyer_lead.buyer_preference_stern_type` and `seller_lead.seller_preference_stern_type` for `stern_type`. Return results matching buyer or seller stern type preferences, including all if both match.
            - `buyer_lead.buyer_budget` for `budget`
            - `buyer_lead.buyer_preference_layout` for `layout`
        - Filters are optional and should be ignored if value is `"all"`, `"any"`, `null`, or `""`.
        - Use `deals.created_at` for the date range filter (`BETWEEN %s AND %s`).

7. Always sort by `deals.created_at ASC` in sales reports.


#### Output Format

Respond **only** with a JSON object:

```json
{{
  "query": "SELECT ... WHERE ... ORDER BY created_at ASC",
  "params": [param1, param2, ...]
}}

Do not define a function. Do not return Python code.  
Respond **only** with a JSON object, like this:

{{
  "query": "SELECT ... WHERE ... ORDER BY created_at ASC",
  "params": ["value1", "value2", ...]
}}

Here are the filters:
{filters}
Now generate the query.


"""
    
    return prompt



# from reports import extract_filters_via_llm
# from llm import llm_response

# fil = extract_filters_via_llm("Generate me a report of buyer who have status won from 1st may 2025 to 20 may 2025, boat type is narrow boat , stern type is cruiser, budget is under £25k and layout is traditional")
# sql, param = llm_response(build_where_clause_query(filters=fil))  

# print(f"{sql} \n\n\n {param}")



    # - For type `"deals"`:
    #     - Base query on `deals` table
    #     - But the following filters come from `leads`:
    #         - `boat_type` → match either `buyer_preference_boat` or `seller_preference_boat`
    #         - `stern_type` → match either `buyer_preference_stern_type` or `seller_preference_stern_type`
    #         - `budget` → match `buyer_budget`
    #         - `layout` → match `buyer_preference_layout`
    #     - Assume proper JOINs or subqueries to access `leads` table fields