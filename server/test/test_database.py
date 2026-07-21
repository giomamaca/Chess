import pytest
from unittest.mock import MagicMock, patch
import bcrypt

USER_REPO = "db.repositories.user_repository.get_connection"
GAME_REPO = "db.repositories.game_repository.get_connection"


# ── AuthService tests ──────────────────────────────────────────────

class TestAuthService:
    def setup_method(self):
        from db.auth_service import AuthService
        self.auth = AuthService()

    def test_register_success(self):
        self.auth.repo.get_user_by_username = MagicMock(return_value=None)
        self.auth.repo.create_user = MagicMock()

        success, msg = self.auth.register("alice", "password123")

        assert success is True
        assert msg == "User created successfully"
        self.auth.repo.create_user.assert_called_once()

    def test_register_duplicate_username(self):
        self.auth.repo.get_user_by_username = MagicMock(return_value=(1, "alice", "hash"))

        success, msg = self.auth.register("alice", "password123")

        assert success is False
        assert msg == "Username already exists"

    def test_login_success(self):
        password = "password123"
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        self.auth.repo.get_user_by_username = MagicMock(return_value=(1, "alice", hashed))

        result = self.auth.login("alice", password)

        assert result is True

    def test_login_wrong_password(self):
        hashed = bcrypt.hashpw(b"correctpassword", bcrypt.gensalt()).decode()
        self.auth.repo.get_user_by_username = MagicMock(return_value=(1, "alice", hashed))

        result = self.auth.login("alice", "wrongpassword")

        assert result is False

    def test_login_user_not_found(self):
        self.auth.repo.get_user_by_username = MagicMock(return_value=None)

        result = self.auth.login("ghost", "password123")

        assert result is False


# ── UserRepository tests ───────────────────────────────────────────

