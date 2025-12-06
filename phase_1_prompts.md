## Phase 1 Prompts: Discovery

Using SELECT functionality only (no CREATE, UPDATE, DELETE), we will examine the Snowflake `SUN_SPECTRA` database.

### Step 1: The High-Level Scan

**Goal:** Verify the connection and see the landscape (Schemas).

> **User:**
> "I have connected you to the `SUN_SPECTRA` database in Snowflake. I need you to act as a Data Scout.
>
> Utilize the snowflake_client.py script for connection. 
>
> First, query the `INFORMATION_SCHEMA` or system catalog. List out all the **Schemas** available within this database. Do not look at tables yet; just give me the high-level buckets."

**Why this matters:**
This confirms the Agent actually has read access. If it can't list schemas, there is no point in asking for sales data. It also helps us identify if there are `DEV`, `PROD`, or `STAGING` schemas we need to be aware of.

### Step 2: The Table Muster

**Goal:** Identify the specific tables that look relevant to our "Executive Update" (Sales & Products).

> **User:**
> "Okay, I see schemas named `CATALOG` and `ANALYTICS` (or `SALES`).
>
> Please list all **Table Names** found within those two schemas. Provide a one-sentence guess on what each table contains based *only* on its name."

**Why this matters:**
This forces the AI to perform a "sanity check." If it sees a table named `SALES_2022_BACKUP`, we want it to flag that *now* so we don't accidentally query old data later.

### Step 3: The Schema Inspection (The "Map")

**Goal:** Now that we have targets (likely `PRODUCT_CATALOG` and `SALES_HISTORY`), we need the technical specs to link them.

> **User:**
> "Target Acquired. I want to focus on two specific tables you found:
>
> 1. `SUN_SPECTRA.CATALOG.PRODUCT_CATALOG`
> 2. `SUN_SPECTRA.ANALYTICS.SALES_HISTORY` (or whatever table name it found in Step 2)
>
> Please query the schema definition (DDL) for these two tables.
>
> * List all column names and their data types.
> * Identify the **Primary Keys** and **Foreign Keys** that would allow these two tables to join.
> * **CRITICAL:** Do these tables share a common column like `SKU`, `PRODUCT_ID`, or `EAN`?"

**Why this matters:**
This is the "Measure Twice, Cut Once" moment. We are making the Agent prove to us that a join is possible *before* we ask it to write a complex analytical query. If the Agent says, "I see `PRODUCT_ID` in one table and `PROD_REF_ID` in the other," we can catch that mismatch immediately.
