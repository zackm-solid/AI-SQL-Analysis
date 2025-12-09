# Human Plus AI Analyst: Defying Gravity

## Introduction

In my previous experiment, **Human Analyst vs. AI Analyst**, we pitted standard LLM chat interfaces against a human using Tableau. We learned that while AI is fast, it often lacks the nuance of a hands-on tool.

Today, we aren't just uploading a CSV to a chat window. We are using **Google's new AI IDE, Antigravity**, to connect directly to a live **Snowflake** database.

The goal? To see if an AI Agent can act as a true extension of the analyst; navigating schemas, writing production-ready SQL, and visualizing the data within the IDE, all from a natural language prompt.

## The Scenario: The Monday Morning "Fire Drill"

We are roleplaying a Senior Analyst at *SunSpectra* (our fictional retail company). It’s Monday morning, and the VP of Sales needs an "Executive Update" immediately. They aren't looking for a deep dive; they want a pulse check on performance to help them tell a story in their afternoon board meeting.

### The VP's Request

The VP has asked for three specific insights:

1. **Quarterly Performance:** What are the total sales, broken down by category and quarter? (Visual: Bar Chart + Table)
2. **Product Extremes:** What are the top 5 and worst 5 performing products for each quarter? (Visual: Diverging Bar Chart + Table)
3. **Customer Demographics:** Which 3 customer age segments purchased the most in the last two quarters? (Visual: Grouped Bar Chart with Avg Spend Line + Table)

*Note: For this analysis, Quarters are defined as calendar Q1 (Jan-Mar), Q2 (Apr-Jun), etc.*

## The Tool Stack

* **Database:** Snowflake (Hosting the *SunSpectra* Retail Dataset)
* **The Agent/IDE:** Google Antigravity
* **The Talent:** Me

## The Approach

Unlike a standard chat where you paste data, this workflow mimics a developer environment.

### Phase 1: Setup

Before asking the Agent to do anything, I need to connect it to the database and give it a context of the schema.

* **Goal:** Establish a "Context Layer" so the AI knows how tables join (e.g., `PRODUCT_ID` to `SKU`) without us explicitly writing the joins every time.

#### The Handshake (Connecting Antigravity to Snowflake)

Antigravity runs on a VS Code backbone, so the connection process feels familiar to developers but might be new to pure analysts.  Admitedly, the first time I set this up it required asking some questions to a coworker Eden Litvin and Gemini.  This is mostly a one-time setup for the project, and should be repeatable for any future projects if you utilize the framework here.

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

### Phase 2: Prompting & Generating

Instead of blind prompting, I used a separate instance of Gemini to generate **Instruction** for the Antigravity Agent. Think of this as translating "Business Ask" into "Robot Instructions."

I prefer to use this method when prompting AI agents, rather than just copy/pasting a large amount of instructions into a chat.

In my experience, this creates a better output with fewer follow-up steps since you're giving the tools a framework and criteria to work from.

While this seems like an extra step, you can use this template for other future projects, just filling in relevant details for the problem, and it enables the rest of this process to run smoothly.

*See full prompts and process [here](phase_2_prompts.md).*

### Phase 3: Execution (The Analysis)

We fed the instructions into the IDE Agent in three tasks as outlined above, one by one. Here is how it handled the workflow:

#### Task 1: Total Sales by Category/Quarter

* **The SQL Generation:** Did it handle the date grouping correctly?
* **The Visualization:** Did it render a clean bar chart?
* **Analyst Grade:** [Pass/Fail]

#### Task 2: Top & Worst 5 Products

* **The Complexity:** This requires ranking functions (like `QUALIFY` or `RANK()` in Snowflake). Did the AI figure that out, or did it try to do it in Python memory?
* **The Visualization:** Diverging bars are tricky. How did it handle the UI?
* **Analyst Grade:** [Pass/Fail]

#### Task 3: Customer Segmentation (The Join Heavy Lift)

* **The Complexity:** This requires joining Sales, Customers, and Products, filtering by specific dates, and grouping by age buckets.
* **The Visualization:** Combo charts (Bar + Line) are notoriously hard for AI agents to format correctly.
* **Analyst Grade:** [Pass/Fail]

## Results & Reflection

*(This section will be populated with the final output comparison)*

### Did it beat the Human?

* **Speed:** [TBD]
* **Accuracy:** [TBD]
* **Frustration Level:** [TBD]

### Key Takeaways for "Pauls" (Practitioners)

1. **Schema Context is King:** The Agent only performed as well as the metadata we exposed to it.
2. **The "Black Box" Problem:** Verifying the SQL generated by the IDE took nearly as long as writing it from scratch.
3. **Future Outlook:** This isn't replacing the analyst, but it might replace the *Junior* Analyst's SQL writing tasks.
