# Kenny Trivia Bot

Kenny is a Slack-integrated trivia bot powered by OpenAI. It generates trivia questions, recognizes when users want to play, and celebrates correct answers with witty responses.

## Features
- Detects when a user wants to start a trivia game
- Generates trivia questions and answers using OpenAI
- Congratulates users with fun, AI-generated messages
- Tracks game state and scores
- Uses a local SQLite database for persistence

## Setup

### Prerequisites
- Python 3.10+
- A valid OpenAI API key
- Slack App credentials (if integrating with Slack)

### Installation
1. Clone the repository:
   ```sh
   git clone <your-repo-url>
   cd kenny
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your OpenAI and Slack credentials:
   ```sh
   cp env.example .env
   # Edit .env with your keys
   ```

### Running the Bot
Run the main entry point:
```sh
python main.py
```

## File Structure
- `main.py` — Entry point for the bot
- `bot/` — Core bot logic
  - `openai_client.py` — Handles OpenAI API calls
  - `game_manager.py` — Manages game state and logic
  - `db.py` — Database interactions
  - `slack_app.py` — Slack integration
  - `trivia.py` — Trivia game logic
- `questions.csv` — Optional: custom trivia questions
- `kenny.db` — SQLite database
- `logs/kenny.log` — Log output

## Environment Variables
Set the following in your `.env` file:
- `OPENAI_API_KEY` — Your OpenAI API key
- `SLACK_BOT_TOKEN` — (If using Slack) Your Slack bot token
- `SLACK_SIGNING_SECRET` — (If using Slack) Your Slack signing secret

## License
MIT

---

*Built with ❤️ and OpenAI.*
