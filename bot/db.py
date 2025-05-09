import aiosqlite
import logging

DB_PATH = "kenny.db"
logger = logging.getLogger(__name__)

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS games (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        channel  TEXT NOT NULL UNIQUE,
        total    INTEGER NOT NULL,
        current  INTEGER NOT NULL DEFAULT 0,
        state    TEXT NOT NULL DEFAULT 'in_progress'
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS scores (
        game_id  INTEGER NOT NULL,
        user     TEXT NOT NULL,
        score    INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(game_id, user),
        FOREIGN KEY(game_id) REFERENCES games(id)
    );
    """
]

async def init_db():
    """
    Initialize the database, creating tables if they don't exist.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        for stmt in SCHEMA:
            await db.execute(stmt)
        await db.commit()
    logger.info("Database initialized at %s", DB_PATH)

async def create_game(channel: str, total: int) -> int:
    """
    Create a new game for a channel. Returns the game_id.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT OR REPLACE INTO games(channel, total, current, state) VALUES (?, ?, 0, 'in_progress')",
            (channel, total)
        )
        await db.commit()
        game_id = cursor.lastrowid
    logger.info("Created game %d in channel %s with total %d", game_id, channel, total)
    return game_id

async def get_active_game(channel: str):
    """
    Fetch the active (in_progress) game for a channel.
    Returns a row dict or None.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM games WHERE channel = ? AND state = 'in_progress'", (channel,)
        )
        row = await cursor.fetchone()
    return dict(row) if row else None

async def increment_round(game_id: int):
    """
    Increment the current round counter for a game.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE games SET current = current + 1 WHERE id = ?", (game_id,)
        )
        await db.commit()
    logger.debug("Incremented round for game %d", game_id)

async def record_score(game_id: int, user: str):
    """
    Increment the score for a user in a game.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # insert or update
        await db.execute(
            "INSERT INTO scores(game_id, user, score) VALUES (?, ?, 1) "
            "ON CONFLICT(game_id, user) DO UPDATE SET score = score + 1",
            (game_id, user)
        )
        await db.commit()
    logger.info("Recorded score for user %s in game %d", user, game_id)

async def finalize_game(game_id: int):
    """
    Mark a game as finished.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE games SET state = 'finished' WHERE id = ?", (game_id,)
        )
        await db.commit()
    logger.info("Finalized game %d", game_id)

async def get_leaderboard(game_id: int, top_n: int = 3):
    """
    Return top N users by score for a game.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT user, score FROM scores WHERE game_id = ? ORDER BY score DESC LIMIT ?",
            (game_id, top_n)
        )
        rows = await cursor.fetchall()
    return [dict(r) for r in rows]
