# Content Safety Testing Guide

## Overview

The quiz generator now includes a comprehensive content safety system with two modes:
- **Kid-Safe Mode (Under 18):** Strict filtering that blocks violence, substances, abuse, vulgar content, and mature themes
- **Adult Mode (18+):** Basic filtering that only blocks extremely inappropriate content

## How to Test

### 1. Start the Backend Locally

```bash
cd backend
uvicorn main:app --reload
```

### 2. Start the Frontend Locally

```bash
cd frontend
npm run dev
```

### 3. Access the App

Open http://localhost:3000 in your browser.

---

## Test Cases for Kid-Safe Mode

### ✅ SHOULD PASS (Kid-Appropriate Content)

1. **Educational Science:**
   - URL: Wikipedia article on Photosynthesis
   - Text: "The water cycle is a continuous process of evaporation, condensation, and precipitation..."

2. **Math Content:**
   - Text: "The Pythagorean theorem states that in a right triangle, the square of the hypotenuse equals the sum of squares of the other two sides..."

3. **Nature/Animals:**
   - Text: "Dolphins are highly intelligent marine mammals known for their playful behavior and complex social structures..."

4. **Arts & Crafts:**
   - Text: "Origami is the Japanese art of paper folding. Start with a square piece of paper..."

5. **Kids' Shows:**
   - Text: "Bluey is an Australian animated television series about a Blue Heeler puppy and her family..."

### 🚫 SHOULD BLOCK (Inappropriate for Kids)

1. **Violence:**
   - Text: "The battle was fierce, with soldiers fighting and weapons causing destruction..."
   - Expected: BLOCKED - Flagged topics: ["violence", "weapons"]

2. **Substances:**
   - Text: "Effects of alcohol consumption on the human body include impaired judgment..."
   - Expected: BLOCKED - Flagged topics: ["alcohol", "substances"]

3. **Mature Themes:**
   - Text: "The couple's romantic relationship evolved as they began dating..."
   - Expected: BLOCKED - Flagged topics: ["relationships", "mature_themes"]

4. **Horror:**
   - Text: "The zombie apocalypse thriller features scary monsters and disturbing imagery..."
   - Expected: BLOCKED - Flagged topics: ["horror", "violence"]

5. **Profanity:**
   - Text containing curse words or vulgar language
   - Expected: BLOCKED - Flagged topics: ["profanity", "inappropriate_language"]

6. **Dangerous Activities:**
   - Text: "How to build explosives..." or "Self-harm methods..."
   - Expected: BLOCKED - Flagged topics: ["dangerous_activities"]

---

## Test Cases for Adult Mode (18+)

### ✅ SHOULD PASS (Appropriate for Adults)

1. **News/Current Events:**
   - Text: "The political debate covered controversial policy changes..."

2. **Mature Education:**
   - Text: "Health education covering reproductive biology and anatomy..."

3. **Historical Events:**
   - Text: "World War II history, including battles and casualties..."

4. **Social Issues:**
   - Text: "Discussion of substance abuse prevention programs..."

5. **Adult Entertainment:**
   - Text: "The R-rated movie features mature themes and strong language..."

### 🚫 SHOULD BLOCK (Extremely Inappropriate Even for Adults)

1. **Illegal Activities:**
   - Text: "How to manufacture illegal drugs..." or "Instructions for illegal hacking..."
   - Expected: BLOCKED

2. **Extreme Violence:**
   - Text: Graphic descriptions of gore or torture
   - Expected: BLOCKED

3. **Explicit Sexual Content:**
   - Text: Pornographic content or explicit descriptions
   - Expected: BLOCKED

4. **Hate Speech:**
   - Text: Content promoting discrimination or extremism
   - Expected: BLOCKED

---

## Testing Procedure

### Option 1: Using the UI

1. Go to http://localhost:3000
2. **Select age mode** (Kid-Safe or 18+)
3. Choose input method (File/URL/Video)
4. Enter test content
5. Click "Generate Quiz"
6. **Expected Results:**
   - Safe content → Quiz generated successfully
   - Unsafe content → Error message showing "Content Safety Violation" with flagged topics

