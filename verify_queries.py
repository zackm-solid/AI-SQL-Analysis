from snowflake_client import run_query
import pandas as pd

print("Verifying Dashboard Queries...")

q1_sql = """
SELECT
    DATE_TRUNC('QUARTER', t.TRANSACTION_DATE) as QUARTER,
    p.CATEGORY,
    SUM(op.PRICE_AFTER_DISCOUNT * op.QUANTITY) as SALES
FROM FINANCE.TRANSACTIONS t
JOIN SHIPBOB.ORDER_PRODUCTS op ON t.ORDER_ID = op.ORDER_ID
JOIN CATALOG.PRODUCT_VARIANTS_CATALOG pvc ON op.VARIANT_ID = pvc.VARIANT_ID
JOIN CATALOG.PRODUCT_CATALOG p ON pvc.PRODUCT_ID = p.PRODUCT_ID
GROUP BY 1, 2
ORDER BY 1, 2
LIMIT 10
"""

q2_sql = """
WITH ProductSales AS (
    SELECT
        DATE_TRUNC('QUARTER', t.TRANSACTION_DATE) as QUARTER,
        p.PRODUCT_NAME,
        SUM(op.PRICE_AFTER_DISCOUNT * op.QUANTITY) as SALES
    FROM FINANCE.TRANSACTIONS t
    JOIN SHIPBOB.ORDER_PRODUCTS op ON t.ORDER_ID = op.ORDER_ID
    JOIN CATALOG.PRODUCT_VARIANTS_CATALOG pvc ON op.VARIANT_ID = pvc.VARIANT_ID
    JOIN CATALOG.PRODUCT_CATALOG p ON pvc.PRODUCT_ID = p.PRODUCT_ID
    GROUP BY 1, 2
),
Ranked AS (
    SELECT
        *,
        RANK() OVER (PARTITION BY QUARTER ORDER BY SALES DESC) as RankDesc,
        RANK() OVER (PARTITION BY QUARTER ORDER BY SALES ASC) as RankAsc
    FROM ProductSales
)
SELECT * FROM Ranked WHERE RankDesc <= 5 OR RankAsc <= 5
ORDER BY QUARTER, SALES DESC
LIMIT 10
"""

q3_sql = """
SELECT
    cs.AGE_RANGE,
    cs.SEGMENT_NAME,
    SUM(t.TRANSACTION_AMOUNT) as TOTAL_SPEND,
    AVG(t.TRANSACTION_AMOUNT) as AVG_SPEND
FROM FINANCE.TRANSACTIONS t
JOIN PUBLIC.ORDERS o ON t.ORDER_ID = o.ORDER_ID
JOIN CUSTOMER.CUSTOMER_SUMMARY csum ON o.CUSTOMER_ID = csum.CUSTOMER_ID
JOIN CUSTOMER.CUSTOMER_SEGMENT cs ON csum.SEGMENT_NAME = cs.SEGMENT_NAME
WHERE t.TRANSACTION_DATE >= DATEADD('MONTH', -6, CURRENT_DATE())
GROUP BY 1, 2
ORDER BY 3 DESC
LIMIT 3
"""

try:
    print("Testing Q1...")
    run_query(q1_sql)
    print("Q1 Passed.")
    
    print("Testing Q2...")
    run_query(q2_sql)
    print("Q2 Passed.")
    
    print("Testing Q3...")
    run_query(q3_sql)
    print("Q3 Passed.")
    
    print("All queries verified successfully.")
except Exception as e:
    print(f"QUERY FAILED: {e}")
    exit(1)
