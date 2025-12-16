# 📚 Demo Links for Educational Content Verification

## ✅ VERIFIED Educational Links (Will show GREEN badge)

### YouTube Videos - Known Educational Channels
These will be verified via the **Tier 1 Educational Platform Whitelist**:

#### **3Blue1Brown** (Mathematics)
- https://www.youtube.com/watch?v=fNk_zzaMoSs (Vectors - Essence of Linear Algebra)
- https://www.youtube.com/watch?v=kfF40MiS7zA (The Essence of Calculus)
- Expected: **GREEN verified badge** (will show "Verified Educational Content")

#### **Khan Academy**
- https://www.youtube.com/watch?v=WUvTyaaNkzM (Intro to Calculus)
- https://www.khanacademy.org/ (Main platform - PDF/URL)
- Expected: **GREEN verified badge** (Platform whitelisted)

#### **CrashCourse**
- https://www.youtube.com/c/CrashCourse (History, Science, Literature)
- Expected: **GREEN verified badge** (Channel in whitelist)

#### **Veritasium**
- https://www.youtube.com/c/veritasium (Physics & Science)
- Expected: **GREEN verified badge** (Channel in whitelist)

#### **TED-Ed**
- https://www.youtube.com/c/TED-Ed (Educational animations)
- Expected: **GREEN verified badge** (Channel in whitelist)

#### **freeCodeCamp**
- https://www.youtube.com/c/freeCodeCamp (Programming tutorials)
- Expected: **GREEN verified badge** (Channel in whitelist)

### Academic Institution Sites
- **MIT OpenCourseWare:** https://ocw.mit.edu/
- **Stanford Online:** https://www.coursera.org/stanford
- **Harvard Courses:** https://www.edx.org/school/harvardx
- Expected: **GREEN verified badge** (Domain whitelisted: .edu, mit.edu, stanford.edu, harvard.edu)

### MOOC Platforms
- **Coursera:** https://www.coursera.org/
- **edX:** https://www.edx.org/
- **Udacity:** https://www.udacity.com/
- **DataCamp:** https://www.datacamp.com/
- **Codecademy:** https://www.codecademy.com/
- Expected: **GREEN verified badge** (Domains whitelisted)

---

## 🟡 UNVERIFIED Educational Links (Will show YELLOW badge)

These are genuinely educational but **NOT in the whitelist**, so they'll be verified via **Tier 2 AI Analysis** and may show as **YELLOW ("Unverified Content")** if API quota exceeded:

### YouTube Videos - Educational but Not in Channel Whitelist
- https://www.youtube.com/watch?v=9vKqVkMQHKk (MIT - How to Speak - Public Speaking)
- https://www.youtube.com/watch?v=HZ1fwFjv2hY (Harvard Medical School - How to Think About Medicine)
- Expected: **YELLOW unverified badge** (if quota exceeded) or **BLUE AI-verified** (if API available, >70% confidence)

### Self-Hosted Educational Content
- Educational blogs, Medium articles, personal learning platforms
- Expected: **YELLOW unverified badge** (if quota exceeded)

### Lesser-Known Educational YouTubers
- Programming tutorials on small channels
- Academic lectures from university channels not in whitelist
- Expected: **YELLOW unverified badge** (if quota exceeded)

---

## ❌ REJECTED Non-Educational Links (Will show RED rejection modal)

These will be **rejected** with error message:

### Entertainment Content
- https://www.youtube.com/watch?v=jNQXAC9IVRw (Me at the zoo - famous but not educational)
- https://www.youtube.com/watch?v=kffacxfA7g4 (Music video)
- Expected: **RED rejection modal** ("Non-educational content detected")

### News & Current Events
- CNN, BBC, News channels (not educational per se)
- Expected: **RED rejection modal** ("Non-educational content detected")

### Entertainment & Gaming
- Gaming videos, movie trailers, vlogs
- Expected: **RED rejection modal** ("Non-educational content detected")

