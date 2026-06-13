import pytest
from unittest.mock import MagicMock, patch
import bcrypt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── AuthService tests ──────────────────────────────────────────────

class TestAuthService:
    def setup_method(self):
        with patch("db.user_repositories.get_connection"), \
             patch("db.init_db.get_connection"):
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
        with patch("db.init_db.get_connection"), \
             patch("db.user_repositories.get_connection"):
            from db.user_repositories import UserRepository
            self.repo = UserRepository()

    def test_create_user(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        with patch("db.user_repositories.get_connection", return_value=mock_conn):
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

        with patch("db.user_repositories.get_connection", return_value=mock_conn):
            result = self.repo.get_user_by_username("alice")

        assert result == (1, "alice", "hashed_pw")

    def test_get_user_by_username_not_found(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None

        with patch("db.user_repositories.get_connection", return_value=mock_conn):
            result = self.repo.get_user_by_username("ghost")

        assert result is None


# ── GameRepository tests ───────────────────────────────────────────

class TestGameRepository:
    def setup_method(self):
        with patch("db.game_repository.get_connection"), \
             patch("db.init_db.get_connection"):
            from db.game_repository import GameRepository
            self.repo = GameRepository()

    def _mock_conn(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        return mock_conn, mock_cur

    def test_create_game(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = (42,)

        with patch("db.game_repository.get_connection", return_value=mock_conn):
            game_id = self.repo.create_game(1, 2)

        assert game_id == 42
        mock_conn.commit.assert_called_once()

    def test_create_open_game_returns_id_and_code(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = (10,)

        with patch("db.game_repository.get_connection", return_value=mock_conn), \
             patch("db.game_repository.random.choice", return_value=True):
            game_id, code = self.repo.create_open_game(1)

        assert game_id == 10
        assert isinstance(code, str)
        assert len(code) == 8
        mock_conn.commit.assert_called_once()

    def test_create_open_game_white_assignment(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = (1,)

        with patch("db.game_repository.get_connection", return_value=mock_conn), \
             patch("db.game_repository.random.choice", return_value=True):
            self.repo.create_open_game(99)

        args = mock_cur.execute.call_args[0][1]
        assert args[1] == 99   # white_player_id
        assert args[2] is None  # black_player_id

    def test_create_open_game_black_assignment(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = (1,)

        with patch("db.game_repository.get_connection", return_value=mock_conn), \
             patch("db.game_repository.random.choice", return_value=False):
            self.repo.create_open_game(99)

        args = mock_cur.execute.call_args[0][1]
        assert args[1] is None  # white_player_id
        assert args[2] == 99    # black_player_id

    def test_create_private_room_returns_code(self):
        mock_conn, mock_cur = self._mock_conn()

        with patch("db.game_repository.get_connection", return_value=mock_conn):
            code = self.repo.create_private_room(1)

        assert isinstance(code, str)
        assert len(code) == 6
        mock_conn.commit.assert_called_once()

    def test_join_private_room_success(self):
        mock_conn, mock_cur = self._mock_conn()
        # player_id=2 joins, white=1, black=2
        mock_cur.fetchone.return_value = (10, 1, 2)

        with patch("db.game_repository.get_connection", return_value=mock_conn):
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

        with patch("db.game_repository.get_connection", return_value=mock_conn):
            result = self.repo.join_private_room("BADCODE", 2)

        assert result is None

    def test_get_free_lobby_found(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = (5, 3, None, "XY12AB34")

        with patch("db.game_repository.get_connection", return_value=mock_conn):
            result = self.repo.get_free_lobby(99)

        assert result == (5, 3, None, "XY12AB34")

    def test_get_free_lobby_not_found(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = None

        with patch("db.game_repository.get_connection", return_value=mock_conn):
            result = self.repo.get_free_lobby(99)

        assert result is None

    def test_join_lobby(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = (1, 2, "ABCD1234")

        with patch("db.game_repository.get_connection", return_value=mock_conn):
            result = self.repo.join_lobby(5, 2)

        assert result == (1, 2, "ABCD1234")
        mock_conn.commit.assert_called_once()

    def test_get_game_found(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = (1, "ABCD1234", 1, 2, "white", "active")

        with patch("db.game_repository.get_connection", return_value=mock_conn):
            result = self.repo.get_game(1)

        assert result == (1, "ABCD1234", 1, 2, "white", "active")

    def test_get_game_not_found(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = None

        with patch("db.game_repository.get_connection", return_value=mock_conn):
            result = self.repo.get_game(999)

        assert result is None

    def test_get_game_by_code_found(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = (1, "ABCD1234", 1, 2, "white", "active")

        with patch("db.game_repository.get_connection", return_value=mock_conn):
            result = self.repo.get_game_by_code("ABCD1234")

        assert result == (1, "ABCD1234", 1, 2, "white", "active")

    def test_get_game_by_code_not_found(self):
        mock_conn, mock_cur = self._mock_conn()
        mock_cur.fetchone.return_value = None

        with patch("db.game_repository.get_connection", return_value=mock_conn):
            result = self.repo.get_game_by_code("INVALID")

        assert result is None