from app.ai.generator import generate_quiz


def main():
    quiz = generate_quiz("Percentages")

    print("\n")
    print("=" * 60)
    print(quiz.title)
    print("=" * 60)

    for q in quiz.questions:
        print(f"\nQ{q.question_number}. [{q.difficulty}]")
        print(f"Topic: {q.topic}")
        print(q.question)

        for option in q.options:
            print(option)

        print(f"\nCorrect Answer: {q.correct_answer}")
        print(f"Explanation: {q.explanation}")
        print(f"Shortcut: {q.shortcut}")
        print("-" * 60)


if __name__ == "__main__":
    main()