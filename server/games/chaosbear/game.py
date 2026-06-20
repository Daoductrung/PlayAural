"""
Chaos Bear - A chase game where players run from a bear.

Players roll dice to move forward. When on multiples of 5, they can draw
cards for special effects. The bear chases from behind, catching players
who fall too far back. Last player standing (or furthest distance) wins!
"""

import random
from dataclasses import dataclass, field
from datetime import datetime

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...ui.keybinds import KeybindState
from ...messages.localization import Localization
from ...users.base import MenuItem


@dataclass
class ChaosBearPlayer(Player):
    """Player state for Chaos Bear."""

    position: int = 0
    alive: bool = True


@dataclass
@register_game
class ChaosBearGame(Game):
    """
    Chaos Bear - run from the bear!

    Players start 30 squares ahead of the bear and must keep moving forward.
    Roll dice to advance, draw cards on multiples of 5 for bonuses/penalties.
    If the bear catches you, you're out! Last player alive wins.
    """

    relevant_preferences = ["brief_announcements"]

    players: list[ChaosBearPlayer] = field(default_factory=list)

    # Game Logic State
    is_rolling: bool = False

    # Game state
    bear_position: int = 0
    bear_energy: int = 1
    round_number: int = 0
    players_moved_this_round: int = 0
    round_start_seat: int = 0
    winner_name: str | None = None
    winner_ids: list[str] = field(default_factory=list)
    winner_position: int = 0
    is_tie: bool = False
    tied_names: list[str] = field(default_factory=list)
    tied_ids: list[str] = field(default_factory=list)

    @classmethod
    def get_name(cls) -> str:
        return "Chaos Bear"

    @classmethod
    def get_type(cls) -> str:
        return "chaosbear"

    @classmethod
    def get_category(cls) -> str:
        return "arcade"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> ChaosBearPlayer:
        """Create a new player."""
        return ChaosBearPlayer(id=player_id, name=name, is_bot=is_bot)

    def _alive_players_in_seat_order(self) -> list[ChaosBearPlayer]:
        """Return alive players in their original table order."""
        return self._alive_runners()

    def _active_runners(self) -> list[ChaosBearPlayer]:
        """Return non-spectator Chaos Bear players."""
        return [
            p
            for p in self.players
            if isinstance(p, ChaosBearPlayer) and not p.is_spectator
        ]

    def _alive_runners(self) -> list[ChaosBearPlayer]:
        """Return living runners in table order."""
        return [p for p in self._active_runners() if p.alive]

    def _seat_index(self, player: ChaosBearPlayer) -> int:
        """Resolve the player's fixed seat index."""
        for index, seat_player in enumerate(self.players):
            if seat_player.id == player.id:
                return index
        return 0

    def _build_round_turn_order(self) -> list[ChaosBearPlayer]:
        """Rotate the round opener so one seat does not always act first."""
        alive_players = self._alive_players_in_seat_order()
        if not alive_players:
            return []

        for offset in range(len(self.players)):
            seat_index = (self.round_start_seat + offset) % len(self.players)
            for start_at, player in enumerate(alive_players):
                if self._seat_index(player) == seat_index:
                    return alive_players[start_at:] + alive_players[:start_at]

        return alive_players

    def _advance_round_start_seat(self) -> None:
        """Move the round opener to the next surviving seat."""
        if not self.players:
            self.round_start_seat = 0
            return

        for offset in range(1, len(self.players) + 1):
            seat_index = (self.round_start_seat + offset) % len(self.players)
            seat_player = self.players[seat_index]
            if (
                isinstance(seat_player, ChaosBearPlayer)
                and seat_player.alive
                and not seat_player.is_spectator
            ):
                self.round_start_seat = seat_index
                return

    def _gap_to_bear(self, position: int) -> int:
        """Return how many squares a position is ahead of the bear."""
        return position - self.bear_position

    def _speak_disabled_reason(self, player: Player, reason: str | None) -> None:
        if not reason or reason == "action-not-available":
            return
        user = self.get_user(player)
        if user:
            payload = {}
            if (
                reason
                in {
                    "chaosbear-error-roll-caught",
                    "chaosbear-error-draw-caught",
                }
                and isinstance(player, ChaosBearPlayer)
            ):
                payload["position"] = player.position
                payload["bear_position"] = self.bear_position
            user.speak_l(reason, buffer="game", **payload)

    def _wants_brief(self, user) -> bool:
        return bool(
            user
            and user.preferences.get_effective(
                "brief_announcements", game_type=self.get_type()
            )
        )

    def _broadcast_runner_event(
        self,
        player: ChaosBearPlayer,
        personal_message_id: str,
        others_message_id: str,
        *,
        brief_personal_message_id: str | None = None,
        brief_others_message_id: str | None = None,
        **kwargs,
    ) -> None:
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue

            is_actor = listener.id == player.id
            key = personal_message_id if is_actor else others_message_id
            if self._wants_brief(user):
                if is_actor and brief_personal_message_id:
                    key = brief_personal_message_id
                elif not is_actor and brief_others_message_id:
                    key = brief_others_message_id

            payload = dict(kwargs)
            if not is_actor:
                payload["player"] = player.name
            user.speak_l(key, buffer="game", **payload)

    def _broadcast_global_event(
        self,
        message_id: str,
        *,
        brief_message_id: str | None = None,
        **kwargs,
    ) -> None:
        """Broadcast a global chase event with listener-specific verbosity."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            key = (
                brief_message_id
                if brief_message_id and self._wants_brief(user)
                else message_id
            )
            user.speak_l(key, buffer="game", **kwargs)

    def _announce_intro(self) -> None:
        """Announce the start of the chase once per listener."""
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if self._wants_brief(user):
                user.speak_l("chaosbear-intro-brief", buffer="game")
                continue
            user.speak_l("chaosbear-intro-1", buffer="game")
            user.speak_l("chaosbear-intro-2", buffer="game")
            user.speak_l("chaosbear-intro-3", buffer="game")

    # ==========================================================================
    # Action Sets
    # ==========================================================================

    def create_turn_action_set(self, player: ChaosBearPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        action_set = ActionSet(name="turn")
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set.add(
            Action(
                id="roll_dice",
                label=Localization.get(locale, "chaosbear-roll-dice"),
                handler="_action_roll_dice",
                is_enabled="_is_roll_dice_enabled",
                is_hidden="_is_roll_dice_hidden",
                show_in_actions_menu=False,
            )
        )

        action_set.add(
            Action(
                id="draw_card",
                label=Localization.get(locale, "chaosbear-draw-card"),
                handler="_action_draw_card",
                is_enabled="_is_draw_card_enabled",
                is_hidden="_is_draw_card_hidden",
                show_in_actions_menu=False,
            )
        )

        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set.add(
            Action(
                id="check_status",
                label=Localization.get(locale, "chaosbear-check-status"),
                handler="_action_check_status",
                is_enabled="_is_check_status_enabled",
                is_hidden="_is_check_status_hidden",
                include_spectators=True,
            )
        )

        # WEB-SPECIFIC: Reorder for Web Clients
        if self.is_touch_client(user):
            target_order = [
                "check_status",
                "check_scores",
                "whose_turn",
                "whos_at_table",
            ]
            self._order_touch_standard_actions(action_set, target_order)

        return action_set

    # WEB-SPECIFIC: Override visibility for standard actions

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (always), hidden otherwise."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if self.is_touch_client(user):
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        self.define_keybind(
            "c",
            "Check status",
            ["check_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        self.define_keybind(
            "r",
            "Roll Dice",
            ["roll_dice"],
            state=KeybindState.ACTIVE,
        )

        self.define_keybind(
            "d",
            "Draw Card",
            ["draw_card"],
            state=KeybindState.ACTIVE,
        )

    # ==========================================================================
    # Declarative Action Callbacks
    # ==========================================================================

    def _is_roll_dice_enabled(self, player: Player) -> str | None:
        """Check if roll dice action is enabled."""
        if self.status != "playing":
            return "chaosbear-error-roll-not-playing"
        if not isinstance(player, ChaosBearPlayer):
            return "action-not-available"
        if self.current_player is None:
            return "chaosbear-error-roll-no-turn"
        if self.current_player != player:
            return "chaosbear-error-roll-not-your-turn"
        if self.is_rolling or self.is_sequence_gameplay_locked():
            return "chaosbear-error-roll-resolving"
        if not player.alive:
            return "chaosbear-error-roll-caught"
        return None

    def _is_turn_action_visible(self, player: Player) -> Visibility:
        """Turn actions stay visible for living players throughout play.

        Visibility no longer depends on whose turn it is or whether the action is
        currently enabled — off-turn players see the same disabled buttons so the
        menu shape (and screen-reader focus anchor) stays stable across turns.
        Per-turn conditions (whose turn, is_rolling, draw eligibility) remain
        enablement concerns handled by the matching `_is_*_enabled` methods.
        """
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if not isinstance(player, ChaosBearPlayer) or not player.alive:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_roll_dice_hidden(self, player: Player) -> Visibility:
        """Check if roll dice is hidden."""
        return self._is_turn_action_visible(player)

    def _is_draw_card_enabled(self, player: Player) -> str | None:
        """Check if draw card action is enabled."""
        if self.status != "playing":
            return "chaosbear-error-draw-not-playing"
        if not isinstance(player, ChaosBearPlayer):
            return "action-not-available"
        if self.current_player is None:
            return "chaosbear-error-draw-no-turn"
        if self.current_player != player:
            return "chaosbear-error-draw-not-your-turn"
        if self.is_rolling or self.is_sequence_gameplay_locked():
            return "chaosbear-error-draw-resolving"
        if not player.alive:
            return "chaosbear-error-draw-caught"
        can_draw = player.position % 5 == 0 and player.position > 0
        if not can_draw:
            return "chaosbear-error-draw-not-on-multiple"
        return None

    def _is_draw_card_hidden(self, player: Player) -> Visibility:
        """Check if draw card is hidden."""
        return self._is_turn_action_visible(player)

    def _is_check_status_enabled(self, player: Player) -> str | None:
        """Check if check status action is enabled."""
        if self.status != "playing":
            return "chaosbear-error-status-not-playing"
        return None

    def _is_check_status_hidden(self, player: Player) -> Visibility:
        """Check status is visible to all during play."""
        if self.status != "playing":
            return Visibility.HIDDEN
        
        # Hide for Python/other clients (they have keybinds/menu)
        user = self.get_user(player)
        if not self.is_touch_client(user):
            return Visibility.HIDDEN

        return Visibility.VISIBLE

    # ==========================================================================
    # Game Flow
    # ==========================================================================

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.cancel_all_sequences()
        self.round_number = 1
        self.players_moved_this_round = 0
        self.winner_name = None
        self.winner_ids = []
        self.winner_position = 0
        self.is_tie = False
        self.tied_names = []
        self.tied_ids = []

        # Set starting positions (fixed at 30 like v10)
        self.bear_position = 0
        self.bear_energy = 1
        for player in self._active_runners():
            player.position = 30
            player.alive = True

        # Initialize turn order
        alive_players = self._active_runners()
        if alive_players:
            self.round_start_seat = self._seat_index(alive_players[0])
        self.set_turn_players(self._build_round_turn_order())

        # Play music and ambience
        self.play_music("game_chaosbear/music.ogg")
        self.play_ambience("game_chaosbear/amloop.ogg")
        self.play_sound("game_3cardpoker/roundstart.ogg")

        self._announce_intro()

        # Rebuild menus and announce first turn
        self.refresh_menus()

        self._announce_turn()

        # Jolt bots (Faster: 10-20 ticks)
        BotHelper.jolt_bots(self, ticks=random.randint(10, 20))

    def _announce_turn(self) -> None:
        """Announce whose turn it is."""
        player = self.current_player
        if not player:
            return

        # Play begin turn sound for human players only
        if not player.is_bot:
            user = self.get_user(player)
            if user and user.preferences.play_turn_sound:
                user.play_sound("game_squares/begin turn.ogg", volume=50)

        if isinstance(player, ChaosBearPlayer):
            self._broadcast_runner_event(
                player,
                "chaosbear-turn-you",
                "chaosbear-turn-other",
                brief_personal_message_id="chaosbear-turn-you-brief",
                brief_others_message_id="chaosbear-turn-other-brief",
                position=player.position,
                gap=self._gap_to_bear(player.position),
            )

    def on_sequence_callback(
        self,
        sequence_id: str,
        callback_id: str,
        payload: dict,
    ) -> None:
        _ = sequence_id
        event_type = callback_id
        data = payload
        player_id = data.get("player_id")
        player = self.get_player_by_id(player_id) if player_id else None

        if event_type == "move":
            if player:
                new_pos = data["pos"]
                # Only update if alive (might have been caught in rare race condition)
                if isinstance(player, ChaosBearPlayer) and player.alive:
                    player.position = new_pos
                    self._broadcast_runner_event(
                        player,
                        "chaosbear-position-you",
                        "chaosbear-position-other",
                        brief_personal_message_id="chaosbear-position-you-brief",
                        brief_others_message_id="chaosbear-position-other-brief",
                        position=new_pos,
                        gap=self._gap_to_bear(new_pos),
                    )

        elif event_type == "card_effect":
            if player and isinstance(player, ChaosBearPlayer):
                if "pos" in data:
                    player.position = data["pos"]
                if "energy" in data:
                    self.bear_energy = data["energy"]
                personal_msg_id = data.get("personal_msg_id")
                others_msg_id = data.get("others_msg_id")
                kwargs = dict(data.get("kwargs") or {})
                if personal_msg_id and others_msg_id:
                    brief_personal_msg_id = data.get("brief_personal_msg_id")
                    brief_others_msg_id = data.get("brief_others_msg_id")
                    self._broadcast_runner_event(
                        player,
                        str(personal_msg_id),
                        str(others_msg_id),
                        brief_personal_message_id=(
                            str(brief_personal_msg_id)
                            if brief_personal_msg_id
                            else None
                        ),
                        brief_others_message_id=(
                            str(brief_others_msg_id) if brief_others_msg_id else None
                        ),
                        **kwargs,
                    )
                else:
                    msg_id = data.get("msg_id")
                    kwargs = dict(data.get("kwargs") or {})
                    if msg_id:
                        self.broadcast_l(str(msg_id), buffer="game", **kwargs)

        elif event_type == "bear_roll_result":
            roll = data["roll"]
            energy = data["energy"]
            total = data["total"]
            self._broadcast_global_event(
                "chaosbear-bear-roll",
                brief_message_id="chaosbear-bear-roll-brief",
                roll=roll,
                energy=energy,
                total=total,
            )

        elif event_type == "bear_energy_up":
            energy = data["energy"]
            self.bear_energy = energy
            self._broadcast_global_event(
                "chaosbear-bear-energy-up",
                brief_message_id="chaosbear-bear-energy-up-brief",
                energy=energy,
            )

        elif event_type == "bear_move":
            new_pos = data["pos"]
            self.bear_position = new_pos
            self._broadcast_global_event(
                "chaosbear-bear-position",
                brief_message_id="chaosbear-bear-position-brief",
                position=new_pos,
            )

        elif event_type == "bear_feast":
            self.bear_energy = data["energy"]
            self._broadcast_global_event(
                "chaosbear-bear-feast",
                brief_message_id="chaosbear-bear-feast-brief",
                energy=self.bear_energy,
            )

        elif event_type == "player_caught":
            if player and isinstance(player, ChaosBearPlayer):
                player.alive = False
                self._broadcast_runner_event(
                    player,
                    "chaosbear-you-caught",
                    "chaosbear-player-caught",
                    brief_personal_message_id="chaosbear-you-caught-brief",
                    brief_others_message_id="chaosbear-player-caught-brief",
                    position=player.position,
                    bear_position=self.bear_position,
                )

        elif event_type == "next_round":
            self._next_round_step()

        elif event_type == "end_turn":
            self.end_turn()

    def on_tick(self) -> None:
        """Called every game tick."""
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()

        if self.status != "playing":
            return

        if not self.is_sequence_bot_paused():
            BotHelper.on_tick(self)

    def bot_think(self, player: ChaosBearPlayer) -> str | None:
        """Determine what action a bot should take."""
        if not player.alive:
            return None

        if player.position % 5 == 0 and player.position > 0:
            gap_to_bear = player.position - self.bear_position
            if gap_to_bear <= 15 or self.bear_energy >= 4:
                return "draw_card"
            if random.random() < 0.5:
                return "draw_card"

        return "roll_dice"

    def end_turn(self) -> None:
        """End the current player's turn."""
        self.players_moved_this_round += 1

        alive_players = [p for p in self.players if p.alive and not p.is_spectator]

        # Check if all alive players have moved this round
        if self.players_moved_this_round >= len(alive_players):
            # Trigger Bear Turn
            self._bear_turn()
        else:
            # Normal turn advance
            self.advance_turn(announce=False)
            self._announce_turn()
            
            # Reset rolling flag for next player
            self.is_rolling = False
            self.refresh_menus()
            
            # Jolt bots (Faster: 10-20 ticks)
            BotHelper.jolt_bots(self, ticks=random.randint(10, 20))

    def _next_round_step(self) -> None:
        """Handle logic after bear turn finishes."""
        self.players_moved_this_round = 0
        self.round_number += 1

        # Check for winner after bear moves
        if self._check_for_winner():
            return

        self._advance_round_start_seat()
        round_order = self._build_round_turn_order()
        if round_order:
            self.set_turn_players(round_order)

        self._announce_turn()
        
        self.is_rolling = False
        self.refresh_menus()

        # Jolt bots (Faster: 10-20 ticks)
        BotHelper.jolt_bots(self, ticks=random.randint(10, 20))

    def _bear_turn(self) -> None:
        """The bear takes its turn."""
        self.cancel_sequences_by_tag("turn_flow")
        self.is_rolling = True
        self.refresh_menus()

        # Check if any players are close - play warning
        for player in self._alive_runners():
            if player.position - self.bear_position <= 10:
                self.play_sound(
                    f"game_chaosbear/bearwarn{random.randint(1, 2)}.ogg"
                )
                break

        # Bear dice roll sounds (scheduled for timing)
        self.schedule_sound("game_chaosbear/beardice0.ogg", delay_ticks=10)
        self.schedule_sound(
            f"game_chaosbear/beardice{random.randint(1, 3)}.ogg", delay_ticks=18
        )

        # Bear rolls 1-3 + energy
        bear_die = random.randint(1, 3)
        original_energy = self.bear_energy
        move_distance = bear_die + original_energy
        updated_energy = original_energy

        beats: list[SequenceBeat] = [
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "bear_roll_result",
                        {"roll": bear_die, "energy": original_energy, "total": move_distance},
                    )
                ],
                delay_after_ticks=10,
            )
        ]

        if bear_die == 3:
            updated_energy = original_energy + 1
            beats[0].delay_after_ticks = 5
            self.schedule_sound(
                f"game_chaosbear/energyup{random.randint(1, 2)}.ogg", delay_ticks=15
            )
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "bear_energy_up",
                            {"energy": updated_energy},
                        )
                    ],
                    delay_after_ticks=15 + move_distance * 4,
                )
            )
        else:
            beats[0].delay_after_ticks = 10 + move_distance * 4

        # Calculate projected position (don't update self.bear_position yet)
        projected_bear_pos = self.bear_position + move_distance

        # Schedule bear step sounds - Exact match to movement
        for i in range(move_distance):
            self.schedule_sound(
                f"game_chaosbear/bearstep{random.randint(1, 5)}.ogg",
                delay_ticks=20 + (10 if bear_die == 3 else 0) + i * 4,
            )

        beats.append(
            SequenceBeat(
                ops=[
                    SequenceOperation.callback_op(
                        "bear_move",
                        {"pos": projected_bear_pos},
                    )
                ],
                delay_after_ticks=4,
            )
        )

        kills = 0
        post_feast_energy = updated_energy

        for player in self._alive_runners():
            if projected_bear_pos >= player.position:
                beats.append(
                    SequenceBeat(
                        ops=[
                            SequenceOperation.callback_op(
                                "player_caught",
                                {"player_id": player.id},
                            )
                        ],
                        delay_after_ticks=30,
                    )
                )
                kills += 1

        if kills > 0:
            post_feast_energy = max(1, updated_energy - 3)
            beats.append(
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "bear_feast",
                            {"energy": post_feast_energy},
                        )
                    ],
                    delay_after_ticks=10,
                )
            )
        else:
            beats[-1].delay_after_ticks = 14

        beats.append(
            SequenceBeat(
                ops=[SequenceOperation.callback_op("next_round")],
                )
            )

        move_offset = 20 + (10 if bear_die == 3 else 0) + move_distance * 4
        if kills > 0:
            catch_offset = move_offset + 4
            for kill_index in range(kills):
                self.schedule_sound(
                    f"game_chaosbear/playerdie{random.randint(1, 2)}.ogg",
                    delay_ticks=catch_offset + kill_index * 30,
                )
                self.schedule_sound(
                    f"game_chaosbear/energydown{random.randint(1, 3)}.ogg",
                    delay_ticks=catch_offset + kill_index * 30 + 30,
                )

        self.start_sequence(
            "turn_flow",
            beats,
            start_delay=10,
            tag="turn_flow",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _check_for_winner(self) -> bool:
        """Check if there's a winner."""
        alive_players = self._alive_runners()

        if len(alive_players) == 1:
            # One player left - they win!
            winner = alive_players[0]
            self._end_game(winner)
            return True
        elif len(alive_players) == 0:
            # Everyone caught - furthest distance wins
            all_players = self._active_runners()
            if not all_players:
                return False
            max_pos = max(p.position for p in all_players)
            winners = [p for p in all_players if p.position == max_pos]
            if len(winners) > 1:
                self._end_game_tie(winners, max_pos)
            else:
                self._end_game(winners[0], distance_tiebreak=True)
            return True

        return False

    def _end_game(
        self, winner: ChaosBearPlayer, *, distance_tiebreak: bool = False
    ) -> None:
        """End the game with a winner."""
        self.winner_name = winner.name
        self.winner_ids = [winner.id]
        self.winner_position = winner.position
        self.is_tie = False
        self.tied_names = []
        self.tied_ids = []
        self.is_rolling = False

        self.schedule_sound("game_chaosbear/wingame.ogg", delay_ticks=5)
        if distance_tiebreak:
            self._broadcast_runner_event(
                winner,
                "chaosbear-distance-winner-you",
                "chaosbear-distance-winner-other",
                brief_personal_message_id="chaosbear-distance-winner-you-brief",
                brief_others_message_id="chaosbear-distance-winner-other-brief",
                position=winner.position,
            )
        else:
            self._broadcast_runner_event(
                winner,
                "chaosbear-winner-you",
                "chaosbear-winner-other",
                brief_personal_message_id="chaosbear-winner-you-brief",
                brief_others_message_id="chaosbear-winner-other-brief",
                position=winner.position,
            )

        self.finish_game()

    def _end_game_tie(self, winners: list[ChaosBearPlayer], position: int) -> None:
        """End the game with a tie."""
        self.winner_name = None
        self.winner_ids = []
        self.winner_position = position
        self.is_tie = True
        self.tied_names = [winner.name for winner in winners]
        self.tied_ids = [winner.id for winner in winners]
        self.is_rolling = False

        tied_ids = {winner.id for winner in winners}
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            names = Localization.format_list_and(user.locale, self.tied_names)
            if listener.id in tied_ids:
                other_names = [
                    winner.name for winner in winners if winner.id != listener.id
                ]
                if other_names:
                    key = (
                        "chaosbear-tie-you-brief"
                        if self._wants_brief(user)
                        else "chaosbear-tie-you"
                    )
                    user.speak_l(
                        key,
                        buffer="game",
                        position=position,
                        players=Localization.format_list_and(
                            user.locale, other_names
                        ),
                    )
                else:
                    key = (
                        "chaosbear-tie-brief"
                        if self._wants_brief(user)
                        else "chaosbear-tie"
                    )
                    user.speak_l(
                        key,
                        buffer="game",
                        position=position,
                        players=names,
                    )
            else:
                key = (
                    "chaosbear-tie-brief"
                    if self._wants_brief(user)
                    else "chaosbear-tie"
                )
                user.speak_l(
                    key,
                    buffer="game",
                    position=position,
                    players=names,
                )

        self.finish_game()

    def _status_lines(self, locale: str) -> list[str]:
        """Build localized status lines for the readable status box."""
        return [item.text for item in self._status_items(locale)]

    def _status_items(self, locale: str) -> list[MenuItem]:
        """Build stable-id status items for the live status box."""
        lines = [
            MenuItem(
                text=Localization.get(locale, "chaosbear-status-header"),
                id="header",
            ),
            MenuItem(
                text=Localization.get(
                    locale, "chaosbear-status-round", round=self.round_number
                ),
                id="round",
            ),
        ]
        current = self.current_player
        if isinstance(current, ChaosBearPlayer) and current.alive:
            lines.append(
                MenuItem(
                    text=Localization.get(
                        locale,
                        "chaosbear-status-turn",
                        player=current.name,
                        position=current.position,
                        gap=self._gap_to_bear(current.position),
                    ),
                    id="turn",
                )
            )
        else:
            lines.append(
                MenuItem(
                    text=Localization.get(locale, "chaosbear-status-no-turn"),
                    id="turn",
                )
            )

        active = sorted(
            self._active_runners(), key=lambda p: (p.position, p.name), reverse=True
        )
        for runner in active:
            if runner.alive:
                lines.append(
                    MenuItem(
                        text=Localization.get(
                            locale,
                            "chaosbear-status-player-alive",
                            player=runner.name,
                            position=runner.position,
                            gap=self._gap_to_bear(runner.position),
                        ),
                        id=f"runner:{runner.id}",
                    )
                )
            else:
                lines.append(
                    MenuItem(
                        text=Localization.get(
                            locale,
                            "chaosbear-status-player-caught",
                            player=runner.name,
                            position=runner.position,
                        ),
                        id=f"runner:{runner.id}",
                    )
                )

        lines.append(
            MenuItem(
                text=Localization.get(
                    locale,
                    "chaosbear-status-bear",
                    position=self.bear_position,
                    energy=self.bear_energy,
                ),
                id="bear",
            )
        )
        return lines

    def build_game_result(self) -> GameResult:
        """Build the game result with ChaosBear-specific data."""
        all_players = [
            p
            for p in self.players
            if isinstance(p, ChaosBearPlayer) and not p.is_spectator
        ]
        sorted_players = sorted(all_players, key=lambda p: p.position, reverse=True)

        # Build final positions
        final_positions = {}
        alive_status = {}
        for p in sorted_players:
            final_positions[p.name] = p.position
            alive_status[p.name] = p.alive

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=p.id,
                    player_name=p.name,
                    is_bot=p.is_bot and not p.replaced_human,
                )
                for p in sorted_players
            ],
            custom_data={
                "winner_name": self.winner_name,
                "winner_ids": self.winner_ids,
                "winner_position": self.winner_position,
                "is_tie": self.is_tie,
                "tied_names": self.tied_names,
                "tied_ids": self.tied_ids,
                "final_positions": final_positions,
                "alive_status": alive_status,
                "bear_position": self.bear_position,
                "rounds_played": self.round_number,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for ChaosBear game."""
        lines = [Localization.get(locale, "chaosbear-final-positions")]

        final_positions = result.custom_data.get("final_positions", {})
        alive_status = result.custom_data.get("alive_status", {})

        for i, (name, position) in enumerate(final_positions.items(), 1):
            is_alive = alive_status.get(name, True)
            status_key = (
                "chaosbear-status-survived"
                if is_alive
                else "chaosbear-status-caught"
            )
            status_str = Localization.get(locale, status_key)

            line = Localization.get(
                locale,
                "chaosbear-line-format",
                rank=i,
                player=name,
                position=position,
                status=status_str,
            )
            lines.append(line)

        return lines

    # ==========================================================================
    # Actions
    # ==========================================================================

    def _action_roll_dice(self, player: Player, action_id: str) -> None:
        """Roll dice to move forward."""
        if not isinstance(player, ChaosBearPlayer):
            return
        reason = self._is_roll_dice_enabled(player)
        if reason:
            self._speak_disabled_reason(player, reason)
            return

        self.cancel_sequences_by_tag("turn_flow")
        self.is_rolling = True
        self.refresh_menus()

        self.play_sound("game_pig/roll.ogg")

        roll = random.randint(1, 6)

        # Broadcast immediately
        self._broadcast_runner_event(
            player,
            "chaosbear-roll-you",
            "chaosbear-roll-other",
            brief_personal_message_id="chaosbear-roll-you-brief",
            brief_others_message_id="chaosbear-roll-other-brief",
            roll=roll,
        )

        # Schedule step sounds
        for i in range(roll):
            self.schedule_sound(
                f"game_chaosbear/playerstep{random.randint(1, 5)}.ogg",
                delay_ticks=6 + i * 4,
            )

        # Calculate new position
        new_pos = player.position + roll

        move_complete_delay = 6 + (roll * 4) + 2
        self.start_sequence(
            "turn_flow",
            [
                SequenceBeat(
                    ops=[
                        SequenceOperation.callback_op(
                            "move",
                            {"player_id": player.id, "pos": new_pos},
                        )
                    ],
                    delay_after_ticks=5,
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("end_turn")],
                ),
            ],
            start_delay=move_complete_delay,
            tag="turn_flow",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _action_draw_card(self, player: Player, action_id: str) -> None:
        """Draw a card for a special effect."""
        if not isinstance(player, ChaosBearPlayer):
            return
        reason = self._is_draw_card_enabled(player)
        if reason:
            self._speak_disabled_reason(player, reason)
            return

        self.cancel_sequences_by_tag("turn_flow")
        self.is_rolling = True
        self.refresh_menus()

        self.play_sound(f"game_chaosbear/draw{random.randint(1, 2)}.ogg")
        self._broadcast_runner_event(
            player,
            "chaosbear-draw-card-you",
            "chaosbear-draw-card-other",
            brief_personal_message_id="chaosbear-draw-card-you-brief",
            brief_others_message_id="chaosbear-draw-card-other-brief",
        )

        card = random.randint(0, 5)
        # Drawing gives a short surge so the action is not strictly weaker than rolling.
        new_pos = player.position + 3

        event_delay = 10
        personal_msg_id = ""
        others_msg_id = ""
        brief_personal_msg_id = ""
        brief_others_msg_id = ""
        kwargs = {}
        payload: dict[str, object] = {"player_id": player.id}

        if card == 0:
            # Impulsion - total forward 6
            new_pos += 3
            self.schedule_sound(
                f"game_chaosbear/impulsion{random.randint(1, 2)}.ogg", delay_ticks=4
            )
            personal_msg_id = "chaosbear-card-impulsion-you"
            others_msg_id = "chaosbear-card-impulsion-other"
            brief_personal_msg_id = "chaosbear-card-impulsion-you-brief"
            brief_others_msg_id = "chaosbear-card-impulsion-other-brief"
            kwargs = {"position": new_pos, "gap": self._gap_to_bear(new_pos)}
            payload["pos"] = new_pos

        elif card == 1:
            # Super impulsion - total forward 8
            new_pos += 5
            self.schedule_sound(
                f"game_chaosbear/impulsion{random.randint(1, 2)}.ogg", delay_ticks=4
            )
            personal_msg_id = "chaosbear-card-super-impulsion-you"
            others_msg_id = "chaosbear-card-super-impulsion-other"
            brief_personal_msg_id = "chaosbear-card-super-impulsion-you-brief"
            brief_others_msg_id = "chaosbear-card-super-impulsion-other-brief"
            kwargs = {"position": new_pos, "gap": self._gap_to_bear(new_pos)}
            payload["pos"] = new_pos

        elif card == 2:
            # Tiredness - surge forward and reduce bear energy
            new_energy = max(1, self.bear_energy - 1)
            self.schedule_sound(
                f"game_chaosbear/tiredness{random.randint(1, 2)}.ogg", delay_ticks=4
            )
            self.schedule_sound(
                f"game_chaosbear/energydown{random.randint(1, 3)}.ogg", delay_ticks=24
            )
            personal_msg_id = "chaosbear-card-tiredness-you"
            others_msg_id = "chaosbear-card-tiredness-other"
            brief_personal_msg_id = "chaosbear-card-tiredness-you-brief"
            brief_others_msg_id = "chaosbear-card-tiredness-other-brief"
            kwargs = {
                "position": new_pos,
                "gap": self._gap_to_bear(new_pos),
                "energy": new_energy,
            }
            payload["energy"] = new_energy
            payload["pos"] = new_pos
            event_delay = 30  # Wait longer for energy sound

        elif card == 3:
            # Hunger - surge forward but increase bear energy
            new_energy = self.bear_energy + 1
            self.schedule_sound(
                f"game_chaosbear/hunger{random.randint(1, 2)}.ogg", delay_ticks=4
            )
            self.schedule_sound(
                f"game_chaosbear/energyup{random.randint(1, 2)}.ogg", delay_ticks=14
            )
            personal_msg_id = "chaosbear-card-hunger-you"
            others_msg_id = "chaosbear-card-hunger-other"
            brief_personal_msg_id = "chaosbear-card-hunger-you-brief"
            brief_others_msg_id = "chaosbear-card-hunger-other-brief"
            kwargs = {
                "position": new_pos,
                "gap": self._gap_to_bear(new_pos),
                "energy": new_energy,
            }
            payload["energy"] = new_energy
            payload["pos"] = new_pos
            event_delay = 20

        elif card == 4:
            # Backward push cancels the draw surge
            new_pos = max(0, new_pos - 3)
            self.schedule_sound("game_chaosbear/backpush.ogg", delay_ticks=4)
            personal_msg_id = "chaosbear-card-backward-you"
            others_msg_id = "chaosbear-card-backward-other"
            brief_personal_msg_id = "chaosbear-card-backward-you-brief"
            brief_others_msg_id = "chaosbear-card-backward-other-brief"
            kwargs = {"position": new_pos, "gap": self._gap_to_bear(new_pos)}
            payload["pos"] = new_pos

        else:
            # Random gift - forward/back 1-6
            self._broadcast_runner_event(
                player,
                "chaosbear-card-random-gift-you",
                "chaosbear-card-random-gift-other",
                brief_personal_message_id="chaosbear-card-random-gift-you-brief",
                brief_others_message_id="chaosbear-card-random-gift-other-brief",
            )
            amount = random.randint(1, 6)
            if random.random() < 0.5:
                new_pos = max(0, new_pos - amount)
                self.schedule_sound("game_chaosbear/backpush.ogg", delay_ticks=4)
                personal_msg_id = "chaosbear-gift-back-you"
                others_msg_id = "chaosbear-gift-back-other"
                brief_personal_msg_id = "chaosbear-gift-back-you-brief"
                brief_others_msg_id = "chaosbear-gift-back-other-brief"
            else:
                new_pos += amount
                self.schedule_sound(
                    f"game_chaosbear/impulsion{random.randint(1, 2)}.ogg",
                    delay_ticks=4,
                )
                personal_msg_id = "chaosbear-gift-forward-you"
                others_msg_id = "chaosbear-gift-forward-other"
                brief_personal_msg_id = "chaosbear-gift-forward-you-brief"
                brief_others_msg_id = "chaosbear-gift-forward-other-brief"
            kwargs = {
                "position": new_pos,
                "gap": self._gap_to_bear(new_pos),
                "amount": amount,
            }
            payload["pos"] = new_pos

        payload["personal_msg_id"] = personal_msg_id
        payload["others_msg_id"] = others_msg_id
        payload["brief_personal_msg_id"] = brief_personal_msg_id
        payload["brief_others_msg_id"] = brief_others_msg_id
        payload["kwargs"] = kwargs

        self.start_sequence(
            "turn_flow",
            [
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("card_effect", payload)],
                    delay_after_ticks=5,
                ),
                SequenceBeat(
                    ops=[SequenceOperation.callback_op("end_turn")],
                ),
            ],
            start_delay=event_delay,
            tag="turn_flow",
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _action_check_status(self, player: Player, action_id: str) -> None:
        """Check the current game status."""
        user = self.get_user(player)
        if not user:
            return

        self.live_status_box(
            player,
            "chaosbear_status",
            lambda _player, live_user: self._status_items(live_user.locale),
        )

