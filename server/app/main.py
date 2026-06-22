import os
import json
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .board import Board
from .move_generator import MoveGenerator
from .rules_engine import RulesEngine

from db.auth_service import AuthService
from db.database_classes.user_account import UserAccount
from db.game_repository import GameRepository
from db.user_repositories import UserRepository
from db.init_db import init_db

from .handlers.game_handler import GameHandlers

from .routes import online_routes, offline_routes, auth_routes

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(offline_routes.router)
app.include_router(online_routes.router)

BUILD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "client", "build")

app.mount("/static", StaticFiles(directory=os.path.join(BUILD_DIR, "static")), name="static")
app.mount("/pieces", StaticFiles(directory=os.path.join(BUILD_DIR, "pieces")), name="pieces")

@app.get("/")
def serve_react():
    return FileResponse(os.path.join(BUILD_DIR, "index.html"))