# How to Get YouTube Data API v3 Key

**Quick guide to obtain a YouTube API key** - Takes ~5 minutes

---

## Step 1: Go to Google Cloud Console

Visit: **https://console.cloud.google.com**

- Sign in with your Google account
- Accept Terms of Service if this is your first time

---

## Step 2: Create New Project

1. Click the project dropdown at the top (says "Select a project")
2. Click **"NEW PROJECT"** (top right corner)
3. Enter project details:
   - **Project name:** `quiz-generator` (or any name)
   - Leave other fields as default
4. Click **"CREATE"**
5. Wait 10-20 seconds

---

## Step 3: Select Your Project

1. Click the project dropdown again
2. Select your newly created project
3. Verify the project name appears at the top

---

## Step 4: Enable YouTube Data API v3

1. Click the hamburger menu (☰) or go to **"APIs & Services"** → **"Library"**
2. In the search bar, type: `YouTube Data API v3`
3. Click on **"YouTube Data API v3"** (the one with YouTube logo)
4. Click the blue **"ENABLE"** button
5. Wait 5-10 seconds

---

## Step 5: Create API Key

1. Click **"Credentials"** in the left sidebar
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"API key"**
4. A popup will show your API key

---

## Step 6: Copy the API Key

**IMPORTANT:** Copy and save the API key immediately!

It will look like this:
```
AIzaSyBXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Send this key securely (don't share publicly).

---

## Step 7: Restrict the Key (Optional but Recommended)

1. Click **"RESTRICT KEY"** in the popup
2. Under "API restrictions":
   - Select **"Restrict key"**
   - Check only **"YouTube Data API v3"**
3. Click **"SAVE"**

This ensures the key can only be used for YouTube API (more secure).

---

## ✅ Done!

You now have your YouTube Data API v3 key. Send it to me and I'll integrate it into the application.

---

## 📊 What You Get (Free Tier)

- **Daily quota:** 10,000 units
- **Videos per day:** ~3,000 video lookups
- **Cost:** $0 (free)
- **Resets:** Daily at midnight Pacific Time

---

## ⚠️ Important Notes

- Keep the API key secret (don't commit to Git or share publicly)
- The key is free to use within quota limits
- Quota resets daily
- You can view usage at: **APIs & Services** → **Dashboard**

---

## Need Help?

If you get stuck, common issues:

**"API not enabled"**
- Make sure you clicked ENABLE on YouTube Data API v3
- Wait 1-2 minutes for it to activate

**"Quota exceeded"**
- Wait until midnight PT for quota to reset
- OR request quota increase in the console

**Can't create project**
- Make sure you're signed into Google account
- Try using a different browser if issues persist

---

## Quick Links

- Google Cloud Console: https://console.cloud.google.com
- YouTube API Docs: https://developers.google.com/youtube/v3
- Quota Management: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas
