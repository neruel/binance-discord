import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Optional: validation
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is not set")
if not BINANCE_API_KEY:
    raise ValueError("BINANCE_API_KEY environment variable is not set")
if not BINANCE_API_SECRET:
    raise ValueError("BINANCE_API_SECRET environment variable is not set")