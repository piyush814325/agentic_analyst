# 🚀 Quick Start Guide

## ⚡ 5-Minute Setup (Windows)

### Step 1: Install Dependencies
```bash
# Open PowerShell in project folder
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy example to .env
copy .env.example .env

# Edit .env - Set these values:
# GROQ_API_KEY=your_key_from_groq_console
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=your_mysql_password
# DB_NAME=agentic_analyst
```

### Step 3: Setup MySQL Database
```bash
# Open MySQL terminal or MySQL Workbench and run:
CREATE DATABASE IF NOT EXISTS agentic_analyst CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 4: Start Application
```bash
# Run startup script (RECOMMENDED)
start.bat

# OR manually:
chainlit run app.py -w
```

**✅ Open browser → http://localhost:8000**

---

## ⚡ 5-Minute Setup (Linux/macOS)

### Step 1: Install Dependencies
```bash
# Open terminal in project folder
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your credentials
nano .env  # or vim .env
```

### Step 3: Setup MySQL Database
```bash
# MySQL terminal:
CREATE DATABASE IF NOT EXISTS agentic_analyst CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 4: Start Application
```bash
# Run startup script (RECOMMENDED)
chmod +x start.sh
./start.sh

# OR manually:
chainlit run app.py -w
```

**✅ Open browser → http://localhost:8000**

---

## 🎯 First Steps After Startup

### Create Sample Data

Save as `sample_sales.csv`:
```csv
date,product,quantity,price,customer_id
2024-01-01,Widget A,10,29.99,1
2024-01-02,Widget B,5,49.99,2
2024-01-03,Widget A,3,29.99,1
2024-01-04,Widget C,8,19.99,3
2024-01-05,Widget B,2,49.99,2
```

### Upload & Query

1. **Upload**: Click 📎 button → Select `sample_sales.csv`
2. **Wait**: See success message with table info
3. **Ask**: Type: *"What are total sales by product?"*
4. **See**: AI generates SQL, runs it, shows results in table

---

## 🔧 Troubleshooting

### Port 8000 Already in Use
```bash
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS: Find and kill process
lsof -i :8000
kill -9 <PID>
```

### "GROQ_API_KEY not found"
- Check `.env` file exists in project root
- Ensure line: `GROQ_API_KEY=gsk_xxxxx` (your actual key)
- Restart application

### "Cannot connect to MySQL"
- Verify MySQL service is running
- Check connection details in `.env`
- Test with: `mysql -h localhost -u root -p`

### File Upload Fails
- Only CSV and XLSX supported
- Check file is not corrupted
- Ensure write permissions in temp directory

### Query Execution Hangs
- Check Groq API status
- Verify internet connection
- Try simpler query: "SELECT * FROM table_name"

---

## 📚 Key Files to Know

| File | What It Does |
|------|-------------|
| `app.py` | Main application (Chainlit UI) |
| `config.py` | Loads environment & settings |
| `db/ingestion.py` | Handles CSV/XLSX file uploads |
| `agent/nodes.py` | AI agent logic (SQL generation, etc.) |
| `.env` | Your credentials (NEVER commit!) |

---

## 💡 Example Queries to Try

After uploading sample data:

```
"How many total items were sold?"
"What's the average price per product?"
"Which customer made the most purchases?"
"Show me sales by date"
"What's the revenue per product?"
```

---

## 🛠️ Development Commands

```bash
# Activate virtual environment
.\venv\Scripts\activate          # Windows
source venv/bin/activate         # Linux/macOS

# Install new dependency
pip install package_name

# Freeze dependencies (if you added packages)
pip freeze > requirements.txt

# Run tests
python -m pytest tests/

# Format code
black . --line-length 100

# Check for issues
flake8 .

# Deactivate environment
deactivate
```

---

## 📖 Documentation Files

| File | Contains |
|------|----------|
| `README.md` | Full documentation & features |
| `TESTING.md` | Complete testing guide with scenarios |
| `PROJECT_STRUCTURE.md` | Architecture diagrams & file reference |
| `QUICK_START.md` | This file - setup & getting started |

---

## 🎓 Next Steps

1. **Explore Features**
   - Upload different CSV files
   - Try complex queries
   - Check self-correction in action

2. **Customize**
   - Edit LLM prompts in `agent/nodes.py`
   - Modify UI styling in Chainlit docs
   - Add new agent nodes

3. **Deploy**
   - Use Docker for containerization
   - Deploy to cloud (Hugging Face Spaces, etc.)
   - Set up database backups

4. **Monitor**
   - Track execution logs
   - Monitor API usage
   - Optimize slow queries

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Start app | `chainlit run app.py -w` |
| Stop app | `Ctrl+C` in terminal |
| View logs | Check terminal output |
| Reset DB | Drop & recreate in MySQL |
| Update deps | `pip install -r requirements.txt --upgrade` |

---

## ✅ Checklist: First Run

- [ ] Python 3.8+ installed (`python --version`)
- [ ] MySQL running (`mysql --version`)
- [ ] Groq API key obtained (from groq.com console)
- [ ] `.env` file created and filled
- [ ] Database created in MySQL
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip list | grep chainlit`)
- [ ] Application starts without errors
- [ ] Browser opens to http://localhost:8000
- [ ] Sample file uploaded successfully
- [ ] Query executed and results displayed

---

**🎉 You're ready to use the Agentic SQL Data Analyst!**

For detailed information, see:
- **Features & Architecture** → [README.md](README.md)
- **Testing Scenarios** → [TESTING.md](TESTING.md)
- **Project Structure** → [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
