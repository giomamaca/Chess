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

app.include_router(auth_routes.router)
app.include_router(offline_routes.router)
app.include_router(online_routes.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     username = None

#     try:
#         username = await websocket.receive_text()
#         connected_users[username] = websocket
#         print(f"[WS] {username} connected")


#         while True:
#             raw = await websocket.receive_text()
#             data = json.loads(raw)
#             msg_type = data.get("type")

#             if msg_type == "create_private_room":
#                 await game_handlers.handle_create_private_room(websocket, username)

#             elif msg_type == "join_private_room":
#                 await game_handlers.handle_join_private_room(websocket, username, data)

#             elif msg_type == "quick_match":
#                 await game_handlers.handle_quick_match(websocket, username)

#     except WebSocketDisconnect:
#         if username and username in connected_users:
#             del connected_users[username]
#             user = user_repo.get_user_by_username(username)
#             game = game_repo.get_game_by_player(user[0])
#             if (game[2] == user[0] and game[3] is None) or (game[3] == user[0] and game[2] is None):
#                 game_repo.remove_game(game[0])
            
#             print(f"[WS] {username} disconnected")


BUILD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "client", "build")

app.mount("/static", StaticFiles(directory=os.path.join(BUILD_DIR, "static")), name="static")
app.mount("/pieces", StaticFiles(directory=os.path.join(BUILD_DIR, "pieces")), name="pieces")

@app.get("/")
def serve_react():
    return FileResponse(os.path.join(BUILD_DIR, "index.html"))