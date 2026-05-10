from db.session import get_connection
from db.init_db import init_db

class UserRepository:
    def __init__(self):
        init_db()
    
    def create_user(self, username, password_hash):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        conn.commit()
        cur.close()
        conn.close()

    def get_user_by_username(self, username):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, password_hash FROM users WHERE username=%s",
            (username,)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user