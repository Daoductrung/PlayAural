"""Heuristic bot for Argentine Truco (uses only the bot's own cards and public state)."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from . import rules

if TYPE_CHECKING:
    from .game import TrucoGame, TrucoPlayer


def _best_power(game: TrucoGame, player: TrucoPlayer) -> int:
    return max((game._bot_strength(card) for card in player.hand), default=0)


def choose_action(game: TrucoGame, player: TrucoPlayer) -> str | None:
    kind = game._pending_kind()
    if kind:
        if not game._can_answer(player):
            return None
        return _answer(game, player, kind)
    if game.current_player is not player or not game._live(player):
        return None
    call = _maybe_call(game, player)
    if call:
        return call
    return _choose_card(game, player)


# ---------------------------------------------------------------------------
# Answers
# ---------------------------------------------------------------------------


def _can(game: TrucoGame, player: TrucoPlayer, action_id: str) -> bool:
    return game._call_error(player, action_id) is None


def _answer(game: TrucoGame, player: TrucoPlayer, kind: str) -> str:
    if kind == "envido":
        return _answer_envido(game, player)
    if kind == "flor":
        return _answer_flor(game, player)
    if kind == "onze":
        return _answer_onze(game, player)
    return _answer_truco(game, player)


def _answer_onze(game: TrucoGame, player: TrucoPlayer) -> str:
    """Mão de onze: play when the hand holds real strength, otherwise usually run."""

    cards = list(player.hand)
    # The side holding 11 may look at each other's cards, so the bot weighs them too.
    for mate in game._team_players(game.onze_team, live_only=True):
        if mate.id != player.id:
            cards.extend(mate.hand)
    strengths = sorted((game._bot_strength(card) for card in cards), reverse=True)
    score = sum(strengths[:2])
    if score >= 20 or random.random() < 0.15:
        return "accept"
    return "decline"


def _answer_envido(game: TrucoGame, player: TrucoPlayer) -> str:
    score = rules.envido_score(player.dealt)
    last = game.envido_chain[-1]
    if (
        score >= 30
        and last != rules.FALTA_ENVIDO
        and random.random() < 0.3
        and _can(game, player, "call_falta_envido")
    ):
        return "call_falta_envido"
    if score >= 28 and _can(game, player, "call_real_envido") and random.random() < 0.4:
        return "call_real_envido"
    threshold = 25 if last == rules.FALTA_ENVIDO or len(game.envido_chain) > 1 else 23
    if score >= threshold or random.random() < 0.08:
        return "accept"
    return "decline"


def _answer_flor(game: TrucoGame, player: TrucoPlayer) -> str:
    score = rules.flor_score(player.dealt)
    pending = game.flor_pending
    if (
        pending == rules.CONTRAFLOR
        and score >= 36
        and _can(game, player, "call_contraflor_al_resto")
        and random.random() < 0.3
    ):
        return "call_contraflor_al_resto"
    needed = 36 if pending == rules.CONTRAFLOR_AL_RESTO else 33
    return "accept" if score >= needed else "decline"


def _answer_truco(game: TrucoGame, player: TrucoPlayer) -> str:
    best = _best_power(game, player)
    strong = sum(1 for card in player.hand if game._bot_strength(card) >= 10)
    if best >= 13 and _can(game, player, "call_truco") and random.random() < 0.4:
        return "call_truco"
    if best >= 10 or strong >= 1 or random.random() < 0.12:
        return "accept"
    # A weak hand still defends the points when the cost of refusing is high.
    if game.truco_pending and game.truco_pending != "truco" and best >= 8:
        return "accept"
    return "decline"


# ---------------------------------------------------------------------------
# Calls
# ---------------------------------------------------------------------------


def _maybe_call(game: TrucoGame, player: TrucoPlayer) -> str | None:
    if game.flor_window:
        return _maybe_contraflor(game, player)
    if _can(game, player, "call_envido"):
        score = rules.envido_score(player.dealt)
        roll = random.random()
        if score >= 31 and roll < 0.3 and _can(game, player, "call_falta_envido"):
            return "call_falta_envido"
        if score >= 28 and roll < 0.55:
            return "call_real_envido"
        if score >= 26 and roll < 0.6:
            return "call_envido"
        if score >= 24 and roll < 0.3:
            return "call_envido"
        if roll < 0.03:
            return "call_envido"
    if _can(game, player, "call_truco"):
        best = _best_power(game, player)
        roll = random.random()
        played = len(game.trick_results)
        if played == 0 and best >= 13 and roll < 0.3:
            return "call_truco"
        if played == 0 and best >= 11 and roll < 0.12:
            return "call_truco"
        if played >= 1 and best >= 10 and roll < 0.35:
            return "call_truco"
        if roll < 0.02:
            return "call_truco"
    return None


def _maybe_contraflor(game: TrucoGame, player: TrucoPlayer) -> str | None:
    if not player.has_flor or not _can(game, player, "call_contraflor"):
        return None
    score = rules.flor_score(player.dealt)
    if score >= 36 and random.random() < 0.2:
        return "call_contraflor_al_resto"
    if score >= 34 and random.random() < 0.35:
        return "call_contraflor"
    return None


# ---------------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------------


def _choose_card(game: TrucoGame, player: TrucoPlayer) -> str | None:
    hand = sorted(player.hand, key=game._power)
    if not hand:
        return None
    if game.blind_hand:
        # Face-down hand: the bot cannot see its cards either, so it picks at random.
        return f"play_{random.choice(player.hand).id}"
    my_team = game._team_index(player)
    plays = game.plays[-1] if game.plays else []
    if plays:
        top = max(plays, key=lambda play: game._power(play.card))
        owner = game.get_player_by_id(top.player_id)
        if owner is not None and game._team_index(owner) == my_team:
            choice = hand[0]
        else:
            beating = [
                card for card in hand if game._power(card) > game._power(top.card)
            ]
            choice = beating[0] if beating else hand[0]
    elif not game.trick_results:
        choice = hand[len(hand) // 2]
    else:
        choice = hand[-1]
    return f"play_{choice.id}"
