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


    conn.commit()
    cur.close()
    conn.close()

    print("Database initialized")