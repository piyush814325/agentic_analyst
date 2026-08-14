"""
Individual node implementations for the LangGraph agent.
Each node performs a specific step in the SQL analysis workflow.
"""

import logging
import re
from typing import Optional, List, Tuple
import pandas as pd
from sqlalchemy import text
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

from db import (
    get_database_schema,
    get_table_sample,
    get_db_connection
)
from agent.state import AgentState
from config import GROQ_API_KEY

logger = logging.getLogger(__name__)

# Initialize Groq LLM
# Note: Parameter names come from langchain-groq 0.1.5 model_fields
llm = ChatGroq(**{
    "model_name": "llama-3.3-70b-versatile",
    "temperature": 0,
    "groq_api_key": GROQ_API_KEY
})


class SQLValidator:
    """Validates SQL queries for safety and correctness."""

    # All standard statement types are now permitted (SELECT, INSERT,
    # UPDATE, DELETE, and common DDL). Anything not on this list is
    # rejected outright rather than keyword-blocked, since an allow-list
    # is far harder to bypass than trying to enumerate every dangerous
    # keyword.
    ALLOWED_STATEMENTS = {
        'SELECT', 'INSERT', 'UPDATE', 'DELETE',
        'CREATE', 'ALTER', 'DROP', 'TRUNCATE', 'REPLACE'
    }

    # Statement types that return rows via fetchall(); everything else
    # (writes/DDL) reports an affected/changed row count instead.
    ROW_RETURNING_STATEMENTS = {'SELECT'}

    @staticmethod
    def get_statement_type(sql: str) -> str:
        """Return the leading keyword of a SQL statement, e.g. 'SELECT', 'UPDATE'."""
        stripped = sql.strip()
        if not stripped:
            return ""
        return stripped.split(None, 1)[0].upper()

    @staticmethod
    def is_safe(sql: str) -> Tuple[bool, Optional[str]]:
        """
        Check if SQL query is well-formed and of a permitted statement type.
        Returns (is_safe, error_message)
        """
        sql_stripped = sql.strip()
        if not sql_stripped:
            return False, "Empty query"

        sql_upper = sql_stripped.upper()
        statement_type = SQLValidator.get_statement_type(sql_stripped)

        if statement_type not in SQLValidator.ALLOWED_STATEMENTS:
            return False, f"Unsupported or unrecognized statement type: {statement_type}"

        # Still reject stacked statements: a trailing semicolon is fine,
        # but a semicolon followed by more SQL means a second statement
        # was smuggled into one response, which makes rowcount/result
        # reporting ambiguous and lets an LLM slip in an unrelated
        # operation alongside the intended one.
        body = sql_upper.rstrip().rstrip(';')
        if ';' in body:
            return False, "Multiple SQL statements in a single query are not allowed"

        return True, None

    @staticmethod
    def clean_markdown(sql: str) -> str:
        """Remove markdown code fences from SQL.

        Handles all common LLM output shapes in one pass:
          - backtick-sql ... backtick
          - backtick ... backtick (no language tag)
          - leading prose before the opening fence
          - closing fence with or without a trailing newline
        Previously three separate regex passes that failed on any response
        where the LLM added a preamble or omitted the newline before the
        closing fence; replaced with a single re.DOTALL search so
        multi-line SQL is always captured correctly.
        """
        sql = sql.strip()
        # Extract content between the outermost fences if present.
        fenced = re.search(
            r'```(?:sql)?\s*\n(.*?)(?:\n```|```)',
            sql,
            re.DOTALL | re.IGNORECASE
        )
        if fenced:
            return fenced.group(1).strip()
        # No fences — strip any stray backtick-only lines defensively.
        sql = re.sub(r'^```[a-z]*\s*$', '', sql, flags=re.MULTILINE)
        return sql.strip()


def _is_valid_input(query: str) -> bool:
    """
    Quick validation to check if input is meaningful.
    Filters out gibberish, empty strings, or pure noise.
    Returns True if input looks valid, False if it's noise.
    """
    if not query or not query.strip():
        return False
    
    # Very short inputs (1-2 chars) are likely typos/noise unless they're valid words
    if len(query.strip()) <= 2:
        common_short_words = {"i", "a", "is", "it", "we", "ok", "hi", "no", "go", "do", "be"}
        return query.strip().lower() in common_short_words
    
    # If mostly gibberish (non-alphanumeric), likely invalid
    alphanumeric_ratio = sum(1 for c in query if c.isalnum() or c.isspace()) / len(query)
    if alphanumeric_ratio < 0.5:
        return False
    
    return True


