# Quiz Generator API Specification

**Base URL:** `https://ai-quiz-generator-f8dr.onrender.com`

**Version:** 1.0

**Last Updated:** January 2026

---

## Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
3. [Request Formats](#request-formats)
4. [Response Format](#response-format)
5. [Error Handling](#error-handling)
6. [Rate Limits](#rate-limits)
7. [Examples](#examples)

---

## Authentication

Currently, the API does **not require authentication**. All endpoints are publicly accessible.

**Note:** Rate limiting may be applied in the future.

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the API is running

**Response:**
```json
{
  "status": "healthy"
}
```

---

### 2. Generate Quiz

**Endpoint:** `POST /api/generate-quiz`

**Description:** Generate a quiz from a document, URL, or video

**Content-Type:** `multipart/form-data`

**Request Parameters:**

You must provide **ONE** of the following:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Optional* | Upload a document or video file |
| `url` | String | Optional* | Web URL to scrape content from |
| `video_url` | String | Optional* | Video URL (YouTube, Vimeo, etc.) |

*At least one parameter is required.

**Supported File Types:**

**Documents:**
- PDF (`.pdf`)
- Text (`.txt`)
- Word (`.doc`, `.docx`)

**Videos:**
- MP4 (`.mp4`)
- AVI (`.avi`)
- MOV (`.mov`)
- MKV (`.mkv`)
- WebM (`.webm`)

**Supported Video Platforms:**
- YouTube
- Vimeo
- Dailymotion
- Twitch
- Direct video URLs

---

## Response Format

### Success Response (HTTP 200)

```json
{
  "success": true,
  "content": {
    "title": "String - Content title",
    "description": "String - AI-generated summary of the content",
    "media_link": "String - Original source URL/filename",
    "duration": "Number - Duration in minutes (for videos) or null",
    "suggested_categories": ["Array", "of", "category", "suggestions"],
    "suggested_media_type": "String - video|document|url|article",
    "creator_name": "String - Author/Channel name or null",
    "thumbnail_url": "String - Thumbnail URL or null"
  },
  "quiz": {
    "num_quiz_questions": "Number - Total questions (always 5)",
    "questions": [
      {
        "question": "String - The question text",
        "num_answers": "Number - Number of answer options (always 4)",
        "answers": [
          {
            "answer": "String - Answer option text",
            "weight": "Number - 2=correct, 1=partially correct, 0=incorrect"
          }
        ]
      }
    ]
  },
  "verification": {
    "status": "String - verified|ai_verified|rejected|pending",
    "confidence_score": "Number - 0-100",
    "platform": "String - Source platform or null",
    "rejection_reason": "String - Reason if rejected, or null",
    "verified_at": "String - ISO 8601 timestamp",
    "verification_method": "String - How it was verified"
  },
  "source_info": {
    "source_type": "String - video_url|video_file|document_file|web_url",
    "source_identifier": "String - URL or filename",
    "title": "String - Title or null",
    "duration": "Number - Duration in seconds or null",
    "transcript_length": "Number - Characters in transcript or null"
  },
  "points_awarded": "Number - Points earned (50-150)",
  "generated_at": "String - ISO 8601 timestamp",
  "expires_at": "String - ISO 8601 timestamp (24 hours from generation)"
}
```

### Error Response (HTTP 4xx/5xx)

```json
{
  "success": false,
  "detail": "String - Error message"
}
```

**Special Case - Content Rejected (HTTP 403):**

```json
{
  "success": false,
  "detail": {
    "error": "Content Rejected",
    "reason": "String - Why content was rejected",
    "confidence": "Number - Confidence score"
  }
}
```

---

## Field Descriptions

### Content Section

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `title` | String | Content title or auto-generated | "Using Technology to Engage Students" |
| `description` | String | AI-generated summary | "This video explores practical strategies..." |
| `media_link` | String | Original source URL or filename | "https://youtube.com/watch?v=..." |
| `duration` | Number/null | Duration in minutes (videos only) | 22 |
| `suggested_categories` | Array | AI-suggested content categories | ["Technology Integration", "Teaching"] |
| `suggested_media_type` | String | Type of media | "video", "document", "url", "article" |
| `creator_name` | String/null | Author or channel name | "EdTech Academy" |
| `thumbnail_url` | String/null | Thumbnail image URL | "https://i.ytimg.com/vi/.../maxres.jpg" |

### Quiz Section

| Field | Type | Description |
|-------|------|-------------|
| `num_quiz_questions` | Number | Always 5 |
| `questions` | Array | Array of question objects |

### Question Object

| Field | Type | Description |
|-------|------|-------------|
| `question` | String | The question text |
| `num_answers` | Number | Always 4 |
| `answers` | Array | Array of answer objects |

### Answer Object

| Field | Type | Description |
|-------|------|-------------|
| `answer` | String | Answer option text |
| `weight` | Number | 2 = Correct, 1 = Partially correct, 0 = Incorrect |

**Note:** Only ONE answer should have `weight: 2` (the correct answer).

### Verification Section

| Field | Type | Description |
|-------|------|-------------|
| `status` | String | "verified" (trusted platform), "ai_verified" (AI checked), "rejected" (non-educational), "pending" (not checked) |
| `confidence_score` | Number | 0-100, confidence in educational quality |
| `platform` | String/null | Platform name if verified |
| `rejection_reason` | String/null | Why content was rejected |
| `verified_at` | String | ISO 8601 timestamp |
| `verification_method` | String | How verification was done |

### Points System

| Status | Points Awarded |
|--------|----------------|
| Verified (trusted platform) | 150 |
| AI Verified | 100 |
| Unverified/Pending | 50 |
| Rejected | 0 (quiz not generated) |

---

## Error Handling

### Common Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 400 | Bad Request | No file/URL provided, invalid format |
| 403 | Forbidden | Content rejected as non-educational |
| 500 | Internal Server Error | Processing error, API failure |
| 504 | Gateway Timeout | Request took too long (>2 minutes) |

### Error Response Format

```json
{
  "success": false,
  "detail": "Error message here"
}
```

---

## Rate Limits

**Current:** No rate limits

**Future:** May implement rate limiting based on:
- IP address
- API usage patterns
- Resource consumption

---

## Request Examples

### Example 1: Upload PDF Document

```bash
curl -X POST https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz \
  -F "file=@/path/to/document.pdf"
```

### Example 2: Web URL

```bash
curl -X POST https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz \
  -F "url=https://en.wikipedia.org/wiki/Photosynthesis"
```

### Example 3: YouTube Video

```bash
curl -X POST https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz \
  -F "video_url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Example 4: JavaScript/Fetch

```javascript
const formData = new FormData();
formData.append('url', 'https://example.com/article');

const response = await fetch('https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data);
```

### Example 5: Python

```python
import requests

url = "https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz"
files = {'file': open('document.pdf', 'rb')}

response = requests.post(url, files=files)
quiz_data = response.json()
print(quiz_data)
```

---

## Complete Response Example

```json
{
  "success": true,
  "content": {
    "title": "Using Technology to Engage Students",
    "description": "This video explores practical strategies for integrating technology into classroom instruction, including interactive tools, assessment platforms, and collaboration software.",
    "media_link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "duration": 22,
    "suggested_categories": ["Technology Integration", "Student Engagement", "EdTech"],
    "suggested_media_type": "video",
    "creator_name": "EdTech Academy",
    "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
  },
  "quiz": {
    "num_quiz_questions": 5,
    "questions": [
      {
        "question": "According to the video, what is the primary benefit of using interactive polling tools in the classroom?",
        "num_answers": 4,
        "answers": [
          {
            "answer": "Increases student engagement and provides real-time feedback to teachers",
            "weight": 2
          },
          {
            "answer": "Reduces the need for homework assignments",
            "weight": 0
          },
          {
            "answer": "Allows teachers to grade automatically",
            "weight": 1
          },
          {
            "answer": "Makes lessons shorter",
            "weight": 0
          }
        ]
      },
      {
        "question": "Which strategy does the presenter recommend for introducing new technology tools?",
        "num_answers": 4,
        "answers": [
          {
            "answer": "Start with one tool and master it before adding more",
            "weight": 2
          },
          {
            "answer": "Introduce all tools at once so students can choose",
            "weight": 0
          },
          {
            "answer": "Only use tools that students already know",
            "weight": 0
          },
          {
            "answer": "Let students figure out tools on their own",
            "weight": 0
          }
        ]
      }
      // ... 3 more questions
    ]
  },
  "verification": {
    "status": "ai_verified",
    "confidence_score": 95.5,
    "platform": null,
    "rejection_reason": null,
    "verified_at": "2024-12-15T14:31:30Z",
    "verification_method": "ai_analysis"
  },
  "source_info": {
    "source_type": "video_url",
    "source_identifier": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "title": "Using Technology to Engage Students",
    "duration": 1320,
    "transcript_length": 5420
  },
  "points_awarded": 100,
  "generated_at": "2024-12-15T14:31:30Z",
  "expires_at": "2024-12-16T14:31:30Z"
}
```

---

## Processing Times

| Content Type | Typical Time | Maximum Time |
|--------------|--------------|--------------|
| Small text file | 5-10 seconds | 30 seconds |
| PDF document | 15-30 seconds | 60 seconds |
| Web URL | 10-20 seconds | 45 seconds |
| YouTube video | 30-90 seconds | 120 seconds |
| Large video file | 60-120 seconds | 120 seconds |

**Note:** First request after inactivity may take +30 seconds (server wake-up time on free tier).

---

## Best Practices

### 1. File Size Limits

- **Documents:** < 10MB recommended
- **Videos:** < 500MB (configurable server-side)

### 2. Content Requirements

- Minimum content length: 50 characters
- Recommended: 200+ words for better quiz quality
- Educational content performs best

### 3. Error Handling

Always check `success` field:

```javascript
if (data.success) {
  // Process quiz
  console.log(data.quiz);
} else {
  // Handle error
  console.error(data.detail);
}
```

### 4. Timeout Handling

Set appropriate timeouts in your HTTP client:

```javascript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minutes

fetch(url, { signal: controller.signal })
  .finally(() => clearTimeout(timeoutId));
```

---

## CORS Configuration

The API allows requests from:
- `http://localhost:3000` (development)
- `https://*.vercel.app` (Vercel deployments)
- Custom origins (configurable via `FRONTEND_URL` env variable)

**Allowed Methods:** GET, POST, PUT, DELETE, OPTIONS

**Allowed Headers:** All

---

## Webhooks

**Status:** Not yet implemented

**Future:** Webhook support for long-running quiz generation jobs may be added.

---

## Support

- **Documentation:** See project README
- **Issues:** https://github.com/shubh1996/ai-quiz-generator/issues
- **API Status:** Check `/health` endpoint

---

## Changelog

### v1.0 (Current)
- Initial release
- Support for documents, URLs, and videos
- AI-powered educational content verification
- 5-question MCQ generation
- Points system based on content quality

---

## Notes

1. **YouTube Videos:** May not work reliably due to YouTube's bot detection. Recommend downloading and uploading files instead.

2. **Free Tier Limitations:** Backend runs on Render free tier, which sleeps after 15 minutes of inactivity. First request after sleep takes ~30 seconds.

3. **API Keys:** No API key required currently, but may be added in the future for rate limiting and analytics.

4. **Response Format:** The API returns the new standardized format as of January 2026. Legacy format is no longer supported.
