# Quiz Generator API - Integration Guide for Backend Teams

**Version:** 1.0
**Last Updated:** January 2026
**Base URL:** `https://ai-quiz-generator-f8dr.onrender.com`

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [Core Endpoint](#core-endpoint)
4. [Request Format](#request-format)
5. [Response Format](#response-format)
6. [Integration Examples](#integration-examples)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Testing](#testing)

---

## Quick Start

### The Only Endpoint You Need

```
POST /api/generate-quiz
```

**What it does:** Accepts a file, URL, or video URL and returns a complete quiz with metadata.

**Simple Example:**

```bash
curl -X POST https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz \
  -F "url=https://en.wikipedia.org/wiki/Python_(programming_language)"
```

---

## Authentication

**Current:** No authentication required
**Future:** May require API key

All endpoints are publicly accessible. Rate limiting may be added in the future.

---

## Core Endpoint

### POST /api/generate-quiz

Generate a quiz from educational content.

**Content-Type:** `multipart/form-data`

**Parameters (send ONE of these):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Optional* | Document or video file upload |
| `url` | String | Optional* | Web URL to scrape |
| `video_url` | String | Optional* | Video URL (YouTube, Vimeo, etc.) |
| `job_id` | String | Optional | Custom job ID (UUID generated if not provided) |

*At least one content parameter is required.

**Supported File Types:**

- **Documents:** `.pdf`, `.txt`, `.doc`, `.docx`
- **Videos:** `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`

**Supported Video Platforms:**

- YouTube (may have reliability issues due to bot detection)
- Vimeo
- Dailymotion
- Twitch
- Direct video URLs

---

## Request Format

### Option 1: File Upload

```bash
curl -X POST https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz \
  -F "file=@/path/to/document.pdf"
```

### Option 2: Web URL

```bash
curl -X POST https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz \
  -F "url=https://example.com/article"
```

### Option 3: Video URL

```bash
curl -X POST https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz \
  -F "video_url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Option 4: With Job ID

```bash
curl -X POST https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz \
  -F "url=https://example.com/article" \
  -F "job_id=your-custom-job-id-123"
```

---

## Response Format

### Success Response (HTTP 200)

```json
{
  "success": true,
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "content": {
    "title": "Python Programming Language",
    "description": "An overview of Python, covering its history, features, and applications in modern software development.",
    "media_link": "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "duration": 15,
    "suggested_categories": ["Programming", "Computer Science", "Software Development"],
    "suggested_media_type": "article",
    "creator_name": null,
    "thumbnail_url": null
  },
  "quiz": {
    "num_quiz_questions": 5,
    "questions": [
      {
        "question": "What is the primary design philosophy of Python?",
        "num_answers": 5,
        "answers": [
          {
            "answer": "Code readability and simplicity",
            "weight": 2
          },
          {
            "answer": "High performance and speed",
            "weight": 1
          },
          {
            "answer": "Maximum code density",
            "weight": 0
          },
          {
            "answer": "Complex syntax for precision",
            "weight": 0
          },
          {
            "answer": "Minimal documentation requirements",
            "weight": 0
          }
        ]
      }
      // ... 4 more questions
    ]
  },
  "verification": {
    "status": "ai_verified",
    "confidence_score": 92.5,
    "platform": null,
    "rejection_reason": null,
    "verified_at": "2026-01-01T10:30:00Z",
    "verification_method": "ai_analysis"
  },
  "source_info": {
    "source_type": "web_url",
    "source_identifier": "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "title": "Python (programming language)",
    "duration": null,
    "transcript_length": null
  },
  "points_awarded": 100,
  "generated_at": "2026-01-01T10:30:00Z"
}
```

### Error Response (HTTP 4xx/5xx)

```json
{
  "success": false,
  "detail": "Error message describing what went wrong"
}
```

### Content Rejected (HTTP 403)

```json
{
  "success": false,
  "detail": {
    "error": "Content Rejected",
    "reason": "This content does not appear to be educational",
    "confidence": 87.3
  }
}
```

---

## Field Descriptions

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | Boolean | Always `true` for successful responses |
| `job_id` | String | UUID for tracking this quiz generation |
| `content` | Object | Content metadata (see below) |
| `quiz` | Object | Quiz data (see below) |
| `verification` | Object/null | Verification metadata (optional) |
| `source_info` | Object/null | Source information (optional) |
| `points_awarded` | Number/null | Points earned (50-150) |
| `generated_at` | String | ISO 8601 timestamp |

### Content Object

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `title` | String | Content title | "Introduction to Machine Learning" |
| `description` | String | AI-generated summary | "This article explores..." |
| `media_link` | String | Original source URL/filename | "https://example.com/article" |
| `duration` | Number/null | Duration in minutes | 22 (for videos) |
| `suggested_categories` | Array | AI-suggested categories | ["AI", "Technology"] |
| `suggested_media_type` | String | Media type | "video", "document", "article" |
| `creator_name` | String/null | Author/channel name | "EdTech Academy" |
| `thumbnail_url` | String/null | Thumbnail URL | "https://..." |

### Quiz Object

| Field | Type | Description |
|-------|------|-------------|
| `num_quiz_questions` | Number | Always 5 |
| `questions` | Array | Array of question objects |

### Question Object

| Field | Type | Description |
|-------|------|-------------|
| `question` | String | The question text |
| `num_answers` | Number | Always 5 |
| `answers` | Array | Array of answer objects |

### Answer Object

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `answer` | String | - | Answer text |
| `weight` | Number | 0, 1, or 2 | 2 = Correct, 1 = Partially correct, 0 = Incorrect |

**Important:** Only ONE answer per question has `weight: 2` (the correct answer).

### Scoring System

To calculate a user's score:

```javascript
let totalScore = 0;
const maxScore = quiz.questions.length * 2; // 5 questions × 2 = 10

quiz.questions.forEach((question, index) => {
  const selectedAnswerIndex = userAnswers[index];
  const selectedAnswer = question.answers[selectedAnswerIndex];
  totalScore += selectedAnswer.weight;
});

const percentageScore = Math.round((totalScore / maxScore) * 100);
// Example: 8/10 = 80%
```

### Verification Object

| Field | Type | Description |
|-------|------|-------------|
| `status` | String | "verified", "ai_verified", "rejected", "pending" |
| `confidence_score` | Number | 0-100 confidence score |
| `platform` | String/null | Platform name if verified |
| `rejection_reason` | String/null | Why content was rejected |
| `verified_at` | String | ISO 8601 timestamp |
| `verification_method` | String | "platform_verification" or "ai_analysis" |

### Verification Statuses

| Status | Meaning | Points Awarded |
|--------|---------|----------------|
| `verified` | Trusted educational platform | 150 |
| `ai_verified` | AI confirmed educational | 100 |
| `pending` | Not checked | 50 |
| `rejected` | Non-educational | 0 (403 error) |

### Source Info Object

| Field | Type | Description |
|-------|------|-------------|
| `source_type` | String | "video_url", "video_file", "document_file", "web_url" |
| `source_identifier` | String | URL or filename |
| `title` | String/null | Extracted title |
| `duration` | Number/null | Duration in seconds (videos) |
| `transcript_length` | Number/null | Transcript character count |

---

## Integration Examples

### JavaScript/TypeScript

```typescript
async function generateQuiz(fileOrUrl: File | string): Promise<QuizResponse> {
  const formData = new FormData();

  if (typeof fileOrUrl === 'string') {
    formData.append('url', fileOrUrl);
  } else {
    formData.append('file', fileOrUrl);
  }

  const response = await fetch(
    'https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz',
    {
      method: 'POST',
      body: formData,
      // Recommended: 2 minute timeout
      signal: AbortSignal.timeout(120000)
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
}

// Usage
const quiz = await generateQuiz('https://example.com/article');
console.log(`Generated ${quiz.quiz.num_quiz_questions} questions`);
```

### Python

```python
import requests

def generate_quiz(file_path=None, url=None, video_url=None):
    """Generate a quiz from content"""
    api_url = "https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz"

    if file_path:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(api_url, files=files, timeout=120)
    elif url:
        data = {'url': url}
        response = requests.post(api_url, data=data, timeout=120)
    elif video_url:
        data = {'video_url': video_url}
        response = requests.post(api_url, data=data, timeout=120)
    else:
        raise ValueError("Must provide file_path, url, or video_url")

    response.raise_for_status()
    return response.json()

# Usage
quiz = generate_quiz(url="https://en.wikipedia.org/wiki/Python")
print(f"Generated {quiz['quiz']['num_quiz_questions']} questions")
```

### PHP

```php
<?php

function generateQuiz($url) {
    $apiUrl = 'https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz';

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $apiUrl);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, ['url' => $url]);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 120);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($httpCode !== 200) {
        throw new Exception("API request failed with code $httpCode");
    }

    return json_decode($response, true);
}

// Usage
$quiz = generateQuiz('https://example.com/article');
echo "Generated " . $quiz['quiz']['num_quiz_questions'] . " questions\n";
?>
```

### Java

```java
import java.net.http.*;
import java.net.URI;
import java.time.Duration;

public class QuizGenerator {
    private static final String API_URL =
        "https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz";

    public static String generateQuiz(String url) throws Exception {
        HttpClient client = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(120))
            .build();

        String boundary = "----Boundary" + System.currentTimeMillis();
        String formData = "--" + boundary + "\r\n" +
            "Content-Disposition: form-data; name=\"url\"\r\n\r\n" +
            url + "\r\n" +
            "--" + boundary + "--\r\n";

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(API_URL))
            .header("Content-Type", "multipart/form-data; boundary=" + boundary)
            .POST(HttpRequest.BodyPublishers.ofString(formData))
            .build();

        HttpResponse<String> response = client.send(request,
            HttpResponse.BodyHandlers.ofString());

        return response.body();
    }
}
```

---

## Error Handling

### Common Error Codes

| Code | Error | Possible Causes | Solution |
|------|-------|-----------------|----------|
| 400 | Bad Request | No file/URL provided, invalid format | Check request format |
| 403 | Forbidden | Content rejected as non-educational | Use educational content |
| 500 | Server Error | Processing failure, API issues | Retry or contact support |
| 504 | Timeout | Processing took too long | Use smaller files or retry |

### Error Response Structure

```json
{
  "success": false,
  "detail": "Error message or object"
}
```

### Handling Rejections

When content is rejected (403):

```javascript
try {
  const quiz = await generateQuiz(url);
} catch (error) {
  if (error.status === 403) {
    console.log('Content rejected:', error.detail.reason);
    console.log('Confidence:', error.detail.confidence + '%');
    // Show error to user, ask for different content
  }
}
```

---

## Best Practices

### 1. Set Appropriate Timeouts

Different content types take different amounts of time:

| Content Type | Typical Time | Recommended Timeout |
|--------------|--------------|---------------------|
| Small text file | 5-10s | 30s |
| PDF document | 15-30s | 60s |
| Web URL | 10-20s | 45s |
| YouTube video | 30-90s | 120s |
| Large video file | 60-120s | 120s |

**Note:** First request after inactivity may take +30s (server wake-up on free tier).

### 2. Handle File Size Limits

- **Documents:** < 10MB recommended
- **Videos:** < 500MB (configurable server-side)
- **Minimum content:** 50 characters
- **Recommended:** 200+ words for quality quizzes

### 3. Implement Retry Logic

```javascript
async function generateQuizWithRetry(url, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await generateQuiz(url);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      // Wait before retry (exponential backoff)
      await new Promise(r => setTimeout(r, Math.pow(2, i) * 1000));
    }
  }
}
```

### 4. Validate Content Type

Before sending to API:

```javascript
function isValidFileType(filename) {
  const validExtensions = [
    '.pdf', '.txt', '.doc', '.docx',
    '.mp4', '.avi', '.mov', '.mkv', '.webm'
  ];
  return validExtensions.some(ext => filename.toLowerCase().endsWith(ext));
}
```

### 5. Cache Results

Quiz generation is expensive. Cache results by content hash:

```javascript
const quizCache = new Map();

