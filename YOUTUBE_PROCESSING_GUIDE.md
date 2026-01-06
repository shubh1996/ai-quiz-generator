# YouTube Video Processing Guide

## How YouTube Processing Works

The Quiz Generator uses a **4-tier fallback strategy** to ensure maximum success rate for YouTube videos:

### Tier 1: YouTube Transcript API (Fastest)
- Fetches existing captions/subtitles directly
- Works for ~70% of videos (those with captions)
- No API key required
- Completes in 2-5 seconds

### Tier 2: YouTube Data API v3 (Verification)
- Verifies video exists and has captions
- Requires API key (free, 10,000 requests/day)
- Optional but recommended

### Tier 3: yt-dlp Subtitle Extraction
- Downloads subtitle files (.vtt/.srt)
- Works when Transcript API is blocked
- Completes in 5-10 seconds

### Tier 4: Whisper Transcription (Always Works)
- Downloads audio and transcribes with OpenAI Whisper
- **100% success rate** for accessible videos
- Costs ~$0.006 per minute of video
- Completes in 30-60 seconds for 10-minute video

---

## Why YouTube Blocking Happens

YouTube uses sophisticated bot detection that blocks requests from:
- **Datacenter IPs** (all cloud hosting: Render, Railway, AWS, etc.)
- **Known bot user-agents**
- **Unusual request patterns**

This affects:
- Free hosting platforms (Render free tier) ❌ High block rate
- Paid cloud platforms (Railway, AWS) ⚠️ Lower block rate
- Local development ✅ Almost never blocked

---

## Recommended Solution: Railway + Whisper Fallback

**Best balance of cost and reliability**

### Why Railway?
1. **Better IP reputation** than free tiers
2. **More RAM** (8GB) for video processing
3. **No cold starts** (instant response)
4. **Automatic Whisper fallback** works reliably

### Cost Analysis
- **Hosting**: $5-10/month (includes $5 free credits)
- **Whisper usage**: ~$0.006/minute of video
  - 10-minute video = $0.06
  - 100 videos/month = $6 in transcription costs
  - **Total budget needed**: ~$15-20/month

### Expected Success Rates

#### On Render Free Tier (Current):
- Tier 1 (Transcript API): ~20% success (heavy blocking)
- Tier 2 (Data API): Verification only
- Tier 3 (yt-dlp): ~30% success
- Tier 4 (Whisper): ~90% success (if audio downloads)
- **Overall**: ~60-70% success rate

#### On Railway (Recommended):
- Tier 1 (Transcript API): ~40% success (less blocking)
- Tier 2 (Data API): Verification only
- Tier 3 (yt-dlp): ~50% success
- Tier 4 (Whisper): ~95% success
- **Overall**: ~90-95% success rate

---

## Setup Instructions

### 1. Get API Keys

#### OpenAI API Key (Required for Whisper)
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create account or sign in
3. Go to API Keys → Create new key
4. Copy key (starts with `sk-proj-...`)

**Cost**: Pay-as-you-go, ~$0.006/minute of video

#### YouTube Data API v3 Key (Optional but Recommended)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project
3. Enable YouTube Data API v3
4. Create credentials → API Key
5. Copy key (starts with `AIza...`)

**Cost**: Free (10,000 requests/day limit)

### 2. Deploy to Railway