def is_question_about_agent(query: str) -> bool:
    """
    Check if the question is about the agent itself.
    
    Returns True if question is about agent, False otherwise.
    """
    logger.info(f"Checking if question is about agent: {query[:100]}")
    
    # Quick validation - skip LLM for invalid inputs
    if not _is_valid_input(query):
        logger.info("Input failed validation - treating as non-agent question")
        return False
    
    try:
        classification_prompt = """You are a question classifier for an Agentic SQL Data Analyst.

Determine if the user's question is asking about the AGENT ITSELF (this AI assistant).

Respond with ONLY "YES" or "NO"

Respond "YES" if the question is about:
- The agent's capabilities or features
- Who the agent is / What is this tool / Introduction
- How the agent helps with SQL/data analysis
- What the agent can do as a SQL engineer
- Agent's role, purpose, or limitations
- "Help me" or "Tell me about you"

Respond "NO" for all other questions including:
- General knowledge questions (history, science, etc.)
- General advice unrelated to SQL/data
- Typos or nonsensical input
- Personal/philosophical questions
- Anything not about the agent or data analysis

Examples:
- "Who are you?" → YES
- "What can you do?" → YES  
- "Help me" → YES (asking agent for help)
- "How do you help with SQL?" → YES
- "What should I eat today?" → NO
- "How to learn Python?" → NO
- "Tell me about history" → NO
- "hlo" or "asdfgh" → NO"""

        messages = [
            SystemMessage(content=classification_prompt),
            HumanMessage(content=f"Question: {query}")
        ]
        
        response = llm.invoke(messages)
        content = response.content
        
        # Handle response content that might be str or list
        if isinstance(content, list):
            content = str(content)
        
        answer = content.strip().upper() if isinstance(content, str) else str(content).upper()
        
        is_agent_question = "YES" in answer
        logger.info(f"Question is about agent: {is_agent_question}")
        
        return is_agent_question
        
    except Exception as e:
        logger.warning(f"Error classifying question: {e}. Assuming database-related.")
        return False  # Default to database-related on error


def is_database_related_question(query: str) -> bool:
    """
    Classify if a question is database-related or out-of-scope.
    Quick validation first, then uses LLM for nuanced classification.
    
    Returns True if database-related, False if out-of-scope.
    """
    logger.info(f"Classifying question: {query[:100]}")
    
    # Quick validation - very short/invalid inputs are out-of-scope
    if not _is_valid_input(query):
        logger.info("Input failed validation - treating as out-of-scope")
        return False
    
    try:
        classification_prompt = """You are a question classifier for an Agentic SQL Data Analyst.

Classify the user's question as either:
- "DATABASE": About analyzing data, SQL queries, database content, data analysis from uploaded files, specific data requests, insights from data
- "OUT-OF-SCOPE": General knowledge, general advice, philosophical questions, personal topics, or anything not related to data/database analysis

Respond with ONLY "DATABASE" or "OUT-OF-SCOPE"

Examples of DATABASE questions:
- "Show me sales data"
- "Analyze my customer data"
- "What are the top products?"
- "Find records where price > 100"
- "Generate a report from my data"
- "How many customers do we have?"
- "Create a summary of this data"

Examples of OUT-OF-SCOPE questions:
- "What should I eat today?"
- "Tell me about history"
- "How to learn Python in general?" (general learning, not analyzing data)
- "What's the weather?" (general knowledge)
- "hlo" or "asdfgh" (gibberish)
- "Tell me a joke"
- "What is love?" (philosophical)"""

        messages = [
            SystemMessage(content=classification_prompt),
            HumanMessage(content=f"Classify: {query}")
        ]
        
        response = llm.invoke(messages)
        content = response.content
        
        # Handle response content that might be str or list
        if isinstance(content, list):
            content = str(content)
        
        classification = content.strip().upper() if isinstance(content, str) else str(content).upper()
        
        is_db_related = "DATABASE" in classification
        logger.info(f"Question classified as: {'DATABASE' if is_db_related else 'OUT-OF-SCOPE'}")
        
        return is_db_related
        
    except Exception as e:
        logger.warning(f"Error classifying question: {e}. Assuming database-related.")
        return True  # Default to database-related on error


