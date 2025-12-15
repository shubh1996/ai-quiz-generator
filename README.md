# AI Quiz Generator

An intelligent quiz generation application that creates multiple-choice questions from documents or web content using AI. Built with Next.js (frontend) and FastAPI (backend).

## Features

- **Upload Documents**: Support for PDF, TXT, and DOCX files
- **URL Parsing**: Extract content from any web URL
- **AI-Powered**: Uses Perplexity AI to generate intelligent quiz questions
- **Interactive Quiz**: Clean, user-friendly quiz interface
- **Instant Feedback**: Pass/fail results with score breakdown
- **Modern UI**: Beautiful gradient design with Tailwind CSS

## Tech Stack

### Frontend
- Next.js 16 (React 19)
- TypeScript
- Tailwind CSS
- Axios for API calls

### Backend
- Python 3.14
- FastAPI
- Perplexity AI API
- PyPDF2, python-docx for document processing
- BeautifulSoup4 for URL scraping

## Project Structure

```
quiz-generator/
├── frontend/                 # Next.js frontend application
│   ├── app/
│   │   ├── components/      # React components
│   │   │   ├── UploadStep.tsx
│   │   │   ├── QuizStep.tsx
│   │   │   └── ResultsStep.tsx
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── package.json
│   └── tsconfig.json
│
└── backend/                  # Python FastAPI backend
    ├── models/              # Pydantic models
    │   └── quiz.py
    ├── services/            # Business logic
    │   ├── document_processor.py
    │   └── quiz_generator.py
    ├── main.py              # FastAPI app
    ├── requirements.txt
    └── .env.example
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- Perplexity API key (get from [perplexity.ai](https://www.perplexity.ai/))

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```

5. Add your Perplexity API key to `.env`:
```
PERPLEXITY_API_KEY=your_api_key_here
```

6. Run the backend server:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Usage

1. **Start both servers** (backend on port 8000, frontend on port 3000)

2. **Open your browser** and go to `http://localhost:3000`

3. **Upload content**:
   - Choose "Upload File" and select a PDF, TXT, or DOCX file, OR
   - Choose "Paste URL" and enter a web page URL

4. **Take the quiz**: Answer all 5 multiple-choice questions

5. **View results**: See your score and pass/fail status (4+ correct answers to pass)

## API Endpoints

- `GET /` - API root endpoint
- `POST /api/generate-quiz` - Generate quiz from file or URL
- `GET /health` - Health check endpoint

## Configuration

### Backend (.env)
```env
PERPLEXITY_API_KEY=your_perplexity_api_key
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Demo Mode

If no Perplexity API key is provided, the application will run in demo mode with sample questions. To use the full AI-powered quiz generation:

1. Sign up at [perplexity.ai](https://www.perplexity.ai/)
2. Get your API key
3. Add it to `backend/.env`
4. Restart the backend server

## Future Improvements

- [ ] Database integration for storing quiz history
- [ ] User authentication and profiles
- [ ] Customizable quiz difficulty and length
- [ ] Multiple AI provider support (OpenAI, Anthropic, etc.)
- [ ] Question type variety (true/false, fill-in-blank, etc.)
- [ ] Timed quizzes
- [ ] Export quiz results
- [ ] Share quiz links with others
- [ ] Admin dashboard for analytics

## Troubleshooting

**Backend not starting?**
- Ensure Python 3.10+ is installed
- Check that all dependencies are installed
- Verify your virtual environment is activated

**Frontend not connecting to backend?**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify the API URL in frontend code

**Quiz generation failing?**
- Check your Perplexity API key is valid
- Ensure you have API credits available
- Check backend logs for error messages

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
