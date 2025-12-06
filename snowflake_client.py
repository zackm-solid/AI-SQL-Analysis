import os
import snowflake.connector
from snowflake.connector import DictCursor
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

def get_connection():
    """
    Connects using Password authentication.
    """
    # Ignore local configuration file to avoid interference
    os.environ["SNOWFLAKE_HOME"] = "/tmp"

    return snowflake.connector.connect(
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA'),
        role=os.getenv('SNOWFLAKE_ROLE')
    )

def run_query(query):
    print(f"Executing: {query}")
    conn = get_connection()
    try:
        cur = conn.cursor(DictCursor)
        cur.execute(query)
        results = cur.fetchall()
        return results
    finally:
        conn.close()

if __name__ == "__main__":
    # Test it out
    try:
        results = run_query("SELECT CURRENT_VERSION(), CURRENT_ROLE()")
        print(f"Results: {results}")
    except Exception as e:
        print(f"Connection failed: {e}")
