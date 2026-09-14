"""Serializable state for temporary, non-nesting gameplay reactions."""

from dataclasses import dataclass, field


@dataclass
class ReactionWindow:
    """Describe one temporary response that suspends ordinary turn flow.

    Games own the meaning of ``kind`` and ``context``.  The shared shape keeps
    player references, resumption intent, and any limited response budget in a
    Mashumaro-safe form so a window can survive save and restore without
    storing rendered menus or runtime callbacks.
    """

    kind: str = ""
    triggering_player_id: str = ""
    responding_player_id: str = ""
    resume_after_player_id: str = ""
    target_player_id: str = ""
    context: dict[str, str] = field(default_factory=dict)
    response_action_points: int = 0
    consumes_activation: bool = False

    @property
    def is_open(self) -> bool:
        """Return whether the minimum routing information is present."""

        return bool(self.kind and self.responding_player_id)
