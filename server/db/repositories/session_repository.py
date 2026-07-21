from db.session import get_connection


class SessionRepository:
    """Persistent login sessions. Rows are keyed by the SHA-256 of the token,
    never the token itself."""

    def create(self, user_id: int, token_hash: str, ttl_days: int):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sessions (token_hash, user_id, expires_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP + (%s * INTERVAL '1 day'))
        """, (token_hash, user_id, ttl_days))
        conn.commit()
        cur.close()
        conn.close()

    def get_user(self, token_hash: str):
        """Returns (user_id, username) for a live session, or None."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, u.username
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token_hash = %s AND s.expires_at > CURRENT_TIMESTAMP
        """, (token_hash,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row

    def touch(self, token_hash: str, ttl_days: int):
        """Slide the expiry forward so an active player is never logged out."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE sessions
            SET expires_at = CURRENT_TIMESTAMP + (%s * INTERVAL '1 day')
            WHERE token_hash = %s
        """, (ttl_days, token_hash))
        conn.commit()
        cur.close()
        conn.close()

    def delete(self, token_hash: str):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM sessions WHERE token_hash = %s", (token_hash,))
        conn.commit()
        cur.close()
        conn.close()

    def delete_expired(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM sessions WHERE expires_at <= CURRENT_TIMESTAMP")
        conn.commit()
        cur.close()
        conn.close()
