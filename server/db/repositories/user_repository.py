from db.session import get_connection

class UserRepository:
    def create_user(self, username: str, password_hash: str):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        conn.commit()
        cur.close()
        conn.close()

    def get_user_by_username(self, username: str):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, password_hash FROM users WHERE username = %s",
            (username,)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user

    def get_user_by_id(self, user_id: int):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, password_hash FROM users WHERE id = %s",
            (user_id,)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user