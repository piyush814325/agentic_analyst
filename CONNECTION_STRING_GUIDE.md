# 🔑 Using Supabase Connection String Directly

## Why Direct Connection String?

Instead of managing 5 separate database variables (host, port, user, password, database), Supabase provides a single connection string that includes everything:

```
postgresql+psycopg2://postgres:your_password@your-project.supabase.co:5432/postgres
```

---

## ⚡ Quick Setup

### Step 1: Get Your Supabase Connection String

1. Go to https://supabase.com/dashboard
2. Click on your project
3. Click **Settings** (⚙️) in sidebar
4. Click **Database** in submenu
5. Find **Connection string** section
6. Switch to **URI** tab
7. Copy the entire connection string:

```
postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

### Step 2: Create `.env` File

```bash
cp .env.example .env
```

### Step 3: Edit `.env` with Your Connection String

```env
# Groq API Key
GROQ_API_KEY=your_groq_api_key_here

# Supabase Connection String
# From: Settings → Database → Connection string → URI
DATABASE_URL=postgresql://postgres:your_password@your-project-ref.supabase.co:5432/postgres

# Application settings (optional)
LOG_LEVEL=INFO
APP_DEBUG=False
PYTHONUNBUFFERED=1
```

**Note:** Make sure to replace `[YOUR-PASSWORD]` with your actual database password!

### Step 4: Test Locally

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Run the app
chainlit run app.py -w

# Test by uploading a CSV file
```

---

## 🔐 For Vercel Deployment

### Add to Vercel Environment Variables

In your Vercel project:
1. Go to Settings → Environment Variables
2. Add these two variables:

```
GROQ_API_KEY = your_groq_api_key
DATABASE_URL = your_supabase_connection_string_from_step_1
```

### Example:
```
GROQ_API_KEY = gsk_abcd1234...

DATABASE_URL = postgresql://postgres:mysecurepassword123@my-project-abc.supabase.co:5432/postgres
```

---

## 📝 Connection String Format

The connection string breakdown:

```
postgresql://postgres:your_password@your-project.supabase.co:5432/postgres
                ↓              ↓                      ↓           ↓
            protocol        user                   host          port
                               ↓                                  ↓
                           password                          database
```

- **Protocol:** `postgresql://` (Supabase uses PostgreSQL)
- **User:** `postgres` (default Supabase user)
- **Password:** Your database password (from project setup)
- **Host:** Your Supabase project reference (e.g., `abc123def.supabase.co`)
- **Port:** `5432` (PostgreSQL default)
- **Database:** `postgres` (default Supabase database)

---

## 🔧 Connection String for SQLAlchemy

In `config.py`, the connection string is automatically converted to SQLAlchemy format:

**Raw Supabase URI:**
```
postgresql://postgres:password@host:5432/postgres
```

**SQLAlchemy with psycopg2 driver:**
```
postgresql+psycopg2://postgres:password@host:5432/postgres
```

The code automatically handles this conversion, so just use the raw Supabase connection string in your `.env` file.

---

## 🧪 Testing the Connection

### Local Test

```python
from sqlalchemy import create_engine, text

# Your DATABASE_URL
database_url = "postgresql://postgres:password@host:5432/postgres"

# Convert for SQLAlchemy (automatic in app)
conn_string = database_url.replace("postgresql://", "postgresql+psycopg2://")

# Test connection
engine = create_engine(conn_string)
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("✅ Connected to Supabase!")
```

### Supabase Console Test

1. In Supabase dashboard → **SQL Editor**
2. Run any query to verify connection
3. You should see results instantly

---

## 🛟 Troubleshooting

### ❌ "password authentication failed"

**Fix:**
- Copy the password carefully from Supabase
- Make sure you're using the database password (not project password)
- Special characters? Try URL-encoding: `@` → `%40`, `:` → `%3A`
- Example: `pass@word123` → `pass%40word123`

### ❌ "could not connect to server"

**Fix:**
- Verify the host ends with `.supabase.co`
- Check port is `5432`
- Verify Supabase project is in "Active" state
- Try from Supabase SQL Editor first

### ❌ "connection timeout"

**Fix:**
- Check internet connection
- Verify Supabase project is running
- Try increasing timeout in connection pool
- Check if firewall is blocking port 5432

### ❌ Error: "NoSuchModuleError: Can't load plugin"

**Fix:**
```bash
# Make sure psycopg2 is installed
pip install psycopg2-binary==2.9.9

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Where to Find Your Connection String

| Step | Where | How |
|------|-------|-----|
| 1 | Supabase Dashboard | https://supabase.com/dashboard |
| 2 | Project Page | Click your project name |
| 3 | Settings | Click ⚙️ icon in sidebar |
| 4 | Database Section | Select "Database" |
| 5 | Connection String | Scroll to "Connection string" section |
| 6 | URI Tab | Click "URI" tab (not "Psql" or others) |
| 7 | Copy | Select and copy entire connection string |

---

## 🎯 Next Steps

1. ✅ Get your Supabase connection string
2. ✅ Create `.env` file
3. ✅ Add `DATABASE_URL` to `.env`
4. ✅ Test locally with `chainlit run app.py -w`
5. ✅ Deploy to Vercel with `DATABASE_URL` env var
6. ✅ Test live application

---

## 💡 Tips

- **Connection Pooling:** Already configured in `db/connection.py`
- **Retries:** Automatic retry on connection failure (up to 3 times)
- **Timeouts:** Configure in `db/connection.py` if needed
- **Backups:** Supabase auto-backups daily (7-day retention)

---

## Resources

- **Supabase Docs:** https://supabase.com/docs/guides/database/connecting-to-postgres
- **Connection Pooling:** https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooling
- **Troubleshooting:** https://supabase.com/docs/guides/database/troubleshooting

---

**That's it! Your app is now using Supabase PostgreSQL directly. 🚀**
