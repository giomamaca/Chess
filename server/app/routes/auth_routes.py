from fastapi import APIRouter, HTTPException
from db.auth_service import AuthService
from db.database_classes.user_account import UserAccount

router = APIRouter(prefix="/auth", tags=["auth"])
auth = AuthService()

@router.post("/login")
def login(userAccount: UserAccount):
    user = auth.login(userAccount.username, userAccount.password)
    if not user:
        return {"success": False, "detail": "Invalid credentials"}
    return {"success": True, "user": user}

@router.post("/register")
def register(userAccount: UserAccount):
    user = auth.register(userAccount.username, userAccount.password)
    if not user:
        raise HTTPException(status_code=400, detail="Registration failed")
    return {"success": True, "user": user}