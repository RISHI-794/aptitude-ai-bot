from app.ai.schemas import Question, Quiz
from app.database.database import (
    initialize_database,
    create_quiz_session,
    save_quiz,
    get_questions_for_session,
)


def main():

    print("Initializing database...")
    initialize_database()

    # Create 5 fake questions.
    # This does NOT call Gemini.
    questions = []

    for i in range(1, 6):
        questions.append(
            Question(
                question_number=i,
                difficulty="Easy" if i == 1 else "Moderate",
                topic="Percentages",
                question=f"Test question number {i}?",
                options=[
                    "A) Option A",
                    "B) Option B",
                    "C) Option C",
                    "D) Option D",
                ],
                correct_answer="A) Option A",
                explanation="This is a test explanation.",
                shortcut="This is a test shortcut.",
            )
        )

    quiz = Quiz(
        title="Test Percentage Quiz",
        questions=questions,
    )

    print("Creating quiz session...")

    session_id = create_quiz_session(
        category="Aptitude",
        topic="Percentages",
        quiz=quiz,
    )

    print(f"Session ID: {session_id}")

    print("\nSaving questions to this session...")

    saved_count, skipped_count = save_quiz(
        quiz,
        session_id,
    )

    print(f"New questions saved: {saved_count}")
    print(f"Duplicate questions skipped: {skipped_count}")

    print("\nReading questions back from database...")

    rows = get_questions_for_session(session_id)

    for row in rows:

        (
            question_id,
            question_number,
            difficulty,
            topic,
            question,
            options,
            correct_answer,
            explanation,
            shortcut,
        ) = row

        print()
        print(f"Question ID: {question_id}")
        print(f"Question Number: {question_number}")
        print(f"Difficulty: {difficulty}")
        print(f"Topic: {topic}")
        print(f"Question: {question}")
        print(f"Correct Answer: {correct_answer}")

    print()
    print("=" * 60)
    print(f"Questions linked to session: {len(rows)}")
    print("=" * 60)

    if len(rows) == 5:
        print("Quiz session test PASSED! ✅")
    else:
        print("Quiz session test FAILED ❌")


if __name__ == "__main__":
    main()