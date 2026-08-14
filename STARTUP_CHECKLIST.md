# ✅ Pre-Startup Checklist

Complete this checklist before running the Agentic SQL Data Analyst application.

---

## 📋 System Requirements Check

- [ ] **Python 3.8+** installed
  - Check: `python --version`
  
- [ ] **MySQL Server** running
  - Check: `mysql --version`
  
- [ ] **Internet connection** available
  - For Groq API access
  - For downloading dependencies

---

## 🔐 Credentials & Configuration

- [ ] **Groq API Key** obtained
  - Visit: https://console.groq.com
  - Copy your API key
  
- [ ] **MySQL credentials** prepared
  - Host: localhost (default)
  - Port: 3306 (default)
  - Username: root (or your username)
  - Password: (your password)
  - Database name: agentic_analyst

- [ ] **.env file** created
  ```bash
  copy .env.example .env    # Windows
  cp .env.example .env      # Linux/macOS
  ```
  
- [ ] **.env file** filled with credentials
  ```
  GROQ_API_KEY=gsk_your_actual_key
  DB_HOST=localhost
  DB_PORT=3306
  DB_USER=root
  DB_PASSWORD=your_mysql_password
  DB_NAME=agentic_analyst
  ```

---

## 🗄️ Database Setup

- [ ] **MySQL running**
  - Windows: Services → MySQL Server
  - Linux: `sudo service mysql start`
  - macOS: `brew services start mysql`
  
- [ ] **Database created**
  ```sql
  CREATE DATABASE IF NOT EXISTS agentic_analyst 
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  ```
  - Can run in MySQL Workbench or command line

---

## 📦 Python Environment

- [ ] **Virtual environment created**
  ```bash
  python -m venv venv
  ```
  
- [ ] **Virtual environment activated**
  - Windows: `venv\Scripts\activate`
  - Linux/macOS: `source venv/bin/activate`
  - Check: Terminal shows `(venv)` prefix
  
- [ ] **Dependencies installed**
  ```bash
  pip install -r requirements.txt
  ```
  - Takes 2-5 minutes depending on internet
  - Watch for any errors

---

## ✔️ Verification

- [ ] **Setup verification passed**
  ```bash
  python verify_setup.py
  ```
  - Should show ✅ for all checks
  - Any ❌ or ⚠️ must be resolved first

---

## 🚀 Ready to Start

Once all checks above are complete:

### Windows Users
```bash
start.bat
```

### Linux/macOS Users
```bash
chmod +x start.sh
./start.sh
```

### Manual Start
```bash
chainlit run app.py -w
```

---

## 🌐 Access Application

- [ ] **Browser opens automatically** to `http://localhost:8000`
  - If not, manually open in browser
  
- [ ] **Chainlit UI loads**
  - Welcome message appears
  - Chat input field visible
  - File upload button visible

---

## 📊 First Steps

Once application starts:

- [ ] **Create test data** (optional but recommended)
  - Save this as `test_data.csv`:
    ```csv
    id,name,value,date
    1,Item A,100,2024-01-01
    2,Item B,200,2024-01-02
    3,Item C,150,2024-01-03
    ```

- [ ] **Upload test file**
  - Click 📎 attachment button
  - Select CSV file
  - Wait for success message
  - Verify table created

- [ ] **Ask first question**
  - Type: "How many items do we have?"
  - Press Enter
  - Wait for AI response
  - See results displayed

- [ ] **Verify features**
  - ✅ File uploaded successfully
  - ✅ Table created in MySQL
  - ✅ Query generated
  - ✅ Results displayed
  - ✅ Business summary shown

---

## 🐛 Troubleshooting During Startup

### Port 8000 Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8000
kill -9 <PID>
```

### Virtual Environment Won't Activate
- Check path is correct
- Try: `python -m venv venv --upgrade`
- Reinstall Python

### Dependencies Installation Fails
- Upgrade pip: `pip install --upgrade pip`
- Try: `pip install -r requirements.txt --no-cache-dir`
- Check internet connection

### MySQL Connection Fails
- Verify MySQL is running: `mysql --version`
- Check credentials in `.env`
- Ensure database exists
- Test connection: `mysql -h localhost -u root -p`

### Groq API Key Invalid
- Double-check key in `.env`
- Ensure no spaces or extra characters
- Get new key from https://console.groq.com

---

## 📞 Need Help?

| Issue | Resource |
|-------|----------|
| Setup problems | [QUICK_START.md](QUICK_START.md#-troubleshooting) |
| Configuration | [README.md](README.md#-configuration-files) |
| Errors | Run `python verify_setup.py` |
| First use | [README.md](README.md#-usage-guide) |

---

## ✨ Success Indicators

You'll know it's working when:

✅ **Application starts without errors**
- Terminal shows no error messages
- Browser opens to http://localhost:8000

✅ **UI appears correctly**
- Welcome message displayed
- Chat input field active
- Attachment button visible

✅ **File upload works**
- CSV file selected and uploaded
- Success message appears
- Table information shown

✅ **Query execution works**
- Ask a question in chat
- SQL gets generated and executed
- Results displayed in table
- Business summary provided

✅ **Self-correction works** (optional test)
- Ask a question with ambiguous terms
- If error occurs, agent self-corrects
- Second attempt succeeds

---

## 📈 Performance Notes

First startup may take:
- **2-3 minutes**: Dependencies installation
- **5-10 seconds**: Database connection
- **3-5 seconds**: Schema retrieval
- **2-3 seconds**: First query

Subsequent operations are faster.

---

## 🎯 Post-Startup Tasks

After successful startup:

1. **Explore features**
   - Try different query types
   - Upload different file formats
   - Test error handling

2. **Read documentation**
   - [README.md](README.md) - Features
   - [TESTING.md](TESTING.md) - Example queries
   - [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Architecture

3. **Customize** (if desired)
   - Modify LLM prompts
   - Change UI styling
   - Add database features

---

## 🔄 Shutdown Checklist

When stopping the application:

- [ ] **Stop the server**
  - Press `Ctrl+C` in terminal
  
- [ ] **Close browser**
  - Close the Chainlit tab
  
- [ ] **Clean up** (optional)
  - Deactivate venv: `deactivate`
  - Keep `.env` file safe

---

## ✅ Final Checklist

Before claiming "ready to use":

- [ ] All system checks passed
- [ ] All credentials configured
- [ ] Database created and accessible
- [ ] Virtual environment working
- [ ] Dependencies installed
- [ ] `verify_setup.py` shows all ✅
- [ ] Application starts without errors
- [ ] UI loads in browser
- [ ] File upload works
- [ ] Query execution works
- [ ] Results display correctly

---

## 🎉 You're Ready!

Once all checks are complete, you can:

✅ Upload CSV/XLSX files to MySQL  
✅ Ask questions in natural language  
✅ Get AI-powered SQL analysis  
✅ See results in interactive tables  
✅ Enjoy automated error correction  

---

**Estimated total time:** 30-45 minutes (including setup and first test)

**Questions?** Check [INDEX.md](INDEX.md) for documentation navigation.

**Need help?** Run `python verify_setup.py` for detailed diagnostics.

---

**Ready to start? Follow the instructions above, then open http://localhost:8000! 🚀**
