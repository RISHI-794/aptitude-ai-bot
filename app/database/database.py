import os
from datetime import datetime
from zoneinfo import ZoneInfo

import psycopg
from psycopg.types.json import Json
from dotenv import load_dotenv

from app.ai.schemas import Quiz


load_dotenv()


SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

if not SUPABASE_DB_URL:
    raise ValueError(
        "SUPABASE_DB_URL is missing. Please add it to the .env file."
    )


INDIA_TZ = ZoneInfo("Asia/Kolkata")


def get_connection():
    return psycopg.connect(SUPABASE_DB_URL)


def initialize_database():

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute("SELECT 1")
            cursor.fetchone()

        connection.commit()

    finally:

        connection.close()


def get_today_india():

    return datetime.now(INDIA_TZ).date()


def create_quiz_session(
    category: str,
    topic: str,
    quiz: Quiz,
) -> int:

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            quiz_date = get_today_india()

            cursor.execute(
                """
                INSERT INTO quiz_sessions
                (
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
                ),
            )

            session_id = cursor.fetchone()[0]

        connection.commit()

        return int(session_id)

    finally:

        connection.close()


def get_todays_quiz_session():

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
                    title,
                    sent_at
                FROM quiz_sessions
                WHERE quiz_date = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (today,),
            )

            row = cursor.fetchone()

        return row

    finally:

        connection.close()


def mark_quiz_as_sent(session_id: int):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE quiz_sessions
                SET sent_at = NOW()
                WHERE id = %s
                """,
                (session_id,),
            )

        connection.commit()

    finally:

        connection.close()


def save_quiz(quiz: Quiz, session_id: int):

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
                    (question.question,),
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
                        ),
                    )

                    continue

                cursor.execute(
                    """
                    INSERT INTO questions
                    (
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
                    VALUES
                    (
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
                    ),
                )

                saved_count += 1

        connection.commit()

        return saved_count, skipped_count

    finally:

        connection.close()


def get_questions_for_session(session_id: int):

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
                (session_id,),
            )

            rows = cursor.fetchall()

        return rows

    finally:

        connection.close()


def save_submission(
    session_id: int,
    telegram_user_id: str,
    username: str,
    display_name: str,
    answers: dict,
    score: int,
    total_questions: int,
):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO user_submissions
                (
                    quiz_session_id,
                    telegram_user_id,
                    username,
                    display_name,
                    answers,
                    score,
                    total_questions
                )
                VALUES
                (
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
                    str(telegram_user_id),
                    username,
                    display_name,
                    Json(answers),
                    score,
                    total_questions,
                ),
            )

        connection.commit()

    finally:

        connection.close()


def save_topic_history(
    category: str,
    topic: str,
):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO topic_history
                (
                    category,
                    topic
                )
                VALUES
                (
                    %s,
                    %s
                )
                """,
                (
                    category,
                    topic,
                ),
            )

        connection.commit()

    finally:

        connection.close()


def get_recent_topics(limit: int = 10):

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
                (limit,),
            )

            rows = cursor.fetchall()

        return rows

    finally:

        connection.close()