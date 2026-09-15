import asyncio
import json

from telegram import Bot

from app.ai.generator import generate_quiz
from app.ai.schemas import Quiz, Question

from app.database.database import (
    initialize_database,
    create_quiz_session,
    save_quiz,
    get_todays_quiz_session,
    get_questions_for_session,
    save_topic_history,
    mark_quiz_as_sent,
)

from app.telegram.bot import BOT_TOKEN, CHAT_ID
from app.telegram.formatter import format_quiz_for_telegram
from app.topic_rotation import get_daily_topic


def load_existing_quiz(session):

    session_id = session[0]

    rows = get_questions_for_session(session_id)

    if len(rows) != 5:
        return None

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

        options = (
            json.loads(options_json)
            if isinstance(options_json, str)
            else options_json
        )

        questions.append(
            Question(
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

    return Quiz(
        title=session[4],
        questions=questions,
    )


def create_daily_quiz():

    initialize_database()

    existing_session = get_todays_quiz_session()

    if existing_session:

        print("Today's quiz already exists.")
        print(f"Session ID: {existing_session[0]}")
        print(f"Category: {existing_session[2]}")
        print(f"Topic: {existing_session[3]}")

        sent_at = existing_session[5]

        if sent_at:
            print(f"Already sent at: {sent_at}")
        else:
            print("Quiz has NOT been sent yet.")

        quiz = load_existing_quiz(existing_session)

        if quiz is None:
            print("Today's quiz exists but is incomplete.")
            return None, False

        print("Loaded existing quiz from Supabase. ✅")

        should_send = sent_at is None

        return quiz, should_send

    category, topic = get_daily_topic()

    print(f"Today's category: {category}")
    print(f"Today's topic: {topic}")

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

    save_topic_history(
        category=category,
        topic=topic,
    )

    print("Topic recorded in history. ✅")

    return quiz, True


async def send_daily_quiz():

    quiz, should_send = create_daily_quiz()

    if quiz is None:

        print("Could not load or create today's quiz.")

        return

    if not should_send:

        print("Today's quiz has already been sent.")
        print("No Telegram message will be sent. ✅")

        return

    message = format_quiz_for_telegram(quiz)

    bot = Bot(token=BOT_TOKEN)

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message,
    )

    print("Daily quiz sent to Telegram! ✅")

    # Only mark the quiz as sent AFTER Telegram confirms
    # that the message was successfully sent.

    session = get_todays_quiz_session()

    if session:

        mark_quiz_as_sent(session[0])

        print("Quiz marked as sent in Supabase. ✅")


if __name__ == "__main__":

    asyncio.run(send_daily_quiz())