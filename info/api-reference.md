# AI Quiz Generation Microservice - API Reference

This document details all API endpoints for the AI Quiz Generation microservice integration.

---

## Base Configuration

| Setting        | Description               | Example                              |
| -------------- | ------------------------- | ------------------------------------ |
| Base URL       | Microservice API base URL | `https://quiz-ai.example.com/api/v1` |
| Authentication | API key in header         | `X-API-Key: your-api-key`            |
| Content-Type   | JSON for all requests     | `application/json`                   |

---

## Endpoints

### 1. Search Content

Search for content matches based on user-provided URL or title.

**Endpoint:** `POST /content/search`

#### Request Examples

**Example 1: Search by URL**

```json
{
    "query": "https://www.youtube.com/watch?v=abc123",
    "query_type": "url",
    "user_context": {
        "user_id": 42,
        "preferred_categories": [
            "Professional Development",
            "Classroom Management"
        ]
    }
}
```

**Example 2: Search by Title (with media type hint)**

When searching by title, the user should also indicate the media type to help narrow down results.

```json
{
    "query": "Culturally Responsive Teaching and the Brain",
    "query_type": "title",
    "media_type_hint": "book",
    "user_context": {
        "user_id": 42
    }
}
```

**Example 3: Search by Title (podcast)**

```json
{
    "query": "Cult of Pedagogy Episode 142",
    "query_type": "title",
    "media_type_hint": "podcast",
    "user_context": {
        "user_id": 88
    }
}
```

**Example 4: Search by Title (article)**

```json
{
    "query": "The Science of Learning: Research Meets Practice",
    "query_type": "title",
    "media_type_hint": "article",
    "user_context": {}
}
```

#### Request Fields

| Field                               | Type    | Required | Description                                                                                                 |
| ----------------------------------- | ------- | -------- | ----------------------------------------------------------------------------------------------------------- |
| `query`                             | string  | Yes      | The URL or title to search for                                                                              |
| `query_type`                        | enum    | Yes      | One of: `url`, `title`                                                                                      |
| `media_type_hint`                   | enum    | No\*     | One of: `video`, `article`, `podcast`, `book`, `course`, `webinar`. \*Required when `query_type` is `title` |
| `user_context`                      | object  | No       | Optional context to improve matching                                                                        |
| `user_context.user_id`              | integer | No       | Ippydippy user ID for personalization                                                                       |
| `user_context.preferred_categories` | array   | No       | User's preferred content categories                                                                         |

#### Response - Success (200)

```json
{
    "success": true,
    "matches": [
        {
            "match_id": "ext_abc123",
            "confidence": 0.95,
            "title": "Effective Classroom Management Strategies",
            "description": "Learn evidence-based strategies for managing your classroom effectively...",
            "source_url": "https://www.youtube.com/watch?v=abc123",
            "thumbnail_url": "https://i.ytimg.com/vi/abc123/hqdefault.jpg",
            "creator": "Education Weekly",
            "duration_minutes": 45,
            "media_type": "video",
            "metadata": {
                "platform": "youtube",
                "publish_date": "2024-03-15",
                "view_count": 125000,
                "language": "en"
            }
        },
        {
            "match_id": "ext_def456",
            "confidence": 0.72,
            "title": "Classroom Management for New Teachers",
            "description": "A beginner's guide to classroom management...",
            "source_url": "https://www.example.com/classroom-management",
            "thumbnail_url": null,
            "creator": "Teacher Resources",
            "duration_minutes": 30,
            "media_type": "article",
            "metadata": {
                "platform": "web",
                "publish_date": "2024-01-20",
                "word_count": 2500,
                "language": "en"
            }
        }
    ],
    "total_matches": 2,
    "search_id": "search_789xyz"
}
```

| Field                        | Type    | Description                                                       |
| ---------------------------- | ------- | ----------------------------------------------------------------- |
| `success`                    | boolean | Whether the search completed successfully                         |
| `matches`                    | array   | List of potential content matches                                 |
| `matches[].match_id`         | string  | Unique identifier for this match (use in quiz generation request) |
| `matches[].confidence`       | float   | Confidence score 0-1 for match relevance                          |
| `matches[].title`            | string  | Content title                                                     |
| `matches[].description`      | string  | Content description/summary                                       |
| `matches[].source_url`       | string  | Original content URL                                              |
| `matches[].thumbnail_url`    | string  | Optional thumbnail image URL                                      |
| `matches[].creator`          | string  | Content creator/author name                                       |
| `matches[].duration_minutes` | integer | Estimated content duration in minutes                             |
| `matches[].media_type`       | enum    | One of: `video`, `article`, `podcast`, `course`, `webinar`        |
| `matches[].metadata`         | object  | Platform-specific metadata                                        |
| `total_matches`              | integer | Total number of matches found                                     |
| `search_id`                  | string  | Search session ID for tracking                                    |