def handle_agent_question(query: str) -> str:
    """
    Handle questions about the agent itself.
    Provides formatted information about capabilities, role, and features.
    
    Returns formatted response string.
    """
    logger.info(f"Handling agent question: {query[:100]}")
    
    try:
        system_prompt = """You are the Agentic SQL Data Analyst - an AI assistant specialized in SQL database analysis.

Answer questions about yourself, your capabilities, and how you help as a SQL engineer.

Context about you:
- You are an AI-powered SQL Data Analyst
- You help users analyze data using natural language queries
- You generate, execute, and correct SQL queries automatically
- You work with uploaded CSV and XLSX files
- You provide business insights from data analysis
- You can handle SELECT, INSERT, UPDATE, DELETE, and DDL operations
- You self-correct SQL errors intelligently

Format your response as:
1. **Direct Answer**: Clear, concise answer to the question
2. **Key Capabilities**: List 2-3 relevant features or abilities
3. **How to Use**: Brief guidance on how the user can benefit

Be professional, helpful, and focus only on your role as a SQL engineer."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        response = llm.invoke(messages)
        answer = response.content
        
        # Ensure answer is string
        if isinstance(answer, list):
            answer = str(answer)
        
        logger.info("Agent question handled successfully")
        return answer
        
    except Exception as e:
        error_msg = f"Error processing your question: {str(e)}"
        logger.error(error_msg)
        return error_msg


def handle_out_of_scope_question(query: str) -> str:
    """
    Handle questions that are outside the scope of the agent.
    Intelligently detects typos, gibberish, and provides contextual responses.
    
    Returns formatted response string.
    """
    logger.info(f"Handling out-of-scope question: {query[:100]}")
    
    # Check if input looks like gibberish or incomplete
    stripped_query = query.strip()
    
    # Very short inputs - likely typo or test
    if len(stripped_query) <= 3:
        logger.info(f"Very short input detected: '{stripped_query}'")
        response = f"""💬 It looks like you typed something very short: **"{stripped_query}"**

Did you mean to ask something? Here are some things I can help with:

✅ **I can help you with:**
- 📊 Uploading and analyzing your data (CSV, XLSX files)
- 🔍 Answering questions about your data
- 📈 Generating reports and insights
- ❓ Explaining what I can do

**Try asking:**
- "What can you do?" - Learn about my capabilities
- "Help me analyze data" - Get started
- "Upload a file" - Use the attachment button to add data

Need more help? I'm here to assist! 😊"""
        return response
    
    # Check for very limited vocabulary (possible gibberish)
    unique_chars = len(set(stripped_query.lower()))
    if unique_chars <= 3:  # Like "hhhh" or "aaabbb"
        logger.info(f"Gibberish detected: only {unique_chars} unique characters")
        response = """👀 That doesn't look like a proper question or command.

I'm an **Agentic SQL Data Analyst** - I help you analyze data! 

**Here's what to do:**
1. 📎 **Upload a data file** (CSV or XLSX) using the attachment button
2. 💬 **Ask me questions** about your data in natural language
3. ❓ **Ask "What can you do?"** to learn more

For example:
- "Show me the top customers by sales"
- "Analyze the sales trends"
- "What's the average order value?"

Ready to get started? 😊"""
        return response
    
    # Standard out-of-scope response with suggestion
    response = f"""I appreciate your question, but that's outside my area of expertise!

💬 **Your question:** "{stripped_query}"

I'm an **Agentic SQL Data Analyst** - I specialize in:
- 📊 Analyzing data from uploaded files (CSV, XLSX)
- 🔍 Converting questions into SQL queries
- 💡 Providing data insights and business intelligence
- ⚙️ Automatically correcting SQL errors

**What you can do instead:**
1. 📎 **Upload a data file** - Use the attachment button to add CSV/XLSX files
2. 💬 **Ask about your data** - I'll generate SQL and show you insights
3. ❓ **Ask "What can you do?"** - to learn more about my capabilities

**Example questions I can answer:**
- "Show me sales by region"
- "What are the top 10 products?"
- "Analyze customer trends"
- "How many orders in 2024?"

Is there any data you'd like me to analyze? 😊"""
    
    return response


def schema_inspector(state: AgentState) -> AgentState:
    """
    Node 1: Fetch and format database schema.
    Retrieves all tables, columns, data types, and sample rows.
    """
    logger.info("Entering schema_inspector node")

    try:
        # Get full schema
        schema = get_database_schema()

        state["table_schema"] = schema
        state["execution_trace"] = [f"✓ Retrieved database schema ({len(schema)} chars)"]

        logger.info("Schema inspection completed successfully")

    except Exception as e:
        error_msg = f"Error retrieving schema: {str(e)}"
        logger.error(error_msg)
        state["error_message"] = error_msg
        state["execution_trace"] = [f"✗ Failed to retrieve schema: {error_msg}"]

    return state


