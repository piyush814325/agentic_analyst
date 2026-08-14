# 🚀 Supabase Setup Guide for Development

## What is Supabase?

Supabase is an open-source Firebase alternative providing:
- **PostgreSQL Database** (instead of MySQL)
- **Real-time APIs** & subscriptions
- **Authentication** (built-in)
- **Automatic backups** & point-in-time recovery
- **Free tier** with generous limits

---

## ⚡ Quick Setup (5 minutes)

### Step 1: Create Supabase Account

1. Go to https://supabase.com
2. Click **"Start your project"**
3. Sign up with:
   - Email
   - GitHub account (recommended)
   - Google account

### Step 2: Create a New Project

1. Click **"New project"** in the dashboard
2. Fill in project details:
   - **Project name:** e.g., `ai-agent-dev`
   - **Organization:** Create or select one
   - **Region:** Choose closest to you (or US East for Vercel)
3. **Database password:** Save this securely! You'll need it.
4. Click **"Create new project"**
5. Wait 1-2 minutes for initialization

### Step 3: Get Your Connection Details

1. Once project loads, click on your **project name**
2. Go to **Settings** (⚙️) in the left sidebar
3. Click **Database** in the submenu
4. You'll see your connection details:

```
Host:     project-ref.supabase.co
Port:     5432
Database: postgres
User:     postgres
Password: [Your database password from Step 2]
```

### Step 4: Create `.env` File

```bash
# Copy from .env.example
cp .env.example .env
```

Edit `.env` and fill in your Supabase details:

```env
GROQ_API_KEY=your_groq_api_key_here

DB_HOST=your-project-ref.supabase.co
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_database_password
DB_NAME=postgres

LOG_LEVEL=INFO
APP_DEBUG=False
PYTHONUNBUFFERED=1
```

**Note:** Replace `your-project-ref` with your actual Supabase project reference ID.

---

## 🔌 Testing Database Connection

### Test Locally

1. Install PostgreSQL client (optional but recommended):
   ```bash
   # Windows: Install psql via PostgreSQL installer
   # Or use Python sqlalchemy to test
   ```

2. Test connection with Python:
   ```bash
   python -c "
   from sqlalchemy import create_engine, text
   
   engine = create_engine(
       'postgresql+psycopg2://postgres:PASSWORD@HOST:5432/postgres'
   )
   
   with engine.connect() as conn:
       result = conn.execute(text('SELECT 1'))
       print('✅ Connection successful!')
   "
   ```

   Replace `PASSWORD` and `HOST` with your Supabase credentials.

### Test in Your App

```bash
# Run the app locally
chainlit run app.py -w

# Upload a CSV file to test
# The app should create a PostgreSQL table
```

---

## 📊 PostgreSQL vs MySQL - Key Differences

| Feature | PostgreSQL (Supabase) | MySQL (PlanetScale) |
|---------|----------------------|---------------------|
| **Port** | 5432 | 3306 |
| **Driver** | psycopg2 | pymysql |
| **Connection String** | postgresql:// | mysql+pymysql:// |
| **JSON Support** | Native JSON type | JSON as text |
| **Full-text Search** | Built-in | Limited |
| **Window Functions** | Yes | Yes |
| **Constraints** | More types | Basic |

---

## 🛠️ Database Management

### Using Supabase Console

1. Go to your project dashboard
2. Click **SQL Editor** in the sidebar
3. Write and run SQL queries directly

Example: View your uploaded tables
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

### Backup & Recovery

**Automatic backups included in free tier:**
- Daily backups (7 days retention)
- Point-in-time recovery
- View in: Settings → Backups

### Reset Database

⚠️ **Warning:** This deletes all data!

1. Go to Settings → Database
2. Scroll to **Danger Zone**
3. Click **Reset database**

---

## 🔐 Security & Best Practices

### Environment Variables

✅ **DO:**
- Keep `.env` file in `.gitignore`
- Use different passwords for dev and production
- Rotate passwords periodically

❌ **DON'T:**
- Commit `.env` to GitHub
- Share database passwords
- Use weak passwords

### Network Access

By default, Supabase allows all IP addresses (useful for development). For production:

1. Go to Settings → Database
2. Set **Restrict connections** to specific IPs
3. Add Vercel's IP range when deploying

### Row Level Security (RLS)

Enable later for production:
- Settings → Authentication → Row Level Security
- Create policies to restrict data access by user

---

## 🚀 Deploying to Vercel with Supabase

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Ready for Vercel deployment with Supabase"
git push origin main
```

### Step 2: Add to Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Add environment variables in **Environment Variables**:

```
GROQ_API_KEY=your_groq_api_key_here
DB_HOST=your-project-ref.supabase.co
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_database_password
DB_NAME=postgres
```

### Step 3: Deploy

Click **Deploy** and wait 3-5 minutes.

### Step 4: Test Live App

Once deployed:
1. Visit your Vercel URL
2. Upload a CSV file
3. Ask a question about your data

---

## 🐛 Troubleshooting

### Connection Refused

**Error:** `psycopg2.OperationalError: could not connect to server`

**Solutions:**
1. Verify host is correct (should end with `.supabase.co`)
2. Verify port is `5432` (not 5433)
3. Check password doesn't have special characters (if it does, URL-encode them)
4. Verify you're not behind a firewall blocking port 5432

### Table Not Found

**Error:** `relation "table_name" does not exist`

**Solutions:**
1. Check table was created (upload CSV first)
2. Verify database name is `postgres`
3. Check schema is `public` (the default)

### Password Reset Forgotten

**Solution:**
1. Go to Supabase Dashboard
2. Settings → Database → Reset database password
3. Update `.env` and Vercel environment variables

### Application Timeout

**Error:** `timeout connecting to database`

**Solutions:**
1. Increase connection pool size in `db/connection.py`
2. Add connection timeout settings
3. Verify Vercel function timeout in `vercel.json` (should be 60 seconds)

---

## 📈 Monitoring & Maintenance

### Check Database Health

1. Dashboard → Settings → Database
2. View:
   - Connection status
   - Database size
   - Storage usage

### View Logs

1. Dashboard → Logs in the sidebar
2. See recent queries and errors

### Upgrade Plan

Free tier includes:
- 500 MB database size
- Limited API requests
- 1 project

For more resources, upgrade to Paid tier:
- https://supabase.com/pricing

---

## 📚 Resources

- **Supabase Docs:** https://supabase.com/docs
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **Connection Pooling:** https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooling
- **Security Guide:** https://supabase.com/docs/guides/database/postgres/configuration

---

## 💡 Next Steps

1. ✅ Create Supabase project
2. ✅ Get connection credentials
3. ✅ Create `.env` file
4. ✅ Test connection locally
5. 📤 Push code to GitHub
6. 🚀 Deploy to Vercel
7. 🧪 Test live application

---

## Need Help?

- **Supabase Discord:** https://discord.supabase.io
- **GitHub Issues:** Check project repo
- **Email Support:** Via Supabase dashboard

Happy developing! 🎉
