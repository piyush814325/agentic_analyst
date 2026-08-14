"""
Chainlit application for Agentic SQL Data Analyst.
Handles UI, file uploads, chat messages, and agent orchestration.
"""

import logging
import os
import asyncio
import tempfile
from typing import Optional
import pandas as pd
import chainlit as cl
from pathlib import Path

from config import GROQ_API_KEY
from db import (
    DataIngestionEngine,
    DatabaseManager,
    get_database_schema
)
from agent import get_agent_graph, AgentState
from agent.nodes import is_question_about_agent, is_database_related_question, handle_agent_question, handle_out_of_scope_question

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# Application Setup & Lifecycle
# ============================================================================

@cl.on_chat_start
async def on_chat_start():
    """
    Initialize chat session.
    Sets up database connection and displays welcome message.
    """
    logger.info("Chat session started")

    try:
        # Initialize database connection if configured; otherwise continue in a degraded mode.
        db_engine = DatabaseManager.get_engine()
        if db_engine is None:
            logger.warning("Database not configured; app started without live SQL connection.")
            await cl.Message(
                content="⚠️ Database not configured yet. Add your Supabase DATABASE_URL in .env to enable SQL analysis and file uploads.",
                author="System"
            ).send()
        
        # Inject custom script to add button labels and tooltips
        # This enhances the UI with proper labels for all buttons
        custom_script = """
        <script>
        (function() {
            function addButtonLabels() {
                // Label attachment/upload button
                const attachButtons = document.querySelectorAll('[data-testid="button-attachment"], button[aria-label*="attach"], button[aria-label*="Attach"]');
                attachButtons.forEach(btn => {
                    btn.setAttribute('title', '📎 Upload Files (CSV/XLSX)');
                    btn.setAttribute('aria-label', 'Upload Files - Click to upload CSV or XLSX files');
                });

                // Label input field
                const inputs = document.querySelectorAll('[class*="composer"] input, [class*="input-box"] input');
                inputs.forEach(input => {
                    if (!input.placeholder) input.setAttribute('placeholder', '💬 Ask a question or type a command...');
                    input.setAttribute('title', 'Type your question in natural language');
                });

                // Label send button
                const sendBtns = document.querySelectorAll('[data-testid="button-send"]');
                sendBtns.forEach(btn => {
                    btn.setAttribute('title', '➤ Send Message (Press Enter)');
                });
            }

            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', addButtonLabels);
            } else {
                addButtonLabels();
            }

            // Watch for changes
            new MutationObserver(addButtonLabels).observe(document.body, { childList: true, subtree: true });
        })();
        </script>
        """
        
        # Store script in session for potential future use
        cl.user_session.set("ui_script_loaded", True)

        # Display welcome message with UI tips
        welcome_content = """# 🤖 Agentic SQL Data Analyst

Welcome! I'm your AI-powered SQL Data Analyst. I help you analyze data without writing SQL!

---

## ⚡ Quick Button Reference - Look Below! 👇

> **📎 ATTACHMENT BUTTON** (Left of message box)
> Click here to upload CSV/XLSX files - I'll create database tables automatically!
>
> **💬 MESSAGE INPUT** (Main text box)  
> Type your questions here. Use natural language - I'll convert to SQL!
>
> **➤ SEND BUTTON** (Right of message box)
> Click to send your question or press Enter
>
> **⚙️ SETTINGS** (Top right corner)
> Access app settings and preferences
>
> **ℹ️ INFO** (Bottom left corner)
> Get help and learn more features

---

## 📋 What I Can Do:

### 📁 Upload & Analyze Data
- Upload CSV or XLSX files to create database tables automatically
- Ask natural language questions about your data
- Get instant insights and business intelligence

### 🔍 Answer Database Questions
- "Show me sales by region"
- "What are the top 10 products?"
- "Analyze customer trends"

### 💡 Ask About My Capabilities
- "Who are you?" / "What can you do?"
- "How can you help as SQL engineer?"
- Learn about my features and limitations

---

## 📝 Example Interactions:

**You:** "Upload my sales.csv"
**Me:** ✅ Creates database table, shows schema

**You:** "Show me top 5 customers by revenue"
**Me:** 🔍 Generates SQL → Executes → Returns results with insights

**You:** "What can you do?"
**Me:** 📚 Explains my capabilities as a SQL engineer

---

## ⏱️ Session Information:

| Feature | Details |
|---------|---------|
| **Auto-Save** | Your conversations are automatically saved for 1 hour |
| **Persistence** | Return within 1 hour to continue your analysis |
| **Security** | Your data stays in your local database |
| **Refresh** | Your session persists even if you refresh the page |

---

**🎯 Next Step:** Click the **📎 ATTACHMENT BUTTON** to upload your first file, or just ask me a question! 😊"""
        
        await cl.Message(
            content=welcome_content,
            author="SQL Analyst"
        ).send()

        logger.info("Welcome message sent")

    except Exception as e:
        logger.error(f"Error in on_chat_start: {e}")
        await cl.Message(
            content=f"⚠️ Error initializing application: {str(e)}",
            author="System"
        ).send()


