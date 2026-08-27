import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

def validate_config():
    """Validate required configuration settings when running the bot."""
    if not DISCORD_TOKEN:
        raise ValueError(
            "DISCORD_TOKEN environment variable is not set. "
            "Please copy .env.example to .env and set your DISCORD_TOKEN."
        )