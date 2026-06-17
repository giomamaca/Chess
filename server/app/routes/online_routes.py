import json
import uuid

from fastapi import APIRouter, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from ..board import Board
from ..move_generator import MoveGenerator
from ..rules_engine import RulesEngine
from ..handlers.game_handler import GameHandlers

from db.user_repositories import UserRepository
from db.game_repository import GameRepository

router = APIRouter(prefix="/online", tags=["online"])

connected_users: dict = {}
user_repo = UserRepository()
game_repo = GameRepository()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    username = None

    try:
        username = await websocket.receive_text()
        connected_users[username] = websocket
        print(f"[WS] {username} connected")


        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type")

            if msg_type == "create_private_room":
                await game_handlers.handle_create_private_room(websocket, username)

            elif msg_type == "join_private_room":
                await game_handlers.handle_join_private_room(websocket, username, data)

            elif msg_type == "quick_match":
                await game_handlers.handle_quick_match(websocket, username)

    except WebSocketDisconnect:
        if username and username in connected_users:
            del connected_users[username]
            user = user_repo.get_user_by_username(username)
            game = game_repo.get_game_by_player(user[0])
            if (game[2] == user[0] and game[3] is None) or (game[3] == user[0] and game[2] is None):
                game_repo.remove_game(game[0])
            
            print(f"[WS] {username} disconnected")