@cl.on_chat_end
def on_chat_end():
    """Clean up resources when chat session ends."""
    logger.info("Chat session ended")
    try:
        DatabaseManager.close()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


# ============================================================================
# Chat Message Handler (includes file uploads)
# ============================================================================

async def process_file_upload(file: cl.File):
    """
    Handle file uploads (CSV or XLSX).
    Automatically creates/populates database tables.
    """
    logger.info(f"Processing file: {file.name}")

    try:
        # Validate file type
        file_ext = Path(file.name).suffix.lower()
        if file_ext not in ['.csv', '.xlsx', '.xls']:
            await cl.Message(
                content=f"❌ Unsupported file format: `{file_ext}`. Please upload CSV or XLSX files.",
                author="System"
            ).send()
            return

        # Display processing message
        msg = cl.Message(
            content=f"📥 Processing file: `{file.name}`...",
            author="System"
        )
        await msg.send()

        # FIX: Chainlit File elements are persisted to disk and exposed via
        # `.path`, not `.content`. Reading `.content` raises AttributeError.
        if not file.path or not file.name:
            await cl.Message(
                content=f"❌ Error: File path or name not available.",
                author="System"
            ).send()
            return
        
        # Use tempfile for cross-platform compatibility (works on Windows and Unix)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, file.name)
            try:
                with open(file.path, "rb") as src, open(temp_path, "wb") as dst:
                    dst.write(src.read())

                # Ingest file
                result = DataIngestionEngine.ingest_file(
                    temp_path,
                    table_name=Path(file.name).stem,
                    if_exists="replace"
                )
            except Exception as e:
                logger.error(f"Error copying/processing file {file.name}: {e}")
                raise

        if result["success"]:
            # Format success message with table info
            table_name = result["table_name"]
            row_count = result["row_count"]
            columns = result["columns"]
            schema = result["schema"]

            # Create detailed message
            schema_text = "\n".join([
                f"  • `{col}`: {schema[col]}"
                for col in columns
            ])

            content = f"""✅ **File imported successfully!**

📊 **Table**: `{table_name}`
📈 **Rows**: {row_count}
📋 **Columns**: {len(columns)}

**Schema**:
{schema_text}

You can now ask questions about this data!"""

            await msg.send()
            # Update message content by replacing it
            msg.content = content
            await msg.update()
            logger.info(f"File ingested successfully: table={table_name}, rows={row_count}")

        else:
            # Error case
            error = result.get("error", "Unknown error")
            msg.content = f"❌ Error importing file: {error}"
            await msg.update()
            logger.error(f"File ingestion failed: {error}")

    except Exception as e:
        logger.error(f"Error processing file {file.name}: {e}")
        await cl.Message(
            content=f"❌ Error processing file `{file.name}`: {str(e)}",
            author="System"
        ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """
    Handle chat messages and file uploads.
    Routes user queries through the LangGraph agent.
    """
    # Handle file uploads first
    if message.elements:
        for element in message.elements:
            if isinstance(element, cl.File):
                await process_file_upload(element)

        # If there's only a file and no text, return after processing
        if not message.content or message.content.strip() == "":
            return

    # Handle text queries
    user_query = message.content
    logger.info(f"User query received: {user_query}")

    try:
        # Step 1: Check if question is about the agent itself
        if is_question_about_agent(user_query):
            logger.info("Agent question detected - answering about the agent")
            agent_answer = handle_agent_question(user_query)
            await cl.Message(
                content=agent_answer,
                author="SQL Analyst"
            ).send()
            return
        
        # Step 2: Check if it's database-related
        is_db_related = is_database_related_question(user_query)
        
        if not is_db_related:
            # Step 3: Out-of-scope question - polite rejection
            logger.info("Out-of-scope question detected")
            polite_response = handle_out_of_scope_question(user_query)
            await cl.Message(
                content=polite_response,
                author="SQL Analyst"
            ).send()
            return
        
        # Step 4: For database-related questions, check if database has tables
        schema = get_database_schema()
        if "No tables found" in schema:
            await cl.Message(
                content="📭 No data tables found. Please upload a CSV or XLSX file first to analyze data.\n\nYou can also ask me about my capabilities or how I can help!",
                author="System"
            ).send()
            return

        # Initialize state
        initial_state: AgentState = {
            "user_query": user_query,
            "table_schema": "",
            "generated_sql": "",
            "query_result": None,
            "rows_affected": None,
            "error_message": None,
            "retry_count": 0,
            "final_answer": "",
            "execution_trace": []
        }

        # Get agent graph
        agent = get_agent_graph()

        # Show thinking animation
        thinking_msg = cl.Message(
            content="🤔 **Analyzing your question...**\n\n`⏳ Generating SQL... → Executing query... → Gathering insights...`",
            author="SQL Analyst"
        )
        await thinking_msg.send()

        def run_agent_sync():
            """Run the LangGraph stream synchronously and return the final state."""
            last_state = None
            for step_output in agent.stream(initial_state):
                for node_name, state_data in step_output.items():
                    if node_name != "__end__":
                        last_state = state_data
            return last_state

        # Execute agent without showing internal progress steps in the chat UI.
        final_state = await asyncio.to_thread(run_agent_sync)

        # Remove thinking message
        await thinking_msg.remove()

        # Display results
        if final_state:
            await display_results(final_state)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await cl.Message(
            content=f"❌ Error processing query: {str(e)}",
            author="System"
        ).send()


async def display_results(state: AgentState):
    """
    Display final results from agent execution.
    Shows answer, SQL query, and data table if applicable.
    Uses markdown formatting with bullet points instead of JSON.
    """
    try:
        # Display final answer
        final_answer = state.get("final_answer", "No answer generated")

        await cl.Message(
            content=final_answer,
            author="SQL Analyst"
        ).send()

        # Display SQL query used
        generated_sql = state.get("generated_sql", "")
        if generated_sql:
            sql_message = f"""**🔍 SQL Query Executed:**
```sql
{generated_sql}
```"""
            await cl.Message(
                content=sql_message,
                author="System"
            ).send()

        # Display results as table if available
        query_result = state.get("query_result")
        rows_affected = state.get("rows_affected")

        if query_result and len(query_result) > 0:
            try:
                # Convert to DataFrame for proper formatting
                df = pd.DataFrame(query_result)

                # Normalize data types for display
                for col in df.columns:
                    if pd.api.types.is_datetime64_any_dtype(df[col]):
                        df[col] = df[col].dt.strftime("%Y-%m-%d")
                    else:
                        sample = df[col].dropna()
                        if len(sample) > 0 and not isinstance(
                            sample.iloc[0], (int, float, str, bool)
                        ):
                            df[col] = df[col].astype(str)

                # Build markdown table
                results_text = "**📊 Query Results:**\n\n"
                
                # Create markdown table header
                columns = list(df.columns)
                results_text += "| " + " | ".join(columns) + " |\n"
                results_text += "|" + "|".join(["---"] * len(columns)) + "|\n"
                
                # Add rows (show first 15)
                for i, (_, row) in enumerate(df.head(15).iterrows()):
                    row_vals = []
                    for val in row:
                        if val is None or (isinstance(val, float) and pd.isna(val)):
                            row_vals.append("—")
                        else:
                            # Truncate long values
                            str_val = str(val)
                            if len(str_val) > 50:
                                str_val = str_val[:47] + "..."
                            row_vals.append(str_val)
                    results_text += "| " + " | ".join(row_vals) + " |\n"
                
                # Add note if there are more rows
                if len(df) > 15:
                    remaining = len(df) - 15
                    results_text += f"\n*... and {remaining} more row(s)*"

                await cl.Message(
                    content=results_text,
                    author="System"
                ).send()

            except Exception as e:
                logger.warning(f"Error formatting results table: {e}")
                # Fallback to bullet-point format
                results_text = "**📋 Query Results:**\n\n"
                
                for i, row in enumerate(query_result[:10]):
                    results_text += f"**Record {i+1}:**\n"
                    if isinstance(row, dict):
                        for key, value in row.items():
                            if value is None:
                                value_display = "(empty)"
                            else:
                                value_display = str(value)[:100]  # Truncate long values
                            results_text += f"  • **{key}:** {value_display}\n"
                    else:
                        results_text += f"  • {str(row)}\n"
                    results_text += "\n"
                
                if len(query_result) > 10:
                    remaining = len(query_result) - 10
                    results_text += f"*... and {remaining} more row(s)*"

                await cl.Message(
                    content=results_text,
                    author="System"
                ).send()

        elif rows_affected is not None:
            # FIX: INSERT/UPDATE/DELETE/DDL have no rows to put in a
            # table — previously nothing rendered after the SQL block for
            # these, giving no confirmation the write actually happened.
            await cl.Message(
                content=f"📝 **{rows_affected} row(s) affected.**",
                author="System"
            ).send()

    except Exception as e:
        logger.error(f"Error displaying results: {e}")
        await cl.Message(
            content=f"⚠️ Error displaying results: {str(e)}",
            author="System"
        ).send()


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    # Validate configuration
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not configured. Please set it in .env file")
        raise ValueError("GROQ_API_KEY is required")

    logger.info("Chainlit application ready")