from pydantic import BaseModel
from typing import List


class Question(BaseModel):
    id: int
    question: str
    options: List[str]
    correctAnswer: int


class QuizResponse(BaseModel):
    questions: List[Question]
