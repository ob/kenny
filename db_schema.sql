-- games table
CREATE TABLE IF NOT EXISTS games (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  channel  TEXT NOT NULL,
  total    INTEGER NOT NULL,
  current  INTEGER NOT NULL DEFAULT 0,
  state    TEXT NOT NULL  -- e.g. 'in_progress', 'finished'
);

-- players & scores
CREATE TABLE IF NOT EXISTS scores (
  game_id  INTEGER REFERENCES games(id),
  user     TEXT,
  score    INTEGER DEFAULT 0,
  PRIMARY KEY(game_id, user)
);
