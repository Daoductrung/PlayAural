"""Public-information-only completion and role strategy for BANG! bots."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import cards

if TYPE_CHECKING:
    from .cards import BangCard
    from .game import BangGame
    from .player import BangPlayer


def _target_score(
    game: BangGame,
    actor: BangPlayer,
    target: BangPlayer,
) -> tuple[int, int, int, int, str]:
    """Score an enemy from public role evidence; lower tuples are preferred."""

    known_role = target.role if target.role_revealed else ""
    if len(game.seated_players) == 3:
        wanted = {
            "deputy": "renegade",
            "renegade": "outlaw",
            "outlaw": "deputy",
        }.get(actor.role, "")
        role_priority = 0 if target.role == wanted else 2
    elif actor.role == "outlaw":
        role_priority = 0 if known_role == "sheriff" else 1
    elif actor.role in {"sheriff", "deputy"}:
        if known_role in {"outlaw", "renegade"}:
            role_priority = 0
        elif known_role == "sheriff":
            role_priority = 4
        else:
            role_priority = 2 - min(
                1,
                actor.bot_role_suspicion.get(target.id, 0),
            )
    else:
        if len(game.players_in_play) <= 2 and known_role == "sheriff":
            role_priority = 0
        elif known_role == "sheriff":
            role_priority = 4
        else:
            role_priority = 2 - min(
                1,
                actor.bot_role_suspicion.get(target.id, 0),
            )
    weapon = game._equipped_weapon(target)
    public_range = cards.WEAPON_RANGES.get(
        weapon.kind if weapon else "",
        1,
    )
    public_threat = (
        public_range * 4
        + len(target.hand) * 2
        + len(target.in_play)
    )
    distance = game.distance(actor, target)
    return (
        role_priority,
        target.life,
        -public_threat,
        distance,
        target.id,
    )


def _best_target(
    game: BangGame,
    actor: BangPlayer,
    target_ids: list[str],
) -> str | None:
    candidates = [
        target
        for target_id in target_ids
        if (
            target := game.get_player_by_id(target_id)
        ) is not None
        and hasattr(target, "life")
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda target: _target_score(game, actor, target)).id


def _trusted_support_priority(
    actor: BangPlayer,
    target: BangPlayer,
) -> int | None:
    """Return a public-information ally rank, or None for an unsafe heal."""

    if target.id == actor.id:
        return 0
    if actor.role == "deputy" and target.role_revealed and target.role == "sheriff":
        return 0
    if (
        actor.role == "sheriff"
        and target.role_revealed
        and target.role == "deputy"
    ):
        return 1
    if (
        actor.role == "outlaw"
        and target.role_revealed
        and target.role == "outlaw"
    ):
        return 1
    return None


def _best_support_target(
    game: BangGame,
    actor: BangPlayer,
    target_ids: list[str],
) -> str | None:
    candidates = []
    for target_id in target_ids:
        target = game.get_player_by_id(target_id)
        if target is None or not hasattr(target, "life"):
            continue
        priority = _trusted_support_priority(actor, target)
        if priority is None or target.life >= target.max_life:
            continue
        candidates.append((target, priority))
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda pair: (
            pair[0].life / max(1, pair[0].max_life),
            pair[1],
            pair[0].id,
        ),
    )[0].id


def _card_value(
    game: BangGame,
    player: BangPlayer,
    card: BangCard,
) -> int:
    """Estimate a card using only the bot's hand and public table state."""

    values = {
        cards.DODGE: 96,
        cards.MISSED: 90,
        cards.BEER: 88 if player.life < player.max_life else 62,
        cards.WELLS_FARGO: 94,
        cards.PONY_EXPRESS: 92,
        cards.STAGECOACH: 84,
        cards.WHISKY: 82 if player.life < player.max_life else 46,
        cards.BIBLE: 82,
        cards.IRON_PLATE: 76,
        cards.SOMBRERO: 76,
        cards.TEN_GALLON_HAT: 76,
        cards.BARREL: 78,
        cards.MUSTANG: 72,
        cards.HIDEOUT: 72,
        cards.SCOPE: 70,
        cards.BINOCULAR: 70,
        cards.GENERAL_STORE: 68,
        cards.CANTEEN: 68,
        cards.BANG: 64,
        cards.TEQUILA: 62,
        cards.SALOON: 58,
        cards.DYNAMITE: 38,
    }
    if card.kind in cards.WEAPONS:
        value = 48 + cards.WEAPON_RANGES[card.kind] * 7
        if card.kind == cards.VOLCANIC:
            bang_count = sum(held.kind == cards.BANG for held in player.hand)
            value += 20 if bang_count >= 2 else 0
        return value
    if card.kind in cards.GREEN_ATTACK_CARDS:
        return 66
    if card.kind in {
        cards.CAT_BALOU,
        cards.PANIC,
        cards.RAG_TIME,
        cards.CAN_CAN,
        cards.CONESTOGA,
    }:
        return 65
    if card.kind in {cards.DUEL, cards.GATLING, cards.INDIANS, cards.HOWITZER}:
        return 60
    return values.get(card.kind, 55)


def _choose_response_card(
    game: BangGame,
    player: BangPlayer,
    card_ids: list[int],
    decision_kind: str,
) -> str | None:
    held = [card for card in player.hand if card.id in card_ids]
    if not held:
        return None
    if decision_kind == "lethal_recovery":
        priority = {cards.BEER: 0}
    elif decision_kind in {"missed", "ricochet"}:
        priority = {
            cards.DODGE: 0,
            cards.MISSED: 1,
            cards.BANG: 2,
        }
    else:
        priority = {
            cards.BANG: 0,
            cards.MISSED: 1,
        }
    chosen = min(
        held,
        key=lambda card: (
            priority.get(card.kind, 5),
            _card_value(game, player, card),
            card.id,
        ),
    )
    return f"play_card_{chosen.id}"


def _character_value(
    player: BangPlayer,
    character_id: str,
) -> int:
    """Estimate a public character ability in the bot's current position."""

    values = {
        "willy_the_kid": 82,
        "slab_the_killer": 80,
        "lucky_duke": 78,
        "jourdonnais": 76,
        "paul_regret": 75,
        "calamity_janet": 74,
        "rose_doolan": 72,
        "pixie_pete": 72,
        "black_jack": 70,
        "kit_carlson": 70,
        "apache_kid": 69,
        "belle_star": 68,
        "elena_fuente": 68,
        "bart_cassidy": 66,
        "el_gringo": 66,
        "sid_ketchum": 65,
        "tequila_joe": 64,
        "bill_noface": 63,
        "chuck_wengam": 62,
        "doc_holyday": 62,
        "jose_delgado": 61,
        "jesse_jones": 60,
        "pedro_ramirez": 60,
        "pat_brennan": 60,
        "sean_mallory": 58,
        "suzy_lafayette": 58,
        "vulture_sam": 56,
        "greg_digger": 54,
        "herb_hunter": 54,
        "molly_stark": 54,
        "claus_the_saint": 52,
        "johnny_kisch": 52,
        "uncle_will": 50,
    }
    value = values.get(character_id, 50)
    bang_count = sum(card.kind == cards.BANG for card in player.hand)
    if character_id == "willy_the_kid":
        value += bang_count * 7
    elif character_id == "slab_the_killer":
        value += bang_count * 5
    elif character_id in {"sid_ketchum", "tequila_joe"}:
        value += max(0, player.max_life - player.life) * 7
    elif character_id == "bill_noface":
        value += max(0, player.max_life - player.life) * 5
    elif character_id in {"doc_holyday", "jose_delgado", "uncle_will"}:
        value += max(0, len(player.hand) - 2) * 3
    elif character_id == "suzy_lafayette" and len(player.hand) <= 1:
        value += 16
    return value


def _best_character_target(
    game: BangGame,
    player: BangPlayer,
    target_ids: list[str],
) -> str | None:
    candidates = [
        target
        for target_id in target_ids
        if (
            target := game.get_player_by_id(target_id)
        ) is not None
        and hasattr(target, "character")
    ]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda target: (
            _character_value(player, target.character),
            target.id,
        ),
    ).id


def _card_for_item(game: BangGame, item_id: str) -> BangCard | None:
    card_id = game._card_id_from_action(item_id)
    for card in [*game.general_store_cards, *game.revealed_cards]:
        if card.id == card_id:
            return card
    found = game._in_play_by_id(card_id)
    return found[1].card if found else None


def _best_visible_card_item(
    game: BangGame,
    player: BangPlayer,
    item_ids: list[str],
    *,
    keep_best: bool,
) -> str | None:
    choices = [
        (item_id, card)
        for item_id in item_ids
        if (card := _card_for_item(game, item_id))
    ]
    if not choices:
        return item_ids[0] if item_ids else None
    chooser = max if keep_best else min
    return chooser(
        choices,
        key=lambda pair: (
            _card_value(game, player, pair[1]),
            -pair[1].id if keep_best else pair[1].id,
        ),
    )[0]


def _draw_check_choice(
    game: BangGame,
    item_ids: list[str],
    purpose: str,
) -> str | None:
    desired_success = purpose != "dynamite"

    def succeeds(item_id: str) -> bool:
        index = game._card_id_from_action(item_id)
        if not 0 <= index < len(game.revealed_cards):
            return False
        card = game.revealed_cards[index]
        suit = game._effective_suit(card)
        if purpose == "dynamite":
            return (
                suit == cards.SPADES
                and cards.RANK_ORDER["2"]
                <= cards.RANK_ORDER.get(card.rank, -1)
                <= cards.RANK_ORDER["9"]
            )
        return suit == cards.HEARTS

    return next(
        (
            item_id
            for item_id in item_ids
            if succeeds(item_id) == desired_success
        ),
        item_ids[0] if item_ids else None,
    )


def _global_attack_is_sensible(game: BangGame, player: BangPlayer) -> bool:
    """Evaluate a table attack using roles and behavior visible to the bot."""

    utility = 0
    remaining = len(game.players_in_play)
    for target in game.players_in_play:
        if target.id == player.id:
            continue
        known_role = target.role if target.role_revealed else ""
        suspicion = player.bot_role_suspicion.get(target.id, 0)
        if len(game.seated_players) == 3:
            wanted = {
                "deputy": "renegade",
                "renegade": "outlaw",
                "outlaw": "deputy",
            }.get(player.role, "")
            attitude = 6 if target.role == wanted else -3
        elif player.role == "outlaw":
            attitude = 8 if known_role == "sheriff" else 1
            if known_role == "outlaw":
                attitude = -5
        elif player.role in {"sheriff", "deputy"}:
            if known_role == "sheriff":
                attitude = -9
            elif known_role == "deputy":
                attitude = -5
            elif known_role in {"outlaw", "renegade"}:
                attitude = 7
            else:
                attitude = max(-2, min(4, 1 + suspicion))
        else:
            if known_role == "sheriff":
                attitude = 8 if remaining <= 2 else -7
                if target.life <= 1 and remaining > 2:
                    attitude -= 5
            else:
                attitude = max(1, min(5, 2 + suspicion))
        if target.life <= 1:
            attitude += 2 if attitude > 0 else -2
        utility += attitude
    return utility > 0


def _saloon_is_sensible(game: BangGame, player: BangPlayer) -> bool:
    """Estimate the public net value of healing everyone by one."""

    utility = 0
    for target in game.players_in_play:
        if target.life >= target.max_life:
            continue
        if target.id == player.id:
            utility += 6
            continue
        support = _trusted_support_priority(player, target)
        if support is not None:
            utility += 4 - min(2, support)
            continue
        known_role = target.role if target.role_revealed else ""
        if player.role == "outlaw" and known_role == "sheriff":
            utility -= 7
        elif (
            player.role in {"sheriff", "deputy"}
            and known_role in {"outlaw", "renegade"}
        ):
            utility -= 5
        elif player.role == "renegade" and known_role == "sheriff":
            utility += 3 if len(game.players_in_play) > 2 else -6
        else:
            utility -= max(
                0,
                player.bot_role_suspicion.get(target.id, 0),
            )
    return utility > 0


def _ricochet_response_action(
    game: BangGame,
    player: BangPlayer,
) -> str | None:
    """Save a valuable public card, but do not trade down automatically."""

    decision = game.decision
    if not decision or decision.kind != "ricochet":
        return None
    frame = game._top_effect() if game.effect_stack else None
    found = (
        game._in_play_by_id(frame.card_ids[0])
        if frame and frame.card_ids
        else None
    )
    if not found or found[0].id != player.id:
        return None
    response = _choose_response_card(
        game,
        player,
        decision.card_ids,
        decision.kind,
    )
    response_values = [
        _card_value(game, player, card)
        for card in player.hand
        if card.id in decision.card_ids
    ]
    response_values.extend(
        _card_value(game, player, in_play.card)
        for in_play in player.in_play
        if in_play.card.id in decision.data.get("green_card_ids", [])
    )
    attacked_value = _card_value(game, player, found[1].card)
    if (
        "lose_in_play" in decision.item_ids
        and response_values
        and attacked_value + 12 < min(response_values)
    ):
        return "choice_lose_in_play"
    if response:
        return response
    green = decision.data.get("green_card_ids", [])
    return f"use_in_play_{green[0]}" if green else None


def _should_equip_weapon(
    game: BangGame,
    player: BangPlayer,
    card: BangCard,
) -> bool:
    current = game._equipped_weapon(player)
    if current is None:
        return True
    return _card_value(game, player, card) > _card_value(game, player, current)


def _choose_decision_action(
    game: BangGame,
    player: BangPlayer,
) -> str | None:
    decision = game.decision
    if not decision or decision.player_id != player.id:
        return None
    if decision.kind == "ricochet":
        action = _ricochet_response_action(game, player)
        if action:
            return action
    if decision.kind in {
        "missed",
        "duel",
        "indians",
        "lethal_recovery",
    }:
        card_action = _choose_response_card(
            game,
            player,
            decision.card_ids,
            decision.kind,
        )
        if card_action:
            return card_action
        green = decision.data.get("green_card_ids", [])
        if green:
            return f"use_in_play_{green[0]}"
    if decision.kind == "discard_excess":
        if len(decision.selected_card_ids) < decision.required:
            available = [
                card
                for card in player.hand
                if card.id not in decision.selected_card_ids
            ]
            if available:
                chosen = min(
                    available,
                    key=lambda card: (
                        _card_value(game, player, card),
                        card.id,
                    ),
                )
                return f"play_card_{chosen.id}"
        return "confirm_selection"
    if decision.kind == "elimination_discard":
        return "choice_finish_elimination_discard"
    if decision.kind == "ranch":
        return "confirm_selection"
    if decision.kind == "blood_brothers":
        chosen_id = _best_support_target(
            game,
            player,
            decision.player_ids,
        )
        return (
            f"choose_player_{chosen_id}"
            if chosen_id
            else "choice_skip_blood_brothers"
        )
    if decision.kind == "vera_custer":
        chosen_id = _best_character_target(
            game,
            player,
            decision.player_ids,
        )
        return f"choose_player_{chosen_id}" if chosen_id else None
    if decision.player_ids:
        chosen_id = _best_target(game, player, decision.player_ids)
        if chosen_id:
            return f"choose_player_{chosen_id}"
    if decision.item_ids:
        preferred: list[str] = []
        if decision.kind == "barrel":
            preferred = ["use_barrel", "skip_barrels"]
        elif decision.kind == "lethal_recovery":
            preferred = ["use_sid", "accept_death"]
        elif decision.kind == "hard_liquor":
            preferred = (
                ["skip_draw_heal", "draw_normally"]
                if player.life <= 1 and player.life < player.max_life
                else ["draw_normally", "skip_draw_heal"]
            )
        elif decision.kind == "new_identity":
            current = _character_value(player, player.character)
            alternate = _character_value(player, player.alternate_character)
            life_change = 2 - player.life
            preferred = (
                ["change_identity", "keep_identity"]
                if alternate - current + life_change * 8 > 4
                else ["keep_identity", "change_identity"]
            )
        elif decision.kind == "peyote":
            preferred = ["guess_red", "guess_black"]
        elif decision.kind == "handcuffs":
            suit_counts = {
                suit: sum(
                    game._effective_suit(card) == suit for card in player.hand
                )
                for suit in cards.SUITS
            }
            preferred = [f"suit_{max(suit_counts, key=suit_counts.get)}"]
        elif decision.kind == "draw_check":
            selected = _draw_check_choice(
                game,
                decision.item_ids,
                str(decision.data.get("purpose", "")),
            )
            preferred = [selected] if selected else []
        elif decision.kind in {"general_store", "kit_keep"}:
            selected = _best_visible_card_item(
                game,
                player,
                decision.item_ids,
                keep_best=True,
            )
            preferred = [selected] if selected else []
        elif decision.kind in {"kit_return", "claus_give"}:
            selected = _best_visible_card_item(
                game,
                player,
                decision.item_ids,
                keep_best=False,
            )
            preferred = [selected] if selected else []
        elif decision.kind in {"target_card", "vulture"}:
            selected = _best_visible_card_item(
                game,
                player,
                [
                    item
                    for item in decision.item_ids
                    if item.startswith("in_play_")
                ],
                keep_best=True,
            )
            if selected:
                preferred = [selected]
            elif "random_hand" in decision.item_ids:
                preferred = ["random_hand"]
        elif decision.kind == "daltons":
            selected = _best_visible_card_item(
                game,
                player,
                [
                    item
                    for item in decision.item_ids
                    if item.startswith("in_play_")
                ],
                keep_best=False,
            )
            preferred = [selected] if selected else []
        elif decision.kind == "pat_brennan":
            selected = _best_visible_card_item(
                game,
                player,
                [
                    item
                    for item in decision.item_ids
                    if item.startswith("in_play_")
                ],
                keep_best=True,
            )
            preferred = [selected] if selected else ["draw_normally"]
        preferred.extend(decision.item_ids)
        for item in preferred:
            if item in decision.item_ids:
                return f"choice_{item}"
    return "confirm_selection"


def _choose_intent_action(
    game: BangGame,
    player: BangPlayer,
) -> str | None:
    intent = game.play_intent
    if not intent or intent.actor_id != player.id:
        return None
    if intent.stage == "cost":
        allowed = set(
            intent.data.get(
                "allowed_card_ids",
                [card.id for card in player.hand],
            )
        )
        candidates = [
            card
            for card in player.hand
            if card.id != intent.card_id
            and card.id in allowed
            and card.id not in intent.selected_card_ids
        ]
        if len(intent.selected_card_ids) < intent.required and candidates:
            chosen = min(
                candidates,
                key=lambda card: (
                    _card_value(game, player, card),
                    card.id,
                ),
            )
            return f"play_card_{chosen.id}"
        return "confirm_selection" if intent.required >= 2 else "cancel_selection"
    if intent.stage == "target":
        targets = game._targets_for_intent(intent)
        if intent.kind == "card":
            card = game._card_in_hand(player, intent.card_id)
            chosen_id = (
                _best_support_target(
                    game,
                    player,
                    [target.id for target in targets],
                )
                if card and card.kind == cards.TEQUILA
                else _best_target(
                    game,
                    player,
                    [target.id for target in targets],
                )
            )
            if (
                chosen_id is None
                and card
                and card.id == player.law_card_id
            ):
                chosen_id = _best_target(
                    game,
                    player,
                    [target.id for target in targets],
                )
        else:
            chosen_id = _best_target(
                game,
                player,
                [target.id for target in targets],
            )
        return f"choose_player_{chosen_id}" if chosen_id else "cancel_selection"
    if intent.stage == "in_play_target":
        choices = game._in_play_choice_ids("ricochet")
        selected = _best_visible_card_item(
            game,
            player,
            choices,
            keep_best=True,
        )
        return f"choice_{selected}" if selected else "cancel_selection"
    return None


def choose_action(
    game: BangGame,
    player: BangPlayer,
) -> str | None:
    """Return one legal action while never inspecting hidden opponent state."""

    if game.decision and game.decision.player_id == player.id:
        return _choose_decision_action(game, player)
    if game.play_intent and game.play_intent.actor_id == player.id:
        return _choose_intent_action(game, player)
    if game.phase != "play" or game.current_player is not player:
        return None

    forced = game._forced_law_card(player)
    if forced and game._can_normally_play(player, forced):
        return f"play_card_{forced.id}"

    def playable(kind_set: set[str] | frozenset[str]) -> list[BangCard]:
        return [
            card
            for card in player.hand
            if card.kind in kind_set
            and game._normal_card_error(player, card) is None
        ]

    draws = playable(
        {
            cards.STAGECOACH,
            cards.WELLS_FARGO,
            cards.GENERAL_STORE,
        }
    )
    if draws:
        chosen = max(
            draws,
            key=lambda card: (_card_value(game, player, card), -card.id),
        )
        return f"play_card_{chosen.id}"

    if player.life < player.max_life:
        heals = playable({cards.BEER, cards.WHISKY})
        if heals:
            chosen = max(
                heals,
                key=lambda card: (_card_value(game, player, card), -card.id),
            )
            return f"play_card_{chosen.id}"

    support_target = _best_support_target(
        game,
        player,
        [target.id for target in game.players_in_play],
    )
    tequila = playable({cards.TEQUILA})
    if tequila and support_target:
        return f"play_card_{tequila[0].id}"

    saloon = playable({cards.SALOON})
    if saloon and _saloon_is_sensible(game, player):
        return f"play_card_{saloon[0].id}"

    deployable = [
        card
        for card in player.hand
        if card.border in {cards.BLUE, cards.GREEN}
        and card.kind not in cards.WEAPONS
        and game._normal_card_error(player, card) is None
    ]
    if deployable:
        chosen = max(
            deployable,
            key=lambda card: (_card_value(game, player, card), -card.id),
        )
        return f"play_card_{chosen.id}"

    weapons = [
        card
        for card in player.hand
        if card.kind in cards.WEAPONS
        and game._normal_card_error(player, card) is None
        and _should_equip_weapon(game, player, card)
    ]
    if weapons:
        chosen = max(
            weapons,
            key=lambda card: (_card_value(game, player, card), -card.id),
        )
        return f"play_card_{chosen.id}"

    ready_green = [
        in_play.card
        for in_play in player.in_play
        if game._is_use_in_play_enabled(
            player,
            action_id=f"use_in_play_{in_play.card.id}",
        )
        is None
        and (
            in_play.card.kind != cards.CANTEEN
            or player.life < player.max_life
        )
        and (
            in_play.card.kind != cards.HOWITZER
            or _global_attack_is_sensible(game, player)
        )
    ]
    if ready_green:
        chosen = max(
            ready_green,
            key=lambda card: (_card_value(game, player, card), -card.id),
        )
        return f"use_in_play_{chosen.id}"

    if (
        game._is_jose_hidden(player).value == "visible"
        and game._is_jose_enabled(player) is None
    ):
        return "jose_delgado"
    if (
        game._is_uncle_hidden(player).value == "visible"
        and game._is_uncle_enabled(player) is None
        and len(player.hand) >= 3
    ):
        return "uncle_will"

    offensive = {
        cards.BANG,
        cards.DUEL,
        cards.PUNCH,
        cards.SPRINGFIELD,
        cards.BUFFALO_RIFLE,
        cards.DERRINGER,
        cards.KNIFE,
        cards.PEPPERBOX,
        cards.CAT_BALOU,
        cards.PANIC,
        cards.RAG_TIME,
        cards.CAN_CAN,
        cards.CONESTOGA,
        cards.JAIL,
    }
    attacks = playable(offensive)
    if attacks:
        chosen = max(
            attacks,
            key=lambda card: (_card_value(game, player, card), -card.id),
        )
        return f"play_card_{chosen.id}"

    globals_ = playable({cards.GATLING, cards.INDIANS, cards.HOWITZER})
    if globals_ and _global_attack_is_sensible(game, player):
        return f"play_card_{globals_[0].id}"

    if (
        game._is_sniper_hidden(player).value == "visible"
        and game._is_sniper_enabled(player) is None
    ):
        return "sniper"
    if (
        game._is_ricochet_hidden(player).value == "visible"
        and game._is_ricochet_enabled(player) is None
    ):
        return "ricochet"
    if (
        game._is_doc_hidden(player).value == "visible"
        and game._is_doc_enabled(player) is None
        and len(player.hand) >= 4
    ):
        return "doc_holyday"
    if (
        player.life < player.max_life
        and game._is_sid_hidden(player).value == "visible"
        and game._is_sid_enabled(player) is None
        and (player.life <= 1 or len(player.hand) > max(2, player.life + 1))
    ):
        return "sid_ketchum"
    if (
        game._is_chuck_hidden(player).value == "visible"
        and game._is_chuck_enabled(player) is None
        and player.life > 2
        and len(player.hand) < 2
    ):
        return "chuck_wengam"

    other = [
        card
        for card in player.hand
        if card.border == cards.BROWN
        and card.kind not in {
            cards.MISSED,
            cards.DODGE,
            cards.BEER,
            cards.WHISKY,
            cards.TEQUILA,
            cards.SALOON,
        }
        and game._normal_card_error(player, card) is None
    ]
    if other:
        chosen = max(
            other,
            key=lambda card: (_card_value(game, player, card), -card.id),
        )
        return f"play_card_{chosen.id}"
    return "end_turn"
