import json
from fastapi import WebSocket

from .. import game_service


class GameHandlers:
    def __init__(self, game_repo, user_repo, connected_users: dict, board_from_game_id: dict):
        self.game_repo = game_repo
        self.user_repo = user_repo
        self.connected_users = connected_users
        self.board_from_game_id = board_from_game_id

    def _game_start_payload(self, game_id, code, color, game):
        board = game["board"]
        return {
            "type": "game_start",
            "game_id": game_id,
            "code": code,
            "color": color,
            "board": board.board_to_json(),
            "current_turn": board.current_turn,
        }

    async def handle_create_private_room(self, websocket: WebSocket, username: str):
        user = self.user_repo.get_user_by_username(username)
        if not user:
            await websocket.send_text(json.dumps({"type": "error", "message": "User not found"}))
            return

        user_id = user[0]
        room_code = self.game_repo.create_private_room(user_id)
        await websocket.send_text(json.dumps({
            "type": "room_created",
            "room_code": room_code
        }))

    async def handle_join_private_room(self, websocket: WebSocket, username: str, data: dict):
        code = data.get("room_code", "").strip().upper()
        user = self.user_repo.get_user_by_username(username)
        if not user:
            await websocket.send_text(json.dumps({"type": "error", "message": "User not found"}))
            return

        user_id = user[0]
        result = self.game_repo.join_private_room(code, user_id)
        if not result:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Room not found or already full"
            }))
            return

        game_id, host_id, joining_color, host_color = result
        host = self.user_repo.get_user_by_id(host_id)
        game = self.board_from_game_id.get(game_id)

        if game is None:
            game = game_service.create_game()
            self.board_from_game_id[game_id] = game

        await websocket.send_text(json.dumps(
            self._game_start_payload(game_id, code, joining_color, game)
        ))

        if host and host[1] in self.connected_users:
            await self.connected_users[host[1]].send_text(json.dumps(
                self._game_start_payload(game_id, code, host_color, game)
            ))

    async def handle_quick_match(self, websocket: WebSocket, username: str):
        user = self.user_repo.get_user_by_username(username)
        if not user:
            await websocket.send_text(json.dumps({"type": "error", "message": "User not found"}))
            return

        user_id = user[0]
        free_game = self.game_repo.get_free_lobby(user_id)
        if free_game:
            game_id, white_id, black_id, code = free_game
            self.game_repo.join_lobby(game_id, user_id)

            host_id = white_id if white_id is not None else black_id
            joining_color = "white" if white_id is None else "black"
            host_color = "black" if joining_color == "white" else "white"
            host_user = self.user_repo.get_user_by_id(host_id)

            game = self.board_from_game_id.get(game_id)
            if game is None:
                game = game_service.create_game()
                self.board_from_game_id[game_id] = game

            await websocket.send_text(json.dumps(
                self._game_start_payload(game_id, code, joining_color, game)
            ))

            if host_user and host_user[1] in self.connected_users:
                await self.connected_users[host_user[1]].send_text(json.dumps(
                    self._game_start_payload(game_id, code, host_color, game)
                ))
        else:
            board, game_id, code = self.game_repo.create_open_game(user_id)
            await websocket.send_text(json.dumps({
                "type": "searching",
                "game_id": game_id,
                "code": code
            }))
            self.board_from_game_id[game_id] = game_service.create_game(board)