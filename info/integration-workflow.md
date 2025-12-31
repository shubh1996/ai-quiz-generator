# AI Quiz Generation - Integration Workflow Guide

**Audience:** External development team building the AI Quiz Generation microservice

This document describes the complete end-to-end workflow between the Ippydippy platform and your microservice. It covers all interaction scenarios with varied examples to help you understand how Ippydippy will consume your API.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Workflow Summary](#workflow-summary)
3. [Detailed Flow: URL-Based Content](#detailed-flow-url-based-content)
4. [Detailed Flow: Title-Based Content](#detailed-flow-title-based-content)
5. [Handling Edge Cases](#handling-edge-cases)
6. [Status Polling Patterns](#status-polling-patterns)
7. [Complete Example Scenarios](#complete-example-scenarios)

---

## System Overview

Ippydippy is a professional development platform for educators. Users earn credits by consuming educational content and passing quizzes. Your microservice will enable users to submit their own content (via URL or title) and have quizzes automatically generated.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                              USER JOURNEY                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1. User enters URL or title  ──►  2. Reviews content matches               │
│                                                                              │
│   3. Selects correct match     ──►  4. Waits for quiz generation             │
│                                                                              │
│   5. Quiz imported to Ippydippy ──► 6. User takes quiz & earns credit        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### What Ippydippy Handles

-   User authentication and authorization
-   Displaying search results to user for selection
-   Polling your service for job status
-   Importing completed quiz data into our database
-   Presenting the quiz to users and grading responses
-   Awarding credits upon quiz completion

### What Your Microservice Handles

-   Content discovery and matching (from URLs or titles)
-   Content analysis and summarization
-   AI-powered quiz question/answer generation
-   Job queue management and progress tracking
-   Storing generated quizzes until retrieved

---

## Workflow Summary

```text
PHASE 1: CONTENT DISCOVERY
═══════════════════════════════════════════════════════════════════════════════

    Ippydippy                          Your Service
        │                                   │
        │   POST /content/search            │
        │   {query, query_type, ...}        │
        │──────────────────────────────────►│
        │                                   │  ← Fetch content metadata
        │                                   │  ← Find potential matches
        │   {matches[], search_id}          │
        │◄──────────────────────────────────│
        │                                   │
        ▼                                   │
    [User reviews matches]                  │
    [User selects one]                      │
        │                                   │

PHASE 2: QUIZ GENERATION
═══════════════════════════════════════════════════════════════════════════════

        │   POST /quiz/generate             │
        │   {match_id, search_id, config}   │
        │──────────────────────────────────►│
        │                                   │  ← Queue job
        │   {job_id, status: "queued"}      │
        │◄──────────────────────────────────│
        │                                   │
        │                                   │  ← Analyze content
        │                                   │  ← Generate questions
        │                                   │  ← Create answers
        │                                   │  ← Validate quiz

PHASE 3: STATUS POLLING
═══════════════════════════════════════════════════════════════════════════════

        │   GET /quiz/status/{job_id}       │
        │──────────────────────────────────►│
        │   {status: "processing", ...}     │
        │◄──────────────────────────────────│
        │                                   │
        │   ... (repeat polling) ...        │
        │                                   │
        │   GET /quiz/status/{job_id}       │
        │──────────────────────────────────►│
        │   {status: "completed", ...}      │
        │◄──────────────────────────────────│
        │                                   │

PHASE 4: QUIZ RETRIEVAL
═══════════════════════════════════════════════════════════════════════════════

        │   GET /quiz/result/{job_id}       │
        │──────────────────────────────────►│
        │                                   │
        │   {content, quiz, questions...}   │
        │◄──────────────────────────────────│
        │                                   │
        ▼
    [Ippydippy imports quiz]
    [User can now take quiz]
```

---

## Detailed Flow: URL-Based Content

This is the most common flow. A user finds educational content online and wants to log it for credit.

### Step 1: User Submits URL

The user pastes a URL into Ippydippy's interface:

```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### Step 2: Ippydippy Calls Search

```json
POST /content/search

{
    "query": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "query_type": "url",
    "user_context": {
        "user_id": 142,
        "preferred_categories": ["Technology Integration", "Digital Literacy"]
    }
}
```

### Step 3: Your Service Returns Matches

Your service should:

1. Fetch metadata from the URL (title, description, duration, thumbnail)
2. Optionally search for related/similar content
3. Return one or more potential matches

```json
{
    "success": true,
    "matches": [
        {
            "match_id": "yt_dQw4w9WgXcQ",
            "confidence": 0.99,
            "title": "Using Technology to Engage Students",
            "description": "This video explores practical strategies for integrating technology into classroom instruction...",
            "source_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "creator": "EdTech Academy",
            "duration_minutes": 22,
            "media_type": "video",
            "metadata": {
                "platform": "youtube",
                "publish_date": "2024-06-15",
                "view_count": 45000
            }
        }
    ],
    "total_matches": 1,
    "search_id": "search_abc123"
}
```

**Note:** For direct URL submissions, there's typically only one match with high confidence. Multiple matches might occur if:

-   The URL redirects to different content
-   You find related/companion content worth suggesting
-   The URL is ambiguous (e.g., a playlist vs. single video)

### Step 4: User Confirms Selection

The user sees the match displayed in Ippydippy and confirms "Yes, this is the content I watched."

### Step 5: Ippydippy Requests Quiz Generation

```json
POST /quiz/generate

{
    "match_id": "yt_dQw4w9WgXcQ",
    "search_id": "search_abc123",
    "quiz_config": {
        "num_questions": 5,
        "num_answers_per_question": 4,
        "difficulty": "medium"
    }
}
```

### Step 6: Your Service Queues the Job

```json
{
    "success": true,
    "job_id": "job_xyz789",
    "status": "queued",
    "estimated_completion_seconds": 90,
    "created_at": "2024-12-15T14:30:00Z"
}
```

### Step 7: Ippydippy Polls for Status

We will poll at increasing intervals. Provide meaningful progress information:

```json
GET /quiz/status/job_xyz789

{
    "success": true,
    "job_id": "job_xyz789",
    "status": "processing",
    "progress": {
        "percentage": 40,
        "current_step": "topic_extraction",
        "steps_completed": ["content_analysis"],
        "steps_remaining": ["generating_questions", "answer_generation", "validation"]
    },
    "estimated_remaining_seconds": 55,
    "updated_at": "2024-12-15T14:30:35Z"
}
```

### Step 8: Job Completes

```json
GET /quiz/status/job_xyz789

{
    "success": true,
    "job_id": "job_xyz789",
    "status": "completed",
    "progress": {
        "percentage": 100,
        "current_step": "complete",
        "steps_completed": ["content_analysis", "topic_extraction", "generating_questions", "answer_generation", "validation"],
        "steps_remaining": []
    },
    "result_url": "/quiz/result/job_xyz789",
    "completed_at": "2024-12-15T14:31:30Z"
}
```

### Step 9: Ippydippy Retrieves the Quiz

```json
GET /quiz/result/job_xyz789

{
    "success": true,
    "job_id": "job_xyz789",
    "content": {
        "title": "Using Technology to Engage Students",
        "description": "This video explores practical strategies for integrating technology into classroom instruction, including interactive tools, assessment platforms, and collaboration software.",
        "media_link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "duration": 22,
        "suggested_categories": ["Technology Integration", "Student Engagement"],
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
                    {"answer": "Increases student engagement and provides real-time feedback to teachers", "weight": 2},
                    {"answer": "Reduces the need for homework assignments", "weight": 0},
                    {"answer": "Allows teachers to grade automatically", "weight": 1},
                    {"answer": "Makes lessons shorter", "weight": 0}
                ]
            },
            {
                "question": "Which strategy does the presenter recommend for introducing new technology tools?",
                "num_answers": 4,
                "answers": [
                    {"answer": "Start with one tool and master it before adding more", "weight": 2},
                    {"answer": "Introduce all tools at once so students can choose", "weight": 0},
                    {"answer": "Only use tools that students already know", "weight": 0},
                    {"answer": "Let students figure out tools on their own", "weight": 0}
                ]
            }
            // ... 3 more questions
        ]
    },
    "generated_at": "2024-12-15T14:31:30Z",
    "expires_at": "2024-12-16T14:31:30Z"
}
```

---

## Detailed Flow: Title-Based Content

Users may also want to log content they've consumed offline or from sources without direct URLs (books, in-person workshops, etc.).

### Step 1: User Enters Title and Media Type

The user types:

-   Title: "Culturally Responsive Teaching and the Brain"
-   Media Type: Book

### Step 2: Ippydippy Calls Search

```json
POST /content/search

{
    "query": "Culturally Responsive Teaching and the Brain",
    "query_type": "title",
    "media_type_hint": "book",
    "user_context": {
        "user_id": 88,
        "preferred_categories": ["Equity & Inclusion", "Neuroscience"]
    }
}
```

### Step 3: Your Service Returns Matches

For title searches, you may return multiple potential matches:

```json
{
    "success": true,
    "matches": [
        {
            "match_id": "book_isbn_9781483308012",
            "confidence": 0.97,
            "title": "Culturally Responsive Teaching and The Brain: Promoting Authentic Engagement and Rigor Among Culturally and Linguistically Diverse Students",
            "description": "A bold, brain-based teaching approach to culturally responsive instruction. The author draws on cutting-edge neuroscience research to offer an innovative approach for designing and implementing brain-compatible culturally responsive instruction.",
            "source_url": "https://www.amazon.com/dp/1483308014",
            "thumbnail_url": "https://images-na.ssl-images-amazon.com/images/I/51example.jpg",
            "creator": "Zaretta Hammond",
            "duration_minutes": 480,
            "media_type": "book",
            "metadata": {
                "platform": "book",
                "publish_date": "2014-11-13",
                "isbn": "978-1483308012",
                "page_count": 192
            }
        },
        {
            "match_id": "book_isbn_9781544374536",
            "confidence": 0.68,
            "title": "Culturally Responsive Teaching: Theory, Research, and Practice",
            "description": "A foundational text exploring the theoretical framework behind culturally responsive pedagogy...",
            "source_url": "https://www.amazon.com/dp/0807758760",
            "thumbnail_url": "https://images-na.ssl-images-amazon.com/images/I/41example.jpg",
            "creator": "Geneva Gay",
            "duration_minutes": 600,
            "media_type": "book",
            "metadata": {
                "platform": "book",
                "publish_date": "2018-03-01",
                "isbn": "978-0807758762",
                "page_count": 280
            }
        }
    ],
    "total_matches": 2,
    "search_id": "search_def456"
}
```

### Step 4: User Selects Correct Match

The user reviews both options and selects the first one (Zaretta Hammond's book).

### Step 5-9: Same as URL Flow

The quiz generation and retrieval process is identical from this point forward.

---

## Handling Edge Cases

### No Matches Found

When your service cannot find any matches:

```json
POST /content/search
{
    "query": "My School's Internal PD Session on Classroom Setup",
    "query_type": "title",
    "media_type_hint": "webinar"
}
```

Response:

```json
{
    "success": true,
    "matches": [],
    "total_matches": 0,
    "search_id": "search_nomatch_123",
    "message": "No matching content found. This may be internal or proprietary content that isn't publicly indexed."
}
```

**Ippydippy's behavior:** We will inform the user that this content cannot be processed for automatic quiz generation, and may offer alternative options (manual entry, etc.).

---

### Content Too Short/Simple

When content doesn't have enough substance for quiz generation:

```json
POST /quiz/generate
{
    "match_id": "article_short123",
    "search_id": "search_xyz"
}
```

Immediate rejection:

```json
{
    "success": false,
    "error": {
        "code": "CONTENT_INSUFFICIENT",
        "message": "This content is too brief to generate meaningful quiz questions. We recommend content that is at least 10 minutes of video/audio or 1000 words of text.",
        "details": {
            "content_length": "350 words",
            "minimum_required": "1000 words"
        }
    }
}
```

Or failure during processing:

```json
GET /quiz/status/job_failed123

{
    "success": true,
    "job_id": "job_failed123",
    "status": "failed",
    "error": {
        "code": "CONTENT_INSUFFICIENT",
        "message": "Unable to generate quality quiz questions from this content. The material lacks sufficient depth or distinct concepts.",
        "recoverable": false
    },
    "failed_at": "2024-12-15T14:35:00Z"
}
```

---

### URL Inaccessible

When your service cannot access the provided URL:

```json
POST /content/search
{
    "query": "https://private-school-portal.edu/internal-pd/session-42",
    "query_type": "url"
}
```

Response:

```json
{
    "success": false,
    "error": {
        "code": "INVALID_URL",
        "message": "Unable to access this URL. It may require authentication or be restricted.",
        "details": {
            "url": "https://private-school-portal.edu/internal-pd/session-42",
            "reason": "HTTP 403 Forbidden"
        }
    }
}
```

---

### Unsupported Platform

When the URL is from a platform you don't support:

```json
{
    "success": false,
    "error": {
        "code": "UNSUPPORTED_PLATFORM",
        "message": "Content from this platform is not currently supported.",
        "details": {
            "platform": "private-lms.example.com",
            "supported_platforms": [
                "youtube.com",
                "vimeo.com",
                "coursera.org",
                "edx.org",
                "ted.com"
            ]
        }
    }
}
```

---

### Job Expired

Quiz results should be retrievable for at least 24 hours. After expiration:

```json
GET /quiz/result/job_old123

{
    "success": false,
    "error": {
        "code": "JOB_EXPIRED",
        "message": "This quiz generation result has expired and is no longer available. Please submit a new request.",
        "details": {
            "job_id": "job_old123",
            "expired_at": "2024-12-14T14:31:30Z"
        }
    }
}
```

---

## Status Polling Patterns

### Expected Polling Behavior from Ippydippy

We will poll your status endpoint with **exponential backoff**:

| Poll # | Delay After  | Cumulative Time |
| ------ | ------------ | --------------- |
| 1      | 1 second     | 1s              |
| 2      | 1.5 seconds  | 2.5s            |
| 3      | 2.25 seconds | 4.75s           |
| 4      | 3.4 seconds  | 8.15s           |
| 5      | 5 seconds    | 13.15s          |
| 6+     | 5-10 seconds | varies          |

**Maximum polling duration:** 10 minutes. If a job hasn't completed by then, we'll show an error to the user.

### Progress Step Labels

We will display progress steps to users. Please use these consistent step identifiers:

| Step ID                | User-Friendly Display          |
| ---------------------- | ------------------------------ |
| `content_analysis`     | "Analyzing content..."         |
| `topic_extraction`     | "Identifying key topics..."    |
| `generating_questions` | "Generating quiz questions..." |
| `answer_generation`    | "Creating answer choices..."   |
| `validation`           | "Validating quiz quality..."   |
| `complete`             | "Complete!"                    |

You may add additional steps, but include these core steps for consistency.

---

## Complete Example Scenarios

### Scenario A: Teacher Logs a YouTube Video

**Context:** A 4th-grade teacher watched a 15-minute YouTube video about differentiated instruction and wants to earn PD credit.

**Search Request:**

```json
{
    "query": "https://www.youtube.com/watch?v=E9XhZ8bKMEI",
    "query_type": "url",
    "user_context": {
        "user_id": 234,
        "preferred_categories": [
            "Differentiated Instruction",
            "Elementary Education"
        ]
    }
}
```

**Search Response:**

```json
{
    "success": true,
    "matches": [
        {
            "match_id": "yt_E9XhZ8bKMEI",
            "confidence": 0.99,
            "title": "Differentiated Instruction: Why, What, and How",
            "description": "Carol Ann Tomlinson explains the key principles of differentiated instruction and provides practical classroom examples.",
            "source_url": "https://www.youtube.com/watch?v=E9XhZ8bKMEI",
            "thumbnail_url": "https://i.ytimg.com/vi/E9XhZ8bKMEI/hqdefault.jpg",
            "creator": "ASCD",
            "duration_minutes": 15,
            "media_type": "video",
            "metadata": {
                "platform": "youtube",
                "publish_date": "2019-04-22"
            }
        }
    ],
    "total_matches": 1,
    "search_id": "search_teacher_001"
}
```

**Quiz Generation Request:**

```json
{
    "match_id": "yt_E9XhZ8bKMEI",
    "search_id": "search_teacher_001",
    "quiz_config": {
        "num_questions": 5,
        "difficulty": "medium"
    }
}
```

**Final Quiz Result (abbreviated):**

```json
{
    "success": true,
    "job_id": "job_teacher_001",
    "content": {
        "title": "Differentiated Instruction: Why, What, and How",
        "description": "Carol Ann Tomlinson explains the key principles of differentiated instruction and provides practical classroom examples for reaching all learners.",
        "media_link": "https://www.youtube.com/watch?v=E9XhZ8bKMEI",
        "duration": 15,
        "suggested_categories": [
            "Differentiated Instruction",
            "Teaching Strategies"
        ],
        "suggested_media_type": "video",
        "creator_name": "ASCD"
    },
    "quiz": {
        "num_quiz_questions": 5,
        "questions": [
            {
                "question": "According to Tomlinson, what is the primary goal of differentiated instruction?",
                "num_answers": 4,
                "answers": [
                    {
                        "answer": "Maximizing each student's growth by meeting them where they are",
                        "weight": 2
                    },
                    {
                        "answer": "Ensuring all students complete the same work",
                        "weight": 0
                    },
                    {
                        "answer": "Reducing teacher workload through group activities",
                        "weight": 0
                    },
                    {
                        "answer": "Preparing students for standardized tests",
                        "weight": 1
                    }
                ]
            }
            // ... more questions
        ]
    }
}
```

---

### Scenario B: Administrator Logs a Professional Book

**Context:** A school administrator read a book over winter break and wants to log it for their license renewal.

**Search Request:**

```json
{
    "query": "The First Days of School Harry Wong",
    "query_type": "title",
    "media_type_hint": "book",
    "user_context": {
        "user_id": 567,
        "preferred_categories": ["School Leadership", "New Teacher Support"]
    }
}
```

**Search Response:**

```json
{
    "success": true,
    "matches": [
        {
            "match_id": "book_978_0976423317",
            "confidence": 0.96,
            "title": "The First Days of School: How to Be an Effective Teacher",
            "description": "The bestselling book for teachers, covering classroom management, lesson planning, and creating a positive learning environment. Used by millions of educators worldwide.",
            "source_url": "https://www.effectiveteaching.com/first-days",
            "thumbnail_url": "https://example.com/first-days-cover.jpg",
            "creator": "Harry K. Wong, Rosemary T. Wong",
            "duration_minutes": 720,
            "media_type": "book",
            "metadata": {
                "platform": "book",
                "isbn": "978-0976423317",
                "page_count": 352,
                "publish_date": "2018-01-01"
            }
        },
        {
            "match_id": "book_978_0962936026",
            "confidence": 0.72,
            "title": "The First Days of School (Original Edition)",
            "description": "The original 1991 edition of this classic teaching resource.",
            "source_url": "https://www.amazon.com/dp/0962936006",
            "thumbnail_url": null,
            "creator": "Harry K. Wong",
            "duration_minutes": 600,
            "media_type": "book",
            "metadata": {
                "platform": "book",
                "isbn": "978-0962936029",
                "page_count": 288,
                "publish_date": "1991-01-01"
            }
        }
    ],
    "total_matches": 2,
    "search_id": "search_admin_001"
}
```

**User selects first match** (the newer edition they actually read).

**Quiz Generation Request:**

```json
{
    "match_id": "book_978_0976423317",
    "search_id": "search_admin_001",
    "quiz_config": {
        "num_questions": 8,
        "difficulty": "medium"
    }
}
```

---

### Scenario C: Podcast Episode

**Context:** A teacher listened to an education podcast during their commute.

**Search Request:**

```json
{
    "query": "Cult of Pedagogy Episode 64 - Total Participation Techniques",
    "query_type": "title",
    "media_type_hint": "podcast",
    "user_context": {
        "user_id": 891
    }
}
```

**Search Response:**

```json
{
    "success": true,
    "matches": [
        {
            "match_id": "podcast_cop_064",
            "confidence": 0.94,
            "title": "Total Participation Techniques",
            "description": "Jennifer Gonzalez interviews Pérsida Himmele and William Himmele about their book Total Participation Techniques, exploring strategies to engage every student in learning.",
            "source_url": "https://www.cultofpedagogy.com/episode-64/",
            "thumbnail_url": "https://www.cultofpedagogy.com/wp-content/uploads/podcast-logo.png",
            "creator": "Cult of Pedagogy / Jennifer Gonzalez",
            "duration_minutes": 42,
            "media_type": "podcast",
            "metadata": {
                "platform": "podcast",
                "publish_date": "2017-05-14",
                "episode_number": 64,
                "series": "Cult of Pedagogy Podcast"
            }
        }
    ],
    "total_matches": 1,
    "search_id": "search_podcast_001"
}
```

---

### Scenario D: Article from Education Website

**Context:** A teacher read an article from Edutopia.

**Search Request:**

```json
{
    "query": "https://www.edutopia.org/article/power-student-choice",
    "query_type": "url",
    "user_context": {
        "user_id": 445
    }
}
```

**Search Response:**

```json
{
    "success": true,
    "matches": [
        {
            "match_id": "article_edutopia_12345",
            "confidence": 0.99,
            "title": "The Power of Student Choice",
            "description": "Research shows that giving students choices in their learning increases motivation and engagement. Here's how to implement choice effectively.",
            "source_url": "https://www.edutopia.org/article/power-student-choice",
            "thumbnail_url": "https://www.edutopia.org/sites/default/files/example.jpg",
            "creator": "Edutopia Staff",
            "duration_minutes": 8,
            "media_type": "article",
            "metadata": {
                "platform": "edutopia",
                "publish_date": "2024-09-10",
                "word_count": 1200
            }
        }
    ],
    "total_matches": 1,
    "search_id": "search_article_001"
}
```

---

### Scenario E: Failed Generation - Content Too Short

**Context:** A user tries to log a very short blog post.

**Search succeeds:**

```json
{
    "success": true,
    "matches": [
        {
            "match_id": "article_short_001",
            "confidence": 0.95,
            "title": "Quick Tip: Exit Tickets",
            "description": "A brief overview of exit tickets.",
            "source_url": "https://blog.example.com/exit-tickets",
            "creator": "Teaching Tips Blog",
            "duration_minutes": 2,
            "media_type": "article",
            "metadata": {
                "word_count": 250
            }
        }
    ],
    "total_matches": 1,
    "search_id": "search_short_001"
}
```

**Generation fails:**

```json
POST /quiz/generate
{
    "match_id": "article_short_001",
    "search_id": "search_short_001"
}

Response:
{
    "success": false,
    "error": {
        "code": "CONTENT_INSUFFICIENT",
        "message": "This content is too brief to generate meaningful quiz questions. We recommend content that is at least 10 minutes of video/audio or 1000 words of text.",
        "details": {
            "content_length": "250 words",
            "minimum_required": "1000 words"
        }
    }
}
```

---

## Questions?

If you have questions about this integration workflow or need clarification on any scenarios, please reach out to the Ippydippy development team.

Key contacts:

-   API questions: [TBD]
-   Quiz format questions: See [quiz-data-format.md](./quiz-data-format.md)
-   API endpoint details: See [api-reference.md](./api-reference.md)
