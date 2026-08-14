# ⚡ Quick Vercel Deployment - 5 Minutes

## What You Need

1. **GitHub Account** (code repository)
2. **Vercel Account** (free at vercel.com)
3. **Supabase Account** (PostgreSQL database - free tier)
4. **Groq API Key** (free at console.groq.com)

---

## Quick Steps

### 1️⃣ Prepare Database (Supabase)

Go to https://supabase.com:
- Create free account
- Create new project (PostgreSQL)
- Go to Settings → Database → Connection string
- Copy the "URI" connection string
- Paste it as `DATABASE_URL` in Vercel environment variables

### 2️⃣ Push Code to GitHub

```bash
git add .
git commit -m "Ready for Vercel deployment"
git branch -M main
git push origin main
```

### 3️⃣ Deploy on Vercel

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Paste GitHub URL → Click "Import"
4. Add Environment Variables:
   - `GROQ_API_KEY` = Your Groq API key
   - `DATABASE_URL` = Supabase connection string (from Settings → Database → Connection string → URI)
5. Click "Deploy"

### 4️⃣ Wait & Access

- Vercel builds automatically (2-5 minutes)
- Visit your project URL when ready
- Test by uploading a CSV file

---

## Get Your API Keys

| Service | Link | What to Copy |
|---------|------|-------------|
| Groq | https://console.groq.com/keys | API Key |
| Supabase | https://supabase.com/dashboard | Connection string (URI) |
| GitHub | https://github.com | Repository URL |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Database connection failed | Verify credentials in environment variables |
| GROQ_API_KEY error | Get new key from console.groq.com |
| Timeout | Increase maxDuration in vercel.json |
| File not found | Check .vercelignore isn't excluding needed files |

---

## Live Deployment URL

After deployment, your URL will be:
```
https://your-project-name.vercel.app
```

---

## Next Steps

✅ App deployed  
✅ Test with sample data  
✅ Share URL with team  
✅ Monitor logs in Vercel dashboard  

For detailed guide, see: `VERCEL_DEPLOYMENT.md`
