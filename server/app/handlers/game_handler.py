import asyncio
import json
from fastapi import WebSocket

from .. import game_service

# How long a player who drops out has to reconnect before forfeiting.
ABANDON_SECONDS = 120


class GameHandlers:
    def __init__(self, game_repo, user_repo, connected_users: dict, board_from_game_id: dict):
        self.game_repo = game_repo
        self.user_repo = user_repo
        self.connected_users = connected_users
        self.board_from_game_id = board_from_game_id
        # username -> {"task", "game_id", "opponent"} while a grace period runs.
        self.abandon_timers: dict = {}

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
            # Reuse a lobby this player already owns instead of stacking up a
            # new one every time the search screen mounts.
            own_lobby = next(
                (g for g in self.game_repo.get_pending_games_by_player(user_id)
                 if g[4] == "waiting"),
                None
            )
            if own_lobby:
                await websocket.send_text(json.dumps({
                    "type": "searching",
                    "game_id": own_lobby[0],
                    "code": own_lobby[1]
                }))
                return

            board, game_id, code = self.game_repo.create_open_game(user_id)
            await websocket.send_text(json.dumps({
                "type": "searching",
                "game_id": game_id,
                "code": code
            }))
            self.board_from_game_id[game_id] = game_service.create_game(board)

    async def handle_cancel_lobby(self, username: str):
        """Player backed out of a waiting room before anyone joined — drop it."""
        user = self.user_repo.get_user_by_username(username)
        if not user:
            return

        for game_row in self.game_repo.get_pending_games_by_player(user[0]):
            self.game_repo.remove_game(game_row[0])
            self.board_from_game_id.pop(game_row[0], None)

    async def handle_leave(self, username: str, game_id, opponent_username,
                           message: str = None):
        """Player walked out of a live game — end it for both sides.

        The game is deleted rather than marked finished: an abandoned match has
        nothing worth keeping, and the row's chat history goes with it via
        ON DELETE CASCADE."""
        if game_id is None:
            return

        # Whoever is still here doesn't need a grace period any more.
        self.cancel_abandon_timer(username)
        self.cancel_abandon_timer(opponent_username)

        opponent_socket = self.connected_users.get(opponent_username)
        if opponent_socket:
            await opponent_socket.send_text(json.dumps({
                "type": "opponent_left",
                "message": message or f"{username} left the match.",
            }))

        self.game_repo.remove_game(game_id)
        self.board_from_game_id.pop(game_id, None)

    # ---------- Dropped connections ----------

    async def handle_disconnect(self, username: str, game_id, opponent_username):
        """Player vanished without pressing Leave — maybe a refresh, maybe a
        dead network. Tell the opponent and start the forfeit clock."""
        if game_id is None or username in self.abandon_timers:
            return

        opponent_socket = self.connected_users.get(opponent_username)
        if opponent_socket:
            await opponent_socket.send_text(json.dumps({
                "type": "opponent_disconnected",
                "seconds": ABANDON_SECONDS,
            }))

        self.abandon_timers[username] = {
            "task": asyncio.create_task(
                self._forfeit_after_grace(username, game_id, opponent_username)
            ),
            "game_id": game_id,
            "opponent": opponent_username,
        }

    async def _forfeit_after_grace(self, username: str, game_id, opponent_username):
        try:
            await asyncio.sleep(ABANDON_SECONDS)
        except asyncio.CancelledError:
            return

        self.abandon_timers.pop(username, None)
        await self.handle_leave(
            username, game_id, opponent_username,
            message=f"{username} did not return in time.",
        )

    def cancel_abandon_timer(self, username: str) -> bool:
        """Stops a running forfeit clock. Returns whether one was in flight."""
        timer = self.abandon_timers.pop(username, None)
        if not timer:
            return False
        timer["task"].cancel()
        return True

    async def handle_reconnect(self, username: str):
        """Player made it back before the clock ran out."""
        timer = self.abandon_timers.get(username)
        if not timer:
            return

        opponent_username = timer["opponent"]
        self.cancel_abandon_timer(username)

        opponent_socket = self.connected_users.get(opponent_username)
        if opponent_socket:
            await opponent_socket.send_text(json.dumps({
                "type": "opponent_reconnected",
            }))