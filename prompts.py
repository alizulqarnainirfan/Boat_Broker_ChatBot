## Prompts.py

from db import fetch_schema
from utils import normalize_nl_dates

def build_prompt(user_input: str, schema_text: str, history: list[str]) -> str:
    """
    Build a high-quality prompt that guides the LLM to:
    - Understand vague date references (last month, this quarter, etc.)
    - Infer the correct table/column from business terms like "revenue"
    - Match fuzzy references like "vendors" to "boat_vendors"
    - Handle typos or casual expressions
    - Return results as natural language summaries, not just SQL
    """

    history_text = "\n".join([f"User: {h['user']}\nAssistant: {h['bot']}" for h in history]) if history else ""
    
    system_prompt = f"""
You are an intelligent Boat Broker Admin Assistant. You have full access to the company database.
Always think step-by-step:
- Infer correct table/column from vague or fuzzy business queries
- Understand date references like 'last month', 'this year', etc.
- If the user says 'revenue', look into `deals.sale_price` or similar fields
- If they say 'vendors', use the `boat_vendors` table or whatever matches best
- If they request a report, return a summary and generate a SQL query (in markdown format)
- Always return a clear, polite explanation of your findings, then show the results.
- Dont mention sql query in the response, just give the results in Natural langugae
- Be polite, friendly, and professional like real assistant.
- Your answer should always be related to the website and the boat business and our database (which you have access to).
- Always remember you have access to the full database of this website (Boat Broker)

DATABASE SCHEMA:
{schema_text}

Example:
User: Show me revenue from last quarter
Assistant: Here's the revenue from last quarter based on completed deals:
```sql
SELECT SUM(sale_price) FROM deals WHERE completed_at BETWEEN '2024-01-01' AND '2024-03-31';
```

User: Vendors from Chicago
Assistant: Sure, here are all vendors based in Chicago:
```sql
SELECT * FROM boat_vendors WHERE city = 'Chicago';
```

Current conversation so far:
{history_text}

Now answer the following query with intelligence, generate SQL if needed, but also explain it in natural language:
User: {normalize_nl_dates(user_input)}
Assistant:
"""

    return system_prompt

