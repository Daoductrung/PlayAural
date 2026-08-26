"""Cross-platform typing-feedback cue definitions and resolution."""

from __future__ import annotations

from dataclasses import dataclass


TYPING_SOUND_FAMILY = "typing"
TYPING_SOUND_HANDLE = "client:typing-feedback"
TYPING_SOUND_VOLUME = 0.5

_DIGIT_NAMES = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
)
DIGIT_SOUND_ASSETS = tuple(
    f"typing_digit_{name}.ogg" for name in _DIGIT_NAMES
)
TYPING_DELETE_ASSET = "typing_delete.ogg"
TYPING_RETURN_ASSET = "typing_return.ogg"
TYPING_EXACT_ASSETS = (
    *DIGIT_SOUND_ASSETS,
    TYPING_DELETE_ASSET,
    TYPING_RETURN_ASSET,
)

_DELETE_KEYS = frozenset({"Backspace", "Delete"})
_RETURN_KEYS = frozenset({"Enter", "NumpadEnter"})


@dataclass(frozen=True, slots=True)
class TypingSoundCue:
    """A single exact asset or dynamically discovered numbered family."""

    asset: str = ""
    family: str = ""

    def __post_init__(self) -> None:
        if bool(self.asset) == bool(self.family):
            raise ValueError("A typing sound cue must specify exactly one source")


GENERIC_TYPING_CUE = TypingSoundCue(family=TYPING_SOUND_FAMILY)


def resolve_typing_sound_cue(
    key: str,
    *,
    modified: bool = False,
    auto_repeat: bool = False,
) -> TypingSoundCue | None:
    """Resolve one physical text-control key press to its feedback cue.

    Key-repeat events are intentionally silent. Delete and Return remain useful
    with modifiers because common text editing commands use Ctrl/Command with
    those keys. Other modified keys are treated as shortcuts.
    """

    if auto_repeat:
        return None
    if key in _DELETE_KEYS:
        return TypingSoundCue(asset=TYPING_DELETE_ASSET)
    if key in _RETURN_KEYS:
        return TypingSoundCue(asset=TYPING_RETURN_ASSET)
    if modified:
        return None
    if len(key) == 1 and key.isdecimal() and key.isascii():
        return TypingSoundCue(asset=DIGIT_SOUND_ASSETS[int(key)])
    if len(key) == 1 and key.isprintable():
        return GENERIC_TYPING_CUE
    return None