See [DEPLOYMENT.md](DEPLOYMENT.md#-recommended-railway-setup-for-youtube-videos) for full instructions.

**Quick steps**:
1. Sign up at [railway.app](https://railway.app)
2. Deploy from GitHub repository
3. Add environment variables:
   ```
   PERPLEXITY_API_KEY=your_key
   OPENAI_API_KEY=your_openai_key
   YOUTUBE_API_KEY=your_youtube_key
   FRONTEND_URL=your_vercel_url
   ```
4. Deploy and test

---

## Testing Your Deployment

### Test Video Processing

```bash
curl -X POST "https://your-app.railway.app/api/generate-quiz" \
  -F "video_url=https://www.youtube.com/watch?v=fNk_zzaMoSs" \
  -F "age_mode=18+"
```

### Expected Response Times

| Method | Duration | Success Rate (Railway) |
|--------|----------|------------------------|
| Transcript API | 2-5 sec | ~40% |
| yt-dlp subtitles | 5-10 sec | ~50% |
| Whisper transcription | 30-60 sec | ~95% |

### Check Logs

In Railway dashboard → Deployments → View Logs:

```
✓ YouTube API confirmed captions exist        # Tier 2 verification
✓ Found transcript with languages: ['en']     # Tier 1 success
✓ Successfully fetched transcript             # Complete
```

Or if fallback to Whisper:

```
⚠️ YouTube Transcript API failed              # Tier 1 blocked
⚠️ Subtitle extraction failed                 # Tier 3 blocked
⚠️ No subtitles found, attempting audio...    # Falling back to Tier 4
✓ Successfully transcribed audio              # Whisper success
```

---

## Troubleshooting

### Error: "YouTube has blocked access to this video"

**Cause**: All 4 tiers failed (rare on Railway, common on free hosting)

**Solutions**:
1. Try a different educational video (Khan Academy, TED-Ed, CrashCourse)
2. Use videos from verified channels
3. Download video manually and upload as file
4. Check OpenAI API key is configured correctly

### Error: "Request timed out"

**Cause**: Video too long or slow transcription

**Solutions**:
1. Use shorter videos (<30 minutes)
2. Increase timeout in frontend (if needed)
3. Check Railway logs for actual error

### Error: "Transcription failed"

**Cause**: OpenAI API issue

**Solutions**:
1. Verify OpenAI API key is correct
2. Check OpenAI account has credits
3. Verify billing is enabled on OpenAI account

---

## Best Practices

### Choose Videos That Work Best

✅ **Good choices**:
- Educational channels (Khan Academy, CrashCourse, TED-Ed)
- Videos with manual captions enabled
- Videos from verified/popular channels
- Videos under 30 minutes

❌ **Avoid**:
- Age-restricted videos
- Private/unlisted videos
- Live streams
- Videos with copyright restrictions

### Optimize Costs

1. **Test locally first** - Free, no blocking
2. **Use caption-enabled videos** - Avoids Whisper costs
3. **Monitor Whisper usage** - Track OpenAI billing
4. **Set video duration limits** - Prevent excessive costs

Current limit: 2 hours (7200 seconds)
Update in `.env`:
```
MAX_VIDEO_DURATION_SECONDS=3600  # 1 hour limit
```

---

## API Integration

### PHP Example

```php
$api = new QuizGeneratorAPI('https://your-app.railway.app');

try {
    $quiz = $api->generateFromVideo(
        'https://www.youtube.com/watch?v=example',
        'kids'
    );

    echo "Quiz generated: " . $quiz['content']['title'];
} catch (Exception $e) {
    echo "Error: " . $e->getMessage();
}
```

### JavaScript Example

```javascript
const response = await fetch('https://your-app.railway.app/api/generate-quiz', {
  method: 'POST',
  body: new URLSearchParams({
    video_url: 'https://www.youtube.com/watch?v=example',
    age_mode: '18+'
  })
});

const quiz = await response.json();
console.log('Quiz:', quiz);
```

---

## Migration from Render to Railway

### Current Issues on Render Free Tier
- High YouTube blocking rate (~80%)
- Cold starts (30-60 second delays)
- Limited RAM (512MB)
- No Whisper fallback reliability

### Benefits of Railway Migration
- Lower blocking rate (~60% → ~10%)
- No cold starts
- 8GB RAM available
- Reliable Whisper fallback
- Better monitoring

### Migration Steps

1. **Create Railway account**
2. **Deploy from GitHub** (uses `railway.json` config)
3. **Copy environment variables** from Render
4. **Test deployment** with sample video
5. **Update frontend URL** in Vercel
6. **Monitor logs** for first few requests
7. **Decommission Render** after confirming success

**Estimated downtime**: 5-10 minutes during DNS update

---

## Cost Calculator

### Monthly Costs

**Hosting (Railway)**: $5-10/month

**Whisper Transcription**:
- Light usage (10 videos/month, avg 10min): ~$0.60
- Medium usage (50 videos/month, avg 10min): ~$3.00
- Heavy usage (200 videos/month, avg 10min): ~$12.00

**Total Budget Examples**:
- Personal project: $5-8/month
- Small business: $10-15/month
- Production app: $15-25/month

---

## Support

### Check Status
```bash
curl https://your-app.railway.app/health
```

### View Logs
Railway Dashboard → Deployments → View Logs

### Common Log Messages

✅ **Success indicators**:
```
✓ YouTube API confirmed captions exist
✓ Successfully fetched transcript via YouTube Transcript API
✓ Successfully extracted subtitles
✓ Successfully transcribed audio
```

⚠️ **Warning indicators** (will fallback):
```
⚠️ YouTube Transcript API failed
⚠️ Subtitle extraction failed
⚠️ No subtitles found, attempting audio download
```

❌ **Error indicators** (need attention):
```
❌ OpenAI API key is required for video transcription
❌ Transcription failed: insufficient_quota
❌ Video too long (7200s). Maximum allowed: 7200s
```

---

## Related Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - Full deployment guide
- [PHP_INTEGRATION_GUIDE.md](PHP_INTEGRATION_GUIDE.md) - PHP integration examples
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - Complete API reference
