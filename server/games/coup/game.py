"""
Coup Game Implementation for PlayAural.

A game of deduction and deception. Players start with two influences (character cards)
and two coins. The goal is to eliminate all other players' influences.

Actions:
- Income: Take 1 coin
- Foreign Aid: Take 2 coins (can be blocked by Duke)
- Coup: Pay 7 coins, choose player to lose influence (mandatory at 10+ coins)
- Duke: Take 3 coins
- Assassin: Pay 3 coins, choose player to lose influence (can be blocked by Contessa)
- Captain: Steal 2 coins from another player (can be blocked by Captain or Ambassador)
- Ambassador: Exchange cards with the deck
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility, MenuInput
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState

from .cards import Deck, Card, Character
from .player import CoupPlayer, CoupOptions
from .bot import CoupBot


@dataclass
@register_game
class CoupGame(Game):
    """
    Coup game implementation.
    """

    players: list[CoupPlayer] = field(default_factory=list)
    options: CoupOptions = field(default_factory=CoupOptions)

    # Game State
    deck: Deck = field(default_factory=Deck)
    turn_phase: str = "main"  # main, action_declared, waiting_block, resolving_challenge, exchanging

    # State tracking for interrupts/challenges
    active_action: str | None = None
    active_target_id: str | None = None
    active_claimer_id: str | None = None
    original_claimer_id: str | None = None
    return_count: int = 0

    # Timer state
    interrupt_timer_ticks: int = 0
    interrupt_duration_ticks: int = 0

    def __post_init__(self):
        super().__post_init__()

    @classmethod
    def get_name(cls) -> str:
        return "Coup"

    @classmethod
    def get_type(cls) -> str:
        return "coup"

    @classmethod
    def get_category(cls) -> str:
        return "category-card-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 6

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> CoupPlayer:
        """Create a new Coup player."""
        return CoupPlayer(id=player_id, name=name, is_bot=is_bot)

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 1

        # Initialize deck
        self.deck = Deck()
        self.deck.build_standard_deck()
        self.deck.shuffle()

        # Initial hands and coins
        active_players = self.get_active_players()
        for player in active_players:
            player.coins = 2
            player.influences = []
            player.is_dead = False
            for _ in range(2):
                card = self.deck.draw()
                if card:
                    player.influences.append(card)

        self.set_turn_players(active_players)

        # Play intro music
        self.play_music("game_coup/music.ogg")

        # Jolt bots
        BotHelper.jolt_bots(self, ticks=random.randint(10, 20))

        # Start first turn
        self.reset_turn_order()
        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player or not isinstance(player, CoupPlayer):
            return

        # Check for game winner
        alive = self.get_alive_players()
        if len(alive) <= 1:
            self._end_game(alive[0] if alive else None)
            return

        # Skip dead players
        if player.is_dead:
            self._end_turn()
            return

        # Announce turn
        self.announce_turn()

        self.turn_phase = "main"
        self.active_action = None
        self.active_target_id = None
        self.active_claimer_id = None
        self.original_claimer_id = None
        self.interrupt_timer_ticks = 0

        self.rebuild_all_menus()

    def _end_turn(self) -> None:
        """End current player's turn."""
        self.advance_turn(announce=False)
        self._start_turn()

    def create_turn_action_set(self, player: CoupPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # Lose Influence Actions
        for i in range(4):
            action_set.add(
                Action(
                    id=f"lose_influence_{i}",
                    label=Localization.get(locale, "coup-action-lose-influence"),
                    handler="_action_lose_influence",
                    is_enabled="_is_lose_influence_enabled",
                    is_hidden="_is_lose_influence_hidden",
                    get_label="_get_lose_influence_label",
                    show_in_actions_menu=False,
                )
            )

        # Exchange Actions
        for i in range(4):
            action_set.add(
                Action(
                    id=f"return_card_{i}",
                    label=Localization.get(locale, "coup-action-return-card"),
                    handler="_action_return_card",
                    is_enabled="_is_return_card_enabled",
                    is_hidden="_is_return_card_hidden",
                    get_label="_get_return_card_label",
                    show_in_actions_menu=False,
                )
            )

        # Interrupt Window Actions
        action_set.add(
            Action(
                id="challenge",
                label=Localization.get(locale, "coup-action-challenge"),
                handler="_action_challenge",
                is_enabled="_is_challenge_enabled",
                is_hidden="_is_interrupt_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="block",
                label=Localization.get(locale, "coup-action-block"),
                handler="_action_block",
                is_enabled="_is_block_enabled",
                is_hidden="_is_interrupt_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="pass",
                label=Localization.get(locale, "coup-action-pass"),
                handler="_action_pass",
                is_enabled="_is_pass_enabled",
                is_hidden="_is_interrupt_hidden",
                show_in_actions_menu=False,
            )
        )

        # Basic Actions
        action_set.add(
            Action(
                id="income",
                label=Localization.get(locale, "coup-action-income"),
                handler="_action_income",
                is_enabled="_is_income_enabled",
                is_hidden="_is_action_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="foreign_aid",
                label=Localization.get(locale, "coup-action-foreign-aid"),
                handler="_action_foreign_aid",
                is_enabled="_is_action_enabled",
                is_hidden="_is_action_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="coup",
                label=Localization.get(locale, "coup-action-coup"),
                handler="_action_coup",
                is_enabled="_is_coup_enabled",
                is_hidden="_is_action_hidden",
                input_request=MenuInput(
                    prompt="coup-select-target",
                    options="_target_options",
                    bot_select="_bot_select_target",
                ),
                show_in_actions_menu=False,
            )
        )

        # Character Actions
        action_set.add(
            Action(
                id="tax",
                label=Localization.get(locale, "coup-action-tax"),
                handler="_action_tax",
                is_enabled="_is_action_enabled",
                is_hidden="_is_action_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="assassinate",
                label=Localization.get(locale, "coup-action-assassinate"),
                handler="_action_assassinate",
                is_enabled="_is_assassinate_enabled",
                is_hidden="_is_action_hidden",
                input_request=MenuInput(
                    prompt="coup-select-target",
                    options="_target_options",
                    bot_select="_bot_select_target",
                ),
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="steal",
                label=Localization.get(locale, "coup-action-steal"),
                handler="_action_steal",
                is_enabled="_is_action_enabled",
                is_hidden="_is_action_hidden",
                input_request=MenuInput(
                    prompt="coup-select-target",
                    options="_target_options",
                    bot_select="_bot_select_target",
                ),
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="exchange",
                label=Localization.get(locale, "coup-action-exchange"),
                handler="_action_exchange",
                is_enabled="_is_action_enabled",
                is_hidden="_is_action_hidden",
                show_in_actions_menu=False,
            )
        )

        return action_set

    # ==========================================================================
    # Action Checks
    # ==========================================================================

    def _is_lose_influence_hidden(self, player: Player) -> Visibility:
        if self.turn_phase != "losing_influence" or player.id != self.active_target_id:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_lose_influence_enabled(self, player: Player, action_id: str | None = None) -> str | None:
        if self.turn_phase != "losing_influence" or player.id != self.active_target_id:
            return "action-not-available"

        if not action_id:
            return None

        coup_player: CoupPlayer = player  # type: ignore
        try:
            idx = int(action_id.split("_")[-1])
        except ValueError:
            return "action-not-available"

        if idx < 0 or idx >= len(coup_player.live_influences):
            return "action-not-available"

        return None

    def _get_lose_influence_label(self, player: Player, action_id: str) -> str:
        coup_player: CoupPlayer = player  # type: ignore
        try:
            idx = int(action_id.split("_")[-1])
        except ValueError:
            return "Lose Influence"

        if idx < 0 or idx >= len(coup_player.live_influences):
            return "Lose Influence"

        card = coup_player.live_influences[idx]
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, f"coup-card-{card.character.value}")

    def _is_return_card_hidden(self, player: Player) -> Visibility:
        if self.turn_phase != "exchanging" or self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_return_card_enabled(self, player: Player, action_id: str | None = None) -> str | None:
        if self.turn_phase != "exchanging" or self.current_player != player:
            return "action-not-available"

        if not action_id:
            return None

        coup_player: CoupPlayer = player  # type: ignore
        try:
            idx = int(action_id.split("_")[-1])
        except ValueError:
            return "action-not-available"

        if idx < 0 or idx >= len(coup_player.live_influences):
            return "action-not-available"

        return None

    def _get_return_card_label(self, player: Player, action_id: str) -> str:
        coup_player: CoupPlayer = player  # type: ignore
        try:
            idx = int(action_id.split("_")[-1])
        except ValueError:
            return "Return Card"

        if idx < 0 or idx >= len(coup_player.live_influences):
            return "Return Card"

        card = coup_player.live_influences[idx]
        user = self.get_user(player)
        locale = user.locale if user else "en"
        card_name = Localization.get(locale, f"coup-card-{card.character.value}")
        return Localization.get(locale, "coup-return-card-format", card=card_name)

    def _is_interrupt_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator or player.is_dead:
            return Visibility.HIDDEN
        if self.turn_phase not in ["action_declared", "waiting_block"]:
            return Visibility.HIDDEN

        # Original claimer/blocker cannot interrupt themselves
        if player.id == self.active_claimer_id:
            return Visibility.HIDDEN

        # In waiting_block (e.g. Duke blocking Foreign Aid), only Challenge or Pass makes sense, no second Block.
        # But this is just visibility, we handle specifics in is_enabled.
        return Visibility.VISIBLE

    def _is_challenge_enabled(self, player: Player) -> str | None:
        if self.turn_phase == "action_declared":
            # Can we challenge this action?
            unchallengeable = ["income", "foreign_aid", "coup"]
            if self.active_action in unchallengeable:
                return "coup-cannot-challenge-action"
            return None
        elif self.turn_phase == "waiting_block":
            # Can challenge a block
            return None
        return "coup-no-active-claim"

    def _is_block_enabled(self, player: Player) -> str | None:
        if self.turn_phase != "action_declared":
            return "coup-cannot-block-now"

        if self.active_action == "foreign_aid":
            return None  # Anyone can block with Duke

        if self.active_action == "assassinate":
            if player.id != self.active_target_id:
                return "coup-only-target-can-block"
            return None

        if self.active_action == "steal":
            if player.id != self.active_target_id:
                return "coup-only-target-can-block"
            return None

        return "coup-cannot-block-action"

    def _is_pass_enabled(self, player: Player) -> str | None:
        return None  # If the interrupt is visible, passing is enabled.

    def _is_action_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator or player.is_dead:
            return Visibility.HIDDEN
        if self.current_player != player or self.turn_phase != "main":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_action_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator or player.is_dead:
            return "action-not-playing"
        if self.current_player != player or self.turn_phase != "main":
            return "action-not-your-turn"

        coup_player: CoupPlayer = player  # type: ignore
        if coup_player.coins >= self.options.mandatory_coup_threshold:
            return "coup-must-coup"

        return None

    def _is_income_enabled(self, player: Player) -> str | None:
        return self._is_action_enabled(player)

    def _is_coup_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator or player.is_dead:
            return "action-not-playing"
        if self.current_player != player or self.turn_phase != "main":
            return "action-not-your-turn"

        coup_player: CoupPlayer = player  # type: ignore
        if coup_player.coins < 7:
            return "coup-not-enough-coins"

        return None

    def _is_assassinate_enabled(self, player: Player) -> str | None:
        err = self._is_action_enabled(player)
        if err:
            return err

        coup_player: CoupPlayer = player  # type: ignore
        if coup_player.coins < 3:
            return "coup-not-enough-coins"

        return None

    def _target_options(self, player: Player) -> list[str]:
        options = []
        for p in self.get_alive_players():
            if p != player:
                options.append(p.name)
        return options

    def _bot_select_target(self, player: Player, options: list[str]) -> str | None:
        if not options:
            return None
        return random.choice(options)

    # ==========================================================================
    # Action Handlers
    # ==========================================================================

    def _action_income(self, player: Player, action_id: str) -> None:
        coup_player: CoupPlayer = player  # type: ignore
        coup_player.coins += 1

        self.play_sound("game_coup/income.ogg")
        self.broadcast_l("coup-takes-income", player=player.name)

        self._end_turn()

    def _action_foreign_aid(self, player: Player, action_id: str) -> None:
        # Declare action, start interrupt timer
        self._declare_action(player.id, "foreign_aid")

    def _action_coup(self, player: Player, target_name: str, action_id: str) -> None:
        coup_player: CoupPlayer = player  # type: ignore
        target = self.get_player_by_name(target_name)

        if not target or target.is_dead:
            return

        coup_player.coins -= 7
        self.play_sound("game_coup/coup.ogg")
        self.broadcast_l("coup-plays-coup", player=player.name, target=target.name)

        self._prompt_lose_influence(target.id, "coup")

    def _action_tax(self, player: Player, action_id: str) -> None:
        self._declare_action(player.id, "tax")

    def _action_assassinate(self, player: Player, target_name: str, action_id: str) -> None:
        coup_player: CoupPlayer = player  # type: ignore
        target = self.get_player_by_name(target_name)

        if not target or target.is_dead:
            return

        coup_player.coins -= 3
        self._declare_action(player.id, "assassinate", target.id)

    def _action_steal(self, player: Player, target_name: str, action_id: str) -> None:
        target = self.get_player_by_name(target_name)

        if not target or target.is_dead:
            return

        self._declare_action(player.id, "steal", target.id)

    def _action_exchange(self, player: Player, action_id: str) -> None:
        self._declare_action(player.id, "exchange")

    def _declare_action(self, player_id: str, action: str, target_id: str | None = None) -> None:
        """Starts the interrupt window for a challengeable/blockable action."""
        self.active_action = action
        self.active_claimer_id = player_id
        self.original_claimer_id = player_id
        self.active_target_id = target_id
        self.turn_phase = "action_declared"
        self.interrupt_timer_ticks = self.options.timer_duration_seconds * 20
        self.interrupt_duration_ticks = self.interrupt_timer_ticks

        player = self.get_player_by_id(player_id)
        target = self.get_player_by_id(target_id) if target_id else None

        # Play claim sound and broadcast
        if action == "tax":
            self.play_sound("game_coup/claim_duke.ogg")
            self.broadcast_l("coup-claims-tax", player=player.name)
        elif action == "foreign_aid":
            # no character claimed, just standard action. Sound plays on resolution.
            self.broadcast_l("coup-claims-foreign-aid", player=player.name)
        elif action == "assassinate":
            self.play_sound("game_coup/claim_assassin.ogg")
            self.broadcast_l("coup-claims-assassinate", player=player.name, target=target.name if target else "")
        elif action == "steal":
            self.play_sound("game_coup/claim_captain.ogg")
            self.broadcast_l("coup-claims-steal", player=player.name, target=target.name if target else "")
        elif action == "exchange":
            self.play_sound("game_coup/claim_ambassador.ogg")
            self.broadcast_l("coup-claims-exchange", player=player.name)

        self.broadcast_l("coup-waiting-for-reactions")
        self.rebuild_all_menus()
        BotHelper.jolt_bots(self, ticks=random.randint(20, 40))

    def _action_challenge(self, player: Player, action_id: str) -> None:
        # Resolve challenge
        if self.turn_phase not in ["action_declared", "waiting_block"]:
            return

        self.interrupt_timer_ticks = 0
        self.play_sound("game_coup/challenge.ogg")
        claimer = self.get_player_by_id(self.active_claimer_id)

        self.broadcast_l("coup-challenges", challenger=player.name, target=claimer.name)

        # Verify if claimer has the required character
        required_char = self._get_required_character_for_action(self.active_action)
        if self.turn_phase == "waiting_block":
            required_char = self._get_required_character_for_block(self.active_action)

        # DOES claimer have the character?
        # required_char could be a list for blocks like Steal
        has_character = False
        revealed_char = None

        if isinstance(required_char, list):
            for rc in required_char:
                if claimer.has_influence(rc):
                    has_character = True
                    revealed_char = rc
                    break
        else:
            if claimer.has_influence(required_char):
                has_character = True
                revealed_char = required_char

        if has_character:
            # Challenge fails! Challenger loses influence
            self.play_sound("game_coup/challengesuccess.ogg") # Claimer successfully proved
            self.broadcast_l("coup-challenge-failed", player=claimer.name, character=revealed_char)

            # Claimer puts card back and draws new one
            for card in claimer.live_influences:
                if card.character == revealed_char:
                    self.deck.add(card)
                    self.deck.shuffle()
                    claimer.influences.remove(card)
                    new_card = self.deck.draw()
                    claimer.influences.append(new_card)
                    break

            # Record state so we know what happens AFTER they lose influence
            if self.turn_phase == "action_declared":
                self._next_action_after_lose = "resolve_action"
            else:
                self._next_action_after_lose = "end_turn" # Block succeeded, turn ends
                self.broadcast_l("coup-bluff-wrong", challenger=player.name)

                # Play block success sound
                self.broadcast_l("coup-block-successful", blocker=claimer.name)
                if self.active_action == "foreign_aid":
                    self.play_sound("game_coup/block_duke.ogg")
                elif self.active_action == "assassinate":
                    self.play_sound("game_coup/block_contessa.ogg")
                elif self.active_action == "steal":
                    self.play_sound("game_coup/block_stealing.ogg")

            # Challenger loses influence
            self._prompt_lose_influence(player.id, "failed_challenge")

        else:
            # Challenge succeeds! Claimer loses influence
            self.play_sound("game_coup/challengefail.ogg") # Claimer failed to prove
            self.broadcast_l("coup-challenge-succeeded", player=claimer.name)

            # Record state so we know what happens AFTER they lose influence
            if self.turn_phase == "action_declared":
                self._next_action_after_lose = "end_turn"
            elif self.turn_phase == "waiting_block":
                self._next_action_after_lose = "resolve_action"

            self.broadcast_l("coup-bluff-called", player=claimer.name)
            # Claimer loses influence
            self._prompt_lose_influence(claimer.id, "lost_challenge")

    def _action_block(self, player: Player, action_id: str) -> None:
        if self.turn_phase != "action_declared":
            return

        self.interrupt_timer_ticks = 0
        claimer = self.get_player_by_id(self.active_claimer_id)

        # Depends on what is blocked
        if self.active_action == "foreign_aid":
            self.play_sound("game_coup/claim_duke.ogg") # Claiming Duke to block
            self.broadcast_l("coup-blocks-foreign-aid", blocker=player.name, target=claimer.name)
        elif self.active_action == "assassinate":
            self.play_sound("game_coup/claim_contessa.ogg") # Claiming Contessa
            self.broadcast_l("coup-blocks-assassinate", blocker=player.name, target=claimer.name)
        elif self.active_action == "steal":
            # For steal, might be Captain or Ambassador. For simplicity, just use Ambassador claim sound
            # or Captain claim sound randomly, or let's just say they claim to block.
            self.play_sound("game_coup/claim_ambassador.ogg")
            self.broadcast_l("coup-blocks-steal", blocker=player.name, target=claimer.name)

        # Enter "waiting_block" phase where the BLOCK can be challenged
        self.turn_phase = "waiting_block"
        self.active_claimer_id = player.id # Blocker is now claiming to have a role
        self.interrupt_timer_ticks = self.options.timer_duration_seconds * 20
        self.interrupt_duration_ticks = self.interrupt_timer_ticks

        self.broadcast_l("coup-waiting-for-reactions")
        self.rebuild_all_menus()
        BotHelper.jolt_bots(self, ticks=random.randint(20, 40))

    def _action_pass(self, player: Player, action_id: str) -> None:
        # A single player passing doesn't end the timer, just stops their jolt or handles UI.
        # But for bots, we can track who passed to speed it up. For now, do nothing special.
        pass

    def _get_required_character_for_action(self, action: str) -> str:
        mapping = {
            "tax": "duke",
            "assassinate": "assassin",
            "steal": "captain",
            "exchange": "ambassador"
        }
        return mapping.get(action, "")

    def _get_required_character_for_block(self, action: str) -> str | list[str]:
        mapping = {
            "foreign_aid": "duke",
            "assassinate": "contessa",
            "steal": ["captain", "ambassador"]
        }
        return mapping.get(action, "")

    def on_tick(self) -> None:
        super().on_tick()
        if not self.game_active:
            return

        if self.interrupt_timer_ticks > 0:
            self.interrupt_timer_ticks -= 1
            if self.interrupt_timer_ticks == 0:
                # Timer expired! Resolve current state
                if self.turn_phase == "action_declared":
                    # Nobody challenged or blocked, action resolves
                    self._resolve_action()
                elif self.turn_phase == "waiting_block":
                    # Nobody challenged the block, action fails
                    blocker = self.get_player_by_id(self.active_claimer_id)
                    self.broadcast_l("coup-block-successful", blocker=blocker.name if blocker else "Someone")
                    if self.active_action == "foreign_aid":
                        self.play_sound("game_coup/block_duke.ogg")
                    elif self.active_action == "assassinate":
                        self.play_sound("game_coup/block_contessa.ogg")
                    elif self.active_action == "steal":
                        self.play_sound("game_coup/block_stealing.ogg")
                    self._end_turn()

        CoupBot.on_tick(self)

    def _resolve_action(self) -> None:
        """Resolves the active action after no challenges/blocks occur or they fail."""
        self.broadcast_l("coup-action-resolves")
        player = self.get_player_by_id(self.original_claimer_id)
        target = self.get_player_by_id(self.active_target_id)

        if self.active_action == "foreign_aid":
            player.coins += 2
            self.play_sound("game_coup/foreign_aid.ogg")
            self.broadcast_l("coup-takes-foreign-aid", player=player.name)
            self._end_turn()

        elif self.active_action == "tax":
            player.coins += 3
            self.play_sound("game_coup/tax.ogg")
            self.broadcast_l("coup-takes-tax", player=player.name)
            self._end_turn()

        elif self.active_action == "assassinate":
            self.play_sound("game_coup/assassinate.ogg")
            self.broadcast_l("coup-assassinates", player=player.name, target=target.name)
            self._prompt_lose_influence(target.id, "assassinated")

        elif self.active_action == "steal":
            stolen = min(2, target.coins)
            target.coins -= stolen
            player.coins += stolen
            self.play_sound("game_coup/steal.ogg")
            self.broadcast_l("coup-steals", player=player.name, target=target.name, amount=stolen)
            self._end_turn()

        elif self.active_action == "exchange":
            self.play_sound("game_coup/exchange_start.ogg")
            self.broadcast_l("coup-exchanges", player=player.name)
            # Add 2 cards to hand, transition to exchange phase
            card1 = self.deck.draw()
            card2 = self.deck.draw()
            if card1: player.influences.append(card1)
            if card2: player.influences.append(card2)

            self.turn_phase = "exchanging"
            self.interrupt_timer_ticks = 0
            self.rebuild_all_menus()

            if player.is_bot:
                BotHelper.jolt_bot(player, ticks=random.randint(10, 20))


    def _action_return_card(self, player: Player, action_id: str) -> None:
        if self.turn_phase != "exchanging" or self.current_player != player:
            return

        coup_player: CoupPlayer = player  # type: ignore
        try:
            idx = int(action_id.split("_")[-1])
        except ValueError:
            return

        if idx < 0 or idx >= len(coup_player.live_influences):
            return

        card = coup_player.live_influences[idx]
        self.deck.add(card)
        self.deck.shuffle()
        coup_player.influences.remove(card)

        # Check if we are done exchanging
        # Target live is original live count (usually 2, sometimes 1)
        # We had live_count + 2 cards. We return 2.
        # So when len(live) == expected, we are done.
        # For now, just count if we've returned 2.
        # It's easier: if len(live) > (2 if alive else 1), keep returning
        # But wait, max normal live is 2. So we return until live == (original count).
        # We don't explicitly store original count.
        # But since we draw 2, we return 2.
        # We need to track how many we returned.
        # Let's just track it via the deck state, but simpler: Add a state variable.
        if getattr(self, "return_count", 0) == 0:
            self.return_count = 1
            self.rebuild_all_menus()
        else:
            self.return_count = 0
            self.play_sound("game_coup/exchange_complete.ogg")
            self.broadcast_l("coup-exchange-complete", player=player.name)
            self._end_turn()

    def _prompt_lose_influence(self, player_id: str, reason: str) -> None:
        """Prompts a player to choose which influence to lose."""
        player = self.get_player_by_id(player_id)
        if not player or player.is_dead:
            self._post_lose_influence()
            return

        live = player.live_influences
        if len(live) == 1:
            # Only one left, auto-lose it
            self.play_sound(f"game_coup/chardestroy{random.randint(1, 2)}.ogg")
            player.reveal_influence(0)
            self.broadcast_l("coup-loses-influence", player=player.name, character=live[0].character)
            if player.is_dead:
                self.broadcast_l("coup-player-eliminated", player=player.name)
            self._post_lose_influence()
        else:
            # Need to pick
            self.turn_phase = "losing_influence"
            self.active_target_id = player.id
            self.rebuild_all_menus()

            if player.is_bot:
                BotHelper.jolt_bot(player, ticks=random.randint(10, 20))
            else:
                user = self.get_user(player)
                if user:
                    user.speak_l("coup-must-lose-influence", buffer="game")

    def _action_lose_influence(self, player: Player, action_id: str) -> None:
        if self.turn_phase != "losing_influence" or player.id != self.active_target_id:
            return

        coup_player: CoupPlayer = player  # type: ignore
        try:
            idx = int(action_id.split("_")[-1])
        except ValueError:
            return

        if idx < 0 or idx >= len(coup_player.live_influences):
            return

        self.play_sound(f"game_coup/chardestroy{random.randint(1, 2)}.ogg")
        char = coup_player.live_influences[idx].character
        coup_player.reveal_influence(idx)
        self.broadcast_l("coup-loses-influence", player=player.name, character=char)

        self._post_lose_influence()

    def _post_lose_influence(self) -> None:
        next_action = getattr(self, "_next_action_after_lose", "end_turn")
        if next_action == "end_turn":
            self._end_turn()
        elif next_action == "resolve_action":
            self._resolve_action()

        self._next_action_after_lose = "end_turn"

    def _end_game(self, winner: CoupPlayer | None) -> None:
        """End the game."""
        self.play_sound("game_chaosbear/wingame.ogg")
        if winner:
            self.broadcast_l("game-winner", player=winner.name)
        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with Coup-specific data."""
        alive = self.get_alive_players()
        winner = alive[0] if alive else None

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=p.id,
                    player_name=p.name,
                    is_bot=p.is_bot,
                )
                for p in self.players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_ids": [winner.id] if winner else None,
                "winner_score": 1,
            },
        )

    def get_alive_players(self) -> list[CoupPlayer]:
        """Get all alive players."""
        return [p for p in self.players if not getattr(p, "is_spectator", False) and not getattr(p, "is_dead", False)]