### Sports & Entertainment
- Sports highlights, celebrity content
- Expected: **RED rejection modal** ("Non-educational content detected")

---

## 🔧 Testing Checklist

### Test Case 1: Verified Platform (MIT.edu)
```bash
URL: https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/
Expected: ✅ GREEN badge - "Verified Educational Content - From MIT"
Points: 150 base points (verified platform bonus)
```

### Test Case 2: AI-Verified Channel (3Blue1Brown Video)
```bash
URL: https://www.youtube.com/watch?v=fNk_zzaMoSs
Expected: ✅ GREEN badge - "Verified Educational Content - From 3Blue1Brown"
OR 🟡 YELLOW badge if quota exceeded
Points: 150 (if verified) or reduced (if unverified)
```

### Test Case 3: Unverified but Educational (Small YouTube Channel)
```bash
URL: https://www.youtube.com/watch?v=... (small educational channel)
Expected: 🟡 YELLOW badge - "Unverified Content - verification unavailable"
Points: Base points without verification bonus
```

### Test Case 4: Non-Educational Content
```bash
URL: https://www.youtube.com/watch?v=jNQXAC9IVRw
Expected: ❌ RED modal - "Content Rejected - Non-educational"
Points: 0 (rejected)
```

---

## 📊 Verification Workflow Visual

```
User Submits Link/Video
        ↓
[Tier 1: Whitelist Check]
├─ YouTube channel in YOUTUBE_EDU_CHANNELS? → GREEN ✅
├─ Domain in VERIFIED_EDUCATIONAL_PLATFORMS? → GREEN ✅
└─ Not matched? → Continue to Tier 2
        ↓
[Tier 2: AI Analysis (GPT-4)]
├─ Confidence > 70% && is_educational=true? → BLUE (AI-Verified) ✅
├─ API Quota Exceeded? → YELLOW (Unverified, allow anyway) 🟡
└─ Confidence < 70% || is_educational=false? → RED (Rejected) ❌
        ↓
[Generate Quiz & Award Points]
- GREEN/BLUE verified: Full points + verification bonus
- YELLOW unverified: Base points (no bonus)
- RED rejected: No quiz, no points, show rejection reason
```

---

## 🎯 Recommended Demo Flow

### For User Demo Presentation:
1. **Show Whitelist Verification (FASTEST)**
   - Use Coursera link → Instant GREEN badge
   - Use MIT.edu link → Instant GREEN badge
   
2. **Show AI Verification**
   - Use 3Blue1Brown link → GREEN badge
   - Use unknown educational channel → YELLOW/BLUE badge (depends on API)

3. **Show Rejection**
   - Use entertainment video → RED modal
   - Show error message clearly

4. **Show Points System**
   - Complete quiz on verified content → Full points shown
   - Complete quiz on unverified content → Lower points
   - Fail quiz → Zero points

---

## 💡 Pro Tips for Demo

- **Start with Coursera/MIT links** - These always show GREEN immediately (fastest demo)
- **Have a backup non-educational link** - If you need to show rejection
- **Show the quiz quality** - Verify that questions are about actual content, not metadata
- **Highlight the points system** - Show how verified content gives more points
- **Test API fallback** - If demonstrating to show robustness, mention the YELLOW badge for quota scenarios

---

## 🚀 Quick Copy-Paste Demo Links

### GREEN (Verified) - Copy these
```
https://www.coursera.org/
https://www.edx.org/
https://ocw.mit.edu/
https://www.khanacademy.org/
https://www.youtube.com/watch?v=fNk_zzaMoSs
```

### YELLOW (Unverified Educational) - Copy these
```
https://www.youtube.com/watch?v=9vKqVkMQHKk
https://medium.com/@personalblog/ml-tutorial
```

### RED (Rejected) - Copy these
```
https://www.youtube.com/watch?v=jNQXAC9IVRw
```
