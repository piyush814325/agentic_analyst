# 🚀 Vercel Deployment Guide - Agentic SQL Data Analyst

## Prerequisites

Before deploying to Vercel, you need:

1. **GitHub Account** - Push your code to a GitHub repository
2. **Vercel Account** - Sign up at https://vercel.com
3. **Supabase Account** - PostgreSQL database at https://supabase.com (free tier)
4. **Groq API Key** - Get from https://console.groq.com/keys
5. **Environment Variables** - Prepare all required secrets

---

## Step 1: Prepare Your GitHub Repository

### 1.1 Push Code to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit - Ready for Vercel deployment"

# Add remote repository (replace with your GitHub repo URL)
git remote add origin https://github.com/YOUR-USERNAME/Ai_Agent.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 1.2 Create .gitignore (if not exists)

```
venv/
__pycache__/
.env
.env.local
*.pyc
.chainlit/
.files/
node_modules/
```

---

## Step 2: Set Up Supabase Database

Supabase provides a free PostgreSQL database perfect for development and small applications.

### Setup Supabase (Recommended - Free PostgreSQL)

1. Go to https://supabase.com
2. Click "Start your project"
3. Sign up with Email, GitHub, or Google
4. Create a new project:
   - **Project name:** e.g., `ai-agent-dev`
   - **Region:** Choose closest to you (e.g., US East for Vercel)
   - **Database password:** Save this securely!
5. Wait 1-2 minutes for project initialization
6. Get your connection credentials:
   - Go to **Settings → Database**
   - **Host:** project-ref.supabase.co
   - **Port:** 5432 (PostgreSQL)
   - **User:** postgres
   - **Password:** Your database password
   - **Database:** postgres

### Production Alternatives

For larger applications, consider:
- **AWS RDS PostgreSQL** - $15-20/month
- **Azure Database for PostgreSQL** - $20-30/month
- **DigitalOcean Managed Database** - $15/month

---

## Step 3: Deploy on Vercel

### 3.1 Connect GitHub Repository

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Paste your GitHub repository URL
4. Click "Import"

### 3.2 Configure Environment Variables

In Vercel project settings, add these environment variables:

```
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql+psycopg2://postgres:password@your-project-ref.supabase.co:5432/postgres
```

**How to get each variable:**

| Variable | Where to Get | Supabase Example |
|----------|-------------|------------------|
| GROQ_API_KEY | https://console.groq.com/keys | gsk_xxxxx... |
| DATABASE_URL | Supabase: Settings → Database → Connection string → URI | postgresql+psycopg2://postgres:password@project-ref.supabase.co:5432/postgres |

### 3.3 Add Environment Variables in Vercel

```
1. Go to your Vercel project dashboard
2. Click "Settings" → "Environment Variables"
3. Add each variable from above
4. Click "Save"
```

---

## Step 4: Configure Vercel Deployment

The project includes these configuration files (already created):

### vercel.json
```json
{
  "buildCommand": "pip install -r requirements.txt",
  "functions": {
    "app.py": {
      "memory": 3008,
      "maxDuration": 60,
      "runtime": "python3.11"
    }
  }
}
```

### runtime.txt
Specifies Python 3.11 version

### .vercelignore
Excludes unnecessary files from deployment

---

## Step 5: Deploy

### Auto-Deploy
Once you push changes to GitHub, Vercel will automatically:
1. Detect changes
2. Install dependencies
3. Run build command
4. Deploy your app

### Manual Deploy

In Vercel dashboard:
1. Click "Deployments"
2. Click "Redeploy" on latest deployment
3. Wait for deployment to complete

---

## Step 6: Database Initialization

After first deployment, your PostgreSQL database is ready:

### Using Supabase Console:

1. Go to your Supabase project dashboard
2. Click **SQL Editor** in the sidebar
3. Verify the database exists (should be `postgres`)
4. Tables will be created automatically when you upload data

### Example: View tables
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

---

## Step 7: Test Your Deployment

1. Go to your Vercel project URL (e.g., `https://your-project.vercel.app`)
2. You should see the Chainlit welcome screen
3. Test by:
   - Uploading a CSV/XLSX file
   - Asking a database question
   - Checking if results display correctly

---

## Troubleshooting

### Issue: "Database Connection Error"

**Solution:**
- Verify all DB_* environment variables are set correctly in Vercel
- Check Supabase host ends with `.supabase.co`
- Verify port is `5432` (PostgreSQL), not `3306`
- Check your Supabase project is active (Settings → Status)
- Ensure password is correct (no special characters or URL-encode them)

### Issue: "GROQ_API_KEY not found"

**Solution:**
- Verify GROQ_API_KEY is set in Vercel environment variables
- Get a new key from https://console.groq.com/keys
- Re-deploy after updating the key

### Issue: "Timeout Error"

**Solution:**
- Increase maxDuration in vercel.json (currently 60 seconds)
- Optimize database queries
- Check database performance

### Issue: "Module not found"

**Solution:**
- Ensure requirements.txt has all dependencies
- Run `pip freeze > requirements.txt` locally before pushing
- Check Python version is 3.11 in runtime.txt

---

## Production Best Practices

### 1. Secure Your API Key
```
Don't commit .env file to GitHub
Use Vercel's environment variables instead
Rotate keys periodically
```

### 2. Monitor Logs
```
In Vercel dashboard:
1. Go to Deployments
2. Click latest deployment
3. View "Runtime Logs"
4. Check for errors
```

### 3. Set Up Custom Domain
```
In Vercel:
1. Go to Settings → Domains
2. Add your custom domain
3. Follow DNS configuration steps
```

### 4. Enable HTTPS
```
Vercel automatically provides free HTTPS/SSL
```

---

## Database Backup & Maintenance

Supabase includes automatic backups:
- Daily backups (7-day retention)
- Point-in-time recovery available
- Access via Supabase dashboard: Settings → Backups
- Keep backups before major changes

---

## Cost Estimation

| Service | Cost | Limit |
|---------|------|-------|
| Vercel | Free | 100GB bandwidth/month |
| Supabase | Free | 500MB storage, 2 projects |
| Groq API | Free | Generous rate limits |
| **Total** | **Free** 🎉 | Start-up friendly |

---

## Quick Start Checklist

- [ ] Code pushed to GitHub
- [ ] Supabase project created (https://supabase.com)
- [ ] Database credentials copied from Settings → Database
- [ ] Groq API key obtained
- [ ] Vercel account created
- [ ] GitHub repo imported to Vercel
- [ ] Environment variables added to Vercel
- [ ] Deployment successful
- [ ] Application tested with sample CSV

---

## Support & Next Steps

After successful deployment:
1. Share your URL with stakeholders
2. Monitor application performance
3. Update data by uploading new files
4. Scale database if needed

For issues:
- Check Vercel deployment logs
- Verify database connectivity
- Review environment variables
- Check Chainlit documentation

---

## Deployment Checklist Completed ✅

- [x] vercel.json configured
- [x] runtime.txt set to Python 3.11
- [x] .vercelignore created
- [x] requirements.txt ready
- [x] Environment variables documented
- [x] Database setup instructions provided
- [x] Deployment guide complete
