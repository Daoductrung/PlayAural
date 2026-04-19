from __future__ import annotations

import random
from typing import TYPE_CHECKING

from ...game_utils.bot_helper import BotHelper

if TYPE_CHECKING:
    from .game import CoupGame
    from .player import CoupPlayer


# ---------------------------------------------------------------------------
# Card valuation weights — higher = more valuable to keep.
# Context (game phase, coins, opponent state) adjusts dynamically.
# ---------------------------------------------------------------------------
_BASE_CARD_VALUES: dict[str, float] = {
    "duke": 8.0,
    "assassin": 7.0,
    "captain": 6.0,
    "ambassador": 4.0,
    "contessa": 5.0,
}


class CoupBot(BotHelper):
    """Dedicated Bot class for Coup — smart, adaptive, human-like."""

    # ------------------------------------------------------------------
    # Helper: game-phase detection
    # ------------------------------------------------------------------

    @classmethod
    def _game_phase(cls, game: "CoupGame") -> str:
        """Return 'early', 'mid', or 'late' based on game state."""
        alive = game.get_alive_players()
        total_live_cards = sum(len(p.live_influences) for p in alive)
        alive_count = len(alive)

        if alive_count <= 2 or total_live_cards <= 3:
            return "late"
        if any(p.coins >= 7 for p in alive):
            return "mid"
        high_card_count = sum(1 for p in alive if len(p.live_influences) == 2)
        if high_card_count >= alive_count - 1:
            return "early"
        return "mid"

    @classmethod
    def _is_1v1(cls, game: "CoupGame") -> bool:
        """True when exactly 2 players are alive."""
        return len(game.get_alive_players()) == 2

    # ------------------------------------------------------------------
    # Helper: opponent modeling
    # ------------------------------------------------------------------

    @classmethod
    def _estimate_opponent_roles(
        cls, game: "CoupGame", bot: "CoupPlayer", target: "CoupPlayer"
    ) -> dict[str, float]:
        """Estimate probability that *target* holds each role.

        Returns a dict mapping role name -> confidence [0, 1].
        Higher means more likely to hold.
        """
        dead_cards: dict[str, int] = {}
        bot_cards: dict[str, int] = {}
        for role in ("duke", "assassin", "captain", "ambassador", "contessa"):
            dead_cards[role] = 0
            bot_cards[role] = 0

        for p in game.get_active_players():
            for c in p.dead_influences:
                dead_cards[c.character.value] = dead_cards.get(c.character.value, 0) + 1
        for c in bot.live_influences:
            bot_cards[c.character.value] = bot_cards.get(c.character.value, 0) + 1

        # Cards that could be in anyone else's hand (3 copies each)
        unknown: dict[str, int] = {}
        total_unknown = 0
        for role in dead_cards:
            remaining = 3 - dead_cards[role] - bot_cards[role]
            unknown[role] = max(remaining, 0)
            total_unknown += max(remaining, 0)

        # Base probability from card distribution
        probs: dict[str, float] = {}
        for role in unknown:
            probs[role] = unknown[role] / total_unknown if total_unknown > 0 else 0.2

        # Adjust based on history — but avoid double-counting with player_claims.
        # player_claims is maintained by game.py in parallel with _player_history
        # action events, so we only use _player_history here.
        history = game._player_history.get(target.id, [])
        claimed_roles_from_history: set[str] = set()
        for event in history:
            etype = event.get("type")
            if etype == "proved_role":
                # They proved they had this role, but card was replaced.
                # Slight downward adjustment (card is now unknown).
                role = event.get("role", "")
                if role in probs:
                    probs[role] = max(probs[role] - 0.05, 0.0)
            elif etype == "claim_unchallenged":
                role = event.get("role", "")
                if role in probs and role not in claimed_roles_from_history:
                    probs[role] = min(probs[role] + 0.20, 1.0)
                    claimed_roles_from_history.add(role)
            elif etype == "action":
                action = event.get("action", "")
                implied = game._get_required_character_for_action(action)
                if implied and implied in probs and implied not in claimed_roles_from_history:
                    probs[implied] = min(probs[implied] + 0.15, 1.0)
                    claimed_roles_from_history.add(implied)

        return probs

    @classmethod
    def _bluff_count(cls, game: "CoupGame", player_id: str) -> int:
        """Count how many times a player was caught bluffing."""
        return sum(
            1 for e in game._player_history.get(player_id, [])
            if e.get("type") == "caught_bluffing"
        )

    @classmethod
    def _trust_score(cls, game: "CoupGame", player_id: str) -> float:
        """Return a trust score [0, 1] for a player.  Lower = less trustworthy."""
        history = game._player_history.get(player_id, [])
        proved = sum(1 for e in history if e.get("type") == "proved_role")
        bluffed = sum(1 for e in history if e.get("type") == "caught_bluffing")
        total = proved + bluffed
        if total == 0:
            return 0.5
        return proved / total

    @classmethod
    def _aggression_toward(
        cls, game: "CoupGame", attacker_id: str, victim_id: str
    ) -> int:
        """Count how many times *attacker* targeted *victim* with hostile actions."""
        hostile = {"assassinate", "steal", "coup"}
        return sum(
            1 for e in game._player_history.get(attacker_id, [])
            if e.get("type") == "action"
            and e.get("action") in hostile
            and e.get("target_id") == victim_id
        )

    @classmethod
    def _hand_quality(cls, game: "CoupGame", bot: "CoupPlayer") -> float:
        """Return average card value of bot's current hand (higher = better)."""
        live = bot.live_influences
        if not live:
            return 0.0
        return sum(cls._card_value(game, bot, c.character.value) for c in live) / len(live)

    # ------------------------------------------------------------------
    # A. Smart influence loss — pick which card to sacrifice
    # ------------------------------------------------------------------

    @classmethod
    def _card_value(
        cls, game: "CoupGame", bot: "CoupPlayer", role: str
    ) -> float:
        """Dynamic card value considering game context."""
        phase = cls._game_phase(game)
        base = _BASE_CARD_VALUES.get(role, 3.0)

        if role == "contessa":
            # Count opponents who can afford assassination
            assassin_threats = sum(
                1 for p in game.get_alive_players()
                if p.id != bot.id and p.coins >= 3
            )
            base += assassin_threats * 1.5
            if phase == "late":
                base += 2.0

        elif role == "duke":
            if phase == "early":
                base += 3.0
            elif phase == "late" and bot.coins >= 7:
                base -= 2.0

        elif role == "assassin":
            if bot.coins < 3:
                base -= 3.0
            else:
                base += 2.0
            if phase == "late":
                base += 2.0

        elif role == "captain":
            rich_opponents = sum(
                1 for p in game.get_alive_players()
                if p.id != bot.id and p.coins >= 2
            )
            base += rich_opponents * 1.0
            if phase == "late":
                base += 1.0

        elif role == "ambassador":
            if phase == "early":
                base += 2.0
            elif phase == "late":
                base -= 2.0

        return base

    @classmethod
    def bot_lose_influence(cls, game: "CoupGame", player: "CoupPlayer") -> None:
        """Bot picks the least valuable influence to lose."""
        live = player.live_influences
        if not live:
            return

        if len(live) == 1:
            game.execute_action(player, "lose_influence_0")
            return

        values = []
        for i, card in enumerate(live):
            values.append((cls._card_value(game, player, card.character.value), i))

        values.sort(key=lambda x: x[0])
        worst_idx = values[0][1]
        game.execute_action(player, f"lose_influence_{worst_idx}")

    # ------------------------------------------------------------------
    # B. Smart exchange — score card combinations
    # ------------------------------------------------------------------

    @classmethod
    def bot_resolve_exchange(cls, game: "CoupGame", player: "CoupPlayer") -> None:
        """Bot resolves Ambassador exchange by keeping the best cards."""
        draw_count = game._exchange_draw_count
        live_count = len([c for c in player.influences if not c.is_revealed])

        target_keep = live_count - draw_count

        if target_keep <= 0:
            cards = player.live_influences[:]
            for c in cards:
                player.influences.remove(c)
                game.deck.add(c)
            game.deck.shuffle()

            if not player.live_influences:
                player.is_dead = True
                game.broadcast_l("coup-player-eliminated", buffer="game", player=player.name)

            game.play_sound("game_coup/exchange_complete.ogg")
            game.broadcast_l("coup-exchange-complete", buffer="game", player=player.name)
            game._end_turn()
            return

        live = player.live_influences[:]
        scored = []
        for card in live:
            scored.append((cls._card_value(game, player, card.character.value), card))

        scored.sort(key=lambda x: x[0], reverse=True)
        keep = [card for _, card in scored[:target_keep]]
        return_cards = [card for _, card in scored[target_keep:]]

        player.influences = [c for c in player.influences if c.is_revealed] + keep
        for c in return_cards:
            game.deck.add(c)
        game.deck.shuffle()

        if not player.live_influences:
            player.is_dead = True
            game.broadcast_l("coup-player-eliminated", buffer="game", player=player.name)

        game.play_sound("game_coup/exchange_complete.ogg")
        game.broadcast_l("coup-exchange-complete", buffer="game", player=player.name)
        game._end_turn()

    # ------------------------------------------------------------------
    # Tick entry point
    # ------------------------------------------------------------------

    @classmethod
    def on_tick(cls, game: "CoupGame") -> None:
        """Process bot actions for Coup."""
        if not game.game_active or game.is_resolving:
            return

        if game.turn_phase in ("action_declared", "waiting_block"):
            for player in game.get_alive_players():
                if player.is_bot and player.id != game.active_claimer_id:
                    cls.process_bot_action(
                        bot=player,
                        think_fn=lambda p=player: cls.bot_think(game, p),
                        execute_fn=lambda action_id, p=player: game.execute_action(p, action_id),
                    )
        elif game.turn_phase == "losing_influence":
            target = game.get_player_by_id(game._losing_player_id)
            if target and target.is_bot:
                if target.bot_think_ticks > 0:
                    target.bot_think_ticks -= 1
                else:
                    cls.bot_lose_influence(game, target)
        elif game.turn_phase == "exchanging":
            current = game.current_player
            if current and current.is_bot:
                if current.bot_think_ticks > 0:
                    current.bot_think_ticks -= 1
                else:
                    cls.bot_resolve_exchange(game, current)
        else:
            current = game.current_player
            if current and current.is_bot:
                cls.process_bot_action(
                    bot=current,
                    think_fn=lambda: cls.bot_think(game, current),
                    execute_fn=lambda action_id: game.execute_action(current, action_id),
                )

    # ------------------------------------------------------------------
    # Core decision dispatcher
    # ------------------------------------------------------------------

    @classmethod
    def bot_think(cls, game: "CoupGame", player: "CoupPlayer") -> str | None:
        if player.is_dead:
            return None

        if game.turn_phase in ("action_declared", "waiting_block"):
            if player.id == game.active_claimer_id:
                return None

            claimer = game.get_player_by_id(game.active_claimer_id)
            if not claimer:
                return None

            if cls._decide_challenge(game, player, claimer):
                return "challenge"

            if game.turn_phase == "action_declared" and game._is_block_enabled(player) is None:
                if cls._decide_block(game, player):
                    return "block"

            # Survival override: if passing guarantees death, force a response.
            # This triggers when assassination targets the bot with 1 card and
            # no Contessa — doing nothing is certain death, so any chance of
            # survival (challenge or bluff-block) is strictly better.
            if cls._is_pass_lethal(game, player):
                return cls._desperation_response(game, player, claimer)

            return "pass"

        if game.turn_phase == "main" and game.current_player == player:
            return cls._decide_main_action(game, player)

        return None

    # ------------------------------------------------------------------
    # Survival logic — "nothing to lose" override
    # ------------------------------------------------------------------

    @classmethod
    def _is_pass_lethal(cls, game: "CoupGame", bot: "CoupPlayer") -> bool:
        """True when passing the current interrupt guarantees the bot's death.

        Currently the only case: assassination target with exactly 1 live card
        and no Contessa (if the bot had Contessa, _decide_block already
        returned True above).
        """
        return (
            game.turn_phase == "action_declared"
            and game.active_action == "assassinate"
            and game.active_target_id == bot.id
            and len(bot.live_influences) == 1
        )

    @classmethod
    def _desperation_response(
        cls, game: "CoupGame", bot: "CoupPlayer", claimer: "CoupPlayer"
    ) -> str:
        """Choose between challenge and bluff-block when passing = death.

        Both options risk death but give a non-zero chance to survive,
        which is strictly better than the 0% survival of passing.
        """
        # --- P(survive by challenging) = P(claimer doesn't have Assassin) ---
        dead_assassins = sum(
            1 for p in game.get_active_players()
            for c in p.dead_influences if c.character.value == "assassin"
        )
        bot_assassins = sum(
            1 for c in bot.live_influences if c.character.value == "assassin"
        )
        remaining_assassins = max(3 - dead_assassins - bot_assassins, 0)

        if remaining_assassins == 0:
            return "challenge"  # 100% certain they're bluffing

        total_other_live = sum(
            len(p.live_influences) for p in game.get_alive_players()
            if p.id != bot.id
        )
        claimer_live = len(claimer.live_influences)

        # P(claimer has no Assassin) via hypergeometric approximation
        pool = max(total_other_live, 1)
        p_claimer_has_none = 1.0
        for _ in range(claimer_live):
            if pool <= 0:
                break
            p_claimer_has_none *= max(1.0 - remaining_assassins / pool, 0.0)
            pool -= 1

        p_challenge_survive = p_claimer_has_none  # They DON'T have it → we win

        # Adjust with trust: untrustworthy players bluff more
        trust = cls._trust_score(game, claimer.id)
        # Low trust → higher chance they're bluffing → higher challenge survival
        p_challenge_survive = p_challenge_survive * (1.3 - trust * 0.6)
        p_challenge_survive = max(0.0, min(p_challenge_survive, 1.0))

        # --- P(survive by bluff-blocking with Contessa) ---
        # = P(nobody challenges our Contessa claim)
        dead_contessas = sum(
            1 for p in game.get_active_players()
            for c in p.dead_influences if c.character.value == "contessa"
        )
        bot_contessas = sum(
            1 for c in bot.live_influences if c.character.value == "contessa"
        )
        known_contessas = dead_contessas + bot_contessas

        if known_contessas >= 3:
            # All Contessas accounted for — everyone knows it's a bluff
            return "challenge"

        # Base believability of the Contessa claim
        if known_contessas == 2:
            p_block_survive = 0.25
        elif known_contessas == 1:
            p_block_survive = 0.55
        else:
            p_block_survive = 0.70

        # Our credibility affects how likely the bluff is challenged
        if cls._bluff_count(game, bot.id) > 0:
            p_block_survive *= 0.65

        past_claims = game.player_claims.get(bot.id, set())
        if len(past_claims) > len(bot.live_influences):
            # We've claimed more roles than we have cards — suspicious
            p_block_survive *= 0.60

        # Player count: more opponents = more potential challengers
        alive_others = len(game.get_alive_players()) - 1
        if alive_others == 1:
            p_block_survive += 0.10  # Only one person to convince
        elif alive_others >= 3:
            p_block_survive -= (alive_others - 2) * 0.08

        p_block_survive = max(0.05, min(p_block_survive, 0.90))

        # Pick the option with higher survival probability
        if p_challenge_survive >= p_block_survive:
            return "challenge"
        return "block"

    # ------------------------------------------------------------------
    # C + E. Challenge decision — EV-based with opponent modeling
    # ------------------------------------------------------------------

    @classmethod
    def _decide_challenge(
        cls, game: "CoupGame", bot: "CoupPlayer", claimer: "CoupPlayer"
    ) -> bool:
        """Expected-value based challenge decision with opponent modeling."""
        if game.turn_phase == "waiting_block":
            required_char = game._get_required_character_for_block(game.active_action)
        else:
            required_char = game._get_required_character_for_action(game.active_action)

        if not required_char:
            return False

        req_list = required_char if isinstance(required_char, list) else [required_char]

        # --- Gather known card information ---
        dead_cards: dict[str, int] = {}
        for role in ("duke", "assassin", "captain", "ambassador", "contessa"):
            dead_cards[role] = 0
        for p in game.get_active_players():
            for c in p.dead_influences:
                dead_cards[c.character.value] = dead_cards.get(c.character.value, 0) + 1

        bot_cards: dict[str, int] = {}
        for c in bot.live_influences:
            bot_cards[c.character.value] = bot_cards.get(c.character.value, 0) + 1

        # --- Mathematical certainty ---
        all_exhausted = True
        for rc in req_list:
            known = dead_cards.get(rc, 0) + bot_cards.get(rc, 0)
            if known < 3:
                all_exhausted = False
                break
        if all_exhausted:
            return True

        # --- Probability claimer has the card ---
        # Use hypergeometric-inspired estimate: P(has at least 1 copy)
        # among claimer's live cards, given remaining copies in the unknown pool.
        total_other_live = sum(
            len(p.live_influences) for p in game.get_alive_players()
            if p.id != bot.id
        )
        claimer_live = len(claimer.live_influences)

        best_p_has = 0.0
        for rc in req_list:
            known = dead_cards.get(rc, 0) + bot_cards.get(rc, 0)
            remaining = max(3 - known, 0)
            if remaining == 0 or total_other_live == 0:
                continue
            # P(claimer has none of role rc) ≈ product of (1 - remaining/pool) for each card
            # Simple approximation for small numbers
            pool = total_other_live
            p_none = 1.0
            for _ in range(claimer_live):
                if pool <= 0:
                    break
                p_none *= max(1.0 - remaining / pool, 0.0)
                pool -= 1
            best_p_has = max(best_p_has, 1.0 - p_none)

        # Adjust with trust score
        trust = cls._trust_score(game, claimer.id)
        # Blend: raw probability weighted by trust.  Low trust = more likely bluffing.
        p_has_card = best_p_has * (0.4 + trust * 0.6)

        # Suspicion: claimed more unique roles than live cards
        past_claims = game.player_claims.get(claimer.id, set())
        if len(past_claims) > claimer_live:
            p_has_card *= 0.55

        # 1v1 adjustment: in heads-up, bluffing is much more common
        if cls._is_1v1(game):
            p_has_card *= 0.75

        p_bluffing = 1.0 - p_has_card

        # --- Expected value ---
        bot_cards_count = len(bot.live_influences)
        is_original_actor = (bot.id == game.original_claimer_id)

        # Value of winning the challenge (they lose a card)
        ev_win = 8.0

        if is_original_actor and game.turn_phase == "waiting_block":
            # Bot's own action was blocked — winning the challenge means
            # the block fails and our original action resolves!
            # The blocker also loses a card from the challenge itself.
            if game.active_action == "assassinate":
                ev_win = 22.0  # Block fails → assassination goes through + they lose challenge card
            elif game.active_action == "steal":
                ev_win = 14.0  # Block fails → steal goes through
            elif game.active_action == "tax":
                ev_win = 12.0  # Block fails → we get our 3 coins
            elif game.active_action == "foreign_aid":
                ev_win = 10.0
        elif game.active_action == "assassinate" and game.active_target_id == bot.id:
            ev_win = 18.0  # Stopping assassination targeting us
        elif game.active_action == "steal" and game.active_target_id == bot.id:
            ev_win = 5.0 + min(bot.coins, 2) * 1.5
        elif game.active_action == "tax":
            ev_win = 6.0  # Stopping tax is lower priority

        # Cost of losing
        ev_lose = -10.0
        if bot_cards_count == 1:
            ev_lose = -25.0

        expected_value = p_bluffing * ev_win + p_has_card * ev_lose

        # --- Phase / situational adjustments ---
        phase = cls._game_phase(game)
        if phase == "early":
            expected_value -= 2.0
        elif phase == "late":
            if claimer.coins >= 7:
                expected_value += 3.0

        # Desperation: being assassinated with 1 card
        if game.active_action == "assassinate" and game.active_target_id == bot.id:
            if bot_cards_count == 1:
                expected_value += 5.0

        # 1v1: be more aggressive overall
        if cls._is_1v1(game):
            expected_value += 2.0

        threshold = random.uniform(-1.0, 1.0)
        return expected_value > threshold

    # ------------------------------------------------------------------
    # G. Smart blocking — risk-aware, role-preserving
    # ------------------------------------------------------------------

    @classmethod
    def _decide_block(cls, game: "CoupGame", bot: "CoupPlayer") -> bool:
        """Decide whether to block the active action."""
        phase = cls._game_phase(game)
        is_1v1 = cls._is_1v1(game)

        if game.active_action == "steal" and game.active_target_id == bot.id:
            if bot.has_influence("captain") or bot.has_influence("ambassador"):
                return True
            stolen = min(2, bot.coins)
            if stolen == 0:
                return False
            bluff_chance = 0.20
            if phase == "late":
                bluff_chance = 0.30
            if is_1v1:
                bluff_chance += 0.15  # More willing to bluff-block in 1v1
            if len(bot.live_influences) == 1:
                bluff_chance *= 0.5
            return random.random() < bluff_chance

        elif game.active_action == "assassinate" and game.active_target_id == bot.id:
            if bot.has_influence("contessa"):
                return True
            bluff_chance = 0.30
            if len(bot.live_influences) == 1:
                # Doing nothing = guaranteed lose our last card = dead.
                # Bluff-blocking at least gives a chance to survive.
                bluff_chance = 0.60
            if is_1v1:
                bluff_chance += 0.10
            if phase == "late":
                bluff_chance += 0.10
            return random.random() < min(bluff_chance, 0.85)

        elif game.active_action == "foreign_aid":
            if bot.has_influence("duke"):
                if is_1v1:
                    return random.random() < 0.90  # Almost always block in 1v1
                alive_count = len(game.get_alive_players())
                if phase == "early" and alive_count >= 4:
                    return random.random() < 0.45  # Cautious with many players
                elif phase == "early":
                    return random.random() < 0.60
                return random.random() < 0.85
            else:
                past_claims = game.player_claims.get(bot.id, set())
                if "duke" in past_claims:
                    return random.random() < 0.50
                if is_1v1:
                    return random.random() < 0.12
                return random.random() < 0.08

        return False

    # ------------------------------------------------------------------
    # D + F. Main action selection — phase-adaptive, strategic
    # ------------------------------------------------------------------

    @classmethod
    def _decide_main_action(cls, game: "CoupGame", bot: "CoupPlayer") -> str:
        """Choose main-phase action with phase awareness and strategic timing."""
        phase = cls._game_phase(game)
        is_1v1 = cls._is_1v1(game)

        # --- Mandatory / forced coup ---
        if bot.coins >= game.options.mandatory_coup_threshold:
            return "coup"
        if bot.coins >= 7:
            if phase == "late":
                return "coup"
            if bot.coins >= 8:
                return "coup"
            # At 7: consider assassination if cheaper and viable
            if bot.has_influence("assassin") and cls._has_viable_assassinate_target(game, bot):
                if random.random() < 0.50:
                    return "assassinate"
            return "coup"

        # --- Build utility scores ---
        utilities: dict[str, float] = {
            "income": 0.0,
            "foreign_aid": 0.0,
            "tax": 0.0,
            "assassinate": 0.0,
            "steal": 0.0,
            "exchange": 0.0,
        }

        # ---- Income ----
        utilities["income"] = 8.0
        if phase == "early":
            utilities["income"] = 10.0
        if bot.coins == 6:
            # Strong silent play — but not so dominant it's predictable
            utilities["income"] = 16.0
            if is_1v1:
                utilities["income"] = 18.0  # Very strong in 1v1

        # ---- Foreign Aid ----
        utilities["foreign_aid"] = 14.0
        duke_block_risk = cls._estimate_block_risk(game, bot, "foreign_aid")
        utilities["foreign_aid"] *= (1.0 - duke_block_risk * 0.7)
        if bot.coins == 5:
            utilities["foreign_aid"] += 5.0

        # ---- Tax (claim Duke) ----
        if bot.has_influence("duke"):
            utilities["tax"] = 35.0
            if phase == "early":
                utilities["tax"] = 40.0
            if bot.coins <= 2:
                utilities["tax"] += 10.0
        else:
            utilities["tax"] = cls._bluff_utility(game, bot, "duke", base=22.0)

        # ---- Assassinate ----
        if bot.coins >= 3:
            if bot.has_influence("assassin"):
                utilities["assassinate"] = 35.0
                if phase == "late":
                    utilities["assassinate"] = 45.0
                if is_1v1:
                    utilities["assassinate"] += 8.0  # Very strong in 1v1
                block_risk = cls._estimate_block_risk(game, bot, "assassinate")
                utilities["assassinate"] *= (1.0 - block_risk * 0.5)
            else:
                utilities["assassinate"] = cls._bluff_utility(
                    game, bot, "assassin", base=18.0
                )
                if phase == "late":
                    utilities["assassinate"] += 5.0
                if is_1v1:
                    utilities["assassinate"] += 3.0
        else:
            utilities["assassinate"] = 0.0

        # ---- Steal (claim Captain) ----
        best_steal_value = cls._best_steal_value(game, bot)
        if best_steal_value > 0:
            if bot.has_influence("captain"):
                utilities["steal"] = 25.0 + best_steal_value * 3.0
                block_risk = cls._estimate_block_risk(game, bot, "steal")
                utilities["steal"] *= (1.0 - block_risk * 0.5)
                if phase == "mid":
                    utilities["steal"] += 5.0
            else:
                utilities["steal"] = cls._bluff_utility(
                    game, bot, "captain", base=16.0
                )
        else:
            utilities["steal"] = 0.0

        # ---- Exchange (claim Ambassador) ----
        hand_q = cls._hand_quality(game, bot)
        if bot.has_influence("ambassador"):
            utilities["exchange"] = 15.0
            if phase == "early":
                utilities["exchange"] = 22.0
            # Much more valuable when hand is weak
            if hand_q < 7.0:
                utilities["exchange"] += (7.0 - hand_q) * 2.0
            if len(bot.live_influences) == 1:
                utilities["exchange"] = 10.0
        else:
            utilities["exchange"] = cls._bluff_utility(
                game, bot, "ambassador", base=8.0
            )
            if phase == "early" and hand_q < 6.0 and len(bot.live_influences) == 2:
                utilities["exchange"] += 5.0

        # ---- Phase adjustments ----
        if phase == "early":
            utilities["income"] += 3.0
            utilities["foreign_aid"] += 2.0
        elif phase == "late":
            utilities["assassinate"] += 5.0
            utilities["steal"] += 3.0
            utilities["income"] = max(utilities["income"] - 3.0, 2.0)

        # ---- Single-card caution ----
        if len(bot.live_influences) == 1:
            for action in ("tax", "assassinate", "steal", "exchange"):
                role = game._get_required_character_for_action(action)
                if role and not bot.has_influence(role):
                    utilities[action] *= 0.35

        # ---- 1v1 adjustments ----
        if is_1v1:
            # In 1v1, aggressive plays are stronger because there's only
            # one person who can challenge/block
            utilities["assassinate"] *= 1.15
            utilities["steal"] *= 1.10
            # Income/foreign_aid are weaker (opponent gains tempo)
            utilities["foreign_aid"] *= 0.85

        # Filter and select
        valid = {k: v for k, v in utilities.items() if v > 0}
        if not valid:
            return "income"

        # Add noise for human-like unpredictability
        for k in valid:
            valid[k] += random.uniform(0, 4.0)

        actions = list(valid.keys())
        weights = [valid[a] for a in actions]
        return random.choices(actions, weights=weights, k=1)[0]

    # ------------------------------------------------------------------
    # H. Smart target selection — avoid blockers, prioritise threats
    # ------------------------------------------------------------------

    @classmethod
    def select_best_target(
        cls, game: "CoupGame", player: "CoupPlayer", options: list[str]
    ) -> str | None:
        if not options:
            return None

        threat_scores: dict[str, float] = {}
        for opt in options:
            target = game.get_player_by_name(opt)
            if not target:
                continue

            score = 0.0

            # --- Coin threat ---
            if target.coins >= 7:
                score += 50.0
            elif target.coins >= 6:
                score += 30.0
            elif target.coins >= 3:
                score += 10.0

            # --- Card advantage ---
            num_live = len(target.live_influences)
            if num_live == 2:
                score += 20.0
            elif num_live == 1:
                score += 5.0

            # --- Action-specific adjustments ---
            if game.active_action == "steal":
                if target.coins >= 2:
                    score += 35.0 + target.coins * 1.0
                elif target.coins == 1:
                    score += 10.0
                else:
                    score -= 100.0

                role_probs = cls._estimate_opponent_roles(game, player, target)
                block_prob = max(
                    role_probs.get("captain", 0),
                    role_probs.get("ambassador", 0),
                )
                score -= block_prob * 25.0

            elif game.active_action in ("assassinate", "coup"):
                if num_live == 1:
                    score += 15.0

                if game.active_action == "assassinate":
                    role_probs = cls._estimate_opponent_roles(game, player, target)
                    contessa_prob = role_probs.get("contessa", 0)
                    score -= contessa_prob * 20.0

            # --- Retaliation: prioritise players who have been aggressive toward us ---
            aggression = cls._aggression_toward(game, target.id, player.id)
            score += aggression * 8.0

            # --- Deprioritise weakened non-threats ---
            if num_live == 1 and target.coins < 3:
                score -= 5.0

            threat_scores[opt] = score + random.uniform(0, 6.0)

        if not threat_scores:
            return random.choice(options)

        return max(threat_scores, key=threat_scores.get)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @classmethod
    def _has_viable_assassinate_target(
        cls, game: "CoupGame", bot: "CoupPlayer"
    ) -> bool:
        """Check if there's a target unlikely to block assassination."""
        for p in game.get_alive_players():
            if p.id == bot.id:
                continue
            role_probs = cls._estimate_opponent_roles(game, bot, p)
            if role_probs.get("contessa", 0) < 0.4:
                return True
        return False

    @classmethod
    def _best_steal_value(cls, game: "CoupGame", bot: "CoupPlayer") -> int:
        """Return max stealable coins from any opponent (0 if nobody worth stealing from)."""
        best = 0
        for p in game.get_alive_players():
            if p.id != bot.id:
                best = max(best, min(2, p.coins))
        return best

    @classmethod
    def _estimate_block_risk(
        cls, game: "CoupGame", bot: "CoupPlayer", action: str
    ) -> float:
        """Estimate probability [0, 1] that someone will block this action."""
        if action == "foreign_aid":
            max_prob = 0.0
            for p in game.get_alive_players():
                if p.id == bot.id:
                    continue
                probs = cls._estimate_opponent_roles(game, bot, p)
                max_prob = max(max_prob, probs.get("duke", 0))
            return min(max_prob, 0.9)

        elif action == "assassinate":
            contessa_probs = []
            for p in game.get_alive_players():
                if p.id == bot.id:
                    continue
                probs = cls._estimate_opponent_roles(game, bot, p)
                contessa_probs.append(probs.get("contessa", 0))
            return max(contessa_probs) if contessa_probs else 0.0

        elif action == "steal":
            cap_probs = []
            for p in game.get_alive_players():
                if p.id == bot.id:
                    continue
                probs = cls._estimate_opponent_roles(game, bot, p)
                cap_probs.append(
                    max(probs.get("captain", 0), probs.get("ambassador", 0))
                )
            return max(cap_probs) if cap_probs else 0.0

        return 0.0

    @classmethod
    def _bluff_utility(
        cls, game: "CoupGame", bot: "CoupPlayer", role: str, base: float
    ) -> float:
        """Calculate utility for bluffing a specific role.

        Returns adjusted utility.  Can return <= 0 if bluffing is too risky.
        """
        dead_count = sum(
            1 for p in game.get_active_players()
            for c in p.dead_influences if c.character.value == role
        )
        bot_count = sum(1 for c in bot.live_influences if c.character.value == role)
        known = dead_count + bot_count
        if known >= 3:
            return 0.0  # Impossible bluff

        # Scarcity penalty
        risk_penalty = 0.0
        if known == 2:
            risk_penalty = base * 0.6
        elif known == 1:
            risk_penalty = base * 0.15

        # Consistency: maintaining an existing bluff is safer
        past_claims = game.player_claims.get(bot.id, set())
        consistency_bonus = 0.0
        if role in past_claims:
            consistency_bonus = base * 0.5

        # Penalty for prior bluff failures
        bluff_penalty = cls._bluff_count(game, bot.id) * 4.0

        # Player-count scaling: fewer opponents = fewer challengers = safer bluff
        alive_others = len(game.get_alive_players()) - 1
        if alive_others <= 1:
            crowd_bonus = base * 0.15
        elif alive_others <= 2:
            crowd_bonus = base * 0.05
        else:
            crowd_bonus = 0.0

        # Strategic gate for new bluffs — base rate depends on context
        if role not in past_claims:
            # Instead of a hard random gate, scale by how "natural" this bluff is.
            # E.g., claiming Duke for tax is very common — lower suspicion.
            natural_rate = {"duke": 0.50, "assassin": 0.40, "captain": 0.40,
                           "ambassador": 0.35, "contessa": 0.30}.get(role, 0.30)
            if cls._is_1v1(game):
                natural_rate += 0.15  # Bluffing is critical in 1v1
            if random.random() > natural_rate:
                return 0.0

        return max(0.0, base - risk_penalty + consistency_bonus - bluff_penalty + crowd_bonus)
