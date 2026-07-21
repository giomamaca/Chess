"""Remember-me sessions: token issuing, lookup and revocation."""

import hashlib
from unittest.mock import MagicMock, patch

from db.auth_service import AuthService, SESSION_TTL_DAYS


def sha256(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# ── AuthService session handling ───────────────────────────────────

class TestIssueSession:
    def setup_method(self):
        self.auth = AuthService()
        self.auth.repo = MagicMock()
        self.auth.sessions = MagicMock()

    def test_stores_the_hash_never_the_raw_token(self):
        self.auth.repo.get_user_by_username.return_value = (7, "alice", "pw_hash")

        token = self.auth.issue_session("alice")

        user_id, token_hash, ttl = self.auth.sessions.create.call_args[0]
        assert user_id == 7
        assert ttl == SESSION_TTL_DAYS
        assert token_hash == sha256(token)
        assert token not in token_hash

    def test_token_is_long_enough_to_be_unguessable(self):
        self.auth.repo.get_user_by_username.return_value = (7, "alice", "pw_hash")

        token = self.auth.issue_session("alice")

        assert len(token) >= 32

    def test_every_token_is_different(self):
        self.auth.repo.get_user_by_username.return_value = (7, "alice", "pw_hash")

        tokens = {self.auth.issue_session("alice") for _ in range(5)}

        assert len(tokens) == 5

    def test_unknown_user_gets_no_session(self):
        self.auth.repo.get_user_by_username.return_value = None

        assert self.auth.issue_session("ghost") is None
        self.auth.sessions.create.assert_not_called()


class TestResolveSession:
    def setup_method(self):
        self.auth = AuthService()
        self.auth.repo = MagicMock()
        self.auth.sessions = MagicMock()

    def test_live_token_returns_username(self):
        self.auth.sessions.get_user.return_value = (7, "alice")

        assert self.auth.resolve_session("raw-token") == "alice"
        self.auth.sessions.get_user.assert_called_once_with(sha256("raw-token"))

    def test_lookup_slides_the_expiry_forward(self):
        self.auth.sessions.get_user.return_value = (7, "alice")

        self.auth.resolve_session("raw-token")

        self.auth.sessions.touch.assert_called_once_with(
            sha256("raw-token"), SESSION_TTL_DAYS
        )

    def test_expired_or_unknown_token_is_rejected(self):
        self.auth.sessions.get_user.return_value = None

        assert self.auth.resolve_session("raw-token") is None
        self.auth.sessions.touch.assert_not_called()

    def test_missing_token_never_hits_the_database(self):
        assert self.auth.resolve_session("") is None
        assert self.auth.resolve_session(None) is None
        self.auth.sessions.get_user.assert_not_called()


class TestRevokeSession:
    def setup_method(self):
        self.auth = AuthService()
        self.auth.repo = MagicMock()
        self.auth.sessions = MagicMock()

    def test_deletes_by_hash(self):
        self.auth.revoke_session("raw-token")

        self.auth.sessions.delete.assert_called_once_with(sha256("raw-token"))

    def test_empty_token_is_a_noop(self):
        self.auth.revoke_session("")

        self.auth.sessions.delete.assert_not_called()


# ── SessionRepository SQL ──────────────────────────────────────────

class TestSessionRepository:
    def setup_method(self):
        from db.repositories.session_repository import SessionRepository
        self.repo = SessionRepository()

    def _mock_conn(self):
        conn = MagicMock()
        cur = MagicMock()
        conn.cursor.return_value = cur
        return conn, cur

    def test_create_persists_hash_user_and_ttl(self):
        conn, cur = self._mock_conn()

        with patch("db.repositories.session_repository.get_connection", return_value=conn):
            self.repo.create(7, "abc123", 30)

        sql, params = cur.execute.call_args[0]
        assert "INSERT INTO sessions" in sql
        assert params == ("abc123", 7, 30)
        conn.commit.assert_called_once()

    def test_get_user_ignores_expired_sessions(self):
        conn, cur = self._mock_conn()
        cur.fetchone.return_value = (7, "alice")

        with patch("db.repositories.session_repository.get_connection", return_value=conn):
            result = self.repo.get_user("abc123")

        sql, params = cur.execute.call_args[0]
        assert "expires_at > CURRENT_TIMESTAMP" in sql
        assert params == ("abc123",)
        assert result == (7, "alice")

    def test_get_user_returns_none_when_missing(self):
        conn, cur = self._mock_conn()
        cur.fetchone.return_value = None

        with patch("db.repositories.session_repository.get_connection", return_value=conn):
            assert self.repo.get_user("nope") is None

    def test_touch_pushes_expiry_out_and_commits(self):
        conn, cur = self._mock_conn()

        with patch("db.repositories.session_repository.get_connection", return_value=conn):
            self.repo.touch("abc123", 30)

        sql, params = cur.execute.call_args[0]
        assert "UPDATE sessions" in sql
        assert params == (30, "abc123")
        conn.commit.assert_called_once()

    def test_delete_removes_the_row(self):
        conn, cur = self._mock_conn()

        with patch("db.repositories.session_repository.get_connection", return_value=conn):
            self.repo.delete("abc123")

        sql, params = cur.execute.call_args[0]
        assert "DELETE FROM sessions" in sql
        assert params == ("abc123",)
        conn.commit.assert_called_once()

    def test_delete_expired_sweeps_stale_rows(self):
        conn, cur = self._mock_conn()

        with patch("db.repositories.session_repository.get_connection", return_value=conn):
            self.repo.delete_expired()

        sql = cur.execute.call_args[0][0]
        assert "DELETE FROM sessions" in sql
        assert "expires_at <= CURRENT_TIMESTAMP" in sql
        conn.commit.assert_called_once()
