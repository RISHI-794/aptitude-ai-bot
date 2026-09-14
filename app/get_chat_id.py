import os
import requests
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing from .env")


url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

response = requests.get(url)

if response.status_code != 200:
    print("Telegram API error:")
    print(response.text)
    exit()

data = response.json()

print("\nTelegram Updates:")
print("=" * 60)

for update in data["result"]:
    message = update.get("message")

    if message:
        chat = message.get("chat")

        print(f"Chat ID: {chat.get('id')}")
        print(f"Chat Type: {chat.get('type')}")
        print(f"Chat Title: {chat.get('title')}")
        print(f"Message: {message.get('text')}")
        print("-" * 60)

if not data["result"]:
    print("No updates found.")
    print("Send /test in the Telegram group and run this program again.")