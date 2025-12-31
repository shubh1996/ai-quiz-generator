# Quiz Data Format - Ippydippy Integration

This document details the exact quiz payload format required by Ippydippy, based on the existing database schema and model relationships.

---

## Database Schema Overview

### Content Table

| Column               | Type       | Description                                               |
| -------------------- | ---------- | --------------------------------------------------------- |
| `id`                 | bigint     | Primary key                                               |
| `title`              | string     | Content title                                             |
| `description`        | mediumtext | Content description (nullable)                            |
| `media_link`         | mediumtext | URL to the content (nullable)                             |
| `duration`           | integer    | Duration in **minutes** (nullable)                        |
| `image_s3_id`        | string     | S3 key for thumbnail image (nullable)                     |
| `num_quiz_questions` | integer    | Number of questions to show per quiz attempt (default: 5) |
| `curator_id`         | bigint     | FK to users table (nullable)                              |
| `creator_id`         | bigint     | FK to creators table (nullable)                           |
| `media_type_id`      | bigint     | FK to media_types table (nullable)                        |
| `is_private`         | boolean    | Whether content is private to a group                     |

### Quiz Questions Table

| Column        | Type       | Description                               |
| ------------- | ---------- | ----------------------------------------- |
| `id`          | bigint     | Primary key                               |
| `question`    | mediumtext | The question text                         |
| `num_answers` | tinyint    | Number of answers to display (default: 4) |
| `content_id`  | bigint     | FK to contents table                      |
| `created_at`  | timestamp  | Creation timestamp                        |
| `updated_at`  | timestamp  | Update timestamp                          |
| `deleted_at`  | timestamp  | Soft delete timestamp                     |

### Quiz Answers Table

| Column             | Type      | Description                            |
| ------------------ | --------- | -------------------------------------- |
| `id`               | bigint    | Primary key                            |
| `answer`           | tinytext  | The answer text                        |
| `weight`           | integer   | Answer weight for scoring (default: 0) |
| `quiz_question_id` | bigint    | FK to quiz_questions table             |
| `deleted_at`       | timestamp | Soft delete timestamp                  |

---

## Weight Scoring System

Ippydippy uses a **weight-based scoring system** rather than simple correct/incorrect:

| Weight | Meaning           | Description                       |
| ------ | ----------------- | --------------------------------- |
| `0`    | Incorrect         | Wrong answer, no credit           |
| `1`    | Partially Correct | Acceptable answer, partial credit |
| `2`    | Correct           | Best/ideal answer, full credit    |

### Scoring Calculation

```text
User Score = (Sum of Selected Answer Weights) / (Sum of Max Available Weights per Question) × 100
```

**Example:**

-   Question 1: User selected answer with weight 2, max available was 2 → 2/2
-   Question 2: User selected answer with weight 1, max available was 2 → 1/2
-   Question 3: User selected answer with weight 0, max available was 2 → 0/2

Total: (2 + 1 + 0) / (2 + 2 + 2) = 3/6 = 50%

### Passing Score

The default passing score is **80%** (configurable via `PASSING_SCORE` environment variable).

---

## Microservice Response Format

The AI Quiz Generation microservice should return quiz data in this exact format:

