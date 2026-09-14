from app.ai.generator import generate_quiz
from app.database.database import initialize_database, save_quiz


def main():
    initialize_database()

    print("Generating quiz...")
    quiz = generate_quiz("Percentages")

    print("Saving quiz to database...")

    saved_count, skipped_count = save_quiz(quiz)

    print(f"New questions saved: {saved_count}")
    print(f"Duplicate questions skipped: {skipped_count}")


if __name__ == "__main__":
    main()