def sql_generator(state: AgentState) -> AgentState:
    """
    Node 2: Generate MySQL-compliant SQL from user query.
    Uses Groq LLM to convert natural language to SQL.
    """
    logger.info("Entering sql_generator node")

    try:
        user_query = state["user_query"]
        schema = state["table_schema"]

        # Build prompt for SQL generation
        system_prompt = """You are an expert MySQL database analyst. Your task is to write ONE pure MySQL statement — SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, TRUNCATE, or REPLACE — whichever matches what the user is asking for.

CRITICAL RULES:
1. Write ONLY valid MySQL syntax
2. Use backticks around table and column names: `table_name`, `column_name`
3. Use MySQL specific keywords: LIMIT (not TOP), DATE_FORMAT for dates, GROUP_CONCAT for string agg
4. Do NOT wrap the query in markdown code blocks (no ```sql)
5. Return ONLY ONE pure SQL statement - NO multiple queries, and no semicolons separating statements
6. If you need to combine SELECT results, use UNION or UNION ALL within that SINGLE query
7. For UPDATE/DELETE, always include a WHERE clause that matches the user's intent — never touch the whole table unless the user explicitly asked for that
8. Choose the statement type that actually matches the request: reads → SELECT, adding rows → INSERT, changing rows → UPDATE, removing rows → DELETE, schema changes → CREATE/ALTER/DROP/TRUNCATE

When writing queries:
- Wrap all identifiers (table/column names) in backticks
- Use MySQL date functions: DATE(), DATE_FORMAT(), STR_TO_DATE()
- Use LIKE for pattern matching
- Use GROUP BY and HAVING for aggregations
- Use LIMIT for result limits on SELECT
- NEVER generate multiple statements separated by semicolons"""

        user_prompt = f"""Based on this database schema:

{schema}

Convert this natural language request into a single MySQL statement:
"{user_query}"

Return ONLY the pure SQL statement, no explanation or markdown formatting."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        # Call Groq LLM
        response = llm.invoke(messages)
        raw_sql = response.content
        
        # Ensure raw_sql is string (response.content can be str or list)
        if isinstance(raw_sql, list):
            raw_sql = str(raw_sql)

        # Clean markdown if present
        sql = SQLValidator.clean_markdown(raw_sql)

        # Validate safety
        is_safe, error = SQLValidator.is_safe(sql)
        if not is_safe:
            state["error_message"] = f"Generated query is not allowed: {error}"
            state["generated_sql"] = sql
            state["execution_trace"] = [f"✗ SQL validation failed: {error}"]
            logger.warning(f"Generated unsafe SQL: {sql}")
            return state

        state["generated_sql"] = sql
        state["execution_trace"] = [f"✓ Generated SQL: {sql[:100]}..."]

        logger.info(f"SQL generation completed: {sql[:100]}...")

    except Exception as e:
        error_msg = f"Error generating SQL: {str(e)}"
        logger.error(error_msg)
        state["error_message"] = error_msg
        state["execution_trace"] = [f"✗ SQL generation failed: {error_msg}"]

    return state


def sql_executor(state: AgentState) -> AgentState:
    """
    Node 3: Execute generated SQL against MySQL.
    Captures results or errors for downstream processing.
    """
    logger.info("Entering sql_executor node")

    try:
        sql = state["generated_sql"]

        # Initialise both output keys unconditionally so langgraph 0.0.82
        # always sees them in the returned state dict regardless of which
        # branch below is taken.  Without this, the early-return path
        # below left rows_affected absent from state, which caused silent
        # state-merge failures in older langgraph versions.
        state["query_result"] = state.get("query_result")
        state["rows_affected"] = None

        if not sql:
            state["error_message"] = "No SQL query to execute"
            state["execution_trace"] = ["✗ No SQL query provided"]
            return state

        statement_type = SQLValidator.get_statement_type(sql)

        # Connect and execute
        connection = get_db_connection()
        try:
            query = text(sql)
            result = connection.execute(query)

            if statement_type in SQLValidator.ROW_RETURNING_STATEMENTS:
                # SELECT: fetch rows as list of dicts for table display.
                rows = result.fetchall()
                columns = result.keys()
                query_result = [dict(zip(columns, row)) for row in rows]

                state["query_result"] = query_result
                state["rows_affected"] = None
                state["error_message"] = None
                state["execution_trace"] = [
                    f"✓ Query executed successfully ({len(query_result)} row(s) returned)"
                ]
                logger.info(f"SQL execution successful: {len(query_result)} rows returned")

            else:
                # FIX: INSERT/UPDATE/DELETE/DDL don't return rows, so
                # calling fetchall()/keys() on them would raise (there's no
                # result set to fetch). They also need an explicit commit —
                # SQLAlchemy 2.0 connections default to "commit as needed"
                # for DDL, but DML writes made outside a `with` transaction
                # block need this to actually persist.
                connection.commit()
                affected = result.rowcount if result.rowcount and result.rowcount >= 0 else 0

                state["query_result"] = None
                state["rows_affected"] = affected
                state["error_message"] = None
                state["execution_trace"] = [
                    f"✓ {statement_type} executed successfully ({affected} row(s) affected)"
                ]
                logger.info(f"SQL execution successful: {statement_type}, {affected} rows affected")

        finally:
            connection.close()

    except Exception as e:
        error_msg = str(e)
        logger.error(f"SQL execution error: {error_msg}")
        state["query_result"] = None
        state["rows_affected"] = None
        state["error_message"] = error_msg
        state["execution_trace"] = [f"✗ SQL execution failed: {error_msg}"]

    return state


def self_corrector(state: AgentState) -> AgentState:
    """
    Node 4: Self-correct invalid SQL based on error message.
    Learns from MySQL errors and rewrites the query.
    """
    logger.info("Entering self_corrector node")

    try:
        previous_sql = state["generated_sql"]
        error_message = state["error_message"]
        schema = state["table_schema"]
        user_query = state["user_query"]
        retry_count = state["retry_count"]

        # Build correction prompt
        system_prompt = """You are an expert MySQL database analyst specializing in error correction. 
