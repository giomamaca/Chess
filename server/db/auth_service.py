import hashlib
import secrets

import bcrypt

from .repositories.user_repository import UserRepository
from .repositories.session_repository import SessionRepository

SESSION_TTL_DAYS = 30


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class AuthService:
    def __init__(self):
        self.repo = UserRepository()
        self.sessions = SessionRepository()

    def register(self, username, password):
        existing = self.repo.get_user_by_username(username)
        if existing:
            return False, "Username already exists"

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        self.repo.create_user(username, hashed)
        return True, "User created successfully"

    def login(self, username, password):
        user = self.repo.get_user_by_username(username)
        if not user:
            return False

        stored_hash = user[2]
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode()

        return bcrypt.checkpw(password.encode(), stored_hash)

    # ---------- Persistent sessions ----------

    def issue_session(self, username: str):
        """Mint a remember-me token for an already-authenticated user.
        Returns the raw token — it is never stored or logged anywhere else."""
        user = self.repo.get_user_by_username(username)
        if not user:
            return None

        token = secrets.token_urlsafe(32)
        self.sessions.create(user[0], _hash_token(token), SESSION_TTL_DAYS)
        return token

    def resolve_session(self, token: str):
        """Returns the username behind a live token, or None."""
        if not token:
            return None

        token_hash = _hash_token(token)
        row = self.sessions.get_user(token_hash)
        if not row:
            return None

        self.sessions.touch(token_hash, SESSION_TTL_DAYS)
        return row[1]

    def revoke_session(self, token: str):
        if token:
            self.sessions.delete(_hash_token(token))
