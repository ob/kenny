import asyncio
import random
import logging
import re
from slack_bolt.async_app import AsyncApp
from bot.db import (
    create_game,
    increment_round,
    record_score,
    finalize_game,
    get_leaderboard,
)
from bot.trivia import load_questions, pick_question
from bot.openai_client import get_witty_response, get_curveball_question

logger = logging.getLogger(__name__)

# Utility to normalize answers for fuzzy matching
def normalize_answer(s: str) -> str:
    s = s.lower()
    # remove leading/trailing whitespace and punctuation
    s = re.sub(r'[^a-z0-9 ]+', '', s)
    # remove common articles
    s = re.sub(r'\b(a|an|the)\b', '', s)
    # collapse multiple spaces
    return ' '.join(s.split())

class GameManager:
    def __init__(self, app: AsyncApp, question_file: str = "questions.csv"):
        self.app = app
        self.active_tasks: dict[str, asyncio.Task] = {}
        # pending answers: channel -> (future, expected_answer)
        self.pending: dict[str, tuple[asyncio.Future, str]] = {}
        self.questions = load_questions(question_file)

        # Global listener for all messages to catch answers
        @self.app.event("message")
        async def _global_message_handler(body, ack):
            await ack()
            event = body.get('event', {})
            channel = event.get('channel')
            text = event.get('text', '') or ''
            user = event.get('user')
            ts = event.get('ts')

            if channel in self.pending:
                future, expected = self.pending[channel]
                if not future.done():
                    norm_text = normalize_answer(text)
                    norm_expected = normalize_answer(expected)
                    # exact match or substring
                    if norm_text == norm_expected or norm_text in norm_expected or norm_expected in norm_text:
                        future.set_result((user, ts))

    async def start_game(self, channel: str, total_rounds: int):
        if channel in self.active_tasks:
            await self.app.client.chat_postMessage(
                channel=channel,
                text=":warning: A trivia game is already in progress in this channel!"
            )
            return
        # Create DB entry
        game_id = await create_game(channel, total_rounds)
        # Launch the game loop
        task = asyncio.create_task(self._run_game(channel, game_id, total_rounds))
        self.active_tasks[channel] = task
        logger.info(f"Started game {game_id} in channel {channel} for {total_rounds} rounds")

    async def _run_game(self, channel: str, game_id: int, total_rounds: int):
        try:
            for round_index in range(total_rounds):
                await increment_round(game_id)
                # Select question: 20% chance of AI curveball
                if random.random() < 0.2:
                    q = await get_curveball_question()
                else:
                    q = pick_question(self.questions)
                question_text, answer = q['question'], q['answer']

                # Post question
                await self.app.client.chat_postMessage(
                    channel=channel,
                    text=f"*Round {round_index+1}/{total_rounds}*: {question_text} :thinking_face:"
                )

                # Wait for answer
                try:
                    user, ts = await self._wait_for_answer(channel, answer)
                except asyncio.TimeoutError:
                    await self.app.client.chat_postMessage(
                        channel=channel,
                        text=f":hourglass_flowing_sand: Time's up! The answer was *{answer}*."
                    )
                    continue

                # Record score & celebrate
                await record_score(game_id, user)
                await self.app.client.reactions_add(
                    channel=channel, name="tada", timestamp=ts
                )
                witty = await get_witty_response(user, question_text)
                await self.app.client.chat_postMessage(channel=channel, text=witty)

            # Final leaderboard
            top_players = await get_leaderboard(game_id)
            medals = ["🥇", "🥈", "🥉"]
            lines = [f"{medals[i]} <@{p['user']}>: {p['score']}" for i, p in enumerate(top_players)]
            await self.app.client.chat_postMessage(
                channel=channel,
                text="*Game Over!* Here are the top scores:\n" + "\n".join(lines)
            )
            await finalize_game(game_id)
        except Exception as e:
            logger.exception(f"Error in game loop for channel {channel}: {e}")
        finally:
            self.active_tasks.pop(channel, None)

    async def _wait_for_answer(self, channel: str, answer: str, timeout: float = 30.0) -> tuple[str, str]:
        """
        Wait for the first matching answer in the channel or timeout.
        Returns (user_id, ts) on correct answer.
        """
        loop = asyncio.get_event_loop()
        fut: asyncio.Future = loop.create_future()
        # Register pending
        self.pending[channel] = (fut, answer)
        try:
            return await asyncio.wait_for(fut, timeout)
        finally:
            # Cleanup pending entry
            self.pending.pop(channel, None)
