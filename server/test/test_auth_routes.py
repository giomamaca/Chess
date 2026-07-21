"""Auth endpoints: credentials in, remember-me token out."""

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.routes import auth_routes
from db.database_classes.user_account import UserAccount


@pytest.fixture(autouse=True)
def stub_auth(monkeypatch):
    """Swap the module-level AuthService so no test touches Postgres."""
    service = MagicMock()
    service.issue_session.return_value = "signed-token"
    monkeypatch.setattr(auth_routes, "auth", service)
    return service


def account(username="alice", password="password123"):
    return UserAccount(username=username, password=password)


class TestLogin:
    def test_good_credentials_return_a_token(self, stub_auth):
        stub_auth.login.return_value = True

        result = auth_routes.login(account())

        assert result["success"] is True
        assert result["username"] == "alice"
        assert result["token"] == "signed-token"
        assert result["expires_in_days"] == auth_routes.SESSION_TTL_DAYS

    def test_bad_credentials_issue_no_token(self, stub_auth):
        stub_auth.login.return_value = False

        result = auth_routes.login(account(password="wrong"))

        assert result["success"] is False
        assert "token" not in result
        stub_auth.issue_session.assert_not_called()


class TestRegister:
    def test_new_account_is_logged_straight_in(self, stub_auth):
        stub_auth.register.return_value = (True, "User created successfully")

        result = auth_routes.register(account())

        assert result["success"] is True
        assert result["token"] == "signed-token"

    def test_duplicate_username_is_rejected(self, stub_auth):
        """Regression: register() returns a tuple, and a non-empty tuple is
        truthy — the old `if not user` check let duplicates report success."""
        stub_auth.register.return_value = (False, "Username already exists")

        result = auth_routes.register(account())

        assert result["success"] is False
        assert result["detail"] == "Username already exists"
        stub_auth.issue_session.assert_not_called()


class TestRestoreSession:
    def test_live_token_names_the_player(self, stub_auth):
        stub_auth.resolve_session.return_value = "alice"

        result = auth_routes.restore_session(auth_routes.SessionToken(token="tok"))

        assert result == {"success": True, "username": "alice"}

    def test_expired_token_is_a_401(self, stub_auth):
        stub_auth.resolve_session.return_value = None

        with pytest.raises(HTTPException) as excinfo:
            auth_routes.restore_session(auth_routes.SessionToken(token="stale"))

        assert excinfo.value.status_code == 401


class TestLogout:
    def test_token_is_revoked_server_side(self, stub_auth):
        result = auth_routes.logout(auth_routes.SessionToken(token="tok"))

        stub_auth.revoke_session.assert_called_once_with("tok")
        assert result["success"] is True
