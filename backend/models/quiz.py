from pydantic import BaseModel
from typing import List, Optional
from .verification import VerificationMetadata, SourceInfo


class Question(BaseModel):
    id: int
    question: str
    options: List[str]
    correctAnswer: int


class QuizResponse(BaseModel):
    questions: List[Question]
    verification: Optional[VerificationMetadata] = None
    source_info: Optional[SourceInfo] = None
    points_awarded: Optional[int] = None