async function getCachedQuiz(url) {
  const cacheKey = btoa(url); // Simple hash

  if (quizCache.has(cacheKey)) {
    return quizCache.get(cacheKey);
  }

  const quiz = await generateQuiz(url);
  quizCache.set(cacheKey, quiz);
  return quiz;
}
```

### 6. Display Progress to Users

```javascript
async function generateQuizWithProgress(url, onProgress) {
  onProgress('Sending request...');
  const startTime = Date.now();

  const progressInterval = setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    onProgress(`Processing... (${elapsed}s)`);
  }, 1000);

  try {
    const quiz = await generateQuiz(url);
    clearInterval(progressInterval);
    onProgress('Complete!');
    return quiz;
  } catch (error) {
    clearInterval(progressInterval);
    throw error;
  }
}
```

---

## Testing

### Health Check

```bash
curl https://ai-quiz-generator-f8dr.onrender.com/health
# Expected: {"status": "healthy"}
```

### Test with Sample URL

```bash
curl -X POST https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz \
  -F "url=https://en.wikipedia.org/wiki/Photosynthesis" \
  | jq '.'
```

### Test Response Fields

```javascript
const quiz = await generateQuiz(testUrl);

// Validate required fields
assert(quiz.success === true);
assert(quiz.job_id);
assert(quiz.content.title);
assert(quiz.quiz.num_quiz_questions === 5);
assert(quiz.quiz.questions.length === 5);

