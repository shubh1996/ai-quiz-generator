from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .verification import VerificationMetadata, SourceInfo


class Answer(BaseModel):
    """Individual answer option with weight"""
    answer: str
    weight: int  # 0 = incorrect, 1 = partially correct, 2 = correct


class Question(BaseModel):
    """Quiz question with multiple weighted answers"""
    question: str
    num_answers: int
    answers: List[Answer]


class ContentMetadata(BaseModel):
    """Metadata about the source content"""
    title: str
    description: str
    media_link: str
    duration: Optional[int] = None  # in minutes
    suggested_categories: List[str]
    suggested_media_type: str  # video, document, url, article
    creator_name: Optional[str] = None
    thumbnail_url: Optional[str] = None


class QuizData(BaseModel):
    """The quiz questions"""
    num_quiz_questions: int
    questions: List[Question]


class QuizResponse(BaseModel):
    """Complete API response"""
    success: bool = True
    job_id: Optional[str] = None
    content: ContentMetadata
    quiz: QuizData
    verification: Optional[VerificationMetadata] = None
    source_info: Optional[SourceInfo] = None
    points_awarded: Optional[int] = None
    generated_at: str
