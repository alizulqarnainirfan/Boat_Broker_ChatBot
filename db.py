## db.py

import os
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()

connection_pool = None

def get_connection():
    global connection_pool
    if connection_pool is None:
        connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="boat_pool",
            pool_size=5,
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=int(os.getenv("DB_PORT")),
            connect_timeout=30,
            auth_plugin="mysql_native_password",
        )
    return connection_pool.get_connection()

def fetch_schema() -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]

    schema_text = ""
    for table in tables:
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        columns = [f"{col[0]}" for col in cursor.fetchall()]
        schema_text += f"{table}({', '.join(columns)})\n"

    cursor.close()
    conn.close()
    return schema_text

def run_sql_query(sql: str):
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

        
def show_database(query):
    """
    Function to show the database's any feature by passing the query.
    This Function will establish a connection to the database and execute the query
    and check if the connection is working perfectly.
    """

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        databases = cursor.fetchall()
        # print("Here are the results of your query:")
        for db in databases:
            print(db[0])

    except mysql.connector.Error as e:
        print(f"Error: {str(e)}")
    
    finally:
        connection.close()

    
# show_database("SHOW TABLES")

    
