from google import genai

from pydantic import BaseModel, Field

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
4. Give a concise, mathematically or logically correct explanation.
5. Give a useful shortcut/trick when one genuinely exists.
6. If there is no useful shortcut, write:
   "No special shortcut; use the standard method."
7. Questions must be mathematically and logically correct.
8. Do not repeat questions.
9. Avoid ambiguous wording.
10. Questions must be suitable for aptitude preparation,
    placement tests and competitive examinations.
11. Use Indian-style currency/units when appropriate.
12. Do not include the answer in the question itself.

IMPORTANT LOGICAL-REASONING RULES:

- Never assume that an object exists merely because a universal statement
  mentions a category.
- "All A are B" does NOT by itself prove that any A exists.
- "No A is B" does NOT by itself prove that any A or B exists.
- "All A are B" and "All B are C" support "All A are C",
  but do not support "Some A are C" unless existence is explicitly
  established.
- "Some A are B" explicitly establishes existence of at least one A and B.
- Check every "some", "all", and "no" conclusion carefully.
- Do not use real-world assumptions about categories.
- Do not infer existence from common sense.
- Do not claim that a conclusion definitely follows when it is only possible.
- The explanation must match the exact premises and conclusion.
- The shortcut must be valid for the exact question.

SYLLOGISM-SPECIFIC RULES:

- Use strict formal syllogistic reasoning.
- Prefer questions with these four answer types:
  "Only Conclusion I follows"
  "Only Conclusion II follows"
  "Both Conclusion I and II follow"
  "Neither Conclusion I nor II follows"
- Avoid "Either Conclusion I or II follows" questions.
- Do not use an "Either/Or" answer merely because both conclusions
  are uncertain.
- A "Some" conclusion must be supported by explicit existence information.
- Universal premises alone must not create existential conclusions.
- Every selected conclusion must necessarily follow from the premises.
- Every rejected conclusion must fail to necessarily follow from the premises.

IMPORTANT MATHEMATICAL RULES:

- Calculate the answer independently before selecting the correct option.
- Check arithmetic, signs, percentages, ratios, units and rounding.
- Make sure exactly one option is correct.
- The explanation must reproduce the correct reasoning.
- Never invent a calculation or shortcut.

Before returning the quiz, internally verify every question and every option.

Return exactly 5 questions using the required JSON schema.
"""


class ReviewResult(BaseModel):
    approved: bool
    reason: str = Field(min_length=1)


REVIEW_PROMPT = """
You are a strict final quality-control reviewer for an aptitude test.

Review the complete quiz below.

Return:
approved = true ONLY if every question is suitable for publication.

Return:
approved = false if ANY question has even one serious correctness,
logic, ambiguity, explanation, or answer problem.

Reject the quiz if ANY question has:

- more than one defensible correct answer
- no correct answer
- an incorrect marked answer
- an incorrect calculation
- an invalid logical inference
- an unsupported existence assumption
- an incorrect explanation
- an incorrect shortcut
- ambiguous wording
- duplicate questions
- duplicate options
- a difficulty mismatch
- a conclusion that does not necessarily follow from the premises

SYLLOGISM REVIEW RULES:

- "All A are B" does not imply that some A exists.
- "No A is B" does not imply that A or B exists.
- Universal premises cannot create existence by themselves.
- A "Some" conclusion requires explicit existential support.
- "All A are B" and "All B are C" support "All A are C",
  but do not establish that any A exists.
- Do not accept conclusions based on common-sense assumptions.
- Do not accept "Either I or II follows" patterns.
- Check every syllogism conclusion independently.
- The marked answer must be the only answer that necessarily follows.

For mathematical questions:

- Recalculate the result independently.
- Check units, arithmetic, signs, percentages, ratios and rounding.
- Verify that exactly one option is correct.
- Verify that the explanation agrees with the calculation.

For every question, independently determine whether the marked answer
is actually correct.

If even ONE question is questionable, return approved=false.

Quiz to review:

{quiz_json}
"""


def validate_quiz(quiz: Quiz) -> None:

    if len(quiz.questions) != 5:
        raise ValueError(
            f"Expected 5 questions, received {len(quiz.questions)}."
        )

    difficulties = [
        question.difficulty
        for question in quiz.questions
    ]

    if difficulties.count("Easy") != 1:
        raise ValueError(
            "Difficulty distribution must contain exactly 1 Easy."
        )

    if difficulties.count("Moderate") != 2:
        raise ValueError(
            "Difficulty distribution must contain exactly 2 Moderate."
        )

    if difficulties.count("Hard") != 2:
        raise ValueError(
            "Difficulty distribution must contain exactly 2 Hard."
        )

    question_numbers = [
        question.question_number
        for question in quiz.questions
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

        correct_answer = (
            question.correct_answer.strip().lower()
        )

        if correct_answer not in option_texts:
            raise ValueError(
                f"Q{question.question_number}: correct answer "
                "does not match any option."
            )

        if not question.explanation.strip():
            raise ValueError(
                f"Q{question.question_number}: explanation is empty."
            )

        if not question.shortcut.strip():
            raise ValueError(
                f"Q{question.question_number}: shortcut is empty."
            )


def review_quiz(quiz: Quiz, model: str) -> None:

    quiz_json = quiz.model_dump_json(indent=2)

    prompt = REVIEW_PROMPT.format(
        quiz_json=quiz_json
    )

    response = client.interactions.create(
        model=model,
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": ReviewResult.model_json_schema(),
        },
    )

    review = ReviewResult.model_validate_json(
        response.output_text
    )

    if not review.approved:
        raise ValueError(
            f"AI quality review rejected quiz: {review.reason}"
        )

    print("✅ AI quality review passed.")


def generate_quiz(topic: str = "Mixed Aptitude") -> Quiz:

    prompt = PROMPT_TEMPLATE.format(
        topic=topic
    )

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

            quiz = Quiz.model_validate_json(
                response.output_text
            )

            validate_quiz(quiz)

            print(f"✅ Generation successful: {model}")
            print("✅ Local validation passed.")

            topic_lower = topic.lower()

            if (
                "syllogism" in topic_lower
                or "logical reasoning" in topic_lower
                or "reasoning" in topic_lower
            ):

                print("🔍 Running additional logical-quality review...")

                review_quiz(
                    quiz=quiz,
                    model=model,
                )

            print("🎉 Quiz accepted.")

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