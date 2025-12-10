# Human Plus AI Analyst: Defying Gravity

<div align="center">
  <img src="assets/Defying%20Gravity.png" width="600" />
</div>

## Introduction

In my previous article, [**Human Analyst vs. AI Analyst**](https://www.datagoats.org/zack-martins-featured/human-analyst-vs-ai-analyst), I examined how three different AI tools would stack up against me (using Tableau) in analyzing a basic CSV dataset to find some insights.

Today, we go beyond the nice clean dataset (minus the date errors!) in a CSV. We're going to connect directly to a live **Snowflake** database and run queries, all within **Google's New AI IDE: Antigravity**.

The goal? To see if an AI Agent can act as a true extension of the analyst; navigating schemas, writing production-ready SQL, and visualizing the data within the IDE, all from a natural language prompt.

Want to follow along in greater detail? I've documented it all in this GitHub repo so you can see examples of code, prompts and more.

## The Scenario: The Monday Morning "Fire Drill"

We are roleplaying a Senior Analyst at *SunSpectra* (our fictional retail company). It’s Monday morning, and the VP of Sales needs an "Executive Update" immediately. They aren't looking for a deep dive; they want a pulse check on performance to help them tell a story in their afternoon meeting with the C-suite.

### The Request

The VP has asked for three specific insights:

1. **Quarterly Performance:** What are the total sales, broken down by category and quarter? (Visual: Small Multiples Chart + Table)
2. **Product Extremes:** What are the top 5 and worst 5 performing products for each quarter? (Visual: Horizontal Bar Chart + Table)
3. **Customer Demographics:** Which 3 customer age segments purchased the most in the last two quarters? (Visual: Bar Chart with Avg Spend Line + Table)

*Note: For this analysis, Quarters are defined as calendar Q1 (Jan-Mar), Q2 (Apr-Jun), etc. and should be grouped by in charts & tables and labeled as Q1, Q2, Q3.*

### The Tool Stack

* **Database:** Snowflake (Hosting the *SunSpectra* Retail Dataset)
* **The Agent/IDE:** Google Antigravity, Utilizing Google Gemini 3 Pro (High) Model
* **The Talent:** Me

### The Approach

The biggest difference from how we used the Cursor IDE previously for data analysis, is that we're connecting to a live database this time.

Antigravity is very similar to Cursor, the IDE is the same, it's just a difference in the agents. Therefore, everything we're doing here should also work in Cursor.

![Antigravity Agent](assets/Antigravity%20Agent.png)

## Phase 1: Connection 

Before asking the Agent to do anything, I need to connect it to the database and give it a context of the schema.

* **Goal:** Establish a "Context Layer" so the AI knows how tables join (e.g., `PRODUCT_ID` to `SKU`) without us explicitly writing the joins every time.

**Key Discoveries documented, as in [`data_documentation.md`](data_documentation.md):**
* **Schemas identified:** `CATALOG` (Products), `FINANCE` (Transactions), `CUSTOMER` (Demographics), and `SHIPBOB` (Fulfillment).
* **The Glue:** The Agent correctly identified that `FINANCE.TRANSACTIONS` did not contain customer or product IDs directly. It found the necessary bridge tables:
    * **Sales to Products:** `SHIPBOB.ORDER_PRODUCTS`
    * **Sales to Customers:** `PUBLIC.ORDERS` (Initially assumed) vs `SHIPBOB.ORDERS` (Actual).

### The Handshake (Connecting Antigravity to Snowflake)

Admitedly, the first time I set this up, it required asking some questions to my coworker (thanks [Eden Litvin](https://www.linkedin.com/in/eden-litvin/)!) and Gemini. I was able to first make a connection to Snowflake via their extension for VS Code, but the agent couldn't interact with it. I thought about opting for setting up MCP server, but this method worked great.

This is mostly a one-time setup for the project, and should be repeatable for any future projects if you utilize the framework here.

1. **Install Dependencies**: Open the Antigravity terminal and install the Snowflake connector and Dotenv to handle credentials securely.
```bash
pip install snowflake-connector-python[pandas] python-dotenv
```

2. **Create the "Bridge" Script**: We created a Python script (`snowflake_client.py`) to handle the connection. We opted for standard password authentication stored in environment variables.
```python
# Snippet from snowflake_client.py
def get_connection():
    return snowflake.connector.connect(
        # ... params ...
        password=os.getenv('SNOWFLAKE_PASSWORD')
    )
```

3.  **Set Environment Variables**: We created a `.env` file to store our credentials. **Crucially, since we're using Github for this repository, we added `.env` to our `.gitignore` file to prevent leaking secrets.**
```ini
SNOWFLAKE_ACCOUNT=YOURACCOUNT-IDENTIFIER
SNOWFLAKE_USER=YOUR_USERNAME
SNOWFLAKE_PASSWORD=YOUR_PASSWORD
SNOWFLAKE_ROLE=YOUR_ROLE
SNOWFLAKE_WAREHOUSE=YOUR_WH
SNOWFLAKE_DATABASE=YOUR_DB
SNOWFLAKE_SCHEMA=YOUR_SCHEMA
```

When substituting in real-world information for the above, a successful test connection was made.

## Phase 2: Prompting & Generating

Instead of blind prompting, I used a separate instance of Gemini to generate an **Instruction Document** for the Antigravity Agent. Think of this as translating "Business Ask" into "Robot Instructions".

I prefer to use this method when prompting agents, rather than just copy/pasting a large amount of instructions into a chat.

In my experience, this creates a better output with fewer follow-up steps since you're giving the tools a framework and criteria to work from.

While this seems like an extra step, you can use this template for other future projects, just filling in relevant details for the problem, and it enables the rest of this process to run smoothly.

*See full prompts and process [here](phase_2_prompts.md).*

## Phase 3: Execution (The Analysis)

We fed the instructions into the IDE Agent in three steps, having the agent work through one step completely & updating documentation, before moving to the next one.

The agent created a [`data_documentation.md`](data_documentation.md) file during the above process. We'll use that now when feeding the following prompt to the agent:

> Utilizing your discoveries within `data_documentation.md`, answer our three key questions from our executive and generate the charts needed for each question in a Streamlit dashboard that I can easily copy to a slide deck.
> For easy reference, here is the questions and charts requested:
> 1. **Quarterly Performance:** What are the total sales, broken down by category and quarter? (Visual: Small Multiples Chart + Table)
> 2. **Product Extremes:** What are the top 5 and worst 5 performing products for each quarter? (Visual: Horizontal Bar Chart + Table)
> 3. **Customer Demographics:** Which 3 customer age segments purchased the most in the last two quarters? (Visual: Grouped Bar Chart with Avg Spend Line + Table)
>
> *Note: For this analysis, Quarters are defined as calendar Q1 (Jan-Mar), Q2 (Apr-Jun), etc. and should be grouped by in charts & tables and labeled as Q1, Q2, Q3.*

Now, I'll go pour another cold brew while I wait for it to do it's thing.

## Phase 4: The Analysis of the Analysis

It's done! We get the message that our Streamlit app is live and we can go view it on `localhost:8501`.  Good news.

We also requested full documentation of the dashboard and data, so we have [`data_documentation.md`](data_documentation.md) and [`dashboard.md`](dashboard_documentation.md) files for those of you who want all of the technical details.

Before I dive into the tasks, I must stop here and say while this felt like a lot of setup, when you see it in action, it feels very "magical" to have it run all of these queries and create documentation of the schemas, tables, and relationships.

But, it's not perfect. We hit a snag on Task 3, I'll dive into that below.

### Task 1: Total Sales by Category/Quarter

* **Analyst Grade:** *Pass*
* **The SQL Generation:** The Agent successfully generated complex SQL queries involving 4-table joins to link `TRANSACTIONS` to `PRODUCT_CATALOG`.
* **The Visualization:** It created a small multiples chart, which I actually changed to after its first output. I originally suggested a stacked bar chart, but it was way too cluttered to read. While there's a lot going on in the small multiples chart, I think it reads much better - we have a lot of categories to report on.

    If I had to make an additional edit, I would simply have it sort the categories in the graph and table to DESC order so it was very easy to see the top performers. But, for our experiment, I figured I'd display what it actually churned out from the initial prompt on this chart type.

![Quarterly Performance](assets/Quarterly%20Performance.png)


### Task 2: Top & Worst 5 Products

* **Analyst Grade:** *Pass*
* **The Complexity:** This requires ranking functions and CTEs. Like in the above, it made some beautiful SQL that appears to pull in the right data.
* **The Visualization:** Not Bad! The spacing is a little weird and sometimes bars overlap as you scroll, but it's easy to read.

    I think doing some additional customization of the visuals would be worth it if we were making a permanent dashboard, but that's easy to do with some follow-up prompts suggesting tweaks to color or format.

    Plus, remember this is for a meeting this afternoon - we were aiming for simplicity.

![Product Extremes](assets/Product%20Extremes.png)


### Task 3: Customer Segmentation (The Join Heavy Lift)

* **The Complexity:** This requires joining Sales, Customers, and Products, filtering by specific dates, and grouping by pre-determined customer segment data.
* **The Visualization:** The final visualization looks great!  A clean combo (bar/line) chart with a good table for details. This time, I did ask it to do a sort of the categories from 18-24, 25-34, and 65+.

For some reason, we don't have a 35-65 category in the table. Sorry, fellow Millenials and Gen X'rs.

This is simulated data, to be fair - and yes, I did check in Snowflake just to make sure.

![Demographics Success](assets/Demographics%20Success.png)

**OK - so what was that snag I mentioned? The initial chart returned no data.**

* **The Failure:** As seen below, the chart axes were drawn, but no data was plotted.

![Demographics Failure](assets/Demographics%20Fail.png)

* **The Investigation:**
    * The Agent initially joined `FINANCE.TRANSACTIONS` to `PUBLIC.ORDERS`.
    * Upon deeper inspection (documented in [`dashboard_documentation.md`](dashboard_documentation.md)), we discovered `PUBLIC.ORDERS` contained only 10 rows of test data.
    * **The Fix:** We redirected the join path to **`SHIPBOB.ORDERS`** (2,000+ rows).  This did take a couple of follow up prompts, but nothing we couldn't solve within Antigravity, chatting with the Agent.
    * **The Result:** The chart populated with the correct segments once the correct join path was identified.

* **Analyst Grade:** *Overall Pass... It just required some additional prompting to correct.*

## Key Takeaways

1. **Schema Context is King:** The Agent performed well overall, but the way we prompted it played a big role in that. It's worth it, to get quality results, to do this prompting up front. Having an agent just start to go write SQL without any discovery or context, has been well-documented in analytics blogs that it doesn't go well.
2. **Not Perfect, but Damn Good:** We needed to dig deeper when things failed, but that's to be expected. Not every query I have ever written has been perfect, and sometimes I've had to go and do a bunch of queries on the side to figure out why things aren't lining up the way I thought they would. Turns out, this the same flow, but just doing it with prompts instead of actually writing SQL.
3. **The "Black Box" Problem:** This is generally just a problem with AI or complex systems where you're not seeing all of the individual inner workings happening, so it's harder to trust. In fact, if I just blindly trust it, I could be feeding my executive bad data. So, I found myself wanting to verify the results, even if everything in the documentation made sense. This feels partly like a human problem, rather than an AI problem. Maybe it's something that can be solved as I continue to use the tool more, review documentation, and build my own confidence in its accuracy.
4. **Future Outlook:** As I have often concluded in my [articles](https://www.datagoats.org/blog) that cover how AI will affect analytics career, nothing's changed. This tool isn't going to replace an analyst. With the right context & documentation prepared, it could take over SQL generation for an analyst. I think that's a good thing. Having more time to tackle bigger work. Nobody wants to just be a SQL Monkey, anyways.