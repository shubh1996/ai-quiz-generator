# 🚀 Deploy NOW - Quick Guide

## Before You Start
1. ✅ GitHub account
2. ✅ Your Perplexity API key ready
3. ✅ Code pushed to GitHub

---

## 🎯 3-Step Deployment (15 minutes total)

### 1️⃣ Push to GitHub (2 min)
```bash
git remote add origin https://github.com/YOUR_USERNAME/quiz-generator.git
git push -u origin main
```

### 2️⃣ Deploy Backend - Render (5 min)
1. Go to **render.com** → Sign up with GitHub
2. New **Web Service** → Connect `quiz-generator`
3. Settings:
   - Root: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Environment: `PERPLEXITY_API_KEY=your_key`
5. Select **FREE** plan → Deploy
6. **Copy backend URL**: `https://xxx.onrender.com`

### 3️⃣ Deploy Frontend - Vercel (3 min)
1. Go to **vercel.com** → Sign up with GitHub
2. New **Project** → Import `quiz-generator`
3. Settings:
   - Root: `frontend`
   - Framework: Next.js (auto)
4. Environment: `NEXT_PUBLIC_API_URL=YOUR_BACKEND_URL`
5. Deploy → **DONE!** ✅

---

## ✅ Test It
Visit your Vercel URL → Upload doc → Generate quiz!

---

## 🆓 FREE Forever
- No credit card needed
- Auto-deploys on git push
- 750 hours/month backend (24/7!)
- Unlimited frontend

---

**Full guide**: See [FREE_DEPLOYMENT.md](FREE_DEPLOYMENT.md)