// Validate question structure
quiz.quiz.questions.forEach(q => {
  assert(q.question);
  assert(q.num_answers === 5);
  assert(q.answers.length === 5);

  // Check exactly one correct answer
  const correctAnswers = q.answers.filter(a => a.weight === 2);
  assert(correctAnswers.length === 1);
});
```

### Performance Testing

```bash
# Test cold start (server sleeping)
time curl -X POST https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz \
  -F "url=https://example.com/article"
# Expected: 30-60 seconds on first call

# Test warm server
time curl -X POST https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz \
  -F "url=https://example.com/article"
# Expected: 10-20 seconds on subsequent calls
```

---

## TypeScript Type Definitions

```typescript
export type Answer = {
  answer: string;
  weight: 0 | 1 | 2; // 0 = incorrect, 1 = partially correct, 2 = correct
};

export type Question = {
  question: string;
  num_answers: number; // Always 5
  answers: Answer[];
};

export type ContentMetadata = {
  title: string;
  description: string;
  media_link: string;
  duration?: number; // in minutes
  suggested_categories: string[];
  suggested_media_type: "video" | "document" | "article" | "url";
  creator_name?: string;
  thumbnail_url?: string;
};

export type VerificationStatus = "verified" | "ai_verified" | "rejected" | "pending";