Your task is to fix SQL statements that have errors.

CRITICAL RULES:
1. Write ONLY valid MySQL syntax
2. Use backticks around all identifiers: `table_name`, `column_name`
3. Use MySQL specific functions and syntax
4. Do NOT wrap output in markdown code blocks
5. Return the corrected pure SQL statement only — keep the same statement type (SELECT/INSERT/UPDATE/DELETE/CREATE/ALTER/DROP/TRUNCATE/REPLACE) as the original unless the error specifically requires changing it
6. Preserve the original WHERE clause intent for UPDATE/DELETE — never widen it to affect more rows than intended"""

        user_prompt = f"""Fix this MySQL query that has an error.

Database schema:
{schema}

Original question: "{user_query}"

Previous SQL (with error):
{previous_sql}

Error message:
{error_message}

Analyze the error and provide the CORRECTED MySQL statement (same type as the original — do NOT change an UPDATE to a SELECT, etc.).
Return ONLY the pure SQL, no explanation or markdown."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = llm.invoke(messages)
        content = response.content
        
        # Ensure content is string (response.content can be str or list)
        if isinstance(content, list):
            content = str(content)
        
        corrected_sql = SQLValidator.clean_markdown(content)

        # Validate corrected SQL
        is_safe, safety_error = SQLValidator.is_safe(corrected_sql)
        if not is_safe:
            state["error_message"] = f"Corrected query failed validation: {safety_error}"
            state["execution_trace"].append(f"✗ Self-correction validation failed: {safety_error}")
            return state

        state["generated_sql"] = corrected_sql
        state["error_message"] = None  # Clear error to attempt re-execution
        state["retry_count"] = retry_count + 1
        state["execution_trace"].append(f"✓ Self-corrected SQL (Attempt {retry_count + 1}): {corrected_sql[:100]}...")

        logger.info(f"SQL corrected (attempt {retry_count + 1}): {corrected_sql[:100]}...")

    except Exception as e:
        error_msg = f"Error during self-correction: {str(e)}"
        logger.error(error_msg)
        state["error_message"] = error_msg
        state["execution_trace"].append(f"✗ Self-correction failed: {error_msg}")

    return state


