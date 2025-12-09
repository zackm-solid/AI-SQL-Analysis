## Phase 2 Prompts: Discovery

Using SELECT functionality only (no CREATE, UPDATE, DELETE), we will examine the Snowflake `SUN_SPECTRA` database.

### Task 1: The High-Level Scan

**Goal:** Verify the connection and see the landscape (Schemas).

> **User:**
> "I have connected you to the `SUN_SPECTRA` database in Snowflake. I need you to act as a Data Scout.
>
> Utilize the snowflake_client.py script for connection. 
>
> First, query the `INFORMATION_SCHEMA` or system catalog. List out all the **Schemas** available within this database. Do not look at tables yet; just give me the high-level buckets."
> 
> Once this is completed, add the information in a well-structured `data_documentation.md` file that we will use in future tasks and phases."

**Why this matters:**
This confirms the Agent actually has read access. If it can't list schemas, there is no point in asking for sales data. It also helps us identify if there are `DEV`, `PROD`, or `STAGING` schemas we need to be aware of.

### Task 2: The Table Muster

**Goal:** Identify the specific tables that look relevant to our "Executive Update" (Sales & Products).

> **User:**
> "Okay, I see the following relevant schemas:
>
>*   **CATALOG**: Likely contains product information, inventory, and SKU details.
>*   **CUSTOMER**: Likely contains customer profiles, accounts, and demographics.
>*   **ANALYTICS**: Likely acts as the serving layer for reporting and dashboards (e.g., Sales History).
>*   **FINANCE**: Likely contains financial records, revenue, and cost data.
>
> Please list all **Table Names** found within those schemas. Provide a one-sentence guess on what each table contains based *only* on its name."
> Add these details into the `data_documentation.md` file."

**Why this matters:**
This forces the AI to perform a "sanity check." If it sees a table named `SALES_2022_BACKUP`, we want it to flag that *now* so we don't accidentally query old data later.

### Task 3: The Schema Inspection (The "Map")

**Goal:** Now that we have targets, we need the technical specs to link them.

> **User:**
> "Target Acquired. I want to focus on specific tables you found:
>
> 1. `CATALOG.PRODUCT_CATALOG` (and possibly using `CATALOG.V_CATEGORY_PERFORMANCE`)
> 2. `FINANCE.TRANSACTIONS` 
> 3. `CUSTOMER.CUSTOMER_SEGMENT`
> 
> Please query the schema definition (DDL) for these tables.
>
> * List all column names and their data types.
> * Identify the **Primary Keys** and **Foreign Keys** that would allow these tables to join.
> * **CRITICAL:** Do these tables share a common column and can you adequately find a link between the tables above so that we can use them in coorellation to answer our original questions from `README.md`?"

**Why this matters:**
This is the "Measure Twice, Cut Once" moment. We are making the Agent prove to us that a join is possible *before* we ask it to write a complex analytical query.

**Results:**

The agent added the following key information to the `data_documentation.md` file.  It actually found a necessary join that I didn't identify at first (`SHIPBOB.ORDER_PRODUCTS`) to tie Transactions to Products for the product category portion of our analysis.

**1. Connecting Sales to Products:**
`FINANCE.TRANSACTIONS`  -->  `SHIPBOB.ORDER_PRODUCTS`  -->  `CATALOG.PRODUCT_VARIANTS_CATALOG`  -->  `CATALOG.PRODUCT_CATALOG`
*(Join Key: ORDER_ID)*        *(Join Key: VARIANT_ID)*          *(Join Key: PRODUCT_ID)*

**2. Connecting Sales to Customers:**
`FINANCE.TRANSACTIONS`  -->  `PUBLIC.ORDERS`  -->  `CUSTOMER.CUSTOMER_SUMMARY`  -->  `CUSTOMER.CUSTOMER_SEGMENT`
*(Join Key: ORDER_ID)*       *(Join Key: CUSTOMER_ID)*    *(Join Key: SEGMENT_NAME)*