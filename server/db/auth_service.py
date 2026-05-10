import bcrypt
from db.user_repositories import UserRepository

class AuthService:
    def __init__(self):
        self.repo = UserRepository()

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