# Vercel Environment Variable Setup

## 🚨 CRITICAL: Frontend Not Working? Fix This!

Your Vercel deployment **MUST** have the backend URL configured, or it will try to call `localhost:8000` which doesn't exist in production!

---

## Quick Fix (Takes 2 Minutes)

### Step 1: Go to Vercel Dashboard

Visit: https://vercel.com/dashboard

### Step 2: Select Your Project

Click on: **ai-quiz-generator** (or your project name)

### Step 3: Go to Settings

1. Click **"Settings"** tab at the top
2. Click **"Environment Variables"** in the left sidebar

### Step 4: Add Backend URL

Click **"Add New"** and enter:

- **Name:** `NEXT_PUBLIC_API_URL`
- **Value:** `https://ai-quiz-generator-f8dr.onrender.com`
- **Environments:** Check all: ✅ Production ✅ Preview ✅ Development

Click **"Save"**

### Step 5: Redeploy

1. Go to **"Deployments"** tab
2. Find the latest deployment
3. Click the **three dots (•••)** on the right
4. Click **"Redeploy"**
5. Wait 1-2 minutes

---

## Verify It's Working

### Test 1: Check the Environment Variable

After redeployment, open your browser console on:
https://ai-quiz-generator-peach.vercel.app

Check the Network tab when you try to upload - it should call:
```
https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz
```

NOT:
```
http://localhost:8000/api/generate-quiz
```

### Test 2: Try Uploading a Document

1. Go to your app
2. Upload a small text file or PDF
3. Should work within 10-20 seconds

---

## Common Issues

### Issue: "Cannot connect to server"

**Fix:**
- Verify `NEXT_PUBLIC_API_URL` is set in Vercel
- Make sure you redeployed after adding the variable
- Check the value doesn't have a trailing slash: ❌ `https://backend.com/` ✅ `https://backend.com`

### Issue: "Request timed out"

**Causes:**
1. Render backend is asleep (first request takes 30s to wake up)
2. Document/video is very large
3. Backend is actually down

**Fix:**
- Wait 30 seconds and try again (Render free tier sleeps)
- Try a smaller file first
- Check Render backend is running: https://ai-quiz-generator-f8dr.onrender.com/health

### Issue: CORS errors in console

**Fix:**
- Backend CORS is already configured for `*.vercel.app`
- Should work automatically
- If not, check Render logs for CORS errors

---

## Environment Variables Summary

### Vercel (Frontend)

| Variable | Value | Required |
|----------|-------|----------|
| `NEXT_PUBLIC_API_URL` | `https://ai-quiz-generator-f8dr.onrender.com` | ✅ YES |

### Render (Backend)

| Variable | Value | Required |
|----------|-------|----------|
| `PERPLEXITY_API_KEY` | Your Perplexity key | ✅ YES |
| `OPENAI_API_KEY` | Your OpenAI key | ⚠️ For videos only |
| `YOUTUBE_API_KEY` | Your YouTube key | ⚠️ Optional |

---

## Why This Happens

`NEXT_PUBLIC_*` environment variables in Next.js are:
- Embedded into the JavaScript bundle at **build time**
- NOT available from server at runtime
- Must be set in Vercel dashboard before deployment

If you forget to set it:
- The app defaults to `http://localhost:8000`
- Works locally but fails in production ❌

---

## Quick Commands to Test

### Test Backend is Alive
```bash
curl https://ai-quiz-generator-f8dr.onrender.com/health
# Should return: {"status":"healthy"}
```

### Test CORS
```bash
curl -X OPTIONS https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz \
  -H "Origin: https://ai-quiz-generator-peach.vercel.app"
# Should return CORS headers
```

---

## Next Steps After Setup

1. ✅ Add `NEXT_PUBLIC_API_URL` to Vercel
2. ✅ Redeploy frontend
3. ✅ Test with a small document
4. ✅ Optionally add `YOUTUBE_API_KEY` to Render (see GET_YOUTUBE_API_KEY.md)

---

## Still Not Working?

Check:
1. Vercel environment variable is saved
2. You redeployed after adding variable
3. Render backend shows "healthy" at /health endpoint
4. Browser console for actual error messages
5. Network tab shows correct backend URL being called
