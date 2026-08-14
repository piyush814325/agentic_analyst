# 🎯 Supabase Connection String Quick Reference

## Simplest Setup Ever

Just 2 environment variables needed:

```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://postgres:your_password@project.supabase.co:5432/postgres
```

That's it! 🎉

---

## ⚡ 5-Minute Setup

### 1. Create Supabase Account
```
https://supabase.com → Click "Start your project"
```

### 2. Create Project
```
Name: ai-agent-dev
Region: US East (for Vercel)
```

### 3. Get Connection String
```
Settings → Database → Connection string → URI
Copy the entire postgresql:// URL
```

### 4. Create .env File
```bash
cp .env.example .env
```

### 5. Edit .env
```env
GROQ_API_KEY=gsk_xxxxx...
DATABASE_URL=postgresql://postgres:password@host.supabase.co:5432/postgres
```

### 6. Test Locally
```bash
chainlit run app.py -w
# Upload a CSV file to test
```

### 7. Deploy to Vercel
```bash
# Push to GitHub
git add .
git commit -m "Ready for Vercel"
git push origin main

# In Vercel dashboard:
# Add same 2 env vars
# Deploy!
```

---

## 📋 What's in the Connection String?

```
postgresql://postgres:yourpassword@yourproject.supabase.co:5432/postgres
             ↓       ↓               ↓                        ↓      ↓
          user   password          host                      port  database
```

- **User:** `postgres` (Supabase default)
- **Password:** From project setup
- **Host:** Your Supabase project reference
- **Port:** `5432` (PostgreSQL standard)
- **Database:** `postgres` (Supabase default)

---

## 🔍 Finding Your Connection String

| What | Where |
|------|-------|
| Go here | https://supabase.com/dashboard |
| Click | Your project name |
| Then | Settings ⚙️ |
| Then | Database |
| Find | "Connection string" section |
| Select | "URI" tab |
| Copy | The entire postgresql:// URL |

---

## 🧪 Quick Test

### Test Connection
```bash
# Run the app
chainlit run app.py -w

# If successful, you'll see database connection logs
# Upload a CSV file - it should create a table
```

### Using Supabase Console
```
In Supabase:
1. Click "SQL Editor"
2. Run: SELECT table_name FROM information_schema.tables WHERE table_schema='public';
3. You should see your uploaded tables
```

---

## 🚀 Files Updated for This

✅ `.env.example` - Now just shows `DATABASE_URL`  
✅ `config.py` - Uses `DATABASE_URL` environment variable  
✅ `requirements.txt` - Has psycopg2-binary for PostgreSQL  
✅ All deployment guides - Updated to use connection string  

---

## 📚 More Details

For comprehensive guides, see:
- **CONNECTION_STRING_GUIDE.md** - Detailed setup & troubleshooting
- **SUPABASE_SETUP.md** - Complete Supabase features guide
- **VERCEL_DEPLOYMENT.md** - Full deployment instructions

---

## 💡 Pro Tips

1. **Special Characters?** URL-encode: `@` → `%40`, `:` → `%3A`
2. **Connection Pooling:** Already configured automatically
3. **Backups:** Supabase auto-backs up daily
4. **Free Tier:** 500MB database, 2 projects, enough for development

---

## Next Steps

1. Create Supabase project (2 minutes)
2. Copy connection string
3. Create `.env` file
4. Test locally
5. Deploy to Vercel

**That's all! Your app is now using Supabase PostgreSQL.** 🚀