#### Response - No Matches (200)

```json
{
    "success": true,
    "matches": [],
    "total_matches": 0,
    "search_id": "search_789xyz",
    "message": "No matching content found. Please verify the URL or try a different search term."
}
```

#### Response - Error (4xx/5xx)

```json
{
    "success": false,
    "error": {
        "code": "INVALID_URL",
        "message": "The provided URL is not accessible or is not a valid content source.",
        "details": {
            "url": "https://invalid-url.example",
            "reason": "DNS resolution failed"
        }
    }
}
```

---

### 2. Request Quiz Generation

Initiate quiz generation for a selected content match.

**Endpoint:** `POST /quiz/generate`

#### Request

```json
{
    "match_id": "ext_abc123",
    "search_id": "search_789xyz",
    "quiz_config": {
        "num_questions": 5,
        "num_answers_per_question": 4,
        "difficulty": "medium",
        "question_types": ["multiple_choice"],
        "focus_areas": []
    },
    "callback_url": "https://ippydippy.example.com/api/webhooks/quiz-ready"
}
```

| Field                                  | Type    | Required | Description                                                |
| -------------------------------------- | ------- | -------- | ---------------------------------------------------------- |
| `match_id`                             | string  | Yes      | The match_id from search results                           |
| `search_id`                            | string  | Yes      | The search_id from the search response                     |
| `quiz_config`                          | object  | No       | Quiz generation configuration                              |
| `quiz_config.num_questions`            | integer | No       | Number of questions to generate (default: 5, max: 20)      |
| `quiz_config.num_answers_per_question` | integer | No       | Answers per question (default: 4, range: 3-6)              |
| `quiz_config.difficulty`               | enum    | No       | One of: `easy`, `medium`, `hard` (default: `medium`)       |
| `quiz_config.question_types`           | array   | No       | Question types to include (default: `["multiple_choice"]`) |
| `quiz_config.focus_areas`              | array   | No       | Specific topics to focus questions on                      |
| `callback_url`                         | string  | No       | Webhook URL for completion notification                    |

#### Response - Success (202 Accepted)

```json
{
    "success": true,
    "job_id": "job_qg_abc123def456",
    "status": "queued",
    "estimated_completion_seconds": 120,
    "status_url": "/quiz/status/job_qg_abc123def456",
    "created_at": "2024-12-15T10:30:00Z"
}
```

| Field                          | Type    | Description                              |
| ------------------------------ | ------- | ---------------------------------------- |
| `success`                      | boolean | Whether the job was accepted             |
| `job_id`                       | string  | Unique job identifier for status polling |
| `status`                       | enum    | Initial status: `queued`                 |
| `estimated_completion_seconds` | integer | Estimated time until completion          |
| `status_url`                   | string  | Relative URL for status polling          |
| `created_at`                   | string  | ISO 8601 timestamp of job creation       |

---

### 3. Check Job Status

Poll for quiz generation job status.

**Endpoint:** `GET /quiz/status/{job_id}`

#### Response - In Progress (200)

```json
{
    "success": true,
    "job_id": "job_qg_abc123def456",
    "status": "processing",
    "progress": {
        "percentage": 60,
        "current_step": "generating_questions",
        "steps_completed": ["content_analysis", "topic_extraction"],
        "steps_remaining": [
            "generating_questions",
            "answer_generation",
            "validation"
        ]
    },
    "estimated_remaining_seconds": 45,
    "updated_at": "2024-12-15T10:31:30Z"
}
```

| Field                         | Type    | Description                                           |
| ----------------------------- | ------- | ----------------------------------------------------- |
| `status`                      | enum    | One of: `queued`, `processing`, `completed`, `failed` |
| `progress.percentage`         | integer | Overall progress 0-100                                |
| `progress.current_step`       | string  | Current processing step                               |
| `progress.steps_completed`    | array   | List of completed steps                               |
| `progress.steps_remaining`    | array   | List of remaining steps                               |
| `estimated_remaining_seconds` | integer | Estimated time remaining                              |

#### Response - Completed (200)

```json
{
    "success": true,
    "job_id": "job_qg_abc123def456",
    "status": "completed",
    "progress": {
        "percentage": 100,
        "current_step": "complete",
        "steps_completed": [
            "content_analysis",
            "topic_extraction",
            "generating_questions",
            "answer_generation",
            "validation"
        ],
        "steps_remaining": []
    },
    "result_url": "/quiz/result/job_qg_abc123def456",
    "completed_at": "2024-12-15T10:32:00Z"
}
```

#### Response - Failed (200)

