"""Tests for the shared cinematic sequence runner."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..game_utils.actions import ActionSet
from ..game_utils.game_result import GameResult
from ..game_utils.options import GameOptions
from ..game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ..games.base import Game, Player
from ..users.test_user import MockUser


@dataclass
class SequenceTestOptions(GameOptions):
    pass


@dataclass
class SequenceTestPlayer(Player):
    pass


@dataclass
class SequenceTestGame(Game):
    players: list[SequenceTestPlayer] = field(default_factory=list)
    options: SequenceTestOptions = field(default_factory=SequenceTestOptions)
    callback_log: list[str] = field(default_factory=list)

    @classmethod
    def get_name(cls) -> str:
        return "Sequence Test"

    @classmethod
    def get_type(cls) -> str:
        return "sequencetest"

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> SequenceTestPlayer:
        return SequenceTestPlayer(id=player_id, name=name, is_bot=is_bot)

    def on_start(self) -> None:
        self.status = "playing"
        self.game_active = True
        self._sync_table_status()
        self.set_turn_players(self.get_active_players())

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()

    def create_turn_action_set(self, player: Player) -> ActionSet:
        return ActionSet(name="turn")

    def bot_think(self, player: Player) -> str | None:
        return None

    def build_game_result(self) -> GameResult:
        return GameResult(
            game_type=self.get_type(),
            timestamp="",
            duration_ticks=self.sound_scheduler_tick,
            player_results=[],
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        return []

    def on_sequence_callback(
        self,
        sequence_id: str,
        callback_id: str,
        payload: dict,
    ) -> None:
        self.callback_log.append(f"{sequence_id}:{callback_id}:{payload.get('value', '')}")


def make_game(locales: list[str] | None = None) -> SequenceTestGame:
    game = SequenceTestGame()
    game.setup_keybinds()
    locales = locales or ["en", "en"]
    for index, locale in enumerate(locales, start=1):
        user = MockUser(f"Player{index}", locale=locale, uuid=f"p{index}")
        game.add_player(user.username, user)
    game.host = "Player1"
    game.on_start()
    return game


def advance_ticks(game: SequenceTestGame, count: int) -> None:
    for _ in range(count):
        game.on_tick()


def test_sequence_runs_sound_then_callback_across_ticks() -> None:
    game = make_game()
    user = game.get_user(game.players[0])
    assert user is not None

    game.start_sequence(
        "intro",
        [
            SequenceBeat(
                ops=[SequenceOperation.sound_op("sound_a.ogg")],
                delay_after_ticks=3,
            ),
            SequenceBeat(
                ops=[SequenceOperation.callback_op("finish", {"value": "done"})],
            ),
        ],
        tag="turn_flow",
        lock_scope=game.SEQUENCE_LOCK_GAMEPLAY,
        pause_bots=True,
    )

    assert user.get_sounds_played() == ["sound_a.ogg"]
    assert game.is_sequence_gameplay_locked() is True
    assert game.is_sequence_bot_paused() is True
    assert game.callback_log == []

    advance_ticks(game, 2)
    assert game.callback_log == []

    advance_ticks(game, 1)
    assert game.callback_log == ["intro:finish:done"]
    assert game.has_active_sequence() is False
    assert game.is_sequence_gameplay_locked() is False
    assert game.is_sequence_bot_paused() is False


def test_sequence_dispatches_localized_sounds_per_listener() -> None:
    game = make_game(["en", "vi"])
    en_user = game.get_user(game.players[0])
    vi_user = game.get_user(game.players[1])
    assert en_user is not None
    assert vi_user is not None

    game.start_sequence(
        "voice",
        [
            SequenceBeat(
                ops=[
                    SequenceOperation.localized_sound_op(
                        {
                            "en": "voice/en_line.ogg",
                            "vi": "voice/vi_line.ogg",
                        }
                    )
                ]
            )
        ],
    )

    assert en_user.get_sounds_played() == ["voice/en_line.ogg"]
    assert vi_user.get_sounds_played() == ["voice/vi_line.ogg"]


def test_sequence_round_trips_and_resumes_after_restore() -> None:
    game = make_game()
    user = game.get_user(game.players[0])
    assert user is not None

    game.start_sequence(
        "restore_me",
        [
            SequenceBeat(
                ops=[SequenceOperation.sound_op("startup.ogg")],
                delay_after_ticks=2,
            ),
            SequenceBeat(
                ops=[SequenceOperation.callback_op("finish", {"value": "restored"})],
            ),
        ],
        tag="restore",
    )

    payload = game.to_json()
    restored = SequenceTestGame.from_json(payload)
    for player in restored.players:
        original_player = game.get_player_by_id(player.id)
        if original_player is None:
            continue
        original_user = game.get_user(original_player)
        if original_user is not None:
            restored.attach_user(player.id, original_user)

    assert restored.has_active_sequence(sequence_id="restore_me") is True
    assert restored.callback_log == []

    advance_ticks(restored, 2)
    assert restored.callback_log == ["restore_me:finish:restored"]


def test_zero_delay_sequence_yields_after_budget_instead_of_looping_forever() -> None:
    game = make_game()
    beats = [
        SequenceBeat(
            ops=[SequenceOperation.callback_op("tick", {"value": str(index)})],
            delay_after_ticks=0,
        )
        for index in range(game.MAX_SEQUENCE_BEATS_PER_TICK + 5)
    ]

    game.start_sequence("budget", beats, start_immediately=False)
    game.process_sequences()

    assert len(game.callback_log) == game.MAX_SEQUENCE_BEATS_PER_TICK
    assert game.has_active_sequence(sequence_id="budget") is True

    advance_ticks(game, 1)
    assert len(game.callback_log) == len(beats)
    assert game.has_active_sequence(sequence_id="budget") is False
