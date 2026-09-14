import re

from app.ai.schemas import Quiz


def normalize_answer(answer: str) -> str:
    """
    Convert a user's answer into a standard form.

    Examples:
        A       -> A
        option a -> A
        Q1-A    -> A
    """
    answer = answer.strip().upper()

    match = re.search(r"\b([ABCD])\b", answer)

    if match:
        return match.group(1)

    return answer


def get_option_letter(question, answer: str) -> str:
    """
    Determine which option letter the user selected.
    """

    normalized = normalize_answer(answer)

    if normalized in ["A", "B", "C", "D"]:
        return normalized

    for index, option in enumerate(question.options):
        if answer.strip().lower() == option.strip().lower():
            return "ABCD"[index]

    return ""


def get_correct_option_letter(question) -> str:
    """
    Find the letter corresponding to the correct answer.
    """

    for index, option in enumerate(question.options):
        if option.strip().lower() == question.correct_answer.strip().lower():
            return "ABCD"[index]

    return ""


def check_quiz_answers(quiz: Quiz, answers: dict[int, str]):
    """
    Check a user's answers.

    answers example:
        {
            1: "A",
            2: "C",
            3: "B",
            4: "D",
            5: "A"
        }

    Returns:
        score
        total
        results
    """

    results = []
    score = 0

    for question in quiz.questions:
        user_answer = answers.get(question.question_number, "")

        user_letter = get_option_letter(
            question,
            user_answer
        )

        correct_letter = get_correct_option_letter(
            question
        )

        is_correct = user_letter == correct_letter

        if is_correct:
            score += 1

        results.append({
            "question_number": question.question_number,
            "user_answer": user_letter,
            "correct_answer": correct_letter,
            "is_correct": is_correct,
            "explanation": question.explanation,
            "shortcut": question.shortcut,
        })

    return score, len(quiz.questions), results