# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                        │
│                     http://localhost:3000                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Requests
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (React)                 │
│  ┌────────────┐  ┌────────────┐  ┌─────────────┐          │
│  │  Upload    │  │   Quiz     │  │   Results   │          │
│  │   Step     │→ │   Step     │→ │    Step     │          │
│  └────────────┘  └────────────┘  └─────────────┘          │
│                                                             │
│  State Management: React useState                          │
│  Styling: Tailwind CSS                                     │
│  Type Safety: TypeScript                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ POST /api/generate-quiz
                              │ (FormData: file or url)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Python)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              main.py (API Routes)                    │  │
│  │  - POST /api/generate-quiz                           │  │
│  │  - GET /health                                       │  │
│  │  - CORS Middleware                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│                         ▼                                   │
│  ┌────────────────────────────────┐                        │
│  │   Document Processor Service   │                        │
│  │  - process_file()              │                        │
│  │  - process_url()               │                        │
│  │  - extract_from_pdf()          │                        │
│  │  - extract_from_docx()         │                        │
│  └────────────────────────────────┘                        │
│                         │                                   │
│                         │ Extracted Text                    │
│                         ▼                                   │
│  ┌────────────────────────────────┐                        │
│  │   Quiz Generator Service       │                        │
│  │  - generate_quiz()             │                        │
│  │  - create_prompt()             │                        │
│  │  - generate_demo_quiz()        │                        │
│  └────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ API Request
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Perplexity AI API                        │
│  Model: llama-3.1-sonar-small-128k-online                  │
│  Input: Content + Prompt                                   │
│  Output: 5 MCQ Questions (JSON)                            │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────┐
│   User   │
└─────┬────┘
      │
      │ 1. Upload File/URL
      ▼
┌──────────────────┐
│  UploadStep.tsx  │
└─────┬────────────┘
      │
      │ 2. FormData with file/url
      ▼
┌──────────────────────────┐
│  POST /api/generate-quiz │
└─────┬────────────────────┘
      │
      │ 3. Extract text content
      ▼
┌────────────────────────┐
│  DocumentProcessor     │
│  - PDF Reader          │
│  - DOCX Reader         │
│  - URL Scraper         │
└─────┬──────────────────┘
      │
      │ 4. Text content
      ▼
┌────────────────────────┐
│  QuizGenerator         │
│  - Build prompt        │
│  - Call AI API         │
│  - Parse response      │
└─────┬──────────────────┘
      │
      │ 5. AI request with prompt
      ▼
┌────────────────────────┐
│  Perplexity AI         │
│  - Generate questions  │
│  - Return JSON         │
└─────┬──────────────────┘
      │
      │ 6. Quiz JSON
      ▼
┌────────────────────────┐
│  QuizResponse Model    │
│  - Validate structure  │
│  - Type checking       │
└─────┬──────────────────┘
      │
      │ 7. Return to frontend
      ▼
┌────────────────────────┐
│  page.tsx (State)      │
│  - Store quiz data     │
│  - Change to quiz step │
└─────┬──────────────────┘
      │
      │ 8. Render quiz
      ▼
┌────────────────────────┐
│  QuizStep.tsx          │
│  - Display questions   │
│  - Track answers       │
│  - Submit quiz         │
└─────┬──────────────────┘
      │
      │ 9. Calculate score
      ▼
┌────────────────────────┐
│  ResultsStep.tsx       │
│  - Show score          │
│  - Show pass/fail      │
│  - Restart option      │
└────────────────────────┘
```

## Component Architecture (Frontend)

```
app/
├── layout.tsx                    # Root layout with global styles
│   └── Provides: HTML structure, global CSS
│
└── page.tsx                      # Main app component
    ├── State:
    │   ├── currentStep: 'upload' | 'quiz' | 'results'
    │   ├── quizData: QuizData | null
    │   └── score: number
    │
    ├── Conditional Rendering:
    │   ├── UploadStep
    │   │   ├── Props: onQuizGenerated
    │   │   ├── State: uploadType, file, url, loading, error
    │   │   └── API: POST /api/generate-quiz
    │   │
    │   ├── QuizStep
    │   │   ├── Props: quizData, onSubmit
    │   │   ├── State: currentQuestion, selectedAnswers
    │   │   └── Logic: Answer tracking, score calculation
    │   │
    │   └── ResultsStep
    │       ├── Props: score, totalQuestions, onRestart
    │       └── Display: Pass/fail status, score
    │
    └── Types:
        ├── Question: { id, question, options, correctAnswer }
        └── QuizData: { questions: Question[] }
```

## Service Architecture (Backend)

```
backend/
├── main.py
│   ├── FastAPI app initialization
│   ├── CORS middleware configuration
│   ├── Route handlers:
│   │   ├── POST /api/generate-quiz
│   │   └── GET /health
│   └── Dependencies:
│       ├── DocumentProcessor instance
│       └── QuizGenerator instance
│
├── services/
│   ├── document_processor.py
│   │   ├── process_file(file: UploadFile) → str
│   │   ├── process_url(url: str) → str
│   │   ├── _extract_from_pdf(content: bytes) → str
│   │   └── _extract_from_docx(content: bytes) → str
│   │
│   └── quiz_generator.py
│       ├── generate_quiz(content: str) → QuizResponse
│       ├── _create_prompt(content: str) → str
│       └── _generate_demo_quiz(content: str) → QuizResponse
│
└── models/
    └── quiz.py
        ├── Question(BaseModel)
        │   ├── id: int
        │   ├── question: str
        │   ├── options: List[str]
        │   └── correctAnswer: int
        │
        └── QuizResponse(BaseModel)
            └── questions: List[Question]
```

## Technology Stack Details

### Frontend Stack
```
┌─────────────────────┐
│      React 19       │  UI Library
├─────────────────────┤
│     Next.js 16      │  Framework (App Router)
├─────────────────────┤
│    TypeScript       │  Type Safety
├─────────────────────┤
│   Tailwind CSS      │  Styling
├─────────────────────┤
│       Axios         │  HTTP Client
└─────────────────────┘
```

### Backend Stack
```
┌─────────────────────┐
│     Python 3.14     │  Programming Language
├─────────────────────┤
│      FastAPI        │  Web Framework
├─────────────────────┤
│      Uvicorn        │  ASGI Server
├─────────────────────┤
│     Pydantic        │  Data Validation
├─────────────────────┤
│  Document Libs      │  PyPDF2, python-docx
├─────────────────────┤
│  BeautifulSoup4     │  HTML Parsing
└─────────────────────┘
```

## API Contract

### Request/Response Flow

**Upload Document:**
```
Client → Server
POST /api/generate-quiz
Content-Type: multipart/form-data

{
  file: <binary data>
}

Server → Client
200 OK
Content-Type: application/json

{
  "questions": [
    {
      "id": 1,
      "question": "What is...?",
      "options": ["A", "B", "C", "D"],
      "correctAnswer": 0
    },
    // ... 4 more questions
  ]
}
```

**Upload URL:**
```
Client → Server
POST /api/generate-quiz
Content-Type: multipart/form-data

{
  url: "https://example.com/article"
}

Server → Client
200 OK
Content-Type: application/json

{
  "questions": [ ... ]
}
```

## Security Architecture

```
┌─────────────────────────────────────────┐
│            Security Layers              │
├─────────────────────────────────────────┤
│  1. CORS                                │
│     - Whitelist: localhost:3000         │
│     - Allow credentials                 │
├─────────────────────────────────────────┤
│  2. Input Validation                    │
│     - File type checking                │
│     - URL format validation             │
│     - Content length limits             │
├─────────────────────────────────────────┤
│  3. API Key Protection                  │
│     - Environment variables             │
│     - Never exposed to client           │
├─────────────────────────────────────────┤
│  4. Error Handling                      │
│     - Generic error messages            │
│     - No stack traces to client         │
├─────────────────────────────────────────┤
│  5. Type Safety                         │
│     - Pydantic models (backend)         │
│     - TypeScript (frontend)             │
└─────────────────────────────────────────┘
```

## Deployment Architecture (Future)

```
┌─────────────────────────────────────────┐
│            Production Setup             │
├─────────────────────────────────────────┤
│  Frontend: Vercel                       │
│  - Next.js optimized                    │
│  - Edge functions                       │
│  - CDN distribution                     │
├─────────────────────────────────────────┤
│  Backend: Railway/Render/AWS            │
│  - Docker container                     │
│  - Auto-scaling                         │
│  - Health checks                        │
├─────────────────────────────────────────┤
│  Database: PostgreSQL (Future)          │
│  - Managed service                      │
│  - Automated backups                    │
│  - Connection pooling                   │
├─────────────────────────────────────────┤
│  Monitoring: Sentry + Analytics         │
│  - Error tracking                       │
│  - Performance monitoring               │
│  - User analytics                       │
└─────────────────────────────────────────┘
```

## File Processing Pipeline

```
Upload File
    │
    ▼
Validate File Type
    │
    ├─ PDF ──→ PyPDF2.PdfReader ──→ Extract Text
    │
    ├─ DOCX ─→ python-docx.Document ─→ Extract Text
    │
    └─ TXT ──→ Direct Read ──────────→ Decode UTF-8
    │
    ▼
Clean & Format Text
    │
    ▼
Truncate if > 3000 chars
    │
    ▼
Return to Quiz Generator
```

## URL Processing Pipeline

```
URL Input
    │
    ▼
Validate URL Format
    │
    ▼
HTTP GET Request
    │
    ▼
Parse HTML with BeautifulSoup
    │
    ▼
Remove Scripts & Styles
    │
    ▼
Extract Text Content
    │
    ▼
Clean Whitespace
    │
    ▼
Return Processed Text
```

## AI Integration Flow

```
Text Content
    │
    ▼
Build Prompt
    │
    ├─ System: "You are a quiz generator..."
    │
    └─ User: "Based on this content: ..."
    │
    ▼
Send to Perplexity API
    │
    ├─ Model: llama-3.1-sonar-small-128k-online
    ├─ Temperature: 0.7
    └─ Max Tokens: 2000
    │
    ▼
Receive JSON Response
    │
    ▼
Clean Markdown (if any)
    │
    ▼
Parse JSON
    │
    ▼
Validate with Pydantic
    │
    ├─ Check question count
    ├─ Check options count
    └─ Check correctAnswer range
    │
    ▼
Return QuizResponse
```

## State Management (Frontend)

```
page.tsx (Root State)
├── currentStep: string
│   └── Controls which component to show
│
├── quizData: QuizData | null
│   └── Stores generated questions
│
└── score: number
    └── Final quiz score

State Transitions:
"upload" ─[Quiz Generated]→ "quiz" ─[Quiz Submitted]→ "results"
    ↑                                                      │
    └──────────────────[Restart]──────────────────────────┘
```

## Error Handling Strategy

```
┌─────────────────────────────────────┐
│         Error Categories            │
├─────────────────────────────────────┤
│  1. User Input Errors               │
│     - Invalid file type             │
│     - Missing file/URL              │
│     - Malformed URL                 │
│     - Content too short             │
│     → Show friendly message         │
├─────────────────────────────────────┤
│  2. Processing Errors               │
│     - PDF extraction failed         │
│     - URL fetch failed              │
│     - HTML parsing error            │
│     → Fallback to demo mode         │
├─────────────────────────────────────┤
│  3. API Errors                      │
│     - Perplexity API down           │
│     - Rate limit exceeded           │
│     - Invalid API key               │
│     → Use demo quiz generator       │
├─────────────────────────────────────┤
│  4. Network Errors                  │
│     - Timeout                       │
│     - Connection refused            │
│     → Retry with exponential backoff│
└─────────────────────────────────────┘
```

## Performance Optimizations

### Frontend
- Code splitting with Next.js dynamic imports
- Image optimization with Next.js Image component
- CSS-in-JS with Tailwind for minimal bundle
- React Server Components where applicable

### Backend
- Async/await for non-blocking I/O
- Connection pooling for HTTP requests
- Content truncation to stay within API limits
- Caching responses (future enhancement)

## Scalability Considerations

### Current (Development)
- Single instance
- In-memory state
- Synchronous processing

### Future (Production)
- Horizontal scaling with load balancer
- Redis for session/cache management
- Message queue for async processing
- Database for persistence
- CDN for static assets
