from app.ai.schemas import Question, Quiz
from app.answer_checker import check_quiz_answers


def main():
    quiz = Quiz(
        title="Test Quiz",
        questions=[
            Question(
                question_number=1,
                difficulty="Easy",
                topic="Percentages",
                question="What is 20% of 100?",
                options=["A) 10", "B) 20", "C) 30", "D) 40"],
                correct_answer="B) 20",
                explanation="20% of 100 is 20.",
                shortcut="10% of 100 is 10, so 20% is 20."
            ),
            Question(
                question_number=2,
                difficulty="Moderate",
                topic="Averages",
                question="What is the average of 10 and 20?",
                options=["A) 10", "B) 15", "C) 20", "D) 30"],
                correct_answer="B) 15",
                explanation="(10 + 20) / 2 = 15.",
                shortcut="For two numbers, average = midpoint."
            ),
            Question(
                question_number=3,
                difficulty="Moderate",
                topic="Ratio",
                question="What is the simplified ratio of 10:20?",
                options=["A) 1:2", "B) 2:3", "C) 3:4", "D) 4:5"],
                correct_answer="A) 1:2",
                explanation="Divide both numbers by 10.",
                shortcut="Divide both terms by their HCF."
            ),
            Question(
                question_number=4,
                difficulty="Hard",
                topic="Number System",
                question="What is 15 × 15?",
                options=["A) 200", "B) 215", "C) 225", "D) 250"],
                correct_answer="C) 225",
                explanation="15 × 15 = 225.",
                shortcut="15² = 225."
            ),
            Question(
                question_number=5,
                difficulty="Hard",
                topic="Probability",
                question="What is the probability of getting heads on a fair coin?",
                options=["A) 1/4", "B) 1/3", "C) 1/2", "D) 1"],
                correct_answer="C) 1/2",
                explanation="There are two equally likely outcomes.",
                shortcut="Favorable outcomes / total outcomes = 1/2."
            ),
        ]
    )

    # Simulated user answers
    answers = {
        1: "B",
        2: "B",
        3: "A",
        4: "C",
        5: "A",
    }

    score, total, results = check_quiz_answers(
        quiz,
        answers
    )

    print("\n" + "=" * 50)
    print("ANSWER CHECKER TEST")
    print("=" * 50)

    print(f"\nScore: {score}/{total}")

    for result in results:
        status = "✅ Correct" if result["is_correct"] else "❌ Wrong"

        print(
            f"Q{result['question_number']}: "
            f"{status} | "
            f"Your answer: {result['user_answer']} | "
            f"Correct: {result['correct_answer']}"
        )

    print("=" * 50)


if __name__ == "__main__":
    main()