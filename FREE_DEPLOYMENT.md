# 🆓 100% FREE Deployment Guide

Deploy your Quiz Generator for **FREE** using:
- **Vercel** (Frontend) - FREE forever
- **Render** (Backend) - FREE with 750 hours/month

---

## ✅ What You Get For Free

### Vercel (Frontend)
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Zero configuration
- ✅ **FREE FOREVER**

### Render (Backend)
- ✅ 750 free hours/month (= 24/7 uptime!)
- ✅ Automatic HTTPS
- ✅ Auto-deploy from GitHub
- ✅ 512MB RAM
- ✅ **FREE TIER** (Sleeps after 15min inactivity - wakes up in ~30 seconds)

---

## 🚀 Step-by-Step Deployment

### STEP 1: Push to GitHub ✅

```bash
# After creating repo on GitHub, run:
git remote add origin https://github.com/YOUR_USERNAME/quiz-generator.git
git branch -M main
git push -u origin main
```

---

### STEP 2: Deploy Backend to Render (5 minutes)

1. **Go to** https://render.com
2. **Sign up** with GitHub (free)
3. Click **"New +"** → **"Web Service"**
4. **Connect GitHub** and select `quiz-generator` repo
5. **Configure:**
   ```
   Name: quiz-generator-backend
   Region: Oregon (US West) - closest to you
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
6. **Select FREE plan**
7. **Add Environment Variable:**
   - Click "Advanced"
   - Add: `PERPLEXITY_API_KEY` = your API key
8. Click **"Create Web Service"**
9. **Wait 3-5 minutes** for deployment
10. **Copy your URL**: `https://quiz-generator-backend-xxxx.onrender.com`

---

### STEP 3: Deploy Frontend to Vercel (3 minutes)

1. **Go to** https://vercel.com
2. **Sign up** with GitHub (free)
3. Click **"Add New..."** → **"Project"**
4. **Import** your `quiz-generator` repository
5. **Configure:**
   ```
   Framework Preset: Next.js (auto-detected)
   Root Directory: frontend
   Build Command: npm run build (auto-filled)
   Output Directory: .next (auto-filled)
   Install Command: npm install (auto-filled)
   ```
6. **Add Environment Variable:**
   - Click "Environment Variables"
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: Your Render backend URL from Step 2
   - Click "Add"
7. Click **"Deploy"**
8. **Wait 2-3 minutes**
9. **Your app is live!** 🎉

---

## 🎯 Your URLs

After deployment:
- **Frontend**: `https://quiz-generator-xxxx.vercel.app`
- **Backend**: `https://quiz-generator-backend-xxxx.onrender.com`

---

## ⚙️ Environment Variables Summary

### Backend (Render)
```env
PERPLEXITY_API_KEY=your_api_key_here
```

### Frontend (Vercel)
```env
NEXT_PUBLIC_API_URL=https://quiz-generator-backend-xxxx.onrender.com
```

---

## 🧪 Testing Your Deployment

1. **Test Backend**
   ```bash
   curl https://your-backend.onrender.com/health
   # Should return: {"status":"healthy"}
   ```

2. **Test Frontend**
   - Visit your Vercel URL
   - Try uploading a file or URL
   - Generate a quiz!

---

## 💡 Important Notes About FREE Tier

### Render Free Tier Behavior
- ✅ 750 hours/month = **24/7 uptime**
- ⚠️ **Sleeps after 15 minutes** of inactivity
- ⏰ **Wakes up in ~30 seconds** on first request
- 💡 First request after sleep will take longer

### What This Means
- If no one uses the app for 15 minutes, it goes to sleep
- Next visitor will wait ~30 seconds for it to wake up
- After that, works normally until inactive again
- **Perfect for personal projects and demos!**

### Want to Keep it Always Awake? (Optional)
Use a free service like **UptimeRobot** or **cron-job.org**:
- Pings your backend every 10 minutes
- Keeps it awake 24/7
- Also 100% free!

---

## 🔄 Auto-Deploy on Git Push

Both platforms auto-deploy when you push to GitHub:

```bash
# Make changes, then:
git add .
git commit -m "Update feature"
git push

# Vercel and Render will automatically redeploy!
```

---

## 📊 Monitoring & Logs

### Vercel
- Dashboard → Your Project → Deployments
- Click any deployment → View Function Logs
- Real-time logs available

### Render
- Dashboard → Your Service → Logs
- Live log streaming
- Shows startup, requests, errors

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: Backend sleeps after 15 minutes
- **Solution**: This is normal for free tier. First request wakes it up.

**Problem**: 500 errors
- **Solution**: Check Render logs for Python errors
- Verify `PERPLEXITY_API_KEY` is set correctly

**Problem**: Build fails
- **Solution**: Check `requirements.txt` is correct
- Ensure Python 3.10+ compatible

### Frontend Issues

**Problem**: API requests fail
- **Solution**: Verify `NEXT_PUBLIC_API_URL` is correct
- Must start with `https://`
- Don't include trailing slash

**Problem**: CORS errors
- **Solution**: Backend CORS is configured for all Vercel domains
- Check browser console for exact error

**Problem**: Build fails
- **Solution**: Check Vercel build logs
- Ensure all dependencies are in `package.json`

---

## 🎨 Custom Domain (Optional - Still Free!)

### Vercel
1. Dashboard → Settings → Domains
2. Add your domain
3. Update DNS records (provided by Vercel)
4. FREE SSL included!

### Render
1. Dashboard → Settings → Custom Domain
2. Add your domain
3. Update DNS to Render's nameservers
4. FREE SSL included!

---

## 📈 Upgrade Path (When Needed)

### Current: 100% FREE
- Vercel: Free
- Render: Free (with sleep)
- **Total: $0/month**

### If you need 24/7 uptime (no sleep):
- Vercel: Still Free
- Render: $7/month (always-on)
- **Total: $7/month**

### Pro Setup:
- Vercel Pro: $20/month (better performance)
- Render Starter: $7/month
- **Total: $27/month**

---

## ✨ You're All Set!

Your app will be:
- ✅ Live on the internet
- ✅ Accessible from anywhere
- ✅ Auto-deployed on git push
- ✅ HTTPS secured
- ✅ 100% FREE

**No credit card required for free tiers!**

---

## 📞 Need Help?

Check logs:
1. Render: Dashboard → Logs
2. Vercel: Dashboard → Deployments → Function Logs

Common issues are in the Troubleshooting section above!

---

**Happy Deploying! 🚀**
