import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from snowflake_client import get_connection

# Page Config
st.set_page_config(page_title="SunSpectra Executive Dashboard", layout="wide")
st.title("SunSpectra Executive Dashboard")

# Snowflake Connection
@st.cache_resource
def init_connection():
    return get_connection()

try:
    conn = init_connection()
except Exception as e:
    st.error(f"Failed to connect to Snowflake: {e}")
    st.stop()

# Helper function to run query
@st.cache_data(ttl=600)
def run_query(query):
    cur = conn.cursor()
    cur.execute(query)
    # Fetch results into a pandas DataFrame
    df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
    return df

# --- Section 1: Quarterly Performance ---
st.header("1. Quarterly Performance")
st.markdown("Total sales broken down by category and quarter.")

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
"""

try:
    df_q1 = run_query(q1_sql)
    # Convert QUARTER to datetime for better sorting/display if needed, though Snowflake returns date
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig1 = px.bar(df_q1, x="QUARTER", y="SALES", color="CATEGORY", title="Sales by Category and Quarter")
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        st.dataframe(df_q1)
        
except Exception as e:
    st.error(f"Error loading Quarterly Performance: {e}")

# --- Section 2: Product Extremes ---
st.markdown("---")
st.header("2. Product Extremes")
st.markdown("Top 5 and Worst 5 performing products per quarter.")

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
"""

try:
    df_q2 = run_query(q2_sql)
    
    # Create a unified visual or simple separate lists
    # For a diverging bar chart, we might want to flag them as "Top" or "Bottom"
    df_q2['Type'] = df_q2.apply(lambda x: 'Top 5' if x['RANKDESC'] <= 5 else 'Bottom 5', axis=1)
    
    # To make the visual interesting, maybe we just show the latest quarter? 
    # Or let user filter by quarter? Let's just show all for now, maybe faceted or colored.
    # Actually, a diverging bar chart is tricky with multiple quarters. 
    # Let's try to plot them, maybe referencing the specific request.
    
    fig2 = px.bar(df_q2, x="SALES", y="PRODUCT_NAME", color="Type", orientation='h', facet_col="QUARTER",
                  title="Top and Bottom 5 Products by Quarter", category_orders={"Type": ["Top 5", "Bottom 5"]})
    # Adjust layout to make sure labels fit
    fig2.update_yaxes(matches=None)
    st.plotly_chart(fig2, use_container_width=True)
    
    st.dataframe(df_q2)

except Exception as e:
    st.error(f"Error loading Product Extremes: {e}")

# --- Section 3: Customer Demographics ---
st.markdown("---")
st.header("3. Customer Demographics")
st.markdown("Top 3 customer age segments by spend (Last 6 Months).")

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
    df_q3 = run_query(q3_sql)
    
    # Dual Axis Chart
    fig3 = go.Figure()
    
    # Bar for Total Spend
    fig3.add_trace(go.Bar(
        x=df_q3['AGE_RANGE'],
        y=df_q3['TOTAL_SPEND'],
        name='Total Spend',
        marker_color='indigo'
    ))
    
    # Line for Avg Spend
    fig3.add_trace(go.Scatter(
        x=df_q3['AGE_RANGE'],
        y=df_q3['AVG_SPEND'],
        name='Avg Spend',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='orange', width=3)
    ))
    
    fig3.update_layout(
        title="Top 3 Age Segments: Total vs Avg Spend",
        yaxis=dict(title="Total Spend"),
        yaxis2=dict(title="Avg Spend", overlaying="y", side="right"),
        legend=dict(x=0.1, y=1.1, orientation="h")
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        st.dataframe(df_q3)

except Exception as e:
    st.error(f"Error loading Customer Demographics: {e}")
