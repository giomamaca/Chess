from db.session import get_connection

class ChatRepository:
    def save_message(self, game_id: int, sender_id: int, text: str) -> None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO chat_messages (game_id, sender_id, text)
            VALUES (%s, %s, %s)
        """, (game_id, sender_id, text))
        conn.commit()
        cur.close()
        conn.close()

    def get_messages_by_game(self, game_id: int) -> list:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.username, m.text, m.created_at
            FROM chat_messages m
            JOIN users u ON u.id = m.sender_id
            WHERE m.game_id = %s
            ORDER BY m.created_at ASC, m.id ASC
        """, (game_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows