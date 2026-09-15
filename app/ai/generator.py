from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, GEMINI_MODELS
from app.ai.schemas import Quiz


client = genai.Client(api_key=GEMINI_API_KEY)


PROMPT_TEMPLATE = """
You are an expert aptitude-test question setter.

Generate exactly 5 high-quality multiple-choice questions.

Topic:
{topic}

Difficulty distribution MUST be exactly:
1 Easy
2 Moderate
2 Hard

Requirements:
1. Every question must have exactly 4 options.
2. There must be exactly one correct answer.
3. The correct answer must exactly match one of the four options.
4. Give a concise but understandable explanation.
5. Give a useful shortcut/trick when one genuinely exists.
6. If there is no useful shortcut, write:
   "No special shortcut; use the standard method."
7. Questions must be mathematically/logically correct.
8. Do not repeat questions.
9. Avoid ambiguous wording.
10. Questions should be suitable for aptitude preparation,
    placement tests and competitive examinations.
11. Use Indian-style currency/units when appropriate.
12. Do not include the answer in the question itself.

Return exactly 5 questions using the required JSON schema.
"""


def validate_quiz(quiz: Quiz) -> None:
    """
    Strict local validation.

    If anything is wrong, raise ValueError so the next
    Gemini model can be tried.
    """

    if len(quiz.questions) != 5:
        raise ValueError(
            f"Expected 5 questions, received {len(quiz.questions)}."
        )

    difficulties = [question.difficulty for question in quiz.questions]

    if difficulties.count("Easy") != 1:
        raise ValueError("Difficulty distribution must contain exactly 1 Easy.")

    if difficulties.count("Moderate") != 2:
        raise ValueError(
            "Difficulty distribution must contain exactly 2 Moderate."
        )

    if difficulties.count("Hard") != 2:
        raise ValueError("Difficulty distribution must contain exactly 2 Hard.")

    question_numbers = [
        question.question_number for question in quiz.questions
    ]

    if sorted(question_numbers) != [1, 2, 3, 4, 5]:
        raise ValueError(
            "Question numbers must be exactly 1, 2, 3, 4, 5."
        )

    question_texts = [
        question.question.strip().lower()
        for question in quiz.questions
    ]

    if len(set(question_texts)) != 5:
        raise ValueError("Duplicate questions detected.")

    for question in quiz.questions:

        if len(question.options) != 4:
            raise ValueError(
                f"Q{question.question_number} does not have exactly 4 options."
            )

        option_texts = [
            option.strip().lower()
            for option in question.options
        ]

        if len(set(option_texts)) != 4:
            raise ValueError(
                f"Q{question.question_number} contains duplicate options."
            )

        correct_answer = question.correct_answer.strip().lower()

        if correct_answer not in option_texts:
            raise ValueError(
                f"Q{question.question_number}: correct answer "
                f"does not match any option."
            )


def generate_quiz(topic: str = "Mixed Aptitude") -> Quiz:

    prompt = PROMPT_TEMPLATE.format(topic=topic)

    last_error = None

    print("\n🤖 Gemini fallback system started.")
    print(f"Models available: {len(GEMINI_MODELS)}")

    for model in GEMINI_MODELS:

        print(f"\n🔄 Trying model: {model}")

        try:
            response = client.interactions.create(
                model=model,
                input=prompt,
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": Quiz.model_json_schema(),
                },
            )

            quiz = Quiz.model_validate_json(response.output_text)

            validate_quiz(quiz)

            print(f"✅ SUCCESS: {model}")
            print("✅ Quiz passed local validation.")

            return quiz

        except Exception as error:

            last_error = error

            print(f"❌ FAILED: {model}")
            print(f"   Reason: {error}")

            print("   Moving to next model...")

    raise RuntimeError(
        "All configured Gemini models failed. "
        f"Last error: {last_error}"
    )