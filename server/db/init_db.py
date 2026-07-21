from db.session import get_connection

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Games table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id SERIAL PRIMARY KEY,
            code VARCHAR(10) UNIQUE,

            white_player_id INTEGER REFERENCES users(id),
            black_player_id INTEGER REFERENCES users(id),

            status VARCHAR(20) DEFAULT 'waiting',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_state (
            id SERIAL PRIMARY KEY,
            game_id INTEGER REFERENCES games(id),
            current_turn VARCHAR(10) DEFAULT 'white',
            board_state VARCHAR(100)
        );
    """)

    # Chat messages — one row per message, tied to a game.
    # ON DELETE CASCADE keeps things tidy: when remove_game deletes a
    # game row, its chat history goes with it automatically.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id SERIAL PRIMARY KEY,
            game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
            sender_id INTEGER REFERENCES users(id),
            text VARCHAR(500) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Speeds up "load all messages for game X ordered by time"
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_chat_messages_game
        ON chat_messages (game_id, created_at);
    """)

    # Long-lived login sessions — lets the client skip the login screen on a
    # revisit. Only the SHA-256 of the token is stored, so a dump of this table
    # can't be replayed as a login.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token_hash CHAR(64) PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL
        );
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_sessions_user
        ON sessions (user_id);
    """)

    conn.commit()
    cur.close()
    conn.close()

    print("Database initialized")

