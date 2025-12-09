from snowflake_client import run_query

print("Debugging Transactions -> Orders Join...")

# 1. Get sample ORDER_IDs from Transactions in the filtered range
sql_sample_ids = """
SELECT ORDER_ID, TRANSACTION_DATE
FROM FINANCE.TRANSACTIONS 
WHERE TRANSACTION_DATE >= DATEADD('MONTH', -6, (SELECT MAX(TRANSACTION_DATE) FROM FINANCE.TRANSACTIONS))
LIMIT 5
"""
print("Sample Transaction IDs:")
trans_samples = run_query(sql_sample_ids)
print(trans_samples)

if not trans_samples:
    print("No transactions found in range!")
    exit()

sample_ids = [str(row['ORDER_ID']) for row in trans_samples]
ids_formatted = ", ".join([f"'{oid}'" for oid in sample_ids])

# 2. Check if these IDs exist in SHIPBOB.ORDERS
sql_check_orders = f"""
SELECT ORDER_ID, CUSTOMER_ID
FROM SHIPBOB.ORDERS
WHERE ORDER_ID IN ({ids_formatted})
"""
print(f"Checking for IDs in SHIPBOB.ORDERS: {ids_formatted}")
found_orders = run_query(sql_check_orders)
print("Found in SHIPBOB.ORDERS:", found_orders)

# 3. Check Order count generally
print("Total SHIPBOB.ORDERS Count:", run_query("SELECT COUNT(*) as CNT FROM SHIPBOB.ORDERS"))

# 4. Check Orders date range (if available, e.g. CREATED_AT?)
# I'll check columns of PUBLIC.ORDERS first to see if there's a date column
print("Columns in PUBLIC.ORDERS:", run_query("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'PUBLIC' AND TABLE_NAME = 'ORDERS'"))
