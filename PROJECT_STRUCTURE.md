# Project Structure Reference

## Directory Tree

```
Ai_Agent/
│
├── .env                        # Environment variables (DO NOT COMMIT)
├── .env.example                # Template for environment setup
├── .gitignore                  # Git ignore rules
│
├── requirements.txt            # Python dependencies
├── config.py                   # Global configuration & environment loading
│
├── app.py                      # 🎯 MAIN ENTRY POINT - Chainlit UI application
├── start.bat                   # Windows startup script
├── start.sh                    # Linux/macOS startup script
│
├── README.md                   # Main documentation
├── TESTING.md                  # Comprehensive testing guide
│
├── db/                         # 📦 Database module
│   ├── __init__.py             # Exports key functions
│   ├── connection.py           # SQLAlchemy engine lifecycle
│   ├── ingestion.py            # File parsing & table creation
│   └── utils.py                # Schema inspection utilities
│
└── agent/                      # 🤖 LangGraph agent module
    ├── __init__.py             # Exports agent components
    ├── state.py                # TypedDict state definition
    ├── nodes.py                # Individual node implementations
    └── graph.py                # LangGraph workflow orchestration
```

## File Purpose Summary

| File | Purpose | Key Functions |
|------|---------|----------------|
| **app.py** | Chainlit UI application | `on_chat_start()`, `on_file_upload()`, `on_message()` |
| **config.py** | Environment & global config | Database URL, API keys, logging setup |
| **db/connection.py** | Database connection pool | `DatabaseManager`, `get_db_engine()` |
| **db/ingestion.py** | File parsing & table creation | `DataIngestionEngine`, `TableNameSanitizer` |
| **db/utils.py** | Schema utilities | `get_database_schema()`, `get_table_sample()` |
| **agent/state.py** | Agent state schema | `AgentState` TypedDict |
| **agent/nodes.py** | Agent workflow nodes | `schema_inspector()`, `sql_generator()`, etc. |
| **agent/graph.py** | Graph orchestration | `build_agent_graph()`, routing logic |

## Module Dependencies

```
app.py
├── config.py
├── db/
│   ├── connection.py
│   ├── ingestion.py
│   └── utils.py
└── agent/
    ├── state.py
    ├── nodes.py
    │   ├── config.py (GROQ_API_KEY)
    │   └── db/utils.py
    └── graph.py
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CHAINLIT UI (app.py)                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────────────┐  │
│  │  File Upload     │         │  Chat Messages           │  │
│  │                  │         │                          │  │
│  │  CSV / XLSX      │         │  Natural Language Query  │  │
│  └────────┬─────────┘         └────────┬─────────────────┘  │
│           │                            │                    │
│           ▼                            ▼                    │
│  ┌──────────────────────┐    ┌────────────────────────────┐ │
│  │ db/ingestion.py      │    │ agent/graph.py             │ │
│  │                      │    │                            │ │
│  │ • Parse CSV/XLSX     │    │ LangGraph Workflow:        │ │
│  │ • Infer schema       │    │ 1. Schema Inspector       │ │
│  │ • Create MySQL table │    │ 2. SQL Generator          │ │
│  │ • Populate rows      │    │ 3. SQL Executor           │ │
│  └────────┬─────────────┘    │ 4. Self-Corrector (opt)   │ │
│           │                  │ 5. Result Summarizer      │ │
│           ▼                  └────────┬─────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           db/connection.py (SQLAlchemy)              │  │
│  │  • Engine creation & pooling                         │  │
│  │  • Connection management                             │  │
│  │  • Query execution                                   │  │
│  └────────┬─────────────────────────────────────────────┘  │
│           │                                                 │
└───────────┼─────────────────────────────────────────────────┘
            │
            ▼
      ┌──────────────┐
      │   MySQL DB   │
      └──────────────┘
```

## Configuration Files Location

```
Project Root/
├── .env                          # Runtime configuration
│   ├── GROQ_API_KEY
│   ├── DB_HOST
│   ├── DB_PORT
│   ├── DB_USER
│   ├── DB_PASSWORD
│   ├── DB_NAME
│   └── APP_DEBUG
│
├── config.py                     # Python config loader
│   └── Reads from .env
```

## Database Schema

After uploading a file, MySQL structure looks like:

```
agentic_analyst/
│
├── sales                        # Example table from CSV
│   ├── id (INT, AUTO_INCREMENT, PRIMARY KEY)
│   ├── date (DATETIME)
│   ├── product_name (VARCHAR(255))
│   ├── quantity (INT)
│   ├── unit_price (FLOAT)
│   ├── customer_id (INT)
│   └── region (VARCHAR(255))
│
├── customers
│   ├── id (INT, AUTO_INCREMENT, PRIMARY KEY)
│   ├── customer_id (INT)
│   ├── customer_name (VARCHAR(255))
│   ├── email (VARCHAR(255))
│   ├── signup_date (DATETIME)
│   └── total_purchases (INT)
│
└── inventory
    ├── id (INT, AUTO_INCREMENT, PRIMARY KEY)
    ├── product_id (INT)
    ├── product_name (VARCHAR(255))
    ├── category (VARCHAR(255))
    ├── stock_quantity (INT)
    ├── reorder_level (INT)
    └── warehouse (VARCHAR(255))
```

## Error Handling Architecture

```
app.py (Chainlit UI)
│
└─► Try-Except Blocks
    ├── File Upload
    │   └─► DataIngestionEngine.ingest_file()
    │       └─► Error → Display to user
    │
    └─► Chat Message Processing
        └─► get_agent_graph().stream()
            ├── schema_inspector
            │   └─► Error → Set error_message
            │
            ├── sql_generator
            │   ├─► LLM Call
            │   ├─► Markdown Cleaning
            │   └─► Safety Validation
            │
            ├── sql_executor
            │   └─► Database execution
            │       ├─► Success → store results
            │       └─► Error → Set error_message
            │
            ├─► [Error & Retries < 3?]
            │   ├─► YES: self_corrector
            │   │   ├─► Call LLM with error context
            │   │   └─► Re-execute sql_executor
            │   │
            │   └─► NO: result_summarizer
            │       └─► Generate business summary
            │
            └─► Display Results
                ├─► Final Answer Text
                ├─► SQL Query Used
                └─► Data Table (Dataframe)
```

## Execution Trace Example

For query "What are top 5 products by revenue?":

```
✓ Retrieved database schema (2145 chars)
✓ Generated SQL: SELECT `product_name`, SUM(`quantity` * `unit_price`) as ...
✓ Query executed successfully (4 rows)
✓ Generated natural language summary
```

For error scenario:

```
✓ Retrieved database schema (2145 chars)
✓ Generated SQL: SELECT * FROM sales GROUP BY unknown_column
✗ SQL execution failed: Unknown column 'unknown_column' in 'group statement'
✓ Self-corrected SQL (Attempt 1): SELECT * FROM sales GROUP BY `product_name`
✓ Query executed successfully (4 rows)
✓ Generated natural language summary
```

## Key Technologies

| Layer | Technology | Version |
|-------|-----------|---------|
| **UI** | Chainlit | 1.3.0 |
| **Agent** | LangGraph | 0.0.82 |
| **LLM** | Groq (llama-3.3-70b) | via langchain-groq 0.1.5 |
| **Database** | MySQL | via SQLAlchemy 2.0.36 + PyMySQL 1.1.1 |
| **Data Handling** | Pandas | 2.2.3 |
| **Excel Support** | OpenPyXL | 3.1.2 |
| **Config** | python-dotenv | 1.0.1 |

## Security Layers

1. **SQL Validation**
   - Only SELECT queries allowed
   - Destructive keywords blocked (DROP, DELETE, INSERT, etc.)
   - Backticks around identifiers

2. **Credential Management**
   - `.env` file for secrets
   - Environment variables loaded at runtime
   - `.env` excluded from git

3. **Database Safety**
   - Read-only connections possible
   - Connection pooling with limits
   - SQL injection prevention via parameterization

## Performance Optimization

1. **Connection Pooling**
   - Pool size: 10 connections
   - Max overflow: 20
   - Auto-recycle after 1 hour

2. **Data Ingestion**
   - Chunked inserts (1000 rows/batch)
   - UTF-8 encoding
   - Bulk insert via SQLAlchemy

3. **LLM Calls**
   - Temperature = 0 (deterministic)
   - Markdown parsing to avoid re-parsing
   - Single API call per operation

4. **Query Execution**
   - Direct SQL via text() for efficiency
   - Result fetching as dict for easy conversion
   - Automatic connection cleanup

## Development Workflow

```
1. Edit code
   ├─► Python files in db/, agent/, or app.py
   └─► No restart needed for most changes (Chainlit reloads)

2. Test locally
   ├─► chainlit run app.py -w
   └─► Upload test CSV files

3. Debug issues
   ├─► Check logs in terminal
   ├─► Review Execution Trace in Chainlit UI
   └─► Inspect .env configuration

4. Deploy
   ├─► Ensure .env is configured
   ├─► MySQL database created
   ├─► Start with: chainlit run app.py -w
   └─► Access UI at http://localhost:8000
```

---

**Complete project architecture for reference and development!**
