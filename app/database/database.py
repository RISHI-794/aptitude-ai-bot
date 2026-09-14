import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Json

from app.ai.schemas import Quiz


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

if not SUPABASE_DB_URL:
    raise ValueError(
        "SUPABASE_DB_URL is missing. "
        "Please add it to the .env file."
    )


# India timezone for daily quiz logic
INDIA_TZ = ZoneInfo("Asia/Kolkata")


# --------------------------------------------------
# Database connection
# --------------------------------------------------

def get_connection():
    """
    Create a connection to the Supabase PostgreSQL database.
    """

    return psycopg.connect(SUPABASE_DB_URL)


# --------------------------------------------------
# Database initialization / connection test
# --------------------------------------------------

def initialize_database():
    """
    Verify that the Supabase database is reachable.

    Tables are created in Supabase separately, so this function
    does not recreate the schema.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        connection.commit()

    finally:
        connection.close()


# --------------------------------------------------
# Current date in India
# --------------------------------------------------

def get_today_india():
    """
    Return today's date according to India Standard Time.
    """

    return datetime.now(INDIA_TZ).date()


# --------------------------------------------------
# Quiz sessions
# --------------------------------------------------

def create_quiz_session(
    category: str,
    topic: str,
    quiz: Quiz
) -> int:

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            quiz_date = get_today_india()

            cursor.execute(
                """
                INSERT INTO quiz_sessions (
                    quiz_date,
                    category,
                    topic,
                    title
                )
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (
                    quiz_date,
                    category,
                    topic,
                    quiz.title,
                )
            )

            session_id = cursor.fetchone()[0]

        connection.commit()

        return int(session_id)

    finally:
        connection.close()


def get_todays_quiz_session():
    """
    Return today's quiz session.

    Return format:
    (
        id,
        quiz_date,
        category,
        topic,
        title
    )
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            today = get_today_india()

            cursor.execute(
                """
                SELECT
                    id,
                    quiz_date,
                    category,
                    topic,
                    title
                FROM quiz_sessions
                WHERE quiz_date = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (today,)
            )

            row = cursor.fetchone()

        return row

    finally:
        connection.close()


# --------------------------------------------------
# Questions
# --------------------------------------------------

def save_quiz(
    quiz: Quiz,
    session_id: int
):
    """
    Save the questions belonging to a quiz session.

    Duplicate questions are detected using the UNIQUE
    question constraint.
    """

    connection = get_connection()

    saved_count = 0
    skipped_count = 0

    try:
        with connection.cursor() as cursor:

            for question in quiz.questions:

                cursor.execute(
                    """
                    SELECT id
                    FROM questions
                    WHERE question = %s
                    """,
                    (question.question,)
                )

                existing_question = cursor.fetchone()

                if existing_question:

                    skipped_count += 1

                    cursor.execute(
                        """
                        UPDATE questions
                        SET
                            quiz_session_id = %s,
                            question_number = %s
                        WHERE id = %s
                        """,
                        (
                            session_id,
                            question.question_number,
                            existing_question[0],
                        )
                    )

                    continue

                cursor.execute(
                    """
                    INSERT INTO questions (
                        quiz_session_id,
                        question_number,
                        difficulty,
                        topic,
                        question,
                        options,
                        correct_answer,
                        explanation,
                        shortcut
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        session_id,
                        question.question_number,
                        question.difficulty,
                        question.topic,
                        question.question,
                        Json(question.options),
                        question.correct_answer,
                        question.explanation,
                        question.shortcut,
                    )
                )

                saved_count += 1

        connection.commit()

        return saved_count, skipped_count

    finally:
        connection.close()


def get_questions_for_session(session_id: int):
    """
    Return all questions belonging to a quiz session.

    The tuple order intentionally matches the old SQLite version
    so the existing Telegram code can continue to work.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    question_number,
                    difficulty,
                    topic,
                    question,
                    options,
                    correct_answer,
                    explanation,
                    shortcut
                FROM questions
                WHERE quiz_session_id = %s
                ORDER BY question_number
                """,
                (session_id,)
            )

            rows = cursor.fetchall()

        return rows

    finally:
        connection.close()


# --------------------------------------------------
# User submissions
# --------------------------------------------------

def save_submission(
    session_id: int,
    telegram_user_id: str,
    username: str,
    display_name: str,
    answers: dict,
    score: int,
    total_questions: int
):
    """
    Save a user's quiz submission.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO user_submissions (
                    quiz_session_id,
                    telegram_user_id,
                    username,
                    display_name,
                    answers,
                    score,
                    total_questions
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    session_id,
                    telegram_user_id,
                    username,
                    display_name,
                    Json(answers),
                    score,
                    total_questions,
                )
            )

        connection.commit()

    finally:
        connection.close()


# --------------------------------------------------
# Topic rotation
# --------------------------------------------------

def save_topic_history(
    category: str,
    topic: str
):
    """
    Record that a topic was used.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO topic_history (
                    category,
                    topic
                )
                VALUES (%s, %s)
                """,
                (
                    category,
                    topic,
                )
            )

        connection.commit()

    finally:
        connection.close()


def get_recent_topics(limit: int = 10):
    """
    Return recently used topics.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    category,
                    topic
                FROM topic_history
                ORDER BY id DESC
                LIMIT %s
                """,
                (limit,)
            )

            rows = cursor.fetchall()

        return rows

    finally:
        connection.close()


# --------------------------------------------------
# Local test
# --------------------------------------------------

if __name__ == "__main__":

    initialize_database()

    print("Supabase PostgreSQL connection successful! ✅")
    print(f"India date: {get_today_india()}")