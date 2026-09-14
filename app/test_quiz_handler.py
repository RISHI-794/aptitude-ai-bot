from app.telegram.quiz_handler import (
    process_answer_message,
)


def main():

    print("=" * 60)
    print("TESTING QUIZ ANSWER HANDLER")
    print("=" * 60)

    answer_text = (
        "Q1-A, Q2-B, Q3-C, Q4-D, Q5-A"
    )

    success, message = process_answer_message(
        text=answer_text,
        telegram_user_id="test_user_123",
        username="testuser",
        display_name="Test User",
    )

    print()
    print("Success:", success)
    print()
    print(message)

    print()
    print("=" * 60)

    if success:
        print("QUIZ HANDLER TEST PASSED! ✅")
    else:
        print("QUIZ HANDLER TEST FAILED ❌")


if __name__ == "__main__":
    main()