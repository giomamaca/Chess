import os
import random
import string
from db.session import get_connection
from app.board import Board

def generate_code(length=8) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

class GameRepository:
    def create_open_game(self, player_id: int) -> tuple:
        """Create a quick match game with random color assignment."""
        board = Board()

        conn = get_connection()
        cur = conn.cursor()
        code = generate_code()

        if random.choice([True, False]):
            white_id = player_id
            black_id = None
        else:
            white_id = None
            black_id = player_id

        cur.execute("""
            INSERT INTO games (
                code, white_player_id, black_player_id, status
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (code, white_id, black_id, "waiting"))

        game_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return board, game_id, code

    def create_private_room(self, player_id: int) -> str:
        """Create a private room with random color assignment. Returns room code."""
        conn = get_connection()
        cur = conn.cursor()
        code = generate_code(6)

        if random.choice([True, False]):
            white_id = player_id
            black_id = None
        else:
            white_id = None
            black_id = player_id

        cur.execute("""
            INSERT INTO games (
                code, white_player_id, black_player_id, status
            )
            VALUES (%s, %s, %s, %s)
        """, (code, white_id, black_id, "private"))
        conn.commit()
        cur.close()
        conn.close()
        return code

    def join_private_room(self, code: str, player_id: int):
        """Join a private room by code. Returns (game_id, host_id, host_color) or None."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE games
            SET
                white_player_id = CASE WHEN white_player_id IS NULL THEN %s ELSE white_player_id END,
                black_player_id = CASE WHEN black_player_id IS NULL THEN %s ELSE black_player_id END,
                status = 'active'
            WHERE code = %s AND status = 'private'
              AND (white_player_id IS NULL OR black_player_id IS NULL)
            RETURNING id, white_player_id, black_player_id
        """, (player_id, player_id, code))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not result:
            return None
        game_id, white_id, black_id = result
        host_id = white_id if black_id == player_id else black_id
        joining_color = "black" if black_id == player_id else "white"
        host_color = "white" if joining_color == "black" else "black"
        return game_id, host_id, joining_color, host_color

    def get_free_lobby(self, player_id: int):
        """Find the oldest waiting quick match game not hosted by this player."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, white_player_id, black_player_id, code
            FROM games
            WHERE status = 'waiting'
              AND (white_player_id IS NULL OR black_player_id IS NULL)
              AND (white_player_id != %s OR white_player_id IS NULL)
              AND (black_player_id != %s OR black_player_id IS NULL)
            ORDER BY created_at ASC
            LIMIT 1
        """, (player_id, player_id))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result

    def join_lobby(self, game_id: int, player_id: int) -> tuple:
        """Fill the open slot in a quick match game."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE games
            SET
                white_player_id = CASE WHEN white_player_id IS NULL THEN %s ELSE white_player_id END,
                black_player_id = CASE WHEN black_player_id IS NULL THEN %s ELSE black_player_id END,
                status = 'active'
            WHERE id = %s
            RETURNING white_player_id, black_player_id, code
        """, (player_id, player_id, game_id))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        print("ipova")
        return result

    def get_game_by_gameId(self, game_id: int):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, code, white_player_id, black_player_id, status
            FROM games WHERE id = %s
        """, (game_id,))
        game = cur.fetchone()
        cur.close()
        conn.close()
        return game

    def get_game_by_code(self, code: str):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, code, white_player_id, black_player_id, status
            FROM games WHERE code = %s
        """, (code,))
        game = cur.fetchone()
        cur.close()
        conn.close()
        return game
    
    def get_game_by_player(self, user_id : int):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, code, white_player_id, black_player_id, status
            FROM games WHERE white_player_id = %s OR black_player_id = %s
        """, (user_id, user_id))
        game = cur.fetchone()
        cur.close()
        conn.close()
        return game
    
    def remove_game(self, game_id: int):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM games WHERE id = %s
        """, (game_id,))
        conn.commit()
        cur.close()
        conn.close()
    
    def get_player_color(self, user_id: int, game):
        if game[2] == user_id:
            return "white"
        return "black"
        