# Deployment Guide

## Quick Deploy Summary

- **Frontend**: Vercel (recommended)
- **Backend**: Railway or Render (both free tier available)

---

## Option 1: Deploy to Vercel (Frontend) + Railway (Backend)

### A. Deploy Backend to Railway

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your quiz-generator repository
   - Select the `backend` folder as the root

3. **Configure Railway**
   - Railway will auto-detect Python
   - Add environment variable:
     - Key: `PERPLEXITY_API_KEY`
     - Value: Your Perplexity API key

4. **Add Start Command** (if not auto-detected)
   - Go to Settings → Deploy
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

5. **Get Your Backend URL**
   - Once deployed, Railway will give you a URL like: `https://your-app.railway.app`
   - Copy this URL

### B. Deploy Frontend to Vercel

1. **Push to GitHub** (if not already done)
   ```bash
   # Create a new repo on GitHub
   # Then push:
   git remote add origin https://github.com/YOUR_USERNAME/quiz-generator.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub
   - Click "New Project"
   - Import your quiz-generator repository
   - **Configure:**
     - Framework Preset: Next.js
     - Root Directory: `frontend`
     - Build Command: `npm run build`
     - Output Directory: `.next`

3. **Add Environment Variable**
   - In Vercel dashboard → Settings → Environment Variables
   - Add:
     - Key: `NEXT_PUBLIC_API_URL`
     - Value: `https://your-app.railway.app` (your Railway backend URL)

4. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Your app will be live at `https://your-app.vercel.app`

---

## Option 2: Deploy to Vercel (Frontend) + Render (Backend)

### A. Deploy Backend to Render

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - Name: `quiz-generator-backend`
     - Root Directory: `backend`
     - Environment: Python 3
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variable**
   - In Render dashboard → Environment
   - Add:
     - Key: `PERPLEXITY_API_KEY`
     - Value: Your API key

4. **Deploy**
   - Click "Create Web Service"
   - Render will give you a URL like: `https://quiz-generator-backend.onrender.com`

### B. Deploy Frontend to Vercel
   - Follow the same Vercel steps as Option 1
   - Use your Render backend URL as `NEXT_PUBLIC_API_URL`

---

## Manual Deployment Commands

If you prefer to deploy via CLI:

### Vercel CLI (Frontend)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel

# Follow prompts
# Set root directory: ./
# Add environment variable when prompted
```

### Railway CLI (Backend)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
cd backend
railway init
railway up

# Add environment variable
railway variables set PERPLEXITY_API_KEY=your_key
```

---

## Post-Deployment: Update Frontend

After deploying the backend, update the frontend API URL:

1. In Vercel dashboard:
   - Go to Settings → Environment Variables
   - Add/Update: `NEXT_PUBLIC_API_URL` = your backend URL

2. Redeploy frontend:
   - Vercel will auto-redeploy on git push, OR
   - Go to Deployments → click "Redeploy"

---

## Environment Variables Summary

### Backend (Railway/Render)
```
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

---

## Testing Deployment

1. **Test Backend**
   ```bash
   curl https://your-backend-url.railway.app/health
   # Should return: {"status":"healthy"}
   ```

2. **Test Frontend**
   - Visit your Vercel URL
   - Try uploading a document or URL
   - Check browser console for any errors

---

## Troubleshooting

### Backend Issues

**Port Binding Error**
- Ensure start command uses: `--host 0.0.0.0 --port $PORT`
- Railway/Render inject $PORT automatically

**API Key Not Working**
- Check environment variable is set correctly
- Restart the service after adding env vars

**CORS Errors**
- Update `backend/main.py` CORS to include your Vercel URL:
  ```python
  allow_origins=["https://your-app.vercel.app"]
  ```

### Frontend Issues

**API Requests Failing**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check browser console for CORS errors
- Ensure backend URL includes `https://`

**Build Failures**
- Check Node version (should be 18+)
- Verify all dependencies in package.json
- Check build logs in Vercel dashboard

---

## Custom Domains (Optional)

### Vercel
- Dashboard → Settings → Domains
- Add your custom domain
- Follow DNS instructions

### Railway/Render
- Dashboard → Settings → Custom Domain
- Add your domain
- Update DNS records

---

## Monitoring & Logs

### Vercel
- Dashboard → Deployments → Click deployment → Function Logs

### Railway
- Dashboard → Your Project → Deployments → View Logs

### Render
- Dashboard → Your Service → Logs

---

## Cost Estimates

### Free Tier Limits

**Vercel (Frontend)**
- 100GB bandwidth/month
- Unlimited deployments
- Free SSL
- Free for personal projects

**Railway (Backend)**
- $5 free credits/month
- ~500 hours runtime
- After credits: ~$5-10/month

**Render (Backend)**
- 750 hours free/month (enough for 24/7)
- Free SSL
- Sleeps after 15min inactivity (free tier)
- $7/month for always-on

---

## Recommended Setup

For best performance and cost:
- **Development**: Free tiers everywhere
- **Production**:
  - Vercel Pro ($20/month) - Better performance
  - Railway Hobby ($5-10/month) - Always on
  - Total: ~$25-30/month

---

## Next Steps

1. Set up monitoring (Sentry for errors)
2. Configure analytics (Vercel Analytics)
3. Set up database (when needed)
4. Add CI/CD pipeline
5. Configure backups

---

## Support

If you encounter issues:
1. Check deployment logs
2. Verify environment variables
3. Test endpoints manually
4. Check CORS configuration
5. Review documentation links above
