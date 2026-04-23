"""Bot AI for Citadels."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from .game import CitadelsGame, CitadelsPlayer, DistrictCard


CHARACTER_ASSASSIN = 1
CHARACTER_THIEF = 2
CHARACTER_MAGICIAN = 3
CHARACTER_KING = 4
CHARACTER_BISHOP = 5
CHARACTER_MERCHANT = 6
CHARACTER_ARCHITECT = 7
CHARACTER_WARLORD = 8
CHARACTER_QUEEN = 9

DISTRICT_NOBLE = "noble"
DISTRICT_RELIGIOUS = "religious"
DISTRICT_TRADE = "trade"
DISTRICT_MILITARY = "military"
DISTRICT_UNIQUE = "unique"

WIN_DISTRICT_COUNT = 7
PHASE_SELECTION = "selection_phase"
PHASE_TURN = "turn_phase"
SUBPHASE_ASSASSIN_TARGET = "assassin_target"
SUBPHASE_THIEF_TARGET = "thief_target"
SUBPHASE_DRAW_KEEP = "draw_keep"
SUBPHASE_MAGICIAN_SWAP = "magician_swap"
SUBPHASE_MAGICIAN_REDRAW = "magician_redraw"
SUBPHASE_LABORATORY = "laboratory_discard"
SUBPHASE_WARLORD_TARGET = "warlord_target"
SUBPHASE_THIEVES_DEN = "thieves_den_payment"

_UNIQUE_BUILD_BONUSES = {
    "dragon_gate": 8.0,
    "factory": 7.0,
    "haunted_quarter": 6.0,
    "imperial_treasury": 7.0,
    "keep": 6.0,
    "laboratory": 6.0,
    "library": 7.0,
    "map_room": 6.0,
    "quarry": 5.0,
    "school_of_magic": 6.0,
    "smithy": 7.0,
    "statue": 6.0,
    "thieves_den": 5.0,
    "wishing_well": 7.0,
}

_ASSASSIN_BASE_WEIGHTS = {
    CHARACTER_ASSASSIN: -100.0,
    CHARACTER_THIEF: 6.5,
    CHARACTER_MAGICIAN: 7.5,
    CHARACTER_KING: 9.0,
    CHARACTER_BISHOP: 6.0,
    CHARACTER_MERCHANT: 8.5,
    CHARACTER_ARCHITECT: 10.5,
    CHARACTER_WARLORD: 9.5,
    CHARACTER_QUEEN: 6.0,
}

_THIEF_BASE_WEIGHTS = {
    CHARACTER_ASSASSIN: -100.0,
    CHARACTER_THIEF: -100.0,
    CHARACTER_MAGICIAN: 6.0,
    CHARACTER_KING: 7.0,
    CHARACTER_BISHOP: 5.5,
    CHARACTER_MERCHANT: 9.0,
    CHARACTER_ARCHITECT: 7.0,
    CHARACTER_WARLORD: 8.0,
    CHARACTER_QUEEN: 6.0,
}


def bot_think(game: "CitadelsGame", player: "CitadelsPlayer") -> str | None:
    if game.phase == PHASE_SELECTION:
        return _choose_character(game, player)

    if game.phase != PHASE_TURN or game.current_player != player:
        return None

    if game.turn_subphase == SUBPHASE_ASSASSIN_TARGET:
        target = _pick_assassin_target(game, player, game._assassin_target_ranks())
        return f"assassinate_target_{target}" if target is not None else None
    if game.turn_subphase == SUBPHASE_THIEF_TARGET:
        target = _pick_thief_target(game, player, game._thief_target_ranks())
        return f"thief_target_{target}" if target is not None else None
    if game.turn_subphase == SUBPHASE_DRAW_KEEP:
        keep = _best_card_to_build(game, player, game.pending_draw_choices)
        return f"keep_draw_{keep.id}" if keep is not None else None
    if game.turn_subphase == SUBPHASE_MAGICIAN_SWAP:
        target = _best_swap_target(game, player)
        return f"magician_swap_target_{target.id}" if target is not None else "cancel_subphase"
    if game.turn_subphase == SUBPHASE_MAGICIAN_REDRAW:
        _prepare_magician_redraw(game, player)
        return "confirm_magician_redraw" if game.selected_card_ids else "cancel_magician_redraw"
    if game.turn_subphase == SUBPHASE_LABORATORY:
        worst = _worst_discard_card(game, player, exclude_card_id=None)
        return f"laboratory_discard_{worst.id}" if worst is not None else "cancel_subphase"
    if game.turn_subphase == SUBPHASE_WARLORD_TARGET:
        target = _best_warlord_target(game, player)
        if target is None:
            return "cancel_subphase"
        owner, district = target
        return f"warlord_destroy_target_{owner.id}_{district.id}"
    if game.turn_subphase == SUBPHASE_THIEVES_DEN:
        pending = game._find_hand_card(player, game.pending_build_card_id)
        if pending is None:
            return "cancel_thieves_den_payment"
        _prepare_thieves_den_payment(game, player, pending)
        return "confirm_thieves_den_payment"

    rank = player.revealed_character_rank
    if not game.turn_resource_taken:
        if rank == CHARACTER_ASSASSIN and game.killed_rank is None:
            game.turn_subphase = SUBPHASE_ASSASSIN_TARGET
            game.rebuild_all_menus()
            return None
        if rank == CHARACTER_THIEF and game.robbed_rank is None:
            game.turn_subphase = SUBPHASE_THIEF_TARGET
            game.rebuild_all_menus()
            return None
        return _choose_resource_action(game, player)

    if game._is_collect_income_enabled(player) is None and game._income_amount(player, rank or 0) > 0:
        return "collect_income"

    if game._is_warlord_destroy_mode_enabled(player) is None and _best_warlord_target(game, player) is not None:
        return "warlord_destroy_mode"

    if game._is_magician_mode_enabled(player) is None:
        swap_target = _best_swap_target(game, player)
        redraw_cards = _cards_to_redraw(game, player)
        if swap_target is not None and len(swap_target.hand) >= len(player.hand) + 2:
            return "magician_swap_mode"
        if redraw_cards:
            return "magician_redraw"

    if game._is_use_laboratory_enabled(player) is None and _should_use_laboratory(game, player):
        return "use_laboratory"

    if game._is_use_smithy_enabled(player) is None and _should_use_smithy(game, player):
        return "use_smithy"

    buildable = [card for card in player.hand if game._can_attempt_build(player, card)]
    best_build = _best_card_to_build(game, player, buildable)
    if best_build is not None:
        return f"build_{best_build.id}"

    return "end_turn"


def _choose_character(game: "CitadelsGame", player: "CitadelsPlayer") -> str | None:
    options = game._selection_options_for_player(player)
    if not options:
        return None

    trade_count = sum(1 for card in player.city if card.district_type == DISTRICT_TRADE)
    noble_count = sum(1 for card in player.city if card.district_type == DISTRICT_NOBLE)
    religious_count = sum(1 for card in player.city if card.district_type == DISTRICT_RELIGIOUS)
    military_count = sum(1 for card in player.city if card.district_type == DISTRICT_MILITARY)
    city_size = len(player.city)
    leader = _leader(game)
    leader_threat = _player_threat_score(game, leader, player) if leader and leader != player else 0.0
    buildable = [card for card in player.hand if game._can_attempt_build(player, card)]
    hand_needs_help = not buildable or _average_build_score(game, player, player.hand) < 8.0

    scores: dict[int, float] = {}
    for rank in options:
        score = 3.0 + random.uniform(0.0, 2.5)
        if rank == CHARACTER_ARCHITECT:
            score += 12.0 + len(buildable) * 2.5
            if city_size >= WIN_DISTRICT_COUNT - 2:
                score += 18.0
        elif rank == CHARACTER_WARLORD:
            score += 9.0 + military_count * 2.5
            if any(len(other.city) >= WIN_DISTRICT_COUNT - 1 for other in _other_players(game, player)):
                score += 15.0
            score += leader_threat * 0.4
        elif rank == CHARACTER_KING:
            score += 8.0 + noble_count * 3.0
            if any(card.effect_key == "statue" for card in player.city):
                score += 7.0
            if game.crown_holder_id != player.id:
                score += 4.0
        elif rank == CHARACTER_BISHOP:
            score += 7.0 + religious_count * 3.0
            if city_size >= WIN_DISTRICT_COUNT - 2:
                score += 10.0
        elif rank == CHARACTER_MERCHANT:
            score += 9.0 + trade_count * 3.0
            if player.gold < 4:
                score += 5.0
        elif rank == CHARACTER_MAGICIAN:
            score += 7.0
            if hand_needs_help:
                score += 10.0
        elif rank == CHARACTER_THIEF:
            score += 7.0 + max((other.gold for other in _other_players(game, player)), default=0) * 1.4
        elif rank == CHARACTER_ASSASSIN:
            score += 6.5 + leader_threat * 0.3
            if any(len(other.city) >= WIN_DISTRICT_COUNT - 1 for other in _other_players(game, player)):
                score += 7.0
        elif rank == CHARACTER_QUEEN:
            score += 5.5
            if leader and leader != player:
                score += 3.0
        scores[rank] = score

    chosen = _weighted_choice(scores)
    return f"select_character_{chosen}" if chosen is not None else None


def _pick_assassin_target(
    game: "CitadelsGame",
    player: "CitadelsPlayer",
    targets: list[int],
) -> int | None:
    if not targets:
        return None

    scores: dict[int, float] = {}
    for rank in targets:
        score = _ASSASSIN_BASE_WEIGHTS.get(rank, 4.0) + random.uniform(0.0, 2.0)
        owner = game._player_with_rank(rank)
        if owner is not None and owner != player:
            score += _player_threat_score(game, owner, player)
            if len(owner.city) >= WIN_DISTRICT_COUNT - 1:
                score += 18.0
            if owner.id == game.crown_holder_id and rank == CHARACTER_KING:
                score += 4.0
        scores[rank] = score
    return _weighted_choice(scores)


def _pick_thief_target(
    game: "CitadelsGame",
    player: "CitadelsPlayer",
    targets: list[int],
) -> int | None:
    if not targets:
        return None

    scores: dict[int, float] = {}
    for rank in targets:
        score = _THIEF_BASE_WEIGHTS.get(rank, 4.0) + random.uniform(0.0, 1.5)
        owner = game._player_with_rank(rank)
        if owner is not None and owner != player:
            score += owner.gold * 4.0
            score += _player_threat_score(game, owner, player) * 0.35
            if owner.gold <= 0:
                score -= 12.0
        scores[rank] = score
    return _weighted_choice(scores)


def _choose_resource_action(game: "CitadelsGame", player: "CitadelsPlayer") -> str:
    buildable_now = [card for card in player.hand if game._can_attempt_build(player, card)]
    gold_after_take = player.gold + 2
    buildable_after_gold = [
        card
        for card in player.hand
        if _can_build_with_gold(game, player, card, gold_after_take)
    ]

    if buildable_now:
        best_now = _best_card_to_build(game, player, buildable_now)
        best_after = _best_card_to_build(game, player, buildable_after_gold)
        if best_after is not None and best_now is not None:
            now_score = _build_card_score(game, player, best_now)
            after_score = _build_card_score(game, player, best_after)
            if after_score >= now_score + 5.0:
                return "take_gold"
        if len(player.hand) <= 2 and _average_build_score(game, player, player.hand) < 10.0:
            return "draw_cards"
        return "take_gold"

    if buildable_after_gold:
        return "take_gold"
    if len(player.hand) < 2:
        return "draw_cards"
    if len(player.hand) >= 5 and player.gold < 2:
        return "take_gold"
    return "draw_cards"


def _best_swap_target(game: "CitadelsGame", player: "CitadelsPlayer") -> "CitadelsPlayer | None":
    options = game._swap_targets()
    if not options:
        return None
    scored: list[tuple[CitadelsPlayer, float]] = []
    for other in options:
        score = (len(other.hand) - len(player.hand)) * 3.0
        score += _player_threat_score(game, other, player) * 0.4
        score += random.uniform(0.0, 1.0)
        scored.append((other, score))
    best = max((score for _, score in scored), default=float("-inf"))
    candidates = [other for other, score in scored if score >= best - 2.0]
    return random.choice(candidates) if candidates else None


def _prepare_magician_redraw(game: "CitadelsGame", player: "CitadelsPlayer") -> None:
    if game.selected_card_ids:
        return
    selections = _cards_to_redraw(game, player)
    game.selected_card_ids[:] = [card.id for card in selections]


def _cards_to_redraw(game: "CitadelsGame", player: "CitadelsPlayer") -> list["DistrictCard"]:
    if len(player.hand) <= 1:
        return []
    scored = sorted(
        player.hand,
        key=lambda card: (_build_card_score(game, player, card), card.cost, card.slug),
    )
    keep = _best_card_to_build(game, player, player.hand)
    redraw: list[DistrictCard] = []
    for card in scored:
        if keep is not None and card.id == keep.id:
            continue
        if len(redraw) >= max(1, len(player.hand) // 2):
            break
        if _build_card_score(game, player, card) < 11.0 or not game._can_attempt_build(player, card):
            redraw.append(card)
    return redraw


def _should_use_laboratory(game: "CitadelsGame", player: "CitadelsPlayer") -> bool:
    if len(player.hand) < 2:
        return False
    if any(game._can_attempt_build(player, card) for card in player.hand):
        return player.gold <= 1 and _average_build_score(game, player, player.hand) < 10.0
    return True


def _should_use_smithy(game: "CitadelsGame", player: "CitadelsPlayer") -> bool:
    if player.gold < 2:
        return False
    if len(player.hand) <= 2:
        return True
    return not any(game._can_attempt_build(player, card) for card in player.hand)


def _best_warlord_target(
    game: "CitadelsGame",
    player: "CitadelsPlayer",
) -> tuple["CitadelsPlayer", "DistrictCard"] | None:
    targets = game._warlord_targets()
    if not targets:
        return None

    scored: list[tuple[tuple[CitadelsPlayer, DistrictCard], float]] = []
    leader = _leader(game)
    for owner, district in targets:
        score = district.cost * 3.0
        score += len(owner.city) * 2.5
        score += _UNIQUE_BUILD_BONUSES.get(district.effect_key, 0.0)
        if owner == leader:
            score += 10.0
        if len(owner.city) >= WIN_DISTRICT_COUNT - 1:
            score += 20.0
        if owner == player:
            score -= 15.0
        score += random.uniform(0.0, 1.0)
        scored.append(((owner, district), score))

    best = max((score for _, score in scored), default=float("-inf"))
    candidates = [entry for entry, score in scored if score >= best - 3.0]
    return random.choice(candidates) if candidates else None


def _prepare_thieves_den_payment(
    game: "CitadelsGame",
    player: "CitadelsPlayer",
    pending: "DistrictCard",
) -> None:
    needed_cards = max(0, game._effective_build_cost(player, pending) - player.gold)
    if needed_cards <= 0:
        game.selected_card_ids.clear()
        return
    candidates = [
        card for card in player.hand
        if card.id != pending.id
    ]
    candidates.sort(key=lambda card: (_build_card_score(game, player, card), card.cost, card.slug))
    game.selected_card_ids[:] = [card.id for card in candidates[:needed_cards]]


def _best_card_to_build(
    game: "CitadelsGame",
    player: "CitadelsPlayer",
    cards: list["DistrictCard"],
) -> "DistrictCard | None":
    if not cards:
        return None
    best_score = float("-inf")
    best_cards: list[DistrictCard] = []
    for card in cards:
        score = _build_card_score(game, player, card)
        if score > best_score + 0.001:
            best_score = score
            best_cards = [card]
        elif abs(score - best_score) <= 2.0:
            best_cards.append(card)
    return random.choice(best_cards) if best_cards else None


def _build_card_score(game: "CitadelsGame", player: "CitadelsPlayer", card: "DistrictCard") -> float:
    effective_cost = game._effective_build_cost(player, card)
    score = card.cost * 2.0
    score += max(0.0, 4.5 - effective_cost) * 0.8

    if len(player.city) + 1 >= WIN_DISTRICT_COUNT:
        score += 100.0

    present_types = {district.district_type for district in player.city}
    if card.district_type not in present_types:
        score += 7.0
    if card.effect_key in {"school_of_magic", "haunted_quarter"}:
        missing_types = {
            DISTRICT_NOBLE,
            DISTRICT_RELIGIOUS,
            DISTRICT_TRADE,
            DISTRICT_MILITARY,
            DISTRICT_UNIQUE,
        } - present_types
        if missing_types:
            score += 6.0

    score += _UNIQUE_BUILD_BONUSES.get(card.effect_key, 0.0)
    if card.effect_key == "factory":
        unique_cards = sum(1 for entry in player.hand if entry.district_type == DISTRICT_UNIQUE)
        score += unique_cards * 1.5
    elif card.effect_key == "quarry":
        duplicate_names = {entry.name for entry in player.hand if entry.name != card.name}
        if any(city_card.name in duplicate_names for city_card in player.city):
            score += 5.0
    elif card.effect_key == "imperial_treasury":
        score += player.gold * 0.8
    elif card.effect_key == "map_room":
        score += len(player.hand) * 0.9
    elif card.effect_key == "wishing_well":
        unique_city = sum(1 for city_card in player.city if city_card.district_type == DISTRICT_UNIQUE)
        unique_hand = sum(1 for hand_card in player.hand if hand_card.district_type == DISTRICT_UNIQUE)
        score += (unique_city + unique_hand) * 0.8
    elif card.effect_key == "statue" and game.crown_holder_id == player.id:
        score += 4.0

    return score


def _average_build_score(game: "CitadelsGame", player: "CitadelsPlayer", cards: list["DistrictCard"]) -> float:
    if not cards:
        return 0.0
    return sum(_build_card_score(game, player, card) for card in cards) / len(cards)


def _worst_discard_card(
    game: "CitadelsGame",
    player: "CitadelsPlayer",
    *,
    exclude_card_id: int | None,
) -> "DistrictCard | None":
    candidates = [card for card in player.hand if card.id != exclude_card_id]
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda card: (_build_card_score(game, player, card), card.cost, card.slug),
    )


def _can_build_with_gold(
    game: "CitadelsGame",
    player: "CitadelsPlayer",
    card: "DistrictCard",
    gold: int,
) -> bool:
    if not game._can_build_duplicate(player, card):
        return False
    cost = game._effective_build_cost(player, card)
    if card.effect_key == "thieves_den":
        return gold + max(0, len(player.hand) - 1) >= cost
    return gold >= cost


def _leader(game: "CitadelsGame") -> "CitadelsPlayer | None":
    players = _active_players(game)
    if not players:
        return None
    return max(players, key=lambda other: (game._score_city(other), len(other.city), other.gold))


def _player_threat_score(
    game: "CitadelsGame",
    target: "CitadelsPlayer | None",
    viewer: "CitadelsPlayer",
) -> float:
    if target is None or target == viewer:
        return 0.0
    score = float(game._score_city(target))
    score += len(target.city) * 4.0
    score += target.gold * 1.5
    score += len(target.hand) * 0.7
    if target.id == game.first_completed_city_player_id:
        score += 6.0
    if target.id == game.crown_holder_id:
        score += 3.0
    return score


def _other_players(game: "CitadelsGame", player: "CitadelsPlayer") -> list["CitadelsPlayer"]:
    return [other for other in _active_players(game) if other != player]


def _active_players(game: "CitadelsGame") -> list["CitadelsPlayer"]:
    return cast(list["CitadelsPlayer"], list(game.get_active_players()))


def _weighted_choice(scores: dict[int, float]) -> int | None:
    if not scores:
        return None
    floor = min(scores.values())
    weights = [max(score - floor + 1.0, 0.1) for score in scores.values()]
    return random.choices(list(scores.keys()), weights=weights, k=1)[0]
