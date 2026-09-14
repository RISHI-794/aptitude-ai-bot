import asyncio

from telegram import Bot

from app.ai.generator import generate_quiz
from app.database.database import (
    initialize_database,
    create_quiz_session,
    save_quiz,
    get_todays_quiz_session,
    save_topic_history,
)
from app.telegram.bot import BOT_TOKEN, CHAT_ID
from app.telegram.formatter import format_quiz_for_telegram
from app.topic_rotation import get_daily_topic


def create_daily_quiz():
    initialize_database()

    existing_session = get_todays_quiz_session()

    if existing_session:
        print("Today's quiz already exists.")
        print(f"Session ID: {existing_session[0]}")
        print(f"Category: {existing_session[2]}")
        print(f"Topic: {existing_session[3]}")
        return None

    category, topic = get_daily_topic()

    print(f"Today's category: {category}")
    print(f"Today's topic: {topic}")

    # Generate the quiz first.
    # We only record the topic after this succeeds.
    quiz = generate_quiz(topic)

    session_id = create_quiz_session(
        category=category,
        topic=topic,
        quiz=quiz,
    )

    print(f"Created quiz session: {session_id}")

    saved_count, skipped_count = save_quiz(
        quiz,
        session_id,
    )

    print(f"New questions saved: {saved_count}")
    print(f"Duplicate questions skipped: {skipped_count}")

    # Record topic only after successful quiz generation
    # and database saving.
    save_topic_history(
        category=category,
        topic=topic,
    )

    print("Topic recorded in history. ✅")

    return quiz


async def send_daily_quiz():
    quiz = create_daily_quiz()

    if quiz is None:
        print("Quiz already exists. Nothing to send.")
        return

    message = format_quiz_for_telegram(quiz)

    bot = Bot(token=BOT_TOKEN)

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message,
    )

    print("Daily quiz sent to Telegram! ✅")


if __name__ == "__main__":
    asyncio.run(send_daily_quiz())