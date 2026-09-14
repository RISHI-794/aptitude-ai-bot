import sqlite3
import json

from app.database.database import DB_PATH


def main():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            question_number,
            difficulty,
            topic,
            question,
            options,
            correct_answer
        FROM questions
        ORDER BY id
    """)

    rows = cursor.fetchall()

    print("\n" + "=" * 70)
    print("QUESTIONS STORED IN DATABASE")
    print("=" * 70)

    for row in rows:
        (
            question_id,
            question_number,
            difficulty,
            topic,
            question,
            options,
            correct_answer
        ) = row

        print(f"\nID: {question_id}")
        print(f"Question Number: {question_number}")
        print(f"Difficulty: {difficulty}")
        print(f"Topic: {topic}")
        print(f"Question: {question}")

        print("Options:")
        for option in json.loads(options):
            print(f"  {option}")

        print(f"Correct Answer: {correct_answer}")
        print("-" * 70)

    print(f"\nTotal questions stored: {len(rows)}")

    connection.close()


if __name__ == "__main__":
    main()