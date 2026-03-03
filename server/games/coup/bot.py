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
    def bot_lose_influence(cls, game: "CoupGame", player: "CoupPlayer") -> None:
        """Bot picks a random influence to lose."""
        game.play_sound(f"game_coup/chardestroy{random.randint(1, 2)}.ogg")
        idx = random.randint(0, len(player.live_influences) - 1)
        char = player.live_influences[idx].character
        player.reveal_influence(idx)
        game._broadcast_card_message("coup-loses-influence", char, player=player.name)
        if player.is_dead:
            game.broadcast_l("coup-player-eliminated", player=player.name)
        game._post_lose_influence()

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
        if not game.game_active:
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
            target = game.get_player_by_id(game.active_target_id)
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

            # Don't do anything 70% of the time right away to simulate thinking
            if random.random() < 0.7:
                return None

            required_char = game._get_required_character_for_action(game.active_action)
            if game.turn_phase == "waiting_block":
                required_char = game._get_required_character_for_block(game.active_action)

            # Track known dead cards
            dead_cards = []
            for p in game.players:
                dead_cards.extend([c.character.value for c in p.dead_influences])

            # Determine logic if required_char is a list
            if isinstance(required_char, list):
                total_exhausted = 0
                hold_any = False
                for rc in required_char:
                    dead_count = dead_cards.count(rc)
                    my_count = sum(1 for c in player.live_influences if c.character.value == rc)
                    if dead_count + my_count == 3:
                        total_exhausted += 1
                    if player.has_influence(rc):
                        hold_any = True
                if total_exhausted == len(required_char):
                    return "challenge"

                if hold_any and random.random() < 0.15:
                    return "challenge"
                elif random.random() < 0.05:
                    return "challenge"
            else:
                dead_count = dead_cards.count(required_char)
                my_count = sum(1 for c in player.live_influences if c.character.value == required_char)

                if dead_count + my_count == 3:
                    return "challenge" # They MUST be bluffing

                if required_char and player.has_influence(required_char) and random.random() < 0.15:
                    return "challenge"
                elif random.random() < 0.05:
                    return "challenge"

            # Blocking logic
            if game.turn_phase == "action_declared" and game._is_block_enabled(player) is None:
                if game.active_action == "steal" and game.active_target_id == player.id:
                    if random.random() < 0.4: return "block"
                elif game.active_action == "assassinate" and game.active_target_id == player.id:
                    if random.random() < 0.6: return "block"
                elif game.active_action == "foreign_aid":
                    if random.random() < 0.1: return "block"

            return "pass"

        # Main turn actions
        if game.turn_phase == "main" and game.current_player == player:
            if player.coins >= game.options.mandatory_coup_threshold:
                return "coup"

            actions = ["income", "foreign_aid", "tax", "exchange"]
            weights = []
            if player.coins >= 7:
                actions = ["coup"]
                weights = [100]
            else:
                if player.coins >= 3: actions.append("assassinate")

                can_steal = any(p.coins > 0 for p in game.get_alive_players() if p.id != player.id)
                if can_steal:
                    actions.append("steal")

                for action in actions:
                    weight = 10
                    if action == "tax" and player.has_influence("duke"): weight = 50
                    elif action == "assassinate" and player.has_influence("assassin"): weight = 40
                    elif action == "steal" and player.has_influence("captain"): weight = 30
                    elif action == "exchange" and player.has_influence("ambassador"): weight = 20
                    elif action == "coup": weight = 100
                    weights.append(weight)

            action = random.choices(actions, weights=weights, k=1)[0]
            return action

        return None