### Option 2: Using cURL

**Test Kid-Safe Mode:**
```bash
# Should PASS - Educational content
curl -X POST http://localhost:8000/api/generate-quiz \
  -F "url=https://en.wikipedia.org/wiki/Python_(programming_language)" \
  -F "age_mode=kids"

# Should BLOCK - Violence
echo "The soldiers fought with weapons causing destruction" > /tmp/violence.txt
curl -X POST http://localhost:8000/api/generate-quiz \
  -F "file=@/tmp/violence.txt" \
  -F "age_mode=kids"
```

**Test Adult Mode:**
```bash
# Should PASS - Mature but educational
curl -X POST http://localhost:8000/api/generate-quiz \
  -F "url=https://en.wikipedia.org/wiki/World_War_II" \
  -F "age_mode=18+"

# Should BLOCK - Illegal content
echo "How to manufacture illegal drugs step by step" > /tmp/illegal.txt
curl -X POST http://localhost:8000/api/generate-quiz \
  -F "file=@/tmp/illegal.txt" \
  -F "age_mode=18+"
```

---

## Expected API Responses

### Success (Content Passed Safety Check)

```json
{
  "success": true,
  "content": { ... },
  "quiz": { ... },
  ...
}
```

### Failure (Content Blocked)

```json
{
  "detail": {
    "error": "Content Safety Violation",
    "reason": "Content contains violence and weapons",
    "flagged_topics": ["violence", "weapons"],
    "age_mode": "kids",
    "message": "This content is not appropriate for kids mode"
  }
}
```

---

## Implementation Details

### Backend Safety Service

Location: `backend/services/content_safety_service.py`

**Kid-Safe Mode Blocks:**
- Violence, gore, weapons
- Drugs, alcohol, substances
- Sexual/mature themes
- Profanity, vulgar language
- Abuse, bullying
- Horror, scary content
- Gambling
- Dangerous activities
- Hate speech
- Political controversy
- Adult products/services

**Adult Mode Blocks:**
- Illegal activities
- Extreme violence/gore
- Explicit sexual content
- Instructions for harm
- Hate speech/extremism

### Frontend Toggle

Location: `frontend/app/components/UploadStep.tsx`

- Prominent toggle at top of upload page
- Visual feedback for selected mode
- Clear description of what each mode blocks

---

## Monitoring & Logs

When content is checked, backend logs show:

```
🛡️ Checking content safety (age_mode: kids)...
✅ Content passed safety check (confidence: 95%)
```

OR

```
🛡️ Checking content safety (age_mode: kids)...
🚫 SAFETY BLOCK: Content contains violence and weapons
   Flagged topics: violence, weapons
```

---

## Important Notes

1. **Default Mode:** 18+ (to avoid blocking adult users by default)
2. **API Failure Handling:**
   - Kid mode: BLOCKS content if safety check fails (fail-safe)
   - Adult mode: ALLOWS content if safety check fails (avoid false positives)
3. **Performance:** Safety check adds ~2-5 seconds to processing time
4. **Accuracy:** Depends on Perplexity API - typically 90-95% accurate

---

## Troubleshooting

### Issue: All content is being blocked

**Cause:** No PERPLEXITY_API_KEY set
**Solution:** Add key to `.env`:
```
PERPLEXITY_API_KEY=your_key_here
```

### Issue: Safety check not working

**Check backend logs** for errors:
```bash
cd backend
uvicorn main:app --reload
# Watch for safety check messages
```

### Issue: Frontend not sending age_mode

**Check browser console** (F12):
- Look for the API request
- Verify `age_mode` is in the FormData

---

## Production Deployment

Before deploying to production:

1. ✅ Test all kid-safe blocks work
2. ✅ Test adult mode allows appropriate content
3. ✅ Verify API key is set on Render
4. ✅ Test with real-world URLs and files
5. ✅ Verify error messages are user-friendly

---

## Future Enhancements

- [ ] Add custom word blacklists
- [ ] Allow administrators to adjust sensitivity
- [ ] Add reporting for false positives
- [ ] Cache safety checks to improve performance
- [ ] Add parental controls with PIN
