from snowflake_client import run_query
import pandas as pd

# Setting pandas display options to ensure we see the full output
pd.set_option('display.max_rows', None)

def list_schemas():
    print("Fetching schema list...")
    # SQL to get schema names. 
    # specific database is already set in .env ("SUN_SPECTRA")
    sql = """
    SELECT SCHEMA_NAME, SCHEMA_OWNER, CREATED, LAST_ALTERED 
    FROM INFORMATION_SCHEMA.SCHEMATA 
    ORDER BY SCHEMA_NAME
    """
    
    try:
        results = run_query(sql)
        
        if results:
            print(f"\nFound {len(results)} schemas:")
            # Convert to DataFrame for nicer printing if we have pandas, 
            # otherwise just print the list of dicts
            df = pd.DataFrame(results)
            print(df[['SCHEMA_NAME', 'SCHEMA_OWNER']])
        else:
            print("No schemas found or empty result.")
            
    except Exception as e:
        print(f"Error executing query: {e}")

if __name__ == "__main__":
    list_schemas()