def _format_result_as_markdown_bullets(query_result: List, max_rows: int = 10) -> str:
    """
    Format query results as readable bullet points and markdown instead of JSON.
    Shows formatted data with clear structure and bullet points.
    """
    if not query_result or len(query_result) == 0:
        return "No results returned."
    
    formatted_output = ""
    
    # Determine number of rows to display
    rows_to_show = min(max_rows, len(query_result))
    
    # Get column names from first row
    if isinstance(query_result[0], dict):
        columns = list(query_result[0].keys())
        
        # Create header info
        total_rows = len(query_result)
        formatted_output += f"📊 **Results:** {total_rows} row(s) found\n\n"
        
        # Format each row as a bullet point with key-value pairs
        for i, row in enumerate(query_result[:rows_to_show]):
            formatted_output += f"**Record {i+1}:**\n"
            for col in columns:
                value = row.get(col, "N/A")
                # Format the value nicely
                if value is None:
                    value_str = "(empty)"
                elif isinstance(value, (int, float)):
                    value_str = str(value)
                else:
                    value_str = str(value)
                formatted_output += f"  • **{col}:** {value_str}\n"
            formatted_output += "\n"
        
        # Add note if there are more rows
        if total_rows > rows_to_show:
            formatted_output += f"*... and {total_rows - rows_to_show} more row(s)*"
    
    return formatted_output.strip()


def result_summarizer(state: AgentState) -> AgentState:
    """
    Node 5: Generate natural language summary of results.
    Converts SQL results and query into readable business insights.
    """
    logger.info("Entering result_summarizer node")

    try:
        user_query = state["user_query"]
        generated_sql = state["generated_sql"]
        query_result = state["query_result"]
        rows_affected = state.get("rows_affected")
        error_message = state["error_message"]
        retry_count = state["retry_count"]

        # Handle error cases
        if error_message:
            if retry_count >= 3:
                final_answer = (
                    f"❌ **Unable to process your question**\n\n"
                    f"After {retry_count} attempts, I encountered an error:\n"
                    f"• {error_message}\n\n"
                    f"**Suggestions:**\n"
                    f"• Try rephrasing your question\n"
                    f"• Check if the required data exists in your database\n"
                    f"• Verify column and table names are correct"
                )
            else:
                final_answer = f"❌ Error: {error_message}"

            state["final_answer"] = final_answer
            state["execution_trace"].append(f"✗ Summary: Query failed with error")
            return state

        # Generate summary if results exist
        if query_result:
            # Format results as readable markdown with bullet points
            formatted_results = _format_result_as_markdown_bullets(query_result, max_rows=15)
            
            # Use LLM to create business summary
            system_prompt = """You are a business analyst summarizing database query results.
Provide clear, concise, natural language insights from the SQL results.
Format your response as:
1. **Direct Answer** - Answer the user's question clearly
2. **Key Insights** - Use bullet points to highlight important findings
3. **Notable Patterns** - Any trends or patterns worth noting
Be concise but informative. Use markdown formatting with bullet points."""

            user_prompt = f"""User Question: "{user_query}"

{formatted_results}

Provide a natural language summary and business insights from these results."""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            response = llm.invoke(messages)
            answer_content = response.content
            # Ensure answer_content is string
            if isinstance(answer_content, list):
                answer_content = str(answer_content)
            final_answer = answer_content

        elif rows_affected is not None:
            # FIX: writes/DDL never populate query_result (there are no
            # rows to return), so this used to fall through to the
            # "returned no results" message even on a successful UPDATE
            # or DELETE. Report the actual outcome instead.
            statement_type = SQLValidator.get_statement_type(generated_sql)
            verb = {
                'INSERT': 'inserted',
                'UPDATE': 'updated',
                'DELETE': 'deleted',
            }.get(statement_type, 'affected')

            if statement_type in ('CREATE', 'ALTER', 'DROP', 'TRUNCATE'):
                final_answer = f"✅ **{statement_type} Completed Successfully**\n\nThe database schema has been updated."
            else:
                final_answer = (
                    f"✅ **Operation Successful**\n\n"
                    f"• **Action:** {rows_affected} row(s) {verb}\n"
                    f"• **Statement Type:** {statement_type}\n\n"
                    f"The operation has completed successfully."
                )

        else:
            final_answer = f"✅ **Query Executed Successfully**\n\nThe query ran without errors but returned no results. This is normal for certain types of queries."

        state["final_answer"] = final_answer
        state["execution_trace"].append("✓ Generated natural language summary")

        logger.info("Result summarization completed")

    except Exception as e:
        error_msg = f"Error summarizing results: {str(e)}"
        logger.error(error_msg)
        state["final_answer"] = f"Error generating summary: {error_msg}"
        state["execution_trace"].append(f"✗ Summarization failed: {error_msg}")

    return state