# 🎯 Supabase Development Setup - Quick Reference

## What Changed?

Your project now uses **Supabase PostgreSQL** instead of MySQL for development. Here's what you need to know:

### Key Differences

| Aspect | MySQL (Old) | PostgreSQL (New) |
|--------|-----------|-----------------|
| **Provider** | PlanetScale | Supabase |
| **Port** | 3306 | 5432 |
| **Driver** | pymysql | psycopg2 |
| **Connection String** | `mysql+pymysql://` | `postgresql+psycopg2://` |
| **Setup Time** | 5 minutes | 2 minutes |
| **Free Tier** | 3 databases | 2 projects, 500MB storage |

---

## Files Updated

✅ **.env.example** - Changed to Supabase format  
✅ **requirements.txt** - Switched from pymysql to psycopg2-binary  
✅ **config.py** - Updated connection string to PostgreSQL  
✅ **QUICK_DEPLOY.md** - Updated with Supabase instructions  
✅ **DEPLOYMENT_READY.md** - Changed database setup steps  
✅ **VERCEL_DEPLOYMENT.md** - Updated deployment guide  
✅ **README.md** - Updated database reference  
✅ **SUPABASE_SETUP.md** - New detailed setup guide (created)

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Create Supabase Project

```bash
# Go to https://supabase.com
# Click "Start your project"
# Create account or login
# Create new project:
#   - Name: ai-agent-dev
#   - Region: US East (recommended for Vercel)
#   - Save database password!
```

### Step 2: Get Connection Details

```bash
# In Supabase dashboard:
# Settings → Database
# Copy these values:
DB_HOST=your-project-ref.supabase.co
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_NAME=postgres
```

### Step 3: Create .env File

```bash
# Copy template
cp .env.example .env

# Edit .env with your Supabase details
# Then test locally:
chainlit run app.py -w
```

### Step 4: Upload Test Data

1. Open http://localhost:8000
2. Click attachment icon (📎)
3. Upload a CSV file
4. Verify table was created in Supabase

### Step 5: Deploy to Vercel

```bash
# Push to GitHub
git add .
git commit -m "Add Supabase PostgreSQL"
git push origin main

# Then:
# 1. Go to https://vercel.com/new
# 2. Import GitHub repo
# 3. Add environment variables
# 4. Deploy!
```

---

## 📋 Environment Variables Needed

Create `.env` file with these values from Supabase:

```env
# From Supabase Console
GROQ_API_KEY=your_groq_api_key_here
DB_HOST=project-ref.supabase.co
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_supabase_password
DB_NAME=postgres

# Application settings
LOG_LEVEL=INFO
APP_DEBUG=False
PYTHONUNBUFFERED=1
```

**Where to get each:**

| Variable | Location |
|----------|----------|
| GROQ_API_KEY | https://console.groq.com/keys |
| DB_HOST | Supabase → Settings → Database |
| DB_PORT | 5432 (PostgreSQL default) |
| DB_USER | postgres (default user) |
| DB_PASSWORD | Password you set when creating project |
| DB_NAME | postgres (default database) |

---

## ✅ Testing Connection

### Test Locally

```bash
# Method 1: Using Supabase connection string
# In Python:
from sqlalchemy import create_engine

conn_string = "postgresql+psycopg2://postgres:password@host:5432/postgres"
engine = create_engine(conn_string)

with engine.connect() as conn:
    print("✅ Connected!")

# Method 2: Using the app
chainlit run app.py -w
# Upload a CSV file - it should create a table in PostgreSQL
```

### Using Supabase Console

1. Go to your Supabase project dashboard
2. Click **SQL Editor**
3. View your tables created from CSV uploads:

```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';
```

---

## 🔧 Database Management

### View Tables & Data

```bash
# In Supabase Console:
# 1. Click "SQL Editor"
# 2. Write queries
# 3. Execute and view results
```

### Reset Database

⚠️ **Caution:** This deletes all data!

```bash
# In Supabase:
# 1. Go to Settings → Database
# 2. Scroll to "Danger Zone"
# 3. Click "Reset database"
```

### Backup Data

```bash
# Automatic backups included in free tier
# View in: Settings → Backups
# Daily backups, 7-day retention
# Point-in-time recovery available
```

---

## 🚨 Common Issues & Fixes

### ❌ Error: "could not connect to server"

**Fix:**
- Verify host ends with `.supabase.co`
- Confirm port is `5432` (not 3306)
- Check password doesn't have special characters
- Ensure Supabase project is active

### ❌ Error: "relation does not exist"

**Fix:**
- Upload a CSV file first (creates table)
- Check table name is correct
- Verify database is `postgres`

### ❌ Error: "password authentication failed"

**Fix:**
- Check .env has correct password
- Verify you're using the database password (not project password)
- Go to Settings → Database → Reset password if forgotten

### ❌ Error: "timeout connecting to database"

**Fix:**
- Increase timeout in `db/connection.py`
- Check Supabase project is in "Active" state
- Verify Vercel environment variables are set

---

## 📚 Documentation

Detailed guides available:

- **SUPABASE_SETUP.md** - Comprehensive Supabase setup guide
- **VERCEL_DEPLOYMENT.md** - Full Vercel deployment instructions
- **QUICK_DEPLOY.md** - 5-minute quick start
- **DEPLOYMENT_READY.md** - Setup checklist

---

## 🔐 Security Reminders

✅ **DO:**
- Keep `.env` in `.gitignore`
- Use strong passwords
- Use different credentials for dev/prod
- Rotate passwords periodically

❌ **DON'T:**
- Commit `.env` to GitHub
- Share database passwords
- Use weak passwords
- Hard-code secrets

---

## 💡 Tips

1. **Local Development:** Always test with Supabase locally before deploying
2. **Backups:** Supabase auto-backups daily, kept for 7 days
3. **Monitoring:** Check Supabase Console → Logs for database activity
4. **Scaling:** Free tier handles development well; upgrade as needed
5. **Connection Pooling:** Already configured in `db/connection.py`

---

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Create Supabase project
3. ✅ Create `.env` file with Supabase credentials
4. ✅ Test locally: `chainlit run app.py -w`
5. ✅ Push to GitHub
6. ✅ Deploy to Vercel
7. ✅ Test live application

---

## Resources

- **Supabase Docs:** https://supabase.com/docs
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **SQLAlchemy:** https://docs.sqlalchemy.org/
- **psycopg2:** https://www.psycopg.org/

---

**All set! Your project is now configured for Supabase PostgreSQL development. 🎉**
