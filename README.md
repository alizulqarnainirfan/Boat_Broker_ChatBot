🚤 Boat Admin Chatbot
An AI-powered FastAPI chatbot built for boat broker admins and project managers to interact with sales, leads, vendors, and generate reports using natural language. The system leverages Gemini Pro (Google Generative AI) to convert user queries into SQL, fetch data from MySQL, and generate structured, downloadable Excel reports with intelligent context handling.

✨ Features
🤖 Smart Natural Language Chatbot
Understands and responds to both casual and business queries from admins and managers.

📊 Auto SQL Generation
Converts natural language into accurate SQL queries using Gemini Pro, with schema awareness.

🧠 Contextual Memory
Maintains in-memory session history to remember previous queries within the same session.

📅 Date Normalization
Converts vague dates like "last month" or "this quarter" into precise SQL date filters.

📄 Report Generator
Automatically generates downloadable Excel reports from natural queries (e.g., “sales in March”).

📁 Modular Code Structure
Clean, scalable, and production-ready code with separate files for database, memory, prompts, utils, and reports.

🔐 Secure MySQL Pooling
Uses pooled connections for efficient and scalable access to the database.

🏗️ Tech Stack
**Technology	        Purpose**
FastAPI	            Backend API framework
Gemini Pro	        Natural language understanding & SQL gen
MySQL	              Backend database
OpenPyXL	          Excel report generation
Pydantic	          Request validation
dotenv	            Secure environment variable management

📂 Project Structure

├── main.py               # FastAPI entry point
├── chat.py               # Handles chat logic
├── db.py                 # Database connections and helpers
├── memory.py             # In-memory chat history
├── prompts.py            # Gemini prompt templates
├── report.py             # Excel report generation
├── utils.py              # Date normalization and utility helpers
├── static/reports/       # Generated report files
├── .env                  # Environment variables (DB, API keys)

🚀 How to Run
Clone the Repository
git clone https://github.com/yourusername/boat-admin-chatbot.git
cd boat-admin-chatbot
Install Dependencies

pip install -r requirements.txt
Set Environment Variables

Create a .env file:

DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password
GEMINI_API_KEY=your_google_genai_key

Run the API

uvicorn main:app --reload
Access API

Chat endpoint: POST /chat

Report generation: POST /generate-report

Download report: GET /static/reports/{filename}

📬 Example Report Request

POST /generate-report
{
  "type": "sales",
  "start": "2024-04-01",
  "end": "2024-04-30",
  "filter": ""
}

📌 Use Case Scenarios
Admin: "Show me total sales last month."
✅ Auto SQL → Fetch → Response.

Manager: "Download vendor report from Jan 1 to Feb 15."
✅ Generate downloadable Excel.

🛠️ Future Improvements
🔍 Add natural language filtering (e.g., by region or status)

📈 Visual dashboard for report insights

🧾 Scheduled email reports

🧠 RAG with vector DB for advanced data sync

📄 License
This project is licensed under the MIT License.
