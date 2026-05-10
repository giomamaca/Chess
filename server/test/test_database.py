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