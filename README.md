# Agentic SQL Data Analyst

A powerful AI-driven SQL query agent built with **Chainlit**, **LangGraph**, and **Groq**, enabling users to upload data files and ask natural language questions about their databases.

## 🎯 Features

- **📥 File Upload**: Automatically ingest CSV/XLSX files into MySQL with dynamic table creation
- **💬 Natural Language Queries**: Ask questions in plain English—AI converts them to SQL
- **🔄 Self-Correcting**: Automatic SQL error detection and correction (up to 3 retries)
- **📊 Rich UI**: Interactive data visualization with Chainlit Dataframes
- **🛡️ Safe Queries**: Read-only SELECT enforcement (no DELETE, DROP, INSERT, ALTER, TRUNCATE)
- **⚡ LangGraph Orchestration**: Sophisticated multi-node agent workflow
- **🤖 Powered by Groq**: Fast LLM inference with llama-3.3-70b-versatile

## 🏗️ Architecture

```
project_root/
├── .env                      # Environment variables (API keys, DB credentials)
├── .env.example              # Template for .env
├── requirements.txt          # Python dependencies
├── config.py                 # Global configuration
├── app.py                    # Chainlit UI entry point
├── db/
│   ├── __init__.py
│   ├── connection.py         # SQLAlchemy engine & connection pooling
│   ├── ingestion.py          # File parsing & dynamic table creation
│   └── utils.py              # Schema inspection utilities
└── agent/
    ├── __init__.py
    ├── state.py              # LangGraph TypedDict state
    ├── nodes.py              # Agent nodes (inspector, generator, executor, etc.)
    └── graph.py              # LangGraph workflow orchestration
```

## 🚀 Quick Start

### 1. Clone & Setup

```bash
# Clone repository (or create directory)
mkdir agentic_sql_analyst
cd agentic_sql_analyst

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your credentials
# Required:
# - GROQ_API_KEY=your_groq_api_key
# - DB_HOST=localhost
# - DB_USER=root
# - DB_PASSWORD=your_mysql_password
# - DB_NAME=agentic_analyst
```

### 3. Create MySQL Database

```sql
CREATE DATABASE IF NOT EXISTS agentic_analyst CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Run Application

```bash
chainlit run app.py -w
```

The UI will open in your browser at `http://localhost:8000`

## 📖 Usage Guide

### Uploading Data

1. Click the **📎 (Attachment)** button in Chainlit
2. Select a CSV or XLSX file
3. The system will:
   - Parse the file
   - Infer data types
   - Create a MySQL table
   - Show schema confirmation

### Querying Data

Type natural language questions:

```
"What are the top 5 customers by total purchases?"
"Show me sales trend by month for last year"
"Which products have inventory below 100 units?"
```

The agent will:
1. **Retrieve Schema** - Fetch database structure
2. **Generate SQL** - Convert question to MySQL query
3. **Execute Query** - Run against database
4. **Self-Correct** (if needed) - Fix errors automatically
5. **Summarize** - Generate business insights

## ⚙️ Configuration Files

### `.env` File

```env
# Groq API
GROQ_API_KEY=gsk_xxxxx

# MySQL Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=agentic_analyst

# App Settings
APP_DEBUG=False
LOG_LEVEL=INFO
```

### `config.py`

Handles environment loading, logging setup, and connection string generation.

## 🔐 Security Features

✅ **Read-Only Enforcement**: Only SELECT queries allowed  
✅ **Destructive Command Blocking**: DROP, DELETE, TRUNCATE, ALTER, INSERT blocked  
✅ **Backtick Escaping**: Dynamic identifiers wrapped in backticks  
✅ **Environment Secrets**: Credentials stored in `.env`, not hardcoded  
✅ **Type Validation**: Schema inference prevents type mismatches  

## 🤖 Agent Architecture

### Node 1: Schema Inspector
- Fetches all tables, columns, and data types
- Retrieves sample rows for context

### Node 2: SQL Generator
- Calls Groq LLM with schema context
- Enforces MySQL syntax (LIMIT, backticks, date functions)
- Strips markdown formatting from output

### Node 3: SQL Executor
- Runs query via SQLAlchemy
- Captures results or error messages

### Node 4: Self-Corrector
- Triggered on SQL errors
- Passes error + schema to LLM for correction
- Retries up to 3 times

### Node 5: Result Summarizer
- Generates plain English business summary
- Formats results for display

### Routing Logic

```
schema_inspector
    ↓
sql_generator
    ↓
sql_executor
    ↓
[Error?] ──NO──→ summarizer → END
    ↓
   YES
    ↓
[Retries < 3?] ──YES──→ self_corrector → sql_executor
    ↓                       ↑
   NO                       │
    └──────────→ summarizer → END
```

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `chainlit` | Web UI & chat framework |
| `langgraph` | Agent orchestration |
| `langchain-groq` | LLM integration |
| `sqlalchemy` | Database ORM |
| `pymysql` | MySQL driver |
| `pandas` | Data manipulation |
| `openpyxl` | Excel file support |
| `python-dotenv` | Environment config |

## 🐛 Troubleshooting

### "GROQ_API_KEY not found"
→ Ensure `.env` file exists and has `GROQ_API_KEY=your_key`

### "Connection to MySQL failed"
→ Check `DB_HOST`, `DB_USER`, `DB_PASSWORD` in `.env`  
→ Ensure MySQL server is running  
→ Verify database exists: `CREATE DATABASE agentic_analyst;`

### "File upload fails"
→ Only CSV and XLSX files supported  
→ Ensure file is valid and not corrupted  
→ Check disk space for temporary files

### "SQL generation timeout"
→ Groq API may be rate-limited  
→ Check GROQ_API_KEY validity  
→ Verify internet connection

## 📝 Example Queries

```
# Aggregate queries
"How many orders were placed in 2024?"
"What's the average order value by customer segment?"

# Time-series analysis
"Show monthly revenue trend for the last 6 months"
"Compare sales performance YoY"

# Filtering and ranking
"List top 10 products by revenue"
"Find customers with no purchases in the last 90 days"

# Join and group queries
"Which categories have the highest average product price?"
"Show customer orders with most purchased items"
```

## 🔄 Development Workflow

### Add New Agent Node

1. Implement node function in `agent/nodes.py`
2. Update `AgentState` in `agent/state.py` if needed
3. Add node to graph in `agent/graph.py`
4. Test with sample queries

### Modify Database Engine

1. Update connection logic in `db/connection.py`
2. Modify ingestion in `db/ingestion.py`
3. Test with sample CSV/XLSX files

### Enhance LLM Prompts

- Schema generator prompt: `agent/nodes.py` → `schema_inspector()`
- SQL generator prompt: `agent/nodes.py` → `sql_generator()`
- Error correction prompt: `agent/nodes.py` → `self_corrector()`
- Result summarizer prompt: `agent/nodes.py` → `result_summarizer()`

## 📊 Sample Data for Testing

Create a test CSV file (`sales.csv`):

```csv
date,product,quantity,price,customer_id
2024-01-01,Widget A,10,29.99,1
2024-01-02,Widget B,5,49.99,2
2024-01-03,Widget A,3,29.99,1
2024-01-04,Widget C,8,19.99,3
2024-01-05,Widget B,2,49.99,2
```

Then ask: *"What are total sales by product?"*

## 🚀 Deployment

### Local Deployment

Run the application locally:

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run Chainlit app
chainlit run app.py -w

# Access at http://localhost:8000
```

### Cloud Deployment - Vercel 🎯

Deploy to Vercel for free! See complete guides:

- **QUICK_DEPLOY.md** - 5-minute quick start
- **VERCEL_DEPLOYMENT.md** - Comprehensive 30+ page guide
- **DEPLOYMENT_READY.md** - Setup summary & checklist

#### Quick Vercel Deploy:

1. Create free account at https://vercel.com
2. Set up database at Supabase (https://supabase.com) - PostgreSQL
3. Push code to GitHub
4. Import GitHub repo into Vercel
5. Add environment variables
6. Deploy!

All configuration files are ready:
- ✅ `vercel.json` - Deployment config
- ✅ `runtime.txt` - Python 3.11
- ✅ `.vercelignore` - Exclude unnecessary files
- ✅ `.env.example` - Environment template
- ✅ `.github/workflows/` - CI/CD pipelines

---

## 🚀 Performance Tuning

- **Connection Pooling**: Configured in `db/connection.py` (pool_size=10)
- **LLM Temperature**: Set to 0 for deterministic SQL generation
- **Chunked Data Ingestion**: 1000-row batches to handle large files
- **Result Caching**: Can be added to `agent/nodes.py` for repeated queries

## 📄 License

MIT License - Feel free to use and modify

## 🤝 Contributing

Contributions welcome! Please:
1. Test with sample data
2. Follow code style (logging, error handling)
3. Add docstrings to new functions
4. Update README with changes

## 📞 Support

For issues or questions:
1. Check `.env` configuration
2. Review logs in terminal
3. Verify MySQL/Groq connectivity
4. Check agent trace in Chainlit UI

---

**Built with ❤️ using Chainlit, LangGraph, and Groq**