### Complete Quiz Payload Structure

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
        "creator_name": "Education Weekly",
        "thumbnail_url": "https://i.ytimg.com/vi/abc123/hqdefault.jpg"
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
            },
            {
                "question": "Which strategy does the video recommend for handling minor disruptions?",
                "num_answers": 4,
                "answers": [
                    {
                        "answer": "Use proximity and non-verbal cues before verbal intervention",
                        "weight": 2
                    },
                    {
                        "answer": "Immediately send the student to the office",
                        "weight": 0
                    },
                    {
                        "answer": "Ignore all minor disruptions completely",
                        "weight": 0
                    },
                    {
                        "answer": "Stop instruction to address every incident",
                        "weight": 0
                    }
                ]
            },
            {
                "question": "According to the presenter, how often should classroom expectations be reviewed with students?",
                "num_answers": 4,
                "answers": [
                    {
                        "answer": "Regularly throughout the year, not just at the beginning",
                        "weight": 2
                    },
                    {
                        "answer": "Only on the first day of school",
                        "weight": 0
                    },
                    {
                        "answer": "Only when problems arise",
                        "weight": 1
                    },
                    {
                        "answer": "Never - students should already know how to behave",
                        "weight": 0
                    }
                ]
            },
            {
                "question": "What does the video suggest is the most effective way to build rapport with challenging students?",
                "num_answers": 4,
                "answers": [
                    {
                        "answer": "Finding their interests and making genuine personal connections",
                        "weight": 2
                    },
                    {
                        "answer": "Offering extra privileges and rewards",
                        "weight": 0
                    },
                    {
                        "answer": "Lowering academic expectations",
                        "weight": 0
                    },
                    {
                        "answer": "Providing positive feedback on academic work",
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

## Field Specifications

### Content Object

| Field                  | Type    | Required | Maps To                       | Description                   |
| ---------------------- | ------- | -------- | ----------------------------- | ----------------------------- |
| `title`                | string  | Yes      | `contents.title`              | Content title (max 255 chars) |
| `description`          | string  | Yes      | `contents.description`        | Content description           |
| `media_link`           | string  | Yes      | `contents.media_link`         | Original content URL          |
| `duration`             | integer | Yes      | `contents.duration`           | Duration in **minutes**       |
| `suggested_categories` | array   | No       | Lookup → `content_categories` | Category labels for matching  |
| `suggested_media_type` | string  | No       | Lookup → `media_types.label`  | Media type for matching       |
| `creator_name`         | string  | No       | Lookup → `creators.name`      | Creator/author name           |
| `thumbnail_url`        | string  | No       | _Download to S3_              | Thumbnail image URL           |

### Quiz Object

| Field                | Type    | Required | Maps To                       | Description                  |
| -------------------- | ------- | -------- | ----------------------------- | ---------------------------- |
| `num_quiz_questions` | integer | Yes      | `contents.num_quiz_questions` | Questions per attempt (3-20) |
| `questions`          | array   | Yes      | `quiz_questions`              | Array of question objects    |

### Question Object

| Field         | Type    | Required | Maps To                      | Description                     |
| ------------- | ------- | -------- | ---------------------------- | ------------------------------- |
| `question`    | string  | Yes      | `quiz_questions.question`    | The question text               |
| `num_answers` | integer | Yes      | `quiz_questions.num_answers` | Number of answers to show (3-6) |
| `answers`     | array   | Yes      | `quiz_answers`               | Array of answer objects         |

### Answer Object

| Field    | Type    | Required | Maps To               | Description                     |
| -------- | ------- | -------- | --------------------- | ------------------------------- |
| `answer` | string  | Yes      | `quiz_answers.answer` | The answer text (max 255 chars) |
| `weight` | integer | Yes      | `quiz_answers.weight` | Weight for scoring: 0, 1, or 2  |

---

## Validation Rules

### Content Validation

-   `title`: Required, max 255 characters
-   `description`: Required, max 16MB (mediumtext)
-   `media_link`: Required, valid URL format, max 16MB
-   `duration`: Required, positive integer (minutes)
-   `num_quiz_questions`: Required, range 3-20

### Question Validation

-   `question`: Required, max 16MB (mediumtext), should end with `?`
-   `num_answers`: Required, range 3-6
-   `answers`: Required, must have at least `num_answers` items

### Answer Validation

-   `answer`: Required, max 255 characters
-   `weight`: Required, must be 0, 1, or 2

### Quiz Integrity Rules

1. **At least one correct answer**: Each question MUST have at least one answer with `weight > 0`
2. **Exactly one best answer recommended**: Each question SHOULD have exactly one answer with `weight = 2`
3. **Answer count**: `answers` array should contain at least `num_answers` items
4. **Question count**: `questions` array should contain at least `num_quiz_questions` items
5. **Unique answers**: Answers within a question should be distinct

---

## Example: Minimal Valid Quiz

The minimum viable quiz payload:

```json
{
    "success": true,
    "job_id": "job_min_123",
    "content": {
        "title": "Introduction to Topic X",
        "description": "A brief introduction to Topic X.",
        "media_link": "https://example.com/video",
        "duration": 10
    },
    "quiz": {
        "num_quiz_questions": 3,
        "questions": [
            {
                "question": "What is the main point of Topic X?",
                "num_answers": 3,
                "answers": [
                    { "answer": "The correct answer", "weight": 2 },
                    { "answer": "A partially correct answer", "weight": 1 },
                    { "answer": "An incorrect answer", "weight": 0 }
                ]
            },
            {
                "question": "Which statement about Topic X is TRUE?",
                "num_answers": 3,
                "answers": [
                    { "answer": "This is true", "weight": 2 },
                    { "answer": "This is false", "weight": 0 },
                    { "answer": "This is also false", "weight": 0 }
                ]
            },
            {
                "question": "How should Topic X be applied?",
                "num_answers": 3,
                "answers": [
                    { "answer": "The best approach", "weight": 2 },
                    { "answer": "An acceptable approach", "weight": 1 },
                    { "answer": "A poor approach", "weight": 0 }
                ]
            }
        ]
    },
    "generated_at": "2024-12-15T10:32:00Z",
    "expires_at": "2024-12-16T10:32:00Z"
}
```

---

## Category Matching

The `suggested_categories` field should contain category labels. Ippydippy will attempt to match these to existing categories in the `content_categories` table.

**Current category examples:**

-   Professional Development
-   Classroom Management
-   Special Education
-   Technology Integration
-   Assessment & Data
-   Social-Emotional Learning
-   Curriculum & Instruction

If no match is found, the categories will be ignored (content can be saved without categories).

---

## Media Type Matching

The `suggested_media_type` field should be one of the standard media type labels:

| Label     | Description                          |
| --------- | ------------------------------------ |
| `video`   | Video content (YouTube, Vimeo, etc.) |
| `article` | Written articles, blog posts         |
| `podcast` | Audio podcast episodes               |
| `course`  | Structured online courses            |
| `webinar` | Live or recorded webinars            |
| `book`    | Books or book chapters               |
| `other`   | Other content types                  |

---

## Import Process

When Ippydippy imports a quiz from the microservice, it will:

1. **Create or match Creator**: Look up by `creator_name`, create if not exists
2. **Create or match MediaType**: Look up by `suggested_media_type`, use default if not found
3. **Create Content record**: With all content fields
4. **Match Categories**: Link to matching `content_categories`
5. **Create QuizQuestions**: For each question in the payload
6. **Create QuizAnswers**: For each answer in each question
7. **Optionally download thumbnail**: If `thumbnail_url` provided, download and upload to S3