export type VerificationMetadata = {
  status: VerificationStatus;
  confidence_score?: number;
  platform?: string;
  rejection_reason?: string;
  verified_at: string; // ISO 8601
  verification_method: string;
};

export type SourceInfo = {
  source_type: "video_url" | "video_file" | "document_file" | "web_url";
  source_identifier: string;
  title?: string;
  duration?: number; // in seconds
  transcript_length?: number;
};

export type QuizResponse = {
  success: boolean;
  job_id: string;
  content: ContentMetadata;
  quiz: {
    num_quiz_questions: number; // Always 5
    questions: Question[];
  };
  verification?: VerificationMetadata;
  source_info?: SourceInfo;
  points_awarded?: number; // 50-150
  generated_at: string; // ISO 8601
};
```

---

## CORS Configuration

The API allows requests from:

- `http://localhost:3000` (development)
- `https://*.vercel.app` (Vercel deployments)
- Custom origins (via `FRONTEND_URL` env variable)

**Allowed Methods:** GET, POST, PUT, DELETE, OPTIONS
**Allowed Headers:** All

---

## Rate Limits

**Current:** No rate limits
**Future:** May implement limits based on:

- IP address
- Request frequency
- Resource consumption

---

## Support & Resources

- **API Documentation:** See `API_SPECIFICATION.md`
- **Health Endpoint:** `GET /health`
- **Issues:** https://github.com/shubh1996/ai-quiz-generator/issues
- **Backend Status:** Check Render dashboard

---

## Changelog

### v1.0 (January 2026)

- Initial release
- 5-question weighted MCQ format
- AI-powered content verification
- Points system (50-150 points)
- Content metadata generation
- Support for documents, URLs, and videos

---

## Known Limitations

1. **YouTube Videos:** May fail due to bot detection. Recommend file uploads instead.
2. **Free Tier:** Backend sleeps after 15 minutes of inactivity. First request takes ~30s.
3. **File Size:** Large files (>10MB) may cause timeouts or memory issues.
4. **Processing Time:** Complex content can take up to 2 minutes to process.

---

## Quick Reference

```bash
# Generate quiz from URL
curl -X POST https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz \
  -F "url=YOUR_URL_HERE"

# Generate quiz from file
curl -X POST https://ai-quiz-generator-f8dr.onrender.com/api/generate-quiz \
  -F "file=@/path/to/file.pdf"

# Check API health
curl https://ai-quiz-generator-f8dr.onrender.com/health
```

---

**Need help?** Contact the backend team or check the full API specification in `API_SPECIFICATION.md`.
