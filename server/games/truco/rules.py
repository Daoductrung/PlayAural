"""Pure rules for Argentine Truco: card comparison, envido, flor, and call values."""

from __future__ import annotations

from collections.abc import Sequence

from .cards import TrucoCard

# Truco chain: each level is worth more; refusing pays the previous level.
TRUCO_LEVELS = ("truco", "retruco", "valecuatro")
TRUCO_ACCEPTED_POINTS = {"truco": 2, "retruco": 3, "valecuatro": 4}
TRUCO_DECLINED_POINTS = {"truco": 1, "retruco": 2, "valecuatro": 3}
NO_TRUCO_POINTS = 1

ENVIDO = "envido"
REAL_ENVIDO = "real_envido"
FALTA_ENVIDO = "falta_envido"
ENVIDO_POINTS = {ENVIDO: 2, REAL_ENVIDO: 3}

FLOR_POINTS = 3
CONTRAFLOR_POINTS = 6
CONTRAFLOR = "contraflor"
CONTRAFLOR_AL_RESTO = "contraflor_al_resto"
# A refused contraflor pays the caller 4; a refused contraflor al resto pays 4 when
# it was called directly and 6 when it raised an earlier contraflor.
CONTRAFLOR_DECLINED_POINTS = 4
CONTRAFLOR_AL_RESTO_DECLINED_DIRECT = 4
CONTRAFLOR_AL_RESTO_DECLINED_RAISED = 6
HALF_POINTS = 15


def compare_cards(first: TrucoCard, second: TrucoCard) -> int:
    """Return 1 if first wins, -1 if second wins, 0 for a tie (parda)."""

    if first.power > second.power:
        return 1
    if first.power < second.power:
        return -1
    return 0


def has_flor(hand: Sequence[TrucoCard]) -> bool:
    """A flor is exactly three cards of the same suit."""

    return len(hand) == 3 and len({card.suit for card in hand}) == 1


def flor_score(hand: Sequence[TrucoCard]) -> int:
    """Flor value used to compare flores: 20 plus all three cards (figures count zero)."""

    if not has_flor(hand):
        return 0
    return 20 + sum(card.envido_value for card in hand)


def envido_score(hand: Sequence[TrucoCard]) -> int:
    """Envido points: best two same-suit cards plus 20, else the best single card."""

    best = max((card.envido_value for card in hand), default=0)
    by_suit: dict[str, list[int]] = {}
    for card in hand:
        by_suit.setdefault(card.suit, []).append(card.envido_value)
    for values in by_suit.values():
        if len(values) >= 2:
            top_two = sorted(values, reverse=True)[:2]
            best = max(best, 20 + sum(top_two))
    return best


def flor_cards(hand: Sequence[TrucoCard]) -> list[TrucoCard]:
    """The three cards that make up a flor, strongest value first."""

    if not has_flor(hand):
        return []
    return sorted(hand, key=lambda card: (-card.envido_value, card.id))


def envido_cards(hand: Sequence[TrucoCard]) -> list[TrucoCard]:
    """The cards that make up a hand's envido: the best same-suit pair, else one card."""

    best_single = sorted(hand, key=lambda card: (-card.envido_value, card.id))[:1]
    best_cards = best_single
    best_value = best_single[0].envido_value if best_single else 0
    by_suit: dict[str, list[TrucoCard]] = {}
    for card in hand:
        by_suit.setdefault(card.suit, []).append(card)
    for suited in by_suit.values():
        if len(suited) >= 2:
            pair = sorted(suited, key=lambda card: (-card.envido_value, card.id))[:2]
            value = 20 + sum(card.envido_value for card in pair)
            if value > best_value:
                best_value = value
                best_cards = pair
    return list(best_cards)


def flor_declined_points(chain: Sequence[str]) -> int:
    """Points the caller wins when the last call of a contraflor chain is refused."""

    if not chain or chain[-1] == CONTRAFLOR:
        return CONTRAFLOR_DECLINED_POINTS
    if len(chain) == 1:
        return CONTRAFLOR_AL_RESTO_DECLINED_DIRECT
    return CONTRAFLOR_AL_RESTO_DECLINED_RAISED


def can_raise_truco(current: str | None) -> bool:
    """Whether the truco chain can still be raised from the current level."""

    if current is None:
        return True
    return current != TRUCO_LEVELS[-1]


def next_truco_level(current: str | None) -> str | None:
    """Return the next call in the truco chain, or None at vale cuatro."""

    if current is None:
        return TRUCO_LEVELS[0]
    index = TRUCO_LEVELS.index(current)
    if index + 1 >= len(TRUCO_LEVELS):
        return None
    return TRUCO_LEVELS[index + 1]


def can_add_envido_call(chain: Sequence[str], call: str) -> bool:
    """Whether a call may be added to the envido chain (envido x2, real, falta)."""

    if FALTA_ENVIDO in chain:
        return False
    if call == ENVIDO:
        return chain.count(ENVIDO) < 2 and REAL_ENVIDO not in chain
    if call == REAL_ENVIDO:
        return REAL_ENVIDO not in chain
    return call == FALTA_ENVIDO


def falta_decides_game(scores: Sequence[int], target: int) -> bool:
    """True when a falta envido can decide the whole game.

    In a 30-point game, while both sides are still in the malas (under 15 points),
    the falta envido is worth the complete game. With a 15-point game there are no
    malas or buenas, so the falta is just what the leader still needs.
    """

    return target > HALF_POINTS and max(scores, default=0) < HALF_POINTS


def falta_envido_points(
    scores: Sequence[int], target: int, winner_score: int = 0
) -> int:
    """Points won by the winner of an accepted falta envido.

    Both sides in the malas: the winner receives what is needed to reach the game
    target, deciding the game. Otherwise (in the buenas): what the leading side still
    needs to win, whichever side wins the envido. Published rules word this
    differently (the Juegos Bonaerenses text says "los tantos que al contrario le
    falte"; other guides say what the leader needs); PlayAural uses the leader's gap.
    """

    if falta_decides_game(scores, target):
        return max(1, target - winner_score)
    return max(1, target - max(scores, default=0))


def envido_accepted_points(chain: Sequence[str], falta_points: int) -> int:
    """Points won by the winner of an accepted envido chain."""

    if FALTA_ENVIDO in chain:
        return falta_points
    return sum(ENVIDO_POINTS[call] for call in chain)


def envido_declined_points(chain: Sequence[str]) -> int:
    """Points won by the caller when the last envido call is refused."""

    earlier = chain[:-1]
    total = sum(ENVIDO_POINTS.get(call, 0) for call in earlier)
    return max(1, total)


def truco_points(level: str | None, *, accepted: bool = True) -> int:
    """Value of the hand at a truco level, or what a refusal pays."""

    if level is None:
        return NO_TRUCO_POINTS
    return TRUCO_ACCEPTED_POINTS[level] if accepted else TRUCO_DECLINED_POINTS[level]


def decide_hand(results: Sequence[int | None], mano_team: int) -> int | None:
    """Decide a hand from its trick results, or None while it is still open.

    Each result is the index of the team that won the trick, or None for a parda.
    Rules: two trick wins win the hand; a parda in the first trick lets the next
    decided trick win; a parda after one win lets that first win stand; if every
    trick is a parda, the team of the mano wins.
    """

    tricks = list(results)
    if not tricks:
        return None
    first = tricks[0]
    if len(tricks) >= 2:
        second = tricks[1]
        if first is not None and second is not None and first == second:
            return first
        if first is not None and second is None:
            return first
        if first is None and second is not None:
            return second
    if len(tricks) >= 3:
        third = tricks[2]
        if third is not None:
            return third
        return first if first is not None else mano_team
    return None


# ---------------------------------------------------------------------------
# Variants: Truco Paulista and Truc Valencià
# ---------------------------------------------------------------------------

ANNULLED = -1


def decide_hand_annulling(results: Sequence[int | None]) -> int | None:
    """Paulista hand decision: three tied tricks annul the hand (returns ``ANNULLED``).

    Every other case follows the same trick rules as ``decide_hand``.
    """

    return decide_hand(results, ANNULLED)


# Valencian envit: envit 2, torna 4 (a replacement, not an addition), la falta.
SPANISH_ENVIT_POINTS = {ENVIDO: 2, REAL_ENVIDO: 4}
SPANISH_ENVIT_ORDER = (ENVIDO, REAL_ENVIDO, FALTA_ENVIDO)


def can_add_envit_call(chain: Sequence[str], call: str) -> bool:
    """A Valencian envit chain only moves up: envit, then torna, then la falta."""

    if call not in SPANISH_ENVIT_ORDER:
        return False
    if not chain:
        return call != REAL_ENVIDO  # torna only ever answers an envit
    return SPANISH_ENVIT_ORDER.index(call) > SPANISH_ENVIT_ORDER.index(chain[-1])


def envit_accepted_points(chain: Sequence[str], falta_points: int) -> int:
    if chain and chain[-1] == FALTA_ENVIDO:
        return falta_points
    return SPANISH_ENVIT_POINTS[chain[-1]]


def envit_declined_points(chain: Sequence[str]) -> int:
    """Points paid to the last caller when the chain is refused.

    A refused first call pays 1. A refused raise pays the value already accepted
    by the step below it: 2 after an envit, 4 after a torna.
    """

    if len(chain) < 2:
        return 1
    return SPANISH_ENVIT_POINTS[chain[-2]]


def envit_falta_points(scores: Sequence[int], target: int) -> int:
    """La falta: what the leading side still needs to finish the current came."""

    return max(1, target - max(scores, default=0))
