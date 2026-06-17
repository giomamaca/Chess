from fastapi import APIRouter
from db.auth_service import AuthService
from db.database_classes.user_account import UserAccount

router = APIRouter(prefix="/auth", tags=["auth"])
auth = AuthService()

@router.post("/login")
def login(userAccount: UserAccount):
    return auth.login(userAccount.username, userAccount.password)

@router.post("/register")
def register(userAccount: UserAccount):
    return auth.register(userAccount.username, userAccount.password)