"""Bot user implementation for AI players."""

from typing import TYPE_CHECKING

from .base import User, MenuItem, EscapeBehavior, generate_uuid

if TYPE_CHECKING:
    pass


class Bot(User):
    """
    Bot implementation of User for AI players.

    Bots don't receive UI updates (they're discarded), but they can
    call game actions directly through the game's action system.
    """

    def __init__(self, name: str, locale: str = "en", uuid: str | None = None):
        self._uuid = uuid or generate_uuid()
        self._username = name
        self._locale = locale

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def username(self) -> str:
        return self._username

    @property
    def locale(self) -> str:
        return self._locale

    @property
    def is_bot(self) -> bool:
        return True

    # All UI methods are no-ops for bots

    def speak(self, text: str, buffer: str = "misc") -> None:
        pass

    def play_sound(
        self, name: str, volume: int = 100, pan: int = 0, pitch: int = 100
    ) -> None:
        pass

    def play_music(self, name: str, looping: bool = True) -> None:
        pass

    def stop_music(self) -> None:
        pass

    def play_ambience(self, loop: str, intro: str = "", outro: str = "") -> None:
        pass

    def stop_ambience(self) -> None:
        pass

    def show_menu(
        self,
        menu_id: str,
        items: list[str | MenuItem],
        *,
        multiletter: bool = True,
        escape_behavior: EscapeBehavior = EscapeBehavior.KEYBIND,
        position: int | None = None,
        grid_enabled: bool = False,
        grid_width: int = 1,
    ) -> None:
        pass

    def update_menu(
        self,
        menu_id: str,
        items: list[str | MenuItem],
        position: int | None = None,
        selection_id: str | None = None,
    ) -> None:
        pass

    def remove_menu(self, menu_id: str) -> None:
        pass

    def show_editbox(
        self,
        input_id: str,
        prompt: str,
        default_value: str = "",
        *,
        multiline: bool = False,
        read_only: bool = False,
    ) -> None:
        pass

    def remove_editbox(self, input_id: str) -> None:
        pass

    def clear_ui(self) -> None:
        pass
