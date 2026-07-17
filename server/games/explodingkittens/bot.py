"""Public-information-only bot strategy for Exploding Kittens."""

from __future__ import annotations

from collections import Counter
import random
from typing import TYPE_CHECKING

from .cards import (
    ATTACK,
    CAT_KINDS,
    DEFUSE,
    EXPLODING_KITTEN,
    FAVOR,
    NOPE,
    REQUESTABLE_KINDS,
    SEE_FUTURE,
    SHUFFLE,
    SKIP,
)
from .state import (
    ACTION_ATTACK,
    ACTION_FAVOR,
    ACTION_PAIR,
    ACTION_SEE_FUTURE,
    ACTION_SHUFFLE,
    ACTION_TRIPLE,
    PHASE_COMBO,
    PHASE_DEFUSE,
    PHASE_FAVOR_GIVE,
    PHASE_NOPE,
    PHASE_NORMAL,
    PHASE_REINSERT,
    PHASE_REQUEST,
    PHASE_TARGET,
)

if TYPE_CHECKING:
    from .game import ExplodingKittensGame
    from .player import ExplodingKittensPlayer


def _card_action(player: "ExplodingKittensPlayer", kind: str) -> str | None:
    card = next((card for card in player.hand if card.kind == kind), None)
    return f"play_card_{card.id}" if card else None


def _next_alive_after(
    game: "ExplodingKittensGame", actor_id: str
) -> "ExplodingKittensPlayer | None":
    if actor_id not in game.turn_player_ids:
        return None
    index = game.turn_player_ids.index(actor_id)
    for offset in range(1, len(game.turn_player_ids) + 1):
        candidate = game.get_player_by_id(
            game.turn_player_ids[(index + offset) % len(game.turn_player_ids)]
        )
        if candidate in game.alive_players:
            return candidate
    return None


def _should_nope(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> bool:
    pending = game.pending_action
    if pending is None:
        return False
    if pending.nope_count % 2:
        probability = 0.9 if pending.actor_id == player.id else 0.2
    else:
        probability = 0.35
        if pending.target_id == player.id and pending.kind in (
            ACTION_FAVOR,
            ACTION_PAIR,
            ACTION_TRIPLE,
        ):
            probability = 0.9
        elif pending.kind == ACTION_ATTACK:
            next_player = _next_alive_after(game, pending.actor_id)
            probability = 0.85 if next_player and next_player.id == player.id else 0.25
        elif pending.kind == ACTION_SHUFFLE and player.known_future_card_ids:
            probability = 0.75
        elif pending.kind == ACTION_SEE_FUTURE and pending.actor_id != player.id:
            probability = 0.5
    nope_count = sum(card.kind == NOPE for card in player.hand)
    if nope_count == 1:
        probability -= 0.12
    return random.random() < max(0.05, min(0.95, probability))  # nosec B311


def _plan_combo(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> bool:
    counts = Counter(
        card.kind
        for card in player.hand
        if card.kind not in (DEFUSE, EXPLODING_KITTEN)
        and (game.options.advanced_combos or card.kind in CAT_KINDS)
    )
    choices = [kind for kind, count in counts.items() if count >= 2]
    if not choices or not game._valid_targets(player):
        return False
    kind = random.choice(choices)  # nosec B311
    count = (
        3
        if game.options.advanced_combos
        and counts[kind] >= 3
        and random.random() < 0.55  # nosec B311
        else 2
    )
    player.bot_combo_kind = "triple" if count == 3 else "pair"
    player.bot_combo_card_ids = [
        card.id for card in player.hand if card.kind == kind
    ][:count]
    return True


def _normal_turn(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> str:
    known = game._known_future_cards(player)
    known_kitten = bool(known and known[0].kind == EXPLODING_KITTEN)

    if known_kitten:
        escape_kinds = [ATTACK, SKIP, SHUFFLE]
        random.shuffle(escape_kinds)
        for kind in escape_kinds:
            action = _card_action(player, kind)
            if action:
                return action

    candidates: list[str] = []
    if not known:
        action = _card_action(player, SEE_FUTURE)
        if action:
            candidates.extend([action, action])
    for kind in (FAVOR, ATTACK, SHUFFLE, SKIP):
        action = _card_action(player, kind)
        if action:
            candidates.append(action)

    if _plan_combo(game, player):
        candidates.append("start_combo")
    if candidates and random.random() < 0.72:  # nosec B311
        return random.choice(candidates)  # nosec B311
    return "draw_card"


def bot_think(
    game: "ExplodingKittensGame", player: "ExplodingKittensPlayer"
) -> str | None:
    """Choose one legal action without consulting hidden opponent or deck state."""
    if game.phase == PHASE_NOPE:
        if any(card.kind == NOPE for card in player.hand) and _should_nope(game, player):
            return "play_nope"
        return "pass_nope"

    if game.phase == PHASE_DEFUSE and player.id == game.decision_player_id:
        return "use_defuse"
    if game.phase == PHASE_REINSERT and player.id == game.decision_player_id:
        if not game.deck:
            return "insert_0"
        upper = min(len(game.deck), max(2, len(game.alive_players) + 1))
        position = random.randint(1, upper)  # nosec B311
        return f"insert_{position}"

    pending = game.pending_action
    if game.phase == PHASE_TARGET and pending and pending.actor_id == player.id:
        targets = game._valid_targets(player)
        if not targets:
            return "cancel_selection"
        max_count = max(len(target.hand) for target in targets)
        strongest = [target for target in targets if len(target.hand) == max_count]
        target = random.choice(strongest)  # nosec B311
        player.bot_planned_target_id = target.id
        return f"target_{target.id}"

    if game.phase == PHASE_REQUEST and pending and pending.actor_id == player.id:
        owned = Counter(card.kind for card in player.hand)
        kinds = sorted(REQUESTABLE_KINDS, key=lambda kind: (owned[kind], random.random()))  # nosec B311
        kind = kinds[0]
        player.bot_requested_kind = kind
        return f"request_{kind}"

    if game.phase == PHASE_FAVOR_GIVE and pending and pending.target_id == player.id:
        priorities = {
            **{kind: 0 for kind in CAT_KINDS},
            SEE_FUTURE: 1,
            FAVOR: 2,
            SHUFFLE: 3,
            SKIP: 4,
            ATTACK: 5,
            NOPE: 6,
            DEFUSE: 10,
        }
        card = min(player.hand, key=lambda held: (priorities.get(held.kind, 8), held.id))
        return f"play_card_{card.id}"

    if game.phase == PHASE_COMBO and game.current_player == player:
        for card_id in player.bot_combo_card_ids:
            if card_id not in player.selected_card_ids:
                return f"play_card_{card_id}"
        return "confirm_combo"

    if game.phase == PHASE_NORMAL and game.current_player == player:
        return _normal_turn(game, player)
    return None
