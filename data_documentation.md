# Data Documentation

## Database: SUN_SPECTRA

### High-Level Schemas
The following schemas have been identified within the `SUN_SPECTRA` database:

#### Core Business Logic
*   **CATALOG**: Likely contains product information, inventory, and SKU details.
*   **CUSTOMER**: Likely contains customer profiles, accounts, and demographics.
*   **ANALYTICS**: Likely acts as the serving layer for reporting and dashboards (e.g., Sales History).
*   **FINANCE**: Likely contains financial records, revenue, and cost data.

#### Integrations & External Data
*   **GOOGLE**: Data from Google Ads, Analytics, or other Google services.
*   **SHIPBOB**: Data from the fulfillment provider ShipBob.
*   **ZENDESK**: Customer support tickets and interaction history.
*   **EMAIL_CAMPAIGNS**: Data related to email marketing (e.g., Mailchimp, Klaviyo).

#### System & Development
*   **PUBLIC**: Default Snowflake schema.
*   **INFORMATION_SCHEMA**: System catalog views.
*   **DBT_DEV**, **DBT_DEV_MARTS**, **DBT_DEV_STAGING**: Development schemas managed by dbt.
*   **PUBLIC_MARTS**, **PUBLIC_STAGING**, **PUBLIC_DBT_STAGING**: Additional staging/mart schemas.

---

### Detailed Table Inspection

#### CATALOG Schema
*   **PRODUCT_CATALOG**: The master list of all products.
    *   *Columns*: `PRODUCT_ID (PK)`, `SKU`, `PRODUCT_NAME`, `CATEGORY`, `BRAND`, `BASE_PRICE`, `COST_PRICE`, etc.
*   **PRODUCT_VARIANTS_CATALOG**: Links Variants to Products.
    *   *Columns*: `VARIANT_ID (PK)`, `PRODUCT_ID (FK)`, `SKU`, `PRICE`, `SIZE`, `COLOR`.
*   **V_CATEGORY_PERFORMANCE**: Aggregate view of product/inventory stats by category.
    *   *Columns*: `CATEGORY`, `TOTAL_PRODUCTS`, `ACTIVE_PRODUCTS`, `TOTAL_STOCK`, `TOTAL_INVENTORY_VALUE`.

#### FINANCE Schema
*   **TRANSACTIONS**: The master ledger of financial transactions.
    *   *Columns*: `TRANSACTION_ID (PK)`, `ORDER_ID (FK)`, `TRANSACTION_DATE`, `TRANSACTION_AMOUNT`, `PAYMENT_STATUS`.
    *   *Note*: Does NOT contain `CUSTOMER_ID` or `PRODUCT_ID` directly.

#### CUSTOMER Schema
*   **CUSTOMER_SEGMENT**: Dictionary of customer segments.
    *   *Columns*: `CUSTOMER_SEGMENT_ID (PK)`, `SEGMENT_NAME`, `AGE_RANGE`.
*   **CUSTOMER_SUMMARY**: Aggregated customer profile data.
    *   *Columns*: `CUSTOMER_ID (PK)`, `SEGMENT_NAME (FK)`, `TOTAL_REWARDS_CLAIMED`, `JOIN_DATE`.

#### KEY BRIDGE TABLES (The "Glue")
*   **PUBLIC.ORDERS**: connecting Transactions to Customers.
    *   *Columns*: `ORDER_ID`, `CUSTOMER_ID`, `ORDER_DATE`, `FULFILLMENT_STATUS`.
*   **SHIPBOB.ORDER_PRODUCTS**: Connecting Orders to Product Variants.
    *   *Columns*: `ORDER_ID`, `VARIANT_ID`, `QUANTITY`, `PRICE_AFTER_DISCOUNT`.

---

### Join Strategy Map
To answer the Executive Questions, we must join across schemas carefully.

**1. Connecting Sales to Products:**
`FINANCE.TRANSACTIONS`  -->  `SHIPBOB.ORDER_PRODUCTS`  -->  `CATALOG.PRODUCT_VARIANTS_CATALOG`  -->  `CATALOG.PRODUCT_CATALOG`
*(Join Key: ORDER_ID)*        *(Join Key: VARIANT_ID)*          *(Join Key: PRODUCT_ID)*

**2. Connecting Sales to Customers:**
`FINANCE.TRANSACTIONS`  -->  `PUBLIC.ORDERS`  -->  `CUSTOMER.CUSTOMER_SUMMARY`  -->  `CUSTOMER.CUSTOMER_SEGMENT`
*(Join Key: ORDER_ID)*       *(Join Key: CUSTOMER_ID)*    *(Join Key: SEGMENT_NAME)*

**Alternative:**
The `ANALYTICS.TRANSACTIONS_DAILY` table was found to contain pre-aggregated metrics but lacks direct Product/Customer dimensions for deep segmentation. The manual join path above is preferred for the requested detailed analysis.

---
*Last Updated: 2025-12-09*
