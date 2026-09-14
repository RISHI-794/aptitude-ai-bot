from typing import List, Literal

from pydantic import BaseModel, Field


class Question(BaseModel):
    question_number: int

    difficulty: Literal[
        "Easy",
        "Moderate",
        "Hard"
    ]

    topic: str

    question: str

    options: List[str] = Field(
        min_length=4,
        max_length=4,
        description="Exactly four multiple-choice options."
    )

    correct_answer: str

    explanation: str

    shortcut: str


class Quiz(BaseModel):
    title: str

    questions: List[Question] = Field(
        min_length=5,
        max_length=5
    )