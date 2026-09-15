import os
from dotenv import load_dotenv

load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. Please add it to the .env file."
    )


# ============================================================
# GEMINI MODEL FALLBACK ORDER
# ============================================================
#
# The bot tries these models from top to bottom.
#
# If a model fails because of:
# - 429 quota/rate limit
# - 500 high demand
# - temporary API error
# - invalid response
# - schema validation failure
#
# the bot automatically moves to the next model.
#
# The first model that produces a valid quiz wins.
#
# This list is designed for the $0/free-tier setup.
# ============================================================

GEMINI_MODELS = [

    # Primary
    "gemini-3.8-flash",

    # Backup 1
    "gemini-3.7-flash",

    # Proven working fallback
    "gemini-3.6-flash",

    # Proven working fallback
    "gemini-3.5-flash",

    # Lightweight proven fallback
    "gemini-3.5-flash-lite",

    # Lightweight proven fallback
    "gemini-3.1-flash-lite",

    # Preview fallback
    "gemini-3-flash-preview",

    # Final AI backup
    "gemma-4-31b-it",
]


# Compatibility with existing code.
# The first model is considered the primary model.

GEMINI_MODEL = GEMINI_MODELS[0]