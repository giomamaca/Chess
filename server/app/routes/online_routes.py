import json
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from .. import game_service
from ..handlers.game_handler import GameHandlers
from db.repositories.user_repository import UserRepository
from db.repositories.game_repository import GameRepository
from db.repositories.chat_repository import ChatRepository

router = APIRouter(prefix="/online", tags=["online"])

connected_users: dict = {}
board_from_game_id: dict = {}
user_repo = UserRepository()
game_repo = GameRepository()
chat_repo = ChatRepository()
game_handlers = GameHandlers(game_repo, user_repo, connected_users, board_from_game_id)


def get_active_game(username: str):
    """Returns (game_dict, game_id, my_color) or raises HTTPException(404)."""
    user = user_repo.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    game_row = game_repo.get_game_by_player(user[0])
    if not game_row:
        raise HTTPException(status_code=404, detail="No active game")
    game = board_from_game_id.get(game_row[0])
    if not game:
        raise HTTPException(status_code=404, detail="Board not found")
    my_color = "white" if game_row[2] == user[0] else "black"
    return game, game_row[0], my_color


def get_opponent_username(game_row, my_user_id: int):
    """game_row columns: id, code, white_player_id, black_player_id, status."""
    white_id, black_id = game_row[2], game_row[3]
    opponent_id = black_id if white_id == my_user_id else white_id
    if not opponent_id:
        return None
    opponent = user_repo.get_user_by_id(opponent_id)
    return opponent[1] if opponent else None


@router.get("/board")
def get_online_board(username: str):
    game, game_id, my_color = get_active_game(username)
    status = game_service.get_status(game)
    return {
        "board": game["board"].board_to_json(),
        "current_turn": status["current_turn"],
        "color": my_color,
    }


@router.get("/chat")
def get_chat_history(username: str):
    """Chat history for the user's active game — used by the frontend to
    restore messages after a refresh/reconnect."""
    _, game_id, _ = get_active_game(username)
    rows = chat_repo.get_messages_by_game(game_id)
    return {
        "messages": [{"sender": sender, "text": text} for sender, text, _ in rows]
    }


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    username = None
    game = None
    game_id = None
    opponent_username = None
    left_intentionally = False

    def ensure_game_context():
        nonlocal game, game_id, opponent_username
        if game is not None:
            return
        game, game_id, _ = get_active_game(username)
        user = user_repo.get_user_by_username(username)
        game_row = game_repo.get_game_by_gameId(game_id)
        opponent_username = get_opponent_username(game_row, user[0])

    try:
        username = await websocket.receive_text()
        connected_users[username] = websocket
        print(f"[WS] {username} connected")

        # Back before the forfeit clock ran out — call off the countdown.
        await game_handlers.handle_reconnect(username)

        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type")
            print(msg_type)

            if msg_type == "create_private_room":
                await game_handlers.handle_create_private_room(websocket, username)

            elif msg_type == "join_private_room":
                await game_handlers.handle_join_private_room(websocket, username, data)

            elif msg_type == "quick_match":
                await game_handlers.handle_quick_match(websocket, username)

            elif msg_type == "cancel_lobby":
                await game_handlers.handle_cancel_lobby(username)

            elif msg_type == "valid_moves":
                try:
                    ensure_game_context()
                except HTTPException:
                    continue
                piece_data = data.get("piece", {})
                moves = game_service.get_valid_moves(game, piece_data.get("x"), piece_data.get("y"))
                await websocket.send_text(json.dumps({"type": "valid_moves", "moves": moves}))

            elif msg_type == "move":
                try:
                    ensure_game_context()
                except HTTPException:
                    continue

                fx, fy = data["from"]
                tx, ty = data["to"]
                result = game_service.make_move(game, fx, fy, tx, ty)

                if not result.get("ok"):
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": result.get("error", "Invalid move"),
                    }))
                    continue

                state_payload = {
                    "type": "state",
                    "board": result["board"],
                    "game_status": result["game_status"],
                    "promotion": result["promotion"],
                }

                game_row = game_repo.get_game_by_gameId(game_id)
                white_user = user_repo.get_user_by_id(game_row[2]) if game_row[2] else None
                black_user = user_repo.get_user_by_id(game_row[3]) if game_row[3] else None
                recipients = {u[1] for u in (white_user, black_user) if u}

                for recipient_username in recipients:
                    socket = connected_users.get(recipient_username)
                    if socket:
                        await socket.send_text(json.dumps(state_payload))

                if result["game_status"]["game_state"] in ("checkmate", "stalemate"):
                    game_over_payload = {
                        "type": "game_over",
                        "result": result["game_status"]["game_state"],
                        "current_turn": result["game_status"]["current_turn"],
                        "winner": result["game_status"]["winner"],
                    }
                    for recipient_username in recipients:
                        socket = connected_users.get(recipient_username)
                        if socket:
                            await socket.send_text(json.dumps(game_over_payload))

                    game_repo.mark_finished(game_id)
                    board_from_game_id.pop(game_id, None)
                    game = None

            elif msg_type == "promote":
                try:
                    ensure_game_context()
                except HTTPException:
                    continue

                game_service.promote_pawn(game, data["x"], data["y"], data["piece"])
                board_obj = game["board"]
                promotion_payload = {
                    "type": "board_update",
                    "board": board_obj.board_to_json(),
                    "current_turn": board_obj.current_turn,
                }
                await websocket.send_text(json.dumps(promotion_payload))
                if opponent_username and opponent_username in connected_users:
                    await connected_users[opponent_username].send_text(json.dumps(promotion_payload))

            elif msg_type == "chat":
                try:
                    ensure_game_context()
                except HTTPException:
                    continue

                text = (data.get("text") or "").strip()
                if not text:
                    continue
                # Basic guard against absurdly long messages
                text = text[:500]

                sender = user_repo.get_user_by_username(username)
                if sender:
                    chat_repo.save_message(game_id, sender[0], text)

                chat_payload = {
                    "type": "chat",
                    "sender": username,
                    "text": text,
                }

                game_row = game_repo.get_game_by_gameId(game_id)
                white_user = user_repo.get_user_by_id(game_row[2]) if game_row[2] else None
                black_user = user_repo.get_user_by_id(game_row[3]) if game_row[3] else None
                recipients = {u[1] for u in (white_user, black_user) if u}

                for recipient_username in recipients:
                    socket = connected_users.get(recipient_username)
                    if socket:
                        await socket.send_text(json.dumps(chat_payload))

            elif msg_type == "leave":
                left_intentionally = True
                try:
                    ensure_game_context()
                except HTTPException:
                    break
                await game_handlers.handle_leave(username, game_id, opponent_username)
                game = None
                break

    except WebSocketDisconnect:
        pass
    finally:
        # A reconnect may already have replaced this entry — don't evict the
        # live socket while tidying up the stale one.
        if username and connected_users.get(username) is websocket:
            del connected_users[username]
            user = user_repo.get_user_by_username(username)
            if user:
                game_row = game_repo.get_game_by_player(user[0])
                if game_row:
                    alone_in_lobby = (
                        (game_row[2] == user[0] and game_row[3] is None)
                        or (game_row[3] == user[0] and game_row[2] is None)
                    )
                    if alone_in_lobby:
                        game_repo.remove_game(game_row[0])
                        board_from_game_id.pop(game_row[0], None)
                    elif not left_intentionally:
                        # Dropped mid-game: start the forfeit countdown.
                        await game_handlers.handle_disconnect(
                            username,
                            game_row[0],
                            get_opponent_username(game_row, user[0]),
                        )
            print(f"[WS] {username} disconnected")