import os
import logging
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN or not OPENAI_API_KEY:
    raise EnvironmentError(
        "Missing required environment variables. Make sure SLACK_BOT_TOKEN, SLACK_APP_TOKEN, and OPENAI_API_KEY are set."
    )

# Configure logging to stdout and file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/kenny.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from bot.db import init_db
from bot.game_manager import GameManager

# Initialize Slack Bolt app
app = AsyncApp(token=SLACK_BOT_TOKEN)

# Create GameManager instance
game_manager = GameManager(app, question_file="questions.csv")

# Handle app mentions for witty responses and trivia start
@app.event("app_mention")
async def handle_mention(event, say):
    user = event.get('user')
    text = event.get('text', '')
    logger.info(f"Mention from {user}: {text}")
    if 'play trivia' in text.lower():
        channel = event.get('channel')
        await say(f":game_die: Starting a trivia game! 🎲")
        await game_manager.start_game(channel, total_rounds=5)
    else:
        await say(f"Hey <@{user}>! You said: {text}")

# Slash command to start trivia
@app.command("/trivia")
async def handle_trivia(ack, body, say):
    await ack()
    text = body.get('text', '').strip()
    try:
        rounds = int(text) if text.isdigit() else 5
    except ValueError:
        rounds = 5
    channel = body.get('channel_id')
    logger.info(f"/trivia invoked in {channel} for {rounds} rounds")
    await say(f":checkered_flag: Kicking off a trivia game with {rounds} rounds! 🏁")
    await game_manager.start_game(channel, total_rounds=rounds)

# Entrypoint
default_async_loop = asyncio.get_event_loop()
async def _start():
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized.")
    handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
    logger.info("Starting Slack Socket Mode handler...")
    await handler.start_async()

if __name__ == "__main__":
    asyncio.run(_start())
