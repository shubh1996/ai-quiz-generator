# Deployment Troubleshooting Guide

## 🔍 Issue: Upload Not Working on Vercel

If document upload is taking more than 1 minute and not responding:

---

## ✅ Step 1: Verify Environment Variable

Even if `NEXT_PUBLIC_API_URL` exists in Vercel, check:

1. **Go to Vercel Dashboard:** https://vercel.com/dashboard
2. **Select your project**
3. **Settings → Environment Variables**
4. **Verify the value is EXACTLY:**
   ```
   https://ai-quiz-generator-f8dr.onrender.com
   ```

### Common Mistakes:
- ❌ Trailing slash: `https://ai-quiz-generator-f8dr.onrender.com/`
- ❌ Wrong protocol: `http://` instead of `https://`
- ❌ Extra spaces before/after the URL
- ❌ Not applied to all environments (Production, Preview, Development)

### Fix:
1. Delete the existing variable
2. Add it again with exact value (copy-paste from below):
   ```
   https://ai-quiz-generator-f8dr.onrender.com
   ```
3. **IMPORTANT:** Check all 3 environment boxes
4. Save and **Redeploy**

---

## ✅ Step 2: Force Redeploy

Environment variables are embedded at **build time**, not runtime!

1. Go to **Deployments** tab
2. Find latest deployment
3. Click **•••** (three dots)
4. Click **"Redeploy"**
5. **IMPORTANT:** Make sure "Use existing Build Cache" is **UNCHECKED**
6. Wait 1-2 minutes for deployment

---

## ✅ Step 3: Check Browser Console

1. Open your app: https://ai-quiz-generator-peach.vercel.app
2. Press **F12** (or right-click → Inspect)
3. Go to **Console** tab
4. Try uploading a file
5. Look for errors

### What to Look For:

**Good Sign:**
```
POST https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz
```

**Bad Signs:**
```
POST http://localhost:8000/api/generate-quiz  ← Still calling localhost!
Failed to fetch  ← Network error
CORS error  ← Backend blocking request
```

---

## ✅ Step 4: Check Network Tab

1. In DevTools, go to **Network** tab
2. Clear network log (🚫 icon)
3. Try uploading a document
4. Look at the requests

### What to Check:

1. **Request URL:** Should be `https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz`
2. **Status Code:**
   - `200 OK` = Success ✅
   - `(pending)` forever = Timeout issue
   - `CORS error` = Backend blocking
   - `404` = Wrong endpoint
   - `500` = Backend error

3. **Request Headers:**
   - Should include `Origin: https://ai-quiz-generator-peach.vercel.app`

---

## ✅ Step 5: Test Backend Directly

Check if Render backend is working:

```bash
# Test health endpoint
curl https://ai-quiz-generator-f8dr.onrender.com/health
# Should return: {"status":"healthy"}

# Test quiz generation (takes 15-30 seconds)
curl -X POST https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz \
  -F 'url=https://en.wikipedia.org/wiki/Photosynthesis'
# Should return JSON with quiz questions
```

If this works but the frontend doesn't, it's a **frontend configuration issue**.

---

## ✅ Step 6: Check Render Status

1. Go to: https://dashboard.render.com
2. Select `quiz-generator-backend`
3. Check **Events** tab for errors
4. Check **Logs** tab for errors

### Common Issues:

**"Service is sleeping"**
- First request takes 30 seconds to wake up
- This is normal on Render free tier
- Wait and try again

**"Build failed"**
- Check if `google-api-python-client` installation failed
- Should see in logs: `✓ YouTube Data API v3 service enabled` or warning

**"Out of memory"**
- Render free tier has 512MB RAM
- Large documents might cause issues

---

## ✅ Step 7: Verify Latest Deployment

### Check Vercel:
```bash
# Get latest commit on main branch
git log -1 --oneline
# Should show: Fix: Add timeout handling...
```

### Check if Vercel deployed it:
1. Go to Vercel Deployments tab
2. Check latest deployment timestamp
3. Click on it
4. Check "Source" matches latest commit hash

### If not deployed:
- **Push changes:** `git push origin main`
- **Manual deploy:** Deployments → Redeploy

---

## ✅ Step 8: Test With Simple File

Don't test with large files first! Try:

1. **Create test.txt:**
   ```
   Python is a high-level programming language.
   It was created by Guido van Rossum in 1991.
   Python emphasizes code readability.
   ```

2. **Upload this file**
3. **Should work in 5-10 seconds**

If small files work but large ones don't:
- Issue is timeout/memory related
- Try smaller documents
- Or wait longer (up to 2 minutes for large files)

---

## ✅ Step 9: Check for Specific Errors

### Error: "Request timed out"
**Cause:** New timeout feature (2 minutes)
**Fix:**
- Render might be sleeping (first request)
- Document is very large
- Video processing taking long

**Solution:**
- Wait 30 seconds and retry
- Try smaller file
- Check Render logs

### Error: "Cannot connect to server"
**Cause:** Frontend can't reach backend
**Fix:**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check it's `https://` not `http://`
- Redeploy frontend with new build

### Error: "Failed to fetch"
**Causes:**
1. CORS blocking (backend rejects frontend origin)
2. Backend is down
3. Network issue

**Fix:**
- Check backend CORS in `main.py` includes `*.vercel.app`
- Test backend health endpoint
- Check browser console for specific CORS error

### Error: Nothing happens (no error)
**Cause:** JavaScript error preventing submission
**Fix:**
- Check browser console for errors
- Try hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
- Clear cache and try again

---

## ✅ Step 10: Nuclear Option - Clean Rebuild

If nothing else works:

### On Vercel:
1. **Settings → General**
2. Scroll to bottom → **Delete Project**
3. **Reimport from GitHub**
4. Set root directory: `frontend`
5. Add environment variable: `NEXT_PUBLIC_API_URL`
6. Deploy

### On Render:
1. **Settings**
2. Scroll to bottom → **Delete Web Service**
3. **Create new Web Service**
4. Root directory: `backend`
5. Add all environment variables
6. Deploy

---

## 🔧 Debug Checklist

Run through this checklist:

- [ ] `NEXT_PUBLIC_API_URL` is set in Vercel
- [ ] Value is `https://ai-quiz-generator-f8dr.onrender.com` (no trailing slash)
- [ ] Applied to Production, Preview, Development
- [ ] Vercel redeployed after adding variable
- [ ] Latest code is deployed (check commit hash)
- [ ] Backend health returns `{"status":"healthy"}`
- [ ] Browser console shows no errors
- [ ] Network tab shows correct backend URL
- [ ] Tried with small test file first
- [ ] Waited 30 seconds for Render to wake up

---

## 📊 Expected Behavior

### Small Text File (< 1KB):
- **Time:** 5-10 seconds
- **Status:** Should succeed

### PDF Document (1-5MB):
- **Time:** 15-30 seconds
- **Status:** Should succeed

### Large Document (10MB+):
- **Time:** 30-60 seconds
- **Status:** May timeout or run out of memory

### Video URL:
- **Time:** 1-2 minutes
- **Status:** Often fails (YouTube blocking)
- **Recommendation:** Download and upload file instead

---

## 🆘 Still Not Working?

If you've tried everything:

1. **Share this info:**
   - Browser console errors (screenshot)
   - Network tab screenshot showing the request
   - Vercel deployment URL
   - Render logs (last 50 lines)

2. **Temporary workaround:**
   - Run backend locally: `cd backend && uvicorn main:app --reload`
   - Update Vercel env to: `http://localhost:8000`
   - Test locally to isolate the issue

3. **Check status pages:**
   - Vercel Status: https://www.vercel-status.com
   - Render Status: https://status.render.com

---

## 💡 Quick Tests

### Test 1: Is environment variable embedded?
```javascript
// In browser console on your Vercel app:
console.log(process.env.NEXT_PUBLIC_API_URL)
// This won't work because env vars aren't available in browser
// But check Network tab - requests should go to Render, not localhost
```

### Test 2: Manual fetch test
```javascript
// In browser console on your Vercel app:
fetch('https://ai-quiz-generator-f8dr.onrender.com/health')
  .then(r => r.json())
  .then(console.log)
// Should log: {status: "healthy"}
```

### Test 3: CORS test
```javascript
// In browser console on your Vercel app:
const formData = new FormData();
formData.append('url', 'https://en.wikipedia.org/wiki/Python');

fetch('https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz', {
  method: 'POST',
  body: formData
})
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
// Should work if CORS is configured correctly
```
