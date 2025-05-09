import os
import json
import logging
import openai

# Initialize OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
logger = logging.getLogger(__name__)

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
        resp = await openai.chat.completions.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0.8,
            max_tokens=150,
        )
        content = resp.choices[0].message.content.strip()
        data = json.loads(content)
        question = data.get("question", "")
        answer = data.get("answer", "")
        return {"question": question, "answer": answer}
    except json.JSONDecodeError:
        logger.exception("Failed to decode JSON from OpenAI curveball response: %s", content)
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
        resp = await openai.chat.completions.acreate(
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
