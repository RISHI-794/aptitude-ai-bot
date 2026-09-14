import os
import asyncio

from dotenv import load_dotenv
from telegram import Bot


load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing from .env")

if not CHAT_ID:
    raise ValueError("TELEGRAM_CHAT_ID is missing from .env")


async def send_test_message():
    bot = Bot(token=BOT_TOKEN)

    message = """
🤖 Aptitude Practice Bot

Telegram connection is working! ✅

Your daily aptitude system is one step closer.
"""

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )

    print("Test message sent successfully! ✅")


if __name__ == "__main__":
    asyncio.run(send_test_message())