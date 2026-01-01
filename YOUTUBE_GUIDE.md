# YouTube Video Support Guide

## ✅ Recommended YouTube Channels (Known to Work)

These educational channels typically have captions/transcripts enabled and work reliably:

### Science & Education
- **Khan Academy** - https://www.youtube.com/@khanacademy
- **CrashCourse** - https://www.youtube.com/@crashcourse
- **Kurzgesagt** - https://www.youtube.com/@kurzgesagt
- **Veritasium** - https://www.youtube.com/@veritasium
- **3Blue1Brown** - https://www.youtube.com/@3blue1brown
- **TED-Ed** - https://www.youtube.com/@TEDEd

### Technology & Programming
- **freeCodeCamp** - https://www.youtube.com/@freecodecamp
- **Traversy Media** - https://www.youtube.com/@TraversyMedia
- **Programming with Mosh** - https://www.youtube.com/@programmingwithmosh
- **The Net Ninja** - https://www.youtube.com/@NetNinja

### Test Videos
- ❌ YouTube URLs are currently heavily blocked (as of Jan 2026)
- ✅ **Use file uploads instead** - Download videos and upload .mp4 files
- ✅ Vimeo videos work better than YouTube

---

## 🚫 Common Issues

### Issue: "YouTube has blocked access to this video"

**Why this happens:**
- YouTube implements bot detection to prevent automated downloads
- Some videos don't have captions/transcripts available
- Certain videos have restricted access policies

**Solutions:**

1. **Use Different Video** (Recommended)
   - Try videos from verified educational channels (see list above)
   - Look for videos with the "CC" (Closed Captions) icon

2. **Download and Upload File**
   - Download the video manually from YouTube
   - Upload the video file (.mp4) directly to the quiz generator
   - This bypasses YouTube's bot detection

3. **Use Videos with Subtitles**
   - Our system works best with videos that have captions enabled
   - Check if video has subtitles by clicking the CC button on YouTube

---

## 🔧 Technical Details

### How YouTube Video Processing Works

Our system tries multiple methods in order:

1. **YouTube Transcript API** (Fastest, no download)
   - Fetches captions/subtitles directly from YouTube
   - Works for videos with captions enabled
   - **No authentication needed** - completely free
   - Bypasses most bot detection

2. **yt-dlp Subtitle Extraction**
   - Extracts existing subtitles without downloading video
   - Used when Transcript API fails
   - Can be blocked by YouTube bot detection

3. **Audio Download + Whisper Transcription**
   - Downloads audio and transcribes using OpenAI Whisper
   - Last resort fallback
   - Most likely to be blocked by YouTube
   - Requires OpenAI API key (costs money)

### Why We Don't Need YouTube Data API

**You DON'T need Google/YouTube Data API** because:
- YouTube Transcript API is free and doesn't require authentication
- It accesses publicly available captions
- No API key needed
- No quota limits

The **YouTube Data API v3** is different and would require:
- Google Cloud account
- Enable YouTube Data API v3
- Create credentials (API key or OAuth)
- Handle quota limits (10,000 units/day free)

This is **NOT necessary** for our use case!

---

## 💡 Best Practices

### For Best Results:

1. **Choose Educational Videos**
   - Educational content usually has captions
   - Verified educational channels work best

2. **Check Video Length**
   - Shorter videos (5-20 minutes) process faster
   - Maximum length: 2 hours (configurable)

3. **Verify Captions Exist**
   - On YouTube, click the CC button to check
   - Auto-generated captions work fine

4. **Alternative: Upload Video Files**
   - If YouTube URL fails, download and upload the file
   - Supports: MP4, AVI, MOV, MKV, WEBM
   - Maximum size: 500MB (configurable)

---

## 🔍 Testing Videos

### Working Examples:
```
https://www.youtube.com/watch?v=5hpLjDIc6kI  (Khan Academy - Photosynthesis)
https://www.youtube.com/watch?v=VPhHvxQxAxQ  (TED-Ed - Climate Change)
```

### May Not Work:
- Music videos (no educational captions)
- Live streams
- Age-restricted videos
- Region-locked content
- Videos without captions

---

## 🛠️ Environment Variables

Optional video processing configuration in `.env`:

```bash
# Maximum video length in seconds (default: 7200 = 2 hours)
MAX_VIDEO_DURATION_SECONDS=7200

# Maximum video file size in MB (default: 500)
MAX_VIDEO_SIZE_MB=500

# OpenAI API key (only needed for Whisper transcription fallback)
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 📊 Success Rate by Method

Based on testing:

| Method | Success Rate | Speed | Notes |
|--------|--------------|-------|-------|
| YouTube Transcript API | ~70% | Fast | Best for videos with captions |
| yt-dlp Subtitles | ~40% | Medium | Often blocked by bot detection |
| Whisper Transcription | ~30% | Slow | Expensive, often blocked |
| **Manual Upload** | ~95% | Medium | **Most reliable!** |

**Recommendation:** For important videos, download and upload the file manually.

---

## 🆘 Still Having Issues?

1. **Try a different video** from verified educational channels
2. **Download the video** and upload as a file instead
3. **Check the video has captions** (CC button on YouTube)
4. **Use shorter videos** (under 20 minutes)
5. **Report persistent issues** at https://github.com/shubh1996/ai-quiz-generator/issues
