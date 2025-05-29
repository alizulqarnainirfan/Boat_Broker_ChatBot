# Database related all functions here

import os
# import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import mysql.connector.pooling


load_dotenv(override=True)

pool = None

def get_connection():
    
    """
    Gets the connection with the database
    """
    global pool

    try:
        if pool is None:
            pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name='boat_pool',
                pool_size=10,
                database = os.getenv("DB_NAME"),
                host = os.getenv("DB_HOST"),
                user = os.getenv("DB_USER"),
                password = os.getenv("DB_PASSWORD"),
                port = os.getenv("DB_PORT"),
                auth_plugin = "mysql_native_password",
                connect_timeout = 30,
                raise_on_warnings = True
            )

        return pool.get_connection()
    
    except mysql.connector.Error as e:
        
        if e.errno == errorcode.CR_CONN_HOST_ERROR:
            raise Exception("Server IP isn't whitelisted. Please add this IP to server Whitelist")
        
        else:
            raise Exception(f"Database Connection Error {str(e)}")
        
    
def fetch_schema():
    
    """
    Fetches the whole database as schema
    """
    
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SHOW TABLES")
        tables = [t[0] for t in cursor.fetchall()]

        schema = ""

        for table in tables:
            
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            columns = [col[0] for col in cursor.fetchall()]

            schema += f"{table}({','.join(columns)})\n"

        return schema

    except Exception as e:
        return f"Error: {str(e)}"
    
    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


def execute_query(sql : str):

    """
    Executes the sql query and fetch result from Database
    """

    cursor = None
    conn = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(sql)
        result = cursor.fetchall()

        return result
    
    except Exception as e:
        return f"Error: {str(e)}"
    
    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

    







        
# ans = execute_query("SELECT * FROM leads;")
# print(ans)