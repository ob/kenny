import os
import json
import logging
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger = logging.getLogger(__name__)

async def is_trivia_request(text: str) -> bool:
    """
    Use OpenAI to classify whether the user's text indicates a desire to start a trivia game.
    """
    prompt = (
        f"You are a classifier that determines if a user wants to play trivia. "
        f"User message: '{text}'. "
        "Respond with 'yes' if they want to start a trivia game, otherwise 'no'."
    )
    try:
        # Use the v1 async API
        resp = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Classify if user intent is to play trivia."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=3,
        )
        answer = resp.choices[0].message.content.strip().lower()
        return answer.startswith("yes")
    except Exception as e:
        logger.exception("Error classifying trivia intent: %s", e)
        return False

async def get_curveball_question() -> dict:
    """
    Ask OpenAI to generate a single trivia question and answer in JSON format.
    Returns a dict with keys 'question' and 'answer'.
    """
    system_prompt = (
        "You are a trivia question generator. "
        "Provide exactly one trivia question and its answer as a JSON object with keys 'question' and 'answer'. "
        "Do not include any additional text."
    )
    try:
        resp = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0.8,
            max_tokens=150,
        )
        content = resp.choices[0].message.content.strip()
        data = json.loads(content)
        return {"question": data.get("question", ""), "answer": data.get("answer", "")}
    except json.JSONDecodeError:
        logger.exception("Failed to decode JSON from curveball: %s", content)
        return {"question": "(curveball) What is the capital of France?", "answer": "Paris"}
    except Exception as e:
        logger.exception("Error fetching curveball question: %s", e)
        return {"question": "(curveball) What is the capital of France?", "answer": "Paris"}

async def get_witty_response(user: str, question_text: str) -> str:
    """
    Ask OpenAI for a witty response celebrating the user for answering the question.
    Returns a string.
    """
    prompt = (
        f"Compose a witty, upbeat message congratulating <@{user}> "
        f"for correctly answering the trivia question: '{question_text}'. "
        "Keep it short and fun."
    )
    try:
        resp = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a witty, enthusiastic host."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=60,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("Error fetching witty response: %s", e)
        return f":tada: Nice job, <@{user}>!"

async def get_witty_chat_response(user: str, message_text: str) -> str:
    """
    Ask OpenAI for a witty, fun response to a general chat message.
    Returns a string.
    """
    prompt = (
        f"Reply to <@{user}>'s message in a witty, fun, and friendly way.\n"
        f"User message: '{message_text}'\n"
        "Keep it short, clever, and conversational."
    )
    try:
        resp = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a witty, friendly chatbot who loves to banter with users."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.95,
            max_tokens=60,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("Error fetching witty chat response: %s", e)
        return f"Hey <@{user}>! (witty response unavailable)"
