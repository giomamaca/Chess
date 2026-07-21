"""Lobby lifecycle: leaving a live game, cancelling a waiting room, and the
quick-match search."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, call, patch

from app.board import Board
from app.handlers.game_handler import ABANDON_SECONDS, GameHandlers


def run(coro):
    return asyncio.run(coro)


def fake_socket():
    socket = MagicMock()
    socket.send_text = AsyncMock()
    return socket


def payloads(socket):
    """Every JSON message pushed to a socket, decoded."""
    return [json.loads(c[0][0]) for c in socket.send_text.call_args_list]


def build(connected=None, boards=None):
    game_repo = MagicMock()
    user_repo = MagicMock()
    handlers = GameHandlers(
        game_repo, user_repo, connected if connected is not None else {},
        boards if boards is not None else {},
    )
    return handlers, game_repo, user_repo


# ── Leaving a live game ────────────────────────────────────────────

class TestHandleLeave:
    def setup_method(self):
        self.opponent = fake_socket()
        self.boards = {10: object(), 11: object()}
        self.handlers, self.game_repo, self.user_repo = build(
            connected={"bob": self.opponent}, boards=self.boards
        )

    def test_opponent_is_told_who_left(self):
        run(self.handlers.handle_leave("alice", 10, "bob"))

        [message] = payloads(self.opponent)
        assert message["type"] == "opponent_left"
        assert "alice" in message["message"]

    def test_game_row_is_deleted_not_just_flagged(self):
        run(self.handlers.handle_leave("alice", 10, "bob"))

        self.game_repo.remove_game.assert_called_once_with(10)
        self.game_repo.mark_finished.assert_not_called()

    def test_only_the_abandoned_board_is_dropped(self):
        run(self.handlers.handle_leave("alice", 10, "bob"))

        assert 10 not in self.boards
        assert 11 in self.boards

    def test_game_still_ends_when_opponent_is_offline(self):
        run(self.handlers.handle_leave("alice", 10, "carol"))

        self.opponent.send_text.assert_not_called()
        self.game_repo.remove_game.assert_called_once_with(10)
        assert 10 not in self.boards

    def test_leaving_without_a_game_changes_nothing(self):
        run(self.handlers.handle_leave("alice", None, "bob"))

        self.opponent.send_text.assert_not_called()
        self.game_repo.remove_game.assert_not_called()
        assert self.boards == {10: self.boards[10], 11: self.boards[11]}


# ── Backing out of a waiting room ──────────────────────────────────

class TestHandleCancelLobby:
    def setup_method(self):
        self.boards = {1: object(), 2: object(), 3: object()}
        self.handlers, self.game_repo, self.user_repo = build(boards=self.boards)
        self.user_repo.get_user_by_username.return_value = (5, "alice", "pw_hash")

    def test_removes_every_lobby_the_player_is_sitting_in(self):
        self.game_repo.get_pending_games_by_player.return_value = [
            (1, "CODE1234", 5, None, "waiting"),
            (2, "ABCDEF", None, 5, "private"),
        ]

        run(self.handlers.handle_cancel_lobby("alice"))

        assert self.game_repo.remove_game.call_args_list == [call(1), call(2)]

    def test_leaves_other_players_boards_alone(self):
        self.game_repo.get_pending_games_by_player.return_value = [
            (1, "CODE1234", 5, None, "waiting"),
        ]

        run(self.handlers.handle_cancel_lobby("alice"))

        assert 1 not in self.boards
        assert 2 in self.boards and 3 in self.boards

    def test_nothing_pending_is_a_noop(self):
        self.game_repo.get_pending_games_by_player.return_value = []

        run(self.handlers.handle_cancel_lobby("alice"))

        self.game_repo.remove_game.assert_not_called()

    def test_unknown_user_is_ignored(self):
        self.user_repo.get_user_by_username.return_value = None

        run(self.handlers.handle_cancel_lobby("ghost"))

        self.game_repo.get_pending_games_by_player.assert_not_called()
        self.game_repo.remove_game.assert_not_called()


# ── Quick match search ─────────────────────────────────────────────

class TestHandleQuickMatch:
    def setup_method(self):
        self.socket = fake_socket()
        self.boards = {}
        self.handlers, self.game_repo, self.user_repo = build(boards=self.boards)
        self.user_repo.get_user_by_username.return_value = (5, "alice", "pw_hash")

    def test_reuses_an_existing_lobby_instead_of_stacking_a_new_one(self):
        """Re-entering the search screen must not leave orphan rows behind."""
        self.game_repo.get_free_lobby.return_value = None
        self.game_repo.get_pending_games_by_player.return_value = [
            (7, "CODE1234", 5, None, "waiting"),
        ]

        run(self.handlers.handle_quick_match(self.socket, "alice"))

        self.game_repo.create_open_game.assert_not_called()
        assert payloads(self.socket) == [
            {"type": "searching", "game_id": 7, "code": "CODE1234"}
        ]

    def test_a_private_room_does_not_count_as_a_quick_match_lobby(self):
        self.game_repo.get_free_lobby.return_value = None
        self.game_repo.get_pending_games_by_player.return_value = [
            (7, "ABCDEF", 5, None, "private"),
        ]
        self.game_repo.create_open_game.return_value = (Board(), 9, "NEWCODE1")

        run(self.handlers.handle_quick_match(self.socket, "alice"))

        self.game_repo.create_open_game.assert_called_once_with(5)
        assert payloads(self.socket)[0]["game_id"] == 9

    def test_opens_a_lobby_when_nobody_is_waiting(self):
        self.game_repo.get_free_lobby.return_value = None
        self.game_repo.get_pending_games_by_player.return_value = []
        self.game_repo.create_open_game.return_value = (Board(), 9, "NEWCODE1")

        run(self.handlers.handle_quick_match(self.socket, "alice"))

        assert payloads(self.socket) == [
            {"type": "searching", "game_id": 9, "code": "NEWCODE1"}
        ]
        assert 9 in self.boards

    def test_pairs_up_with_a_waiting_player_and_starts_both(self):
        host_socket = fake_socket()
        self.handlers.connected_users["bob"] = host_socket
        # Host took white, so the joining player gets black.
        self.game_repo.get_free_lobby.return_value = (7, 3, None, "CODE1234")
        self.user_repo.get_user_by_id.return_value = (3, "bob", "pw_hash")

        run(self.handlers.handle_quick_match(self.socket, "alice"))

        self.game_repo.join_lobby.assert_called_once_with(7, 5)

        [joiner] = payloads(self.socket)
        [host] = payloads(host_socket)
        assert joiner["type"] == host["type"] == "game_start"
        assert joiner["game_id"] == host["game_id"] == 7
        assert {joiner["color"], host["color"]} == {"white", "black"}

    def test_both_players_are_handed_the_same_board(self):
        host_socket = fake_socket()
        self.handlers.connected_users["bob"] = host_socket
        self.game_repo.get_free_lobby.return_value = (7, 3, None, "CODE1234")
        self.user_repo.get_user_by_id.return_value = (3, "bob", "pw_hash")

        run(self.handlers.handle_quick_match(self.socket, "alice"))

        [joiner] = payloads(self.socket)
        [host] = payloads(host_socket)
        assert joiner["board"] == host["board"]
        assert joiner["current_turn"] == host["current_turn"] == "white"

    def test_unknown_user_gets_an_error(self):
        self.user_repo.get_user_by_username.return_value = None

        run(self.handlers.handle_quick_match(self.socket, "ghost"))

        [message] = payloads(self.socket)
        assert message["type"] == "error"
        self.game_repo.create_open_game.assert_not_called()


# ── Dropped connection: the 120s forfeit clock ─────────────────────

class TestAbandonTimer:
    """The real grace period is 120s, so every test here drives the handler
    inside one event loop with sleep patched out."""

    def setup_method(self):
        self.opponent = fake_socket()
        self.boards = {10: object()}
        self.handlers, self.game_repo, self.user_repo = build(
            connected={"bob": self.opponent}, boards=self.boards
        )

    def test_opponent_is_warned_with_the_countdown_length(self):
        async def scenario():
            await self.handlers.handle_disconnect("alice", 10, "bob")
            self.handlers.cancel_abandon_timer("alice")

        run(scenario())

        [message] = payloads(self.opponent)
        assert message["type"] == "opponent_disconnected"
        assert message["seconds"] == ABANDON_SECONDS

    def test_the_game_survives_the_disconnect_itself(self):
        async def scenario():
            await self.handlers.handle_disconnect("alice", 10, "bob")
            self.handlers.cancel_abandon_timer("alice")

        run(scenario())

        self.game_repo.remove_game.assert_not_called()
        assert 10 in self.boards

    def test_the_grace_period_is_two_minutes(self):
        assert ABANDON_SECONDS == 120

    def test_running_out_of_time_ends_the_game(self):
        async def scenario():
            # Countdown collapses to a single event-loop tick.
            sleep = AsyncMock()
            with patch("app.handlers.game_handler.asyncio.sleep", new=sleep):
                await self.handlers.handle_disconnect("alice", 10, "bob")
                await self.handlers.abandon_timers["alice"]["task"]
            return sleep

        sleep = run(scenario())

        sleep.assert_awaited_once_with(ABANDON_SECONDS)
        self.game_repo.remove_game.assert_called_once_with(10)
        assert 10 not in self.boards

    def test_forfeit_message_says_they_never_came_back(self):
        async def scenario():
            with patch("app.handlers.game_handler.asyncio.sleep", new=AsyncMock()):
                await self.handlers.handle_disconnect("alice", 10, "bob")
                await self.handlers.abandon_timers["alice"]["task"]

        run(scenario())

        forfeit = payloads(self.opponent)[-1]
        assert forfeit["type"] == "opponent_left"
        assert "did not return" in forfeit["message"]

    def test_reconnecting_in_time_saves_the_game(self):
        async def scenario():
            await self.handlers.handle_disconnect("alice", 10, "bob")
            await self.handlers.handle_reconnect("alice")
            await asyncio.sleep(0)

        run(scenario())

        self.game_repo.remove_game.assert_not_called()
        assert 10 in self.boards
        assert "alice" not in self.handlers.abandon_timers

    def test_opponent_is_told_the_player_is_back(self):
        async def scenario():
            await self.handlers.handle_disconnect("alice", 10, "bob")
            await self.handlers.handle_reconnect("alice")

        run(scenario())

        assert [m["type"] for m in payloads(self.opponent)] == [
            "opponent_disconnected", "opponent_reconnected",
        ]

    def test_reconnect_without_a_pending_timer_is_silent(self):
        run(self.handlers.handle_reconnect("alice"))

        self.opponent.send_text.assert_not_called()

    def test_a_second_drop_does_not_stack_a_second_clock(self):
        async def scenario():
            await self.handlers.handle_disconnect("alice", 10, "bob")
            await self.handlers.handle_disconnect("alice", 10, "bob")
            count = len(payloads(self.opponent))
            self.handlers.cancel_abandon_timer("alice")
            return count

        assert run(scenario()) == 1

    def test_no_clock_starts_without_a_game(self):
        run(self.handlers.handle_disconnect("alice", None, "bob"))

        assert self.handlers.abandon_timers == {}
        self.opponent.send_text.assert_not_called()

    def test_opponent_leaving_first_stops_the_clock(self):
        """Bob presses Leave while alice's countdown is running."""
        async def scenario():
            await self.handlers.handle_disconnect("alice", 10, "bob")
            await self.handlers.handle_leave("bob", 10, "alice")
            await asyncio.sleep(0)

        run(scenario())

        assert self.handlers.abandon_timers == {}
        self.game_repo.remove_game.assert_called_once_with(10)
