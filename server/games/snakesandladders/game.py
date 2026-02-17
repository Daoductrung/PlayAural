"""
Snakes and Ladders Game Implementation for PlayAural.

Classic board game where players race to 100.
"""





from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState


@dataclass
class SnakesPlayer(Player):
    """Player state for Snakes and Ladders."""

    position: int = 1  # Start at square 1
    finished: bool = False





@dataclass
@register_game
class SnakesAndLaddersGame(Game):
    """
    Snakes and Ladders.
    
    Race to square 100. Ladders move you up, Snakes move you down.
    Exact roll required to win (bounce back rule).
    """


    
    # Game State - Override players list with specific type for Mashumaro
    players: list[SnakesPlayer] = field(default_factory=list)
    
    # Game Logic State
    is_rolling: bool = False
    event_queue: list[tuple[int, str, dict]] = field(default_factory=list)

    # Game Constants
    WINNING_SQUARE = 100
    
    # Sound configurations
    NUM_STEP_SOUNDS = 3
    NUM_LADDER_SOUNDS = 3
    
    # Standard Snakes and Ladders board layout
    LADDERS = {
        1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 36: 44, 51: 67, 71: 91, 80: 100
    }
    SNAKES = {
        16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78
    }

    @classmethod
    def get_name(cls) -> str:
        return "Snakes and Ladders"

    @classmethod
    def get_type(cls) -> str:
        return "snakesandladders"

    @classmethod
    def get_category(cls) -> str:
        return "category-board-games"

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["rating", "games_played"]

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> SnakesPlayer:
        return SnakesPlayer(id=player_id, name=name, is_bot=is_bot)

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True

        # Initialize players
        for p in self.players:
            p.position = 1
            p.finished = False

        # Set turn order
        self.set_turn_players(self.get_active_players())

        # Play intro music/sounds (Reuse Pig music)
        self.play_music("game_pig/mus.ogg") 
        self.broadcast_l("game-snakesandladders-desc")
        
        self._start_turn()

    def _start_turn(self) -> None:
        """Start the current player's turn."""
        player = self.current_player
        if not player:
            return

        # Announce turn using custom message
        # We do NOT call self.announce_turn() to avoid the generic "It's X's turn" message.
        
        # Manually play turn sound (logic borrowed from TurnManagementMixin)
        user = self.get_user(player)
        # Note: We assume user object has preferences.play_turn_sound as used in base mixin
        if user and getattr(user.preferences, "play_turn_sound", True):
             user.play_sound("game_pig/turn.ogg")

        self.broadcast_l(
            "snakes-turn", 
            player=player.name, 
            position=player.position
        )

        # Jolt bots
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(20, 40))

        self.rebuild_all_menus()

    def create_turn_action_set(self, player: SnakesPlayer) -> ActionSet:
        action_set = ActionSet(name="turn")
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set.add(
            Action(
                id="roll",
                label=Localization.get(locale, "snakes-roll"),
                handler="_action_roll",
                is_enabled="_is_roll_enabled",
                is_hidden="_is_roll_hidden"
            )
        )
        return action_set

    # Visibility / Enabled checks
    def _is_roll_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.is_rolling:
            return "action-game-in-progress"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_roll_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
             return Visibility.HIDDEN
        if self.current_player != player:
             return Visibility.HIDDEN
        return Visibility.VISIBLE
        
    # WEB-SPECIFIC: Visibility Overrides
    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def create_standard_action_set(self, player: Player) -> ActionSet:
        """Add Check Positions to standard actions."""
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        # Add Check Positions action
        action_set.add(
            Action(
                id="check_positions",
                label=Localization.get(locale, "check-positions"),
                handler="_action_check_positions",
                is_enabled=None, # Always enabled
                # Only show in menu for Web clients
                is_hidden="_is_check_positions_hidden"
            )
        )
        
        # Reorder actions to put "Check positions" at the top of the standard lists
        # This makes it appear higher in the Actions menu
        if "check_positions" in action_set._order:
            action_set._order.remove("check_positions")
            action_set._order.insert(0, "check_positions")
            
        return action_set

    def _is_check_positions_hidden(self, player: Player) -> Visibility:
        """Hide Check Positions from menu unless on Web AND playing."""
        if self.status != "playing":
             return Visibility.HIDDEN
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("r", "Roll dice", ["roll"], state=KeybindState.ACTIVE)
        self.define_keybind("space", "Roll dice", ["roll"], state=KeybindState.ACTIVE)
        self.define_keybind("c", "Check positions", ["check_positions"], state=KeybindState.ALWAYS, include_spectators=True)

    def _action_check_positions(self, player: Player, action_id: str) -> None:
        """Announce current player positions."""
        user = self.get_user(player)
        if not user:
            return
            
        # Format for speech: "Trung 1, Bot 5"
        # Use comma for natural pause
        speech_parts = []
        
        for p in self.get_active_players():
            sp: SnakesPlayer = p # type: ignore
            speech_parts.append(f"{p.name} {sp.position}")
        
        # Speak the positions
        header = Localization.get(user.locale, "snakes-positions-header")
        user.speak(f"{header} {', '.join(speech_parts)}")


    def _action_roll(self, player: Player, action_id: str) -> None:
        """Handle roll action with sequential events."""
        snakes_player: SnakesPlayer = player # type: ignore
        self.is_rolling = True
        self.rebuild_all_menus() # Update UI to disable button
        
        # Roll dice (1-6)
        roll = random.randint(1, 6)
        
        # Play random dice roll sound (1-3)
        roll_variant = random.randint(1, 3)
        self.play_sound(f"game_squares/diceroll{roll_variant}.ogg")
        
        self.broadcast_l("snakes-roll-result", player=player.name, roll=roll)
        
        # Current tick for scheduling
        current_tick = self.sound_scheduler_tick
        
        # Delays
        step_delay_start = 8 # Wait after roll
        step_interval = 4    # Fast steps
        
        # --- PHASE 1: Movement Steps ---
        # Schedule sounds
        for i in range(roll):
             step_variant = random.randint(1, self.NUM_STEP_SOUNDS)
             self.schedule_sound(
                 f"game_squares/step{step_variant}.ogg", 
                 delay_ticks=step_delay_start + (i * step_interval)
             )

        # Calculate logical new position
        old_pos = snakes_player.position
        intermediate_pos = old_pos + roll
        
        # Event: Update position AFTER steps
        move_complete_tick = current_tick + step_delay_start + (roll * step_interval)
        self.event_queue.append((
            move_complete_tick, 
            "move", 
            {"player_id": player.id, "pos": intermediate_pos}
        ))
        
        next_event_tick = move_complete_tick + 2 # Tiny pause after move (reduced from 5)
        
        # --- PHASE 2: Bounce Back ---
        final_pre_interaction_pos = intermediate_pos
        
        if intermediate_pos > self.WINNING_SQUARE:
            overshoot = intermediate_pos - self.WINNING_SQUARE
            final_pre_interaction_pos = self.WINNING_SQUARE - overshoot
            
            # Bounce sound
            self.schedule_sound(
                "game_snakes/bounce.ogg", 
                delay_ticks=next_event_tick - current_tick
            )
            
            # Event: Bounce update
            self.event_queue.append((
                next_event_tick,
                "bounce",
                {"player_id": player.id, "pos": final_pre_interaction_pos}
            ))
            
            next_event_tick += 8 # Pause after bounce (reduced from 15)
            
        # --- PHASE 3: Interactions (Snake/Ladder) ---
        # Check interaction at the position where player landed (after potential bounce)
        
        final_pos = final_pre_interaction_pos
        is_win = False
        
        if final_pos == self.WINNING_SQUARE:
            # Win immediately (no further interactions)
            is_win = True
        elif final_pos in self.LADDERS:
            # Ladder
            top = self.LADDERS[final_pos]
            
            # Sound
            ladder_variant = random.randint(1, self.NUM_LADDER_SOUNDS)
            self.schedule_sound(
                f"game_snakes/ladder{ladder_variant}.ogg", 
                delay_ticks=next_event_tick - current_tick
            )
            
            # Event: Ladder Climb
            self.event_queue.append((
                next_event_tick,
                "ladder",
                {"player_id": player.id, "start": final_pos, "end": top}
            ))
            
            final_pos = top
            next_event_tick += 15 # Pause for ladder (reduced from 30)
            
            if final_pos == self.WINNING_SQUARE:
                is_win = True
                
        elif final_pos in self.SNAKES:
            # Snake
            tail = self.SNAKES[final_pos]
            
            # Sound
            self.schedule_sound(
                "game_snakes/snake.ogg", 
                delay_ticks=next_event_tick - current_tick
            )
            
            # Event: Snake Bite
            self.event_queue.append((
                next_event_tick,
                "snake",
                {"player_id": player.id, "start": final_pos, "end": tail}
            ))
            
            final_pos = tail
            next_event_tick += 12 # Pause for snake (reduced from 25)

        # --- PHASE 4: Conclusion ---
        
        if is_win:
             # Win event
             self.event_queue.append((
                 next_event_tick,
                 "win",
                 {"player_id": player.id}
             ))
        else:
             # End Turn event
             self.event_queue.append((
                 next_event_tick + 5, # Quick turn change (reduced from 10)
                 "end_turn",
                 {}
             ))

        # We do NOT manually set position here anymore. 
        # It is set by the event processor.

    def _process_events(self) -> None:
        """Process queued game events."""
        if not self.event_queue:
            return

        # Sort by tick just in case, though usually added in order
        # self.event_queue.sort(key=lambda x: x[0]) 
        # (Assuming append order is chronological for simplicity)
        
        # Process all events up to current tick
        remaining_events = []
        current_tick = self.sound_scheduler_tick
        
        for tick, event_type, data in self.event_queue:
            if tick <= current_tick:
                self._handle_event(event_type, data)
            else:
                remaining_events.append((tick, event_type, data))
        
        self.event_queue = remaining_events

    def _handle_event(self, event_type: str, data: dict) -> None:
        """Execute a single game event."""
        player_id = data.get("player_id")
        player = self.get_player_by_id(player_id) if player_id else None
        
        if event_type == "move":
            if player:
                new_pos = data["pos"]
                player.position = new_pos
                self.broadcast_l("snakes-move", player=player.name, position=new_pos)

        elif event_type == "bounce":
            if player:
                new_pos = data["pos"]
                player.position = new_pos
                self.broadcast_l("snakes-bounce", player=player.name, position=new_pos)

        elif event_type == "ladder":
            if player:
                start = data["start"]
                end = data["end"]
                player.position = end
                self.broadcast_l("snakes-ladder", player=player.name, start=start, end=end)

        elif event_type == "snake":
            if player:
                start = data["start"]
                end = data["end"]
                player.position = end
                self.broadcast_l("snakes-snake", player=player.name, start=start, end=end)

        elif event_type == "win":
            if player:
                self._handle_win(player) # type: ignore

        elif event_type == "end_turn":
            self.is_rolling = False
            self.end_turn()

    def _handle_win(self, winner: SnakesPlayer, delay: int = 0) -> None:
        """Handle win condition."""
        winner.finished = True
        self.winner = winner
        
        # Reuse Pig win sound
        self.play_sound("game_pig/win.ogg")
        self.broadcast_l("snakes-win", player=winner.name)
        
        self.finish_game()

    def end_turn(self) -> None:
        """Advance turn."""
        self.advance_turn(announce=False)
        self._start_turn()

    def on_tick(self) -> None:
        super().on_tick()
        # Process sound scheduler
        self.process_scheduled_sounds()
        # Process logic queue
        self._process_events()
        
        if self.status == "playing":
            BotHelper.on_tick(self)

    def bot_think(self, player: SnakesPlayer) -> str | None:
        """Bot always rolls."""
        return "roll"

    def build_game_result(self) -> GameResult:
        """Build standard game result."""
        winner = getattr(self, "winner", None)
        
        # Sort players by position (descending)
        sorted_players = sorted(
            self.get_active_players(), 
            key=lambda p: (p.finished, p.position), # Finished first, then highest position
            reverse=True
        )
        
        # Store final positions for end screen
        final_positions = {p.name: p.position for p in self.players}

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=p.id,
                    player_name=p.name,
                    is_bot=p.is_bot
                ) for p in sorted_players # Return sorted list
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "final_positions": final_positions
            }
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        
        # Players are already sorted in result.player_results
        for i, p_result in enumerate(result.player_results, 1):
            pos = result.custom_data["final_positions"].get(p_result.player_name, 0)
            lines.append(
                Localization.get(
                    locale, 
                    "snakes-end-score", 
                    rank=i, 
                    player=p_result.player_name, 
                    position=pos
                )
            )
            
        return lines


