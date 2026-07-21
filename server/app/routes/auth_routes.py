from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db.auth_service import AuthService, SESSION_TTL_DAYS
from db.database_classes.user_account import UserAccount

router = APIRouter(prefix="/auth", tags=["auth"])
auth = AuthService()


class SessionToken(BaseModel):
    token: str


@router.post("/login")
def login(userAccount: UserAccount):
    if not auth.login(userAccount.username, userAccount.password):
        return {"success": False, "detail": "Invalid credentials"}
    return _session_response(userAccount.username)


@router.post("/register")
def register(userAccount: UserAccount):
    created, detail = auth.register(userAccount.username, userAccount.password)
    if not created:
        return {"success": False, "detail": detail}
    return _session_response(userAccount.username)


@router.post("/session")
def restore_session(body: SessionToken):
    """Exchange a remember-me token for the username behind it, so a returning
    player skips the login screen."""
    username = auth.resolve_session(body.token)
    if not username:
        raise HTTPException(status_code=401, detail="Session expired")
    return {"success": True, "username": username}


@router.post("/logout")
def logout(body: SessionToken):
    auth.revoke_session(body.token)
    return {"success": True}


def _session_response(username: str):
    return {
        "success": True,
        "username": username,
        "token": auth.issue_session(username),
        "expires_in_days": SESSION_TTL_DAYS,
    }
