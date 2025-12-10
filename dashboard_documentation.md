# Streamlit Dashboard Documentation

This document consolidates the implementation plan and the final walkthrough for the SunSpectra Executive Dashboard.

---

# Part 1: Implementation Plan

## Goal Description
Build a Streamlit dashboard to answer Executive Questions regarding Quarterly Performance, Product Extremes, and Customer Demographics. The dashboard will query the `SUN_SPECTRA` Snowflake database live, utilizing the join paths verified in Phase 2.

## User Review Required
> [!IMPORTANT]
> **Dependencies**: Will install `streamlit`, `pandas`, `plotly`.
> **Calculation Logic**:
> *   Sales by Category will use `SHIPBOB.ORDER_PRODUCTS.PRICE_AFTER_DISCOUNT * QUANTITY` to ensure accurate attribution to products, rather than the total `TRANSACTION_AMOUNT`.
> *   "Last two quarters" for demographics will be defined as the last 6 months of data relative to the max date in the database (or current date if live).

## Proposed Changes

### Configuration
#### [NEW] [requirements.txt](requirements.txt)
*   Add `streamlit`, `pandas`, `plotly`.

### Application Logic
#### [NEW] [dashboard.py](dashboard.py)
*   **Imports**: `streamlit`, `pandas`, `plotly.express`, `plotly.graph_objects`.
*   **Connection**: properties from `snowflake_client.py` or reusing the existing connection logic customized for Streamlit caching (`@st.cache_data`).
*   **Section 1: Quarterly Performance**
    *   **SQL**:
        ```sql
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
        ```
    *   **SQL**: Updates to extract `QUARTER_LABEL` (e.g., 'Q1').
    *   **Visual**: Small Multiples Bar Chart, faceted by Category.

*   **Section 2: Product Extremes**
    *   **SQL**:
        ```sql
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
        ```
    *   **SQL**: Updates to extract `QUARTER_LABEL`.
    *   **Visual**: Horizontal Bar Chart (`orientation='h'`), faceted by Quarter, showing Top 5 and Bottom 5.

*   **Section 3: Customer Demographics**
    *   **SQL**:
        ```sql
        SELECT
            cs.AGE_RANGE,
            cs.SEGMENT_NAME,
            SUM(t.TRANSACTION_AMOUNT) as TOTAL_SPEND,
            AVG(t.TRANSACTION_AMOUNT) as AVG_SPEND
        FROM FINANCE.TRANSACTIONS t
        JOIN SHIPBOB.ORDERS o ON t.ORDER_ID = o.ORDER_ID
        JOIN CUSTOMER.CUSTOMER_SUMMARY csum ON o.CUSTOMER_ID = csum.CUSTOMER_ID
        JOIN CUSTOMER.DIM_SEGMENTS ds ON csum.SEGMENT_NAME = ds.SEGMENT_NAME
        JOIN CUSTOMER.CUSTOMER_SEGMENT cs ON ds.CUSTOMER_SEGMENT_ID = cs.CUSTOMER_SEGMENT_ID
        WHERE t.TRANSACTION_DATE >= DATEADD('MONTH', -6, (SELECT MAX(TRANSACTION_DATE) FROM FINANCE.TRANSACTIONS))
        GROUP BY 1, 2
        ORDER BY 3 DESC
        LIMIT 3
        ```
    *   **Visual**: Combo Chart (Bar for Total Spend, Line for Avg Spend) for the top 3 segments.

## Verification Plan
*   Run the `dashboard.py` and manually verify the visuals match specific executive requests (Small Multiples, Horizontal Bars).

---

# Part 2: Walkthrough

## Overview
We have successfully built a Streamlit dashboard that connects live to the `SUN_SPECTRA` Snowflake database. This dashboard answers the three key Executive Questions using real-time data.

## Features implemented

### 1. Quarterly Performance
*   **Question:** What are the total sales, broken down by category and quarter?
*   **Visualization:** Small Multiples Chart (Sales vs Quarter, faceted by Category).
*   **Logic:** Joins `FINANCE.TRANSACTIONS` to `CATALOG.PRODUCT_CATALOG` via `SHIPBOB` and `VARIANTS` tables to ensure accurate product attribution. Displays clean "Q1, Q2" labels.

### 2. Product Extremes
*   **Question:** What are the top 5 and worst 5 performing products for each quarter?
*   **Visualization:** Horizontal Bar Chart (Top 5 vs Bottom 5).
*   **Logic:** Uses `RANK()` window functions to dynamically identify the best and worst performers per quarter based on sales volume. Faceted by Quarter for distinct lists.

### 3. Customer Demographics
*   **Question:** Which 3 customer age segments purchased the most in the last two quarters?
*   **Visualization:** Combo Chart (Bar for Total Spend, Line for Avg Spend).
*   **Logic:**
    *   *Initial Attempt (Failed)*: Tried joining `CUSTOMER_SUMMARY` directly to `CUSTOMER_SEGMENT`.
    *   *Correction 1 (Partial)*: Added `DIM_SEGMENTS` as bridge. Still returned 0 results due to date filter.
    *   *Correction 2 (Partial)*: Fixed date filter to use `MAX(DATE)` instead of `CURRENT_DATE`. Still returned 0 results due to joining `PUBLIC.ORDERS`.
    *   *Correction 3 (Final)*: Identified `PUBLIC.ORDERS` has only 10 rows. Switched to **`SHIPBOB.ORDERS`** (2000 rows) as the correct bridge table, populated the chart successfully.
    *   *Final Join Path:* `FINANCE.TRANSACTIONS` -> **`SHIPBOB.ORDERS`** -> `CUSTOMER.CUSTOMER_SUMMARY` -> `CUSTOMER.DIM_SEGMENTS` -> `CUSTOMER.CUSTOMER_SEGMENT`.
    *   Aggregates spend by Age Range for the last 6 months (relative to max transaction date).
    *   *Sorting:* Results (Top 3 by Spend) are sorted by `AGE_RANGE` ascending (18-24, 25-34, 65+) for visual consistency.
    *   *Formatting:* Spend columns displayed as Currency ($).

## How to Run

1.  **Ensure Dependencies are Installed:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Launch the Dashboard:**
    ```bash
    streamlit run dashboard.py
    ```

3.  **View:**
    Open the URL provided in the terminal (usually `http://localhost:8501`).

## Verification Results
*   **Automated Query Test:** Passed. All SQL queries execute against the live database without error.
*   **Startup Test:** Passed. Streamlit application launches successfully.
