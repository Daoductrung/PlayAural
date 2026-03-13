from __future__ import annotations

import random
from typing import TYPE_CHECKING

from ...game_utils.bot_helper import BotHelper

if TYPE_CHECKING:
    from .game import CoupGame
    from .player import CoupPlayer


class CoupBot(BotHelper):
    """Dedicated Bot class for Coup."""

    @classmethod
    def select_best_target(cls, game: "CoupGame", player: "Player", options: list[str]) -> str | None:
        if not options:
            return None

        # Build threat scores for opponents
        threat_scores = {}
        for opt in options:
            target = game.get_player_by_name(opt)
            if not target:
                continue

            score = 0
            # Coins threat
            if target.coins >= 7:
                score += 50  # Imminent coup threat
            elif target.coins >= 6:
                score += 30  # Close to coup, good target for steal
            elif target.coins >= 3:
                score += 10

            # Card advantage threat
            num_live = len(target.live_influences)
            if num_live == 2:
                score += 20
            elif num_live == 1:
                score += 5  # Sometimes we want to eliminate them, but 2-card players are inherently more dangerous overall

            # If the bot is specifically stealing, prioritize people who actually have 2+ coins
            if game.active_action == "steal":
                if target.coins >= 2:
                    score += 40
                elif target.coins == 1:
                    score += 10
                else:
                    score -= 100 # Worthless to steal from

            # If the bot is assassinating or couping, prioritize killing off a 1-card player if they are a threat,
            # but still heavily weigh 2-card 6+ coin players.
            if game.active_action in ["assassinate", "coup"]:
                if num_live == 1:
                    score += 15 # Finishing blow bonus

            threat_scores[opt] = score + random.randint(0, 10) # Add slight noise for unpredictability

        if not threat_scores:
            return random.choice(options)

        # Return the player name with the highest threat score
        return max(threat_scores, key=threat_scores.get)

    @classmethod
    def bot_lose_influence(cls, game: "CoupGame", player: "CoupPlayer") -> None:
        """Bot picks a random influence to lose."""
        if not player.live_influences:
            return
        idx = random.randint(0, len(player.live_influences) - 1)
        action_id = f"lose_influence_{idx}"
        game.execute_action(player, action_id)

    @classmethod
    def bot_resolve_exchange(cls, game: "CoupGame", player: "CoupPlayer") -> None:
        """Bot resolves the Ambassador exchange."""
        live_count = len([c for c in player.influences if not c.is_revealed])

        # We need to end up with original number of live cards
        # Currently, exchange gave them +2 cards.
        target_live = live_count - 2

        # Shuffle their live cards, keep target_live, return 2
        cards = player.live_influences
        random.shuffle(cards)
        keep = cards[:target_live]
        return_cards = cards[target_live:]

        player.influences = [c for c in player.influences if c.is_revealed] + keep
        for c in return_cards:
            game.deck.add(c)
        game.deck.shuffle()

        game.play_sound("game_coup/exchange_complete.ogg")
        game.broadcast_l("coup-exchange-complete", player=player.name)
        game._end_turn()

    @classmethod
    def on_tick(cls, game: "CoupGame") -> None:
        """Process bot actions for Coup."""
        if not game.game_active or game.is_resolving:
            return

        # In Coup, any player can interrupt, not just the current player.
        # We must process all alive bots during interrupt windows.
        if game.turn_phase in ["action_declared", "waiting_block"]:
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
                # Bots don't need a pending action loop for lose_influence/exchange
                # if we just execute it directly, but let's adhere to the structure or
                # directly process the logic if it's their turn to lose influence.
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
            # Main phase
            current = game.current_player
            if current and current.is_bot:
                cls.process_bot_action(
                    bot=current,
                    think_fn=lambda: cls.bot_think(game, current),
                    execute_fn=lambda action_id: game.execute_action(current, action_id),
                )

    @classmethod
    def bot_think(cls, game: "CoupGame", player: "CoupPlayer") -> str | None:
        if player.is_dead:
            return None

        # Interrupt window logic
        if game.turn_phase in ["action_declared", "waiting_block"]:
            if player.id == game.active_claimer_id:
                return None

            claimer = game.get_player_by_id(game.active_claimer_id)
            if not claimer: return None

            # Challenge evaluation
            challenge_decision = cls._decide_challenge(game, player, claimer)
            if challenge_decision:
                return "challenge"

            # Blocking logic
            if game.turn_phase == "action_declared" and game._is_block_enabled(player) is None:
                block_decision = cls._decide_block(game, player)
                if block_decision:
                    return "block"

            return "pass"

        # Main turn actions
        if game.turn_phase == "main" and game.current_player == player:
            return cls._decide_main_action(game, player)

        return None

    @classmethod
    def _decide_challenge(cls, game: "CoupGame", bot: "CoupPlayer", claimer: "CoupPlayer") -> bool:
        """Smart logic for challenging."""
        required_char = game._get_required_character_for_action(game.active_action)
        if game.turn_phase == "waiting_block":
            required_char = game._get_required_character_for_block(game.active_action)

        if not required_char:
            return False

        req_list = required_char if isinstance(required_char, list) else [required_char]

        # Gather dead cards
        dead_cards = []
        for p in game.get_active_players():
            dead_cards.extend([c.character.value for c in p.dead_influences])

        # Mathematical Certainty: Is the claimed role impossible?
        total_exhausted = 0
        bot_has_any = False
        scarcity_score = 0.0 # higher means less likely the claimer has it

        for rc in req_list:
            dead_count = dead_cards.count(rc)
            bot_count = sum(1 for c in bot.live_influences if c.character.value == rc)
            total_known = dead_count + bot_count

            if total_known == 3:
                total_exhausted += 1
            if bot_count > 0:
                bot_has_any = True

            # Calculate scarcity: 3 total copies.
            # If 2 are known (dead or in bot's hand), only 1 is unknown in the deck/other players' hands.
            if total_known == 2:
                scarcity_score += 0.5
            elif total_known == 1:
                scarcity_score += 0.2

        if total_exhausted == len(req_list):
            return True # 100% certainty they are lying

        # Probabilistic Challenge
        base_chance = 0.05
        if bot_has_any:
            base_chance += 0.10 # Bot holds the card, slightly higher chance they challenge

        # Add scarcity multiplier
        base_chance += (scarcity_score * 0.20)

        # Memory Deduction: Is the player acting highly suspicious?
        # If they have claimed more unique roles than they have cards, they are definitely lying
        # ABOUT SOMETHING. We can't guarantee their *current* action is the lie, but they are highly suspicious.
        if claimer.id in game.player_claims:
            claims = game.player_claims[claimer.id]
            live_count = len(claimer.live_influences)
            if len(claims) > live_count:
                base_chance += 0.25  # Increase challenge chance significantly, but don't guarantee it to avoid bot suicide.

        # Aggression towards threats
        if claimer.coins >= 7:
            base_chance += 0.15 # Need to stop them
        if game.active_target_id == bot.id and game.active_action == "assassinate":
            base_chance += 0.30 # Desperation

        # Cap the challenge chance so it's not guaranteed unless 100% proven
        challenge_chance = min(base_chance, 0.45)

        return random.random() < challenge_chance

    @classmethod
    def _decide_block(cls, game: "CoupGame", bot: "CoupPlayer") -> bool:
        """Smart logic for blocking actions targeting the bot or the table."""
        # Decide if we should block.
        if game.active_action == "steal" and game.active_target_id == bot.id:
            if bot.has_influence("captain") or bot.has_influence("ambassador"):
                return True # Always block if we actually have the card
            # Bluff block steal?
            if random.random() < 0.25:
                return True
        elif game.active_action == "assassinate" and game.active_target_id == bot.id:
            if bot.has_influence("contessa"):
                return True
            # Bluff block assassinate? High desperation
            if random.random() < 0.35:
                return True
        elif game.active_action == "foreign_aid":
            if bot.has_influence("duke"):
                # Usually block, but sometimes let it slide to not reveal role instantly every time
                if random.random() < 0.85:
                    return True
            else:
                # Bluff block foreign aid?
                # Check consistency
                past_claims = game.player_claims.get(bot.id, set())
                if "duke" in past_claims:
                    # Maintain the bluff
                    if random.random() < 0.60:
                        return True
                else:
                    if random.random() < 0.10:
                        return True

        return False

        # Main turn actions
        if game.turn_phase == "main" and game.current_player == player:
            return cls._decide_main_action(game, player)

        return None

    @classmethod
    def _decide_main_action(cls, game: "CoupGame", bot: "CoupPlayer") -> str:
        """Smart logic for choosing a main phase action."""
        if bot.coins >= game.options.mandatory_coup_threshold:
            return "coup"
        if bot.coins >= 7:
            return "coup"

        # Calculate base utilities
        utilities = {
            "income": 5,          # Low reward, but safe
            "foreign_aid": 15,    # Better reward, slightly unsafe
            "tax": 0,
            "assassinate": 0,
            "steal": 0,
            "exchange": 0,
        }

        # Tax Utility
        if bot.coins <= 2:
            utilities["tax"] = 50 # High need for coins
        else:
            utilities["tax"] = 30

        # Assassinate Utility
        if bot.coins >= 3:
            utilities["assassinate"] = 40
            if bot.coins >= 6:
                utilities["assassinate"] += 20 # Better to assassinate and save for coup than just wait

        # Steal Utility
        # Only steal if there's a good target
        has_good_steal_target = False
        for p in game.get_alive_players():
            if p.id != bot.id and p.coins >= 2:
                has_good_steal_target = True
                break
        if has_good_steal_target:
            utilities["steal"] = 35

        # Exchange Utility
        # If bot only has 1 card, exchanging is dangerous (could get caught).
        # But if it has weak cards, it might want to.
        utilities["exchange"] = 15

        # Adjust utilities based on what the bot actually holds (Truth)
        if bot.has_influence("duke"): utilities["tax"] += 40
        if bot.has_influence("assassin"): utilities["assassinate"] += 30
        if bot.has_influence("captain"): utilities["steal"] += 30
        if bot.has_influence("ambassador"): utilities["exchange"] += 20

        # Smart Bluffing adjustments
        past_claims = game.player_claims.get(bot.id, set())
        dead_cards = []
        for p in game.get_active_players():
            dead_cards.extend([c.character.value for c in p.dead_influences])

        def apply_bluff_risk(action: str, role: str, utility_bonus: int):
            if not bot.has_influence(role):
                known_count = dead_cards.count(role)
                if known_count == 3:
                    # Impossible to bluff
                    utilities[action] = 0
                elif known_count == 2:
                    # Very risky
                    utilities[action] = max(0, utilities[action] - 20)
                else:
                    # Possible to bluff. Cap the max bonus so the bot only bluffs ~30-40% of the time at best
                    if role in past_claims:
                        utilities[action] += int(utility_bonus * 0.8) # Maintain consistency!
                    else:
                        # Only occasionally decide to start a new bluff
                        if random.random() < 0.35:
                            utilities[action] += utility_bonus
                        else:
                            utilities[action] = max(0, utilities[action] - 15)

        apply_bluff_risk("tax", "duke", 25)
        apply_bluff_risk("assassinate", "assassin", 20)
        apply_bluff_risk("steal", "captain", 15)
        apply_bluff_risk("exchange", "ambassador", 10)

        # Ensure only available actions are selected
        if bot.coins < 3: utilities["assassinate"] = 0
        if not has_good_steal_target: utilities["steal"] = 0

        # Filter out 0 utility options
        valid_actions = {k: v for k, v in utilities.items() if v > 0}

        actions = list(valid_actions.keys())
        weights = list(valid_actions.values())

        return random.choices(actions, weights=weights, k=1)[0]