```json
{
    "success": true,
    "job_id": "job_qg_abc123def456",
    "status": "failed",
    "error": {
        "code": "CONTENT_INSUFFICIENT",
        "message": "The content does not have enough substance to generate meaningful quiz questions.",
        "recoverable": false
    },
    "failed_at": "2024-12-15T10:31:45Z"
}
```

---

### 4. Get Quiz Result

Retrieve the generated quiz payload.

**Endpoint:** `GET /quiz/result/{job_id}`

#### Response - Success (200)

See [Quiz Data Format](./quiz-data-format.md) for the complete quiz payload structure.

```json
{
    "success": true,
    "job_id": "job_qg_abc123def456",
    "content": {
        "title": "Effective Classroom Management Strategies",
        "description": "Learn evidence-based strategies for managing your classroom effectively. This comprehensive video covers proactive techniques, relationship building, and handling challenging behaviors.",
        "media_link": "https://www.youtube.com/watch?v=abc123",
        "duration": 45,
        "suggested_categories": [
            "Professional Development",
            "Classroom Management"
        ],
        "suggested_media_type": "video",
        "creator_name": "Education Weekly"
    },
    "quiz": {
        "num_quiz_questions": 5,
        "questions": [
            {
                "question": "According to the video, what is the FIRST step in establishing an effective classroom management system?",
                "num_answers": 4,
                "answers": [
                    {
                        "answer": "Building positive relationships with students",
                        "weight": 2
                    },
                    {
                        "answer": "Establishing clear rules and consequences",
                        "weight": 1
                    },
                    {
                        "answer": "Creating a seating chart",
                        "weight": 0
                    },
                    {
                        "answer": "Sending home a syllabus",
                        "weight": 0
                    }
                ]
            },
            {
                "question": "What does the presenter identify as a key indicator of proactive classroom management?",
                "num_answers": 4,
                "answers": [
                    {
                        "answer": "Preventing problems before they occur through preparation",
                        "weight": 2
                    },
                    {
                        "answer": "Having a strict discipline policy",
                        "weight": 0
                    },
                    {
                        "answer": "Relying on administrative support",
                        "weight": 0
                    },
                    {
                        "answer": "Using rewards-only systems",
                        "weight": 1
                    }
                ]
            }
        ]
    },
    "generated_at": "2024-12-15T10:32:00Z",
    "expires_at": "2024-12-16T10:32:00Z"
}
```

---

### 5. Webhook: Quiz Ready (Optional)

If a `callback_url` was provided, the microservice will POST to it when the quiz is ready.

**Endpoint:** `POST {callback_url}` (your webhook endpoint)

#### Webhook Payload

```json
{
    "event": "quiz.completed",
    "job_id": "job_qg_abc123def456",
    "status": "completed",
    "result_url": "https://quiz-ai.example.com/api/v1/quiz/result/job_qg_abc123def456",
    "timestamp": "2024-12-15T10:32:00Z",
    "signature": "sha256=abc123..."
}
```

| Field        | Type   | Description                                   |
| ------------ | ------ | --------------------------------------------- |
| `event`      | string | Event type: `quiz.completed` or `quiz.failed` |
| `job_id`     | string | The job identifier                            |
| `status`     | enum   | Final status: `completed` or `failed`         |
| `result_url` | string | Full URL to retrieve the quiz result          |
| `timestamp`  | string | ISO 8601 timestamp                            |
| `signature`  | string | HMAC signature for verification               |

---

## Error Codes Reference

| Code                   | HTTP Status | Description                                            |
| ---------------------- | ----------- | ------------------------------------------------------ |
| `INVALID_URL`          | 400         | The provided URL is invalid or inaccessible            |
| `UNSUPPORTED_PLATFORM` | 400         | The content platform is not supported                  |
| `INVALID_MATCH_ID`     | 400         | The match_id is invalid or expired                     |
| `SEARCH_EXPIRED`       | 400         | The search session has expired                         |
| `CONTENT_INSUFFICIENT` | 422         | Content lacks sufficient substance for quiz generation |
| `CONTENT_TOO_LONG`     | 422         | Content exceeds maximum processable length             |
| `RATE_LIMITED`         | 429         | Too many requests, please retry later                  |
| `JOB_NOT_FOUND`        | 404         | The job_id was not found                               |
| `JOB_EXPIRED`          | 410         | The job result has expired and been deleted            |
| `SERVICE_UNAVAILABLE`  | 503         | Service temporarily unavailable                        |
| `INTERNAL_ERROR`       | 500         | An unexpected error occurred                           |

---

## Rate Limits

| Endpoint                    | Limit        | Window     |
| --------------------------- | ------------ | ---------- |
| `POST /content/search`      | 60 requests  | per minute |
| `POST /quiz/generate`       | 10 requests  | per minute |
| `GET /quiz/status/{job_id}` | 120 requests | per minute |
| `GET /quiz/result/{job_id}` | 30 requests  | per minute |

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1702638000
```
