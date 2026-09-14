import json

from app.answer_checker import check_quiz_answers
from app.database.database import (
    get_questions_for_session,
    get_todays_quiz_session,
    save_submission,
)
from app.telegram.answer_parser import (
    parse_answers,
    is_valid_answer_submission,
)


class QuestionData:
    """
    Lightweight question object used by the answer checker.
    """

    def __init__(
        self,
        question_number,
        difficulty,
        topic,
        question,
        options,
        correct_answer,
        explanation,
        shortcut,
    ):
        self.question_number = question_number
        self.difficulty = difficulty
        self.topic = topic
        self.question = question
        self.options = options
        self.correct_answer = correct_answer
        self.explanation = explanation
        self.shortcut = shortcut


def load_today_questions():
    """
    Load today's quiz questions from Supabase.
    """

    session = get_todays_quiz_session()

    if not session:
        return None, []

    session_id = session[0]

    rows = get_questions_for_session(session_id)

    questions = []

    for row in rows:

        (
            _question_id,
            question_number,
            difficulty,
            topic,
            question,
            options_json,
            correct_answer,
            explanation,
            shortcut,
        ) = row

        # PostgreSQL JSONB is normally returned as a Python list.
        # The string check keeps this compatible with old SQLite data.
        if isinstance(options_json, str):
            options = json.loads(options_json)
        else:
            options = options_json

        questions.append(
            QuestionData(
                question_number=question_number,
                difficulty=difficulty,
                topic=topic,
                question=question,
                options=options,
                correct_answer=correct_answer,
                explanation=explanation,
                shortcut=shortcut,
            )
        )

    return session, questions


def format_result_message(
    score,
    total_questions,
    results,
):
    """
    Format quiz results for Telegram.
    """

    lines = []

    lines.append("📊 QUIZ RESULT")
    lines.append("")
    lines.append(
        f"🏆 Score: {score}/{total_questions}"
    )
    lines.append("")

    for result in results:

        question_number = result["question_number"]
        user_answer = result["user_answer"]
        correct_answer = result["correct_answer"]
        is_correct = result["is_correct"]

        if is_correct:
            lines.append(
                f"Q{question_number}: ✅ {user_answer}"
            )
        else:
            lines.append(
                f"Q{question_number}: ❌ {user_answer} "
                f"(Correct: {correct_answer})"
            )

        lines.append(
            f"💡 Explanation: {result['explanation']}"
        )

        lines.append(
            f"⚡ Shortcut: {result['shortcut']}"
        )

        lines.append("")

    return "\n".join(lines)


def process_answer_message(
    text: str,
    telegram_user_id: str = "test_user",
    username: str = "",
    display_name: str = "Test User",
):
    """
    Process a user's submitted answers.

    Returns:
        (success, message)
    """

    answers = parse_answers(text)

    if not is_valid_answer_submission(answers):

        return (
            False,
            (
                "❌ Invalid answer format.\n\n"
                "Please answer all 5 questions like:\n"
                "Q1-A, Q2-C, Q3-B, Q4-D, Q5-A"
            ),
        )

    session, questions = load_today_questions()

    if not session:

        return (
            False,
            "❌ There is no quiz available for today.",
        )

    if len(questions) != 5:

        return (
            False,
            (
                "❌ Today's quiz is incomplete. "
                "Please try again later."
            ),
        )

    session_id = session[0]

    quiz_like_object = type(
        "QuizLikeObject",
        (),
        {
            "questions": questions
        },
    )()

    score, total_questions, results = check_quiz_answers(
        quiz_like_object,
        answers,
    )

    save_submission(
        session_id=session_id,
        telegram_user_id=str(telegram_user_id),
        username=username,
        display_name=display_name,
        answers=answers,
        score=score,
        total_questions=total_questions,
    )

    message = format_result_message(
        score=score,
        total_questions=total_questions,
        results=results,
    )

    return True, message


if __name__ == "__main__":

    test_answers = (
        "Q1-A, Q2-B, Q3-C, Q4-D, Q5-A"
    )

    result = process_answer_message(
        answer_text=test_answers
    )

    print(result["message"])