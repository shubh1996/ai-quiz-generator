from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import os
from dotenv import load_dotenv

from services.document_processor import DocumentProcessor
from services.quiz_generator import QuizGenerator
from models.quiz import QuizResponse

load_dotenv()

app = FastAPI(title="Quiz Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

document_processor = DocumentProcessor()
quiz_generator = QuizGenerator()


@app.get("/")
async def root():
    return {"message": "Quiz Generator API is running"}


@app.post("/api/generate-quiz", response_model=QuizResponse)
async def generate_quiz(
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None)
):
    """
    Generate a quiz from either an uploaded file or a URL
    """
    if not file and not url:
        raise HTTPException(status_code=400, detail="Please provide either a file or URL")

    try:
        if file:
            content = await document_processor.process_file(file)
        else:
            content = await document_processor.process_url(url)

        if not content or len(content.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="The provided content is too short to generate a quiz"
            )

        quiz_data = await quiz_generator.generate_quiz(content)

        return quiz_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