class TestUserRepository:
    def setup_method(self):
        from db.repositories.user_repository import UserRepository
        self.repo = UserRepository()

    def test_create_user(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        with patch(USER_REPO, return_value=mock_conn):
            self.repo.create_user("alice", "hashed_pw")

        mock_cur.execute.assert_called_once()
        args = mock_cur.execute.call_args[0]
        assert "alice" in args[1]
        assert "hashed_pw" in args[1]
        mock_conn.commit.assert_called_once()

    def test_get_user_by_username_found(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = (1, "alice", "hashed_pw")

        with patch(USER_REPO, return_value=mock_conn):
            result = self.repo.get_user_by_username("alice")

        assert result == (1, "alice", "hashed_pw")

    def test_get_user_by_username_not_found(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None

        with patch(USER_REPO, return_value=mock_conn):
            result = self.repo.get_user_by_username("ghost")

        assert result is None


# ── GameRepository tests ───────────────────────────────────────────

class TestGameRepository:
    def setup_method(self):
        from db.repositories.game_repository import GameRepository
        self.repo = GameRepository()

    def _mock_conn(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        return mock_conn, mock_cur

    def test_create_open_game_returns_board_id_and_code(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = (10,)

        with patch(GAME_REPO, return_value=mock_conn), \
             patch("db.repositories.game_repository.random.choice", return_value=True):
            board, game_id, code = self.repo.create_open_game(1)

        assert board is not None
        assert game_id == 10
        assert isinstance(code, str)
        assert len(code) == 8
        mock_conn.commit.assert_called_once()

    def test_create_open_game_white_assignment(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = (1,)

        with patch(GAME_REPO, return_value=mock_conn), \
             patch("db.repositories.game_repository.random.choice", return_value=True):
            self.repo.create_open_game(99)

        args = mock_cur.execute.call_args[0][1]
        assert args[1] == 99   # white_player_id
        assert args[2] is None  # black_player_id

    def test_create_open_game_black_assignment(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = (1,)

        with patch(GAME_REPO, return_value=mock_conn), \
             patch("db.repositories.game_repository.random.choice", return_value=False):
            self.repo.create_open_game(99)

        args = mock_cur.execute.call_args[0][1]
        assert args[1] is None  # white_player_id
        assert args[2] == 99    # black_player_id

    def test_create_private_room_returns_code(self):
        mock_conn, mock_cur = self._mock_conn()

        with patch(GAME_REPO, return_value=mock_conn):
            code = self.repo.create_private_room(1)

        assert isinstance(code, str)
        assert len(code) == 6
        mock_conn.commit.assert_called_once()

    def test_join_private_room_success(self):
        mock_conn, mock_cur = self._mock_conn()
        # player_id=2 joins, white=1, black=2
        mock_cur.fetchone.return_value = (10, 1, 2)

        with patch(GAME_REPO, return_value=mock_conn):
            result = self.repo.join_private_room("ABC123", 2)

        assert result is not None
        game_id, host_id, joining_color, host_color = result
        assert game_id == 10
        assert host_id == 1
        assert joining_color == "black"
        assert host_color == "white"

    def test_join_private_room_not_found(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = None

        with patch(GAME_REPO, return_value=mock_conn):
            result = self.repo.join_private_room("BADCODE", 2)

        assert result is None

    def test_get_free_lobby_found(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = (5, 3, None, "XY12AB34")

        with patch(GAME_REPO, return_value=mock_conn):
            result = self.repo.get_free_lobby(99)

        assert result == (5, 3, None, "XY12AB34")

    def test_get_free_lobby_not_found(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = None

        with patch(GAME_REPO, return_value=mock_conn):
            result = self.repo.get_free_lobby(99)

        assert result is None

    def test_join_lobby(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = (1, 2, "ABCD1234")

        with patch(GAME_REPO, return_value=mock_conn):
            result = self.repo.join_lobby(5, 2)

        assert result == (1, 2, "ABCD1234")
        mock_conn.commit.assert_called_once()

    def test_get_game_by_gameId_found(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = (1, "ABCD1234", 1, 2, "active")

        with patch(GAME_REPO, return_value=mock_conn):
            result = self.repo.get_game_by_gameId(1)

        assert result == (1, "ABCD1234", 1, 2, "active")

    def test_get_game_by_gameId_not_found(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = None

        with patch(GAME_REPO, return_value=mock_conn):
            result = self.repo.get_game_by_gameId(999)

        assert result is None

    def test_get_game_by_code_found(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = (1, "ABCD1234", 1, 2, "white", "active")

        with patch(GAME_REPO, return_value=mock_conn):
            result = self.repo.get_game_by_code("ABCD1234")

        assert result == (1, "ABCD1234", 1, 2, "white", "active")

    def test_get_game_by_code_not_found(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = None

        with patch(GAME_REPO, return_value=mock_conn):
            result = self.repo.get_game_by_code("INVALID")

        assert result is None

    def test_get_game_by_player_skips_finished_games(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = None

        with patch(GAME_REPO, return_value=mock_conn):
            self.repo.get_game_by_player(5)

        sql = mock_cur.execute.call_args[0][0]
        assert "status IN ('waiting', 'private', 'active')" in sql

    def test_get_pending_games_matches_only_half_empty_lobbies(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchall.return_value = [(1, "CODE1234", 5, None, "waiting")]

        with patch(GAME_REPO, return_value=mock_conn):
            result = self.repo.get_pending_games_by_player(5)

        sql, params = mock_cur.execute.call_args[0]
        # A lobby only counts as pending while the other seat is still empty.
        assert "white_player_id = %s AND black_player_id IS NULL" in sql
        assert "black_player_id = %s AND white_player_id IS NULL" in sql
        assert params == (5, 5)
        assert result == [(1, "CODE1234", 5, None, "waiting")]

    def test_get_pending_games_returns_every_stale_lobby(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchall.return_value = [
            (2, "CODE5678", None, 5, "waiting"),
            (1, "CODE1234", 5, None, "waiting"),
        ]

        with patch(GAME_REPO, return_value=mock_conn):
            result = self.repo.get_pending_games_by_player(5)

        assert len(result) == 2

    def test_get_pending_games_none(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchall.return_value = []

        with patch(GAME_REPO, return_value=mock_conn):
            assert self.repo.get_pending_games_by_player(5) == []

    def test_mark_finished_keeps_the_row(self):
        mock_conn, mock_cur = self._mock_conn()

        with patch(GAME_REPO, return_value=mock_conn):
            self.repo.mark_finished(7)

        sql, params = mock_cur.execute.call_args[0]
        assert "UPDATE games SET status = 'finished'" in sql
        assert params == (7,)
        mock_conn.commit.assert_called_once()

    def test_remove_game_deletes_the_row(self):
        mock_conn, mock_cur = self._mock_conn()

        with patch(GAME_REPO, return_value=mock_conn):
            self.repo.remove_game(7)

        sql, params = mock_cur.execute.call_args[0]
        assert "DELETE FROM games" in sql
        assert params == (7,)
        mock_conn.commit.assert_called_once()