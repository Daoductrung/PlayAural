"""Serializable phase state for Exploding Kittens."""

from dataclasses import dataclass, field

from mashumaro.mixins.json import DataClassJSONMixin


PHASE_NORMAL = "normal"
PHASE_STARTING = "starting"
PHASE_RESOLVING = "resolving"
PHASE_COMBO = "combo"
PHASE_TARGET = "target"
PHASE_REQUEST = "request"
PHASE_NOPE = "nope"
PHASE_FAVOR_GIVE = "favor_give"
PHASE_DEFUSE = "defuse"
PHASE_REINSERT = "reinsert"
PHASE_GAME_OVER = "game_over"

ACTION_ATTACK = "attack"
ACTION_SKIP = "skip"
ACTION_FAVOR = "favor"
ACTION_SHUFFLE = "shuffle"
ACTION_SEE_FUTURE = "see_future"
ACTION_PAIR = "pair"
ACTION_TRIPLE = "triple"


@dataclass
class PendingAction(DataClassJSONMixin):
    """An action being assembled, challenged, or resolved."""

    kind: str = ""
    actor_id: str = ""
    card_ids: list[int] = field(default_factory=list)
    target_id: str = ""
    requested_kind: str = ""
    nope_count: int = 0
    passed_player_ids: list[str] = field(default_factory=list)
    last_nope_player_id: str = ""
    timer_ticks: int = 0
