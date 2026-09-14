from google import genai

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.ai.schemas import Quiz


client = genai.Client(api_key=GEMINI_API_KEY)


def generate_quiz(topic: str = "Mixed Aptitude") -> Quiz:
    prompt = f"""
You are an expert aptitude-test question setter.

Generate exactly 5 high-quality multiple-choice aptitude questions.

Topic:
{topic}

Difficulty distribution MUST be exactly:

1 Easy
2 Moderate
2 Hard

Requirements:

1. Every question must have exactly 4 options.
2. There must be exactly one correct answer.
3. The correct answer must actually match one of the four options.
4. Give a concise but understandable explanation.
5. Give a shortcut/trick when one genuinely exists.
6. If there is no useful shortcut, write:
   "No special shortcut; use the standard method."
7. Questions must be mathematically/logically correct.
8. Do not repeat the same question.
9. Avoid ambiguous wording.
10. Questions should be suitable for aptitude preparation,
    placement tests and competitive examinations.
11. Use Indian-style currency/units when appropriate.
12. Do not include the answer in the question itself.

Return exactly 5 questions.
"""

    response = client.interactions.create(
        model=GEMINI_MODEL,
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": Quiz.model_json_schema(),
        },
    )

    return Quiz.model_validate_json(response.output_text)