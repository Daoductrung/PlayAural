"""Native Windows key observation for typing feedback during IME input."""

from __future__ import annotations

from collections.abc import Callable
import ctypes
from dataclasses import dataclass
import logging
import sys

from typing_sounds import TypingSoundCue, resolve_typing_sound_cue


_SCAN_CODE_SHIFT = 16
_SCAN_CODE_MASK = 0xFF
_EXTENDED_KEY_FLAG = 1 << 24
_EXTENDED_SCAN_PREFIX = 0xE000
_PREVIOUS_KEY_STATE_FLAG = 1 << 30
_KEY_MESSAGE_FLAGS_MASK = 0xFFFFFFFF
_KEY_DOWN_MASK = 0x8000
_MAPVK_VSC_TO_VK_EX = 3

_MESSAGE_KEY_DOWN = 0x0100
_MESSAGE_SYSTEM_KEY_DOWN = 0x0104
_MESSAGE_IME_KEY_DOWN = 0x0290
_MESSAGE_NC_DESTROY = 0x0082

_VIRTUAL_KEY_BACK = 0x08
_VIRTUAL_KEY_RETURN = 0x0D
_VIRTUAL_KEY_CONTROL = 0x11
_VIRTUAL_KEY_ALT = 0x12
_VIRTUAL_KEY_SPACE = 0x20
_VIRTUAL_KEY_DELETE = 0x2E
_VIRTUAL_KEY_DIGIT_ZERO = 0x30
_VIRTUAL_KEY_DIGIT_NINE = 0x39
_VIRTUAL_KEY_LETTER_A = 0x41
_VIRTUAL_KEY_LETTER_Z = 0x5A
_VIRTUAL_KEY_LEFT_WINDOWS = 0x5B
_VIRTUAL_KEY_RIGHT_WINDOWS = 0x5C
_VIRTUAL_KEY_NUMPAD_ZERO = 0x60
_VIRTUAL_KEY_NUMPAD_NINE = 0x69
_VIRTUAL_KEY_RIGHT_ALT = 0xA5
_VIRTUAL_KEY_PROCESS = 0xE5
_GENERIC_VIRTUAL_KEYS = frozenset(
    {
        0x6A,  # Numpad multiply
        0x6B,  # Numpad add
        0x6D,  # Numpad subtract
        0x6E,  # Numpad decimal
        0x6F,  # Numpad divide
        0xBA,  # OEM punctuation keys
        0xBB,
        0xBC,
        0xBD,
        0xBE,
        0xBF,
        0xC0,
        0xDB,
        0xDC,
        0xDD,
        0xDE,
        0xDF,
        0xE1,
        0xE2,
    }
)
_KEY_DOWN_MESSAGES = frozenset(
    {_MESSAGE_KEY_DOWN, _MESSAGE_SYSTEM_KEY_DOWN, _MESSAGE_IME_KEY_DOWN}
)

_LOGGER = logging.getLogger("playaural")


def recover_windows_virtual_key(raw_key_flags: int) -> int:
    """Recover the physical key when a Windows IME reports VK_PROCESSKEY."""

    if sys.platform != "win32":
        return 0
    flags = int(raw_key_flags or 0)
    scan_code = (flags >> _SCAN_CODE_SHIFT) & _SCAN_CODE_MASK
    if not scan_code:
        return 0
    if flags & _EXTENDED_KEY_FLAG:
        scan_code |= _EXTENDED_SCAN_PREFIX
    try:
        return int(
            ctypes.windll.user32.MapVirtualKeyW(  # type: ignore[attr-defined]
                scan_code,
                _MAPVK_VSC_TO_VK_EX,
            )
        )
    except (AttributeError, OSError, TypeError, ValueError):
        return 0


def _windows_key_down(virtual_key: int) -> bool:
    if sys.platform != "win32":
        return False
    try:
        state = ctypes.windll.user32.GetKeyState(  # type: ignore[attr-defined]
            virtual_key
        )
    except (AttributeError, OSError, TypeError, ValueError):
        return False
    return bool(int(state) & _KEY_DOWN_MASK)


def windows_alt_graph_active() -> bool:
    """Return whether Windows Right Alt is currently acting as AltGraph."""

    return _windows_key_down(_VIRTUAL_KEY_RIGHT_ALT)


def _typing_key_from_windows_message(virtual_key: int, key_flags: int) -> str:
    resolved_key = int(virtual_key or 0)
    if resolved_key == _VIRTUAL_KEY_PROCESS:
        resolved_key = recover_windows_virtual_key(key_flags)
    if resolved_key == _VIRTUAL_KEY_BACK:
        return "Backspace"
    if resolved_key == _VIRTUAL_KEY_DELETE:
        return "Delete"
    if resolved_key == _VIRTUAL_KEY_RETURN:
        return "Enter"
    if _VIRTUAL_KEY_DIGIT_ZERO <= resolved_key <= _VIRTUAL_KEY_DIGIT_NINE:
        return str(resolved_key - _VIRTUAL_KEY_DIGIT_ZERO)
    if _VIRTUAL_KEY_NUMPAD_ZERO <= resolved_key <= _VIRTUAL_KEY_NUMPAD_NINE:
        return str(resolved_key - _VIRTUAL_KEY_NUMPAD_ZERO)
    if (
        resolved_key == _VIRTUAL_KEY_SPACE
        or _VIRTUAL_KEY_LETTER_A <= resolved_key <= _VIRTUAL_KEY_LETTER_Z
        or resolved_key in _GENERIC_VIRTUAL_KEYS
    ):
        return " "
    return ""


def resolve_windows_typing_sound_cue(
    virtual_key: int,
    key_flags: int,
    *,
    control: bool = False,
    alt: bool = False,
    meta: bool = False,
    alt_graph: bool = False,
) -> TypingSoundCue | None:
    """Resolve a raw Windows key message before wx/IME event translation."""

    key = _typing_key_from_windows_message(virtual_key, key_flags)
    return resolve_typing_sound_cue(
        key,
        modified=meta or ((control or alt) and not alt_graph),
        auto_repeat=bool(int(key_flags) & _PREVIOUS_KEY_STATE_FLAG),
    )


@dataclass(slots=True)
class _SubclassState:
    callback: Callable[[TypingSoundCue], None]
    last_signature: tuple[int, int] | None = None
    last_message: int = 0


_SUBCLASS_STATES: dict[int, _SubclassState] = {}
_SUBCLASS_PROC = None
_SET_SUBCLASS = None
_REMOVE_SUBCLASS = None
_DEFAULT_SUBCLASS_PROC = None
_GET_MESSAGE_TIME = None


if sys.platform == "win32":
    from ctypes import wintypes

    _SubclassProcType = ctypes.WINFUNCTYPE(
        ctypes.c_ssize_t,
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
        ctypes.c_size_t,
        ctypes.c_size_t,
    )
    _comctl32 = ctypes.WinDLL("comctl32", use_last_error=True)
    _user32 = ctypes.WinDLL("user32", use_last_error=True)
    _SET_SUBCLASS = _comctl32.SetWindowSubclass
    _SET_SUBCLASS.argtypes = (
        wintypes.HWND,
        _SubclassProcType,
        ctypes.c_size_t,
        ctypes.c_size_t,
    )
    _SET_SUBCLASS.restype = wintypes.BOOL
    _REMOVE_SUBCLASS = _comctl32.RemoveWindowSubclass
    _REMOVE_SUBCLASS.argtypes = (
        wintypes.HWND,
        _SubclassProcType,
        ctypes.c_size_t,
    )
    _REMOVE_SUBCLASS.restype = wintypes.BOOL
    _DEFAULT_SUBCLASS_PROC = _comctl32.DefSubclassProc
    _DEFAULT_SUBCLASS_PROC.argtypes = (
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
    )
    _DEFAULT_SUBCLASS_PROC.restype = ctypes.c_ssize_t
    _GET_MESSAGE_TIME = _user32.GetMessageTime
    _GET_MESSAGE_TIME.argtypes = ()
    _GET_MESSAGE_TIME.restype = wintypes.LONG

    @_SubclassProcType
    def _typing_subclass_proc(
        window_handle,
        message,
        virtual_key,
        message_flags,
        subclass_id,
        _reference_data,
    ):
        state = _SUBCLASS_STATES.get(int(subclass_id))
        if state and int(message) in _KEY_DOWN_MESSAGES:
            flags = int(message_flags) & _KEY_MESSAGE_FLAGS_MASK
            scan_signature = flags & (
                _SCAN_CODE_MASK << _SCAN_CODE_SHIFT | _EXTENDED_KEY_FLAG
            )
            signature = (scan_signature, int(_GET_MESSAGE_TIME()))
            is_ime_duplicate = (
                state.last_signature == signature
                and state.last_message != int(message)
                and _MESSAGE_IME_KEY_DOWN in (state.last_message, int(message))
            )
            state.last_signature = signature
            state.last_message = int(message)
            if not is_ime_duplicate:
                cue = resolve_windows_typing_sound_cue(
                    int(virtual_key),
                    flags,
                    control=_windows_key_down(_VIRTUAL_KEY_CONTROL),
                    alt=_windows_key_down(_VIRTUAL_KEY_ALT),
                    meta=(
                        _windows_key_down(_VIRTUAL_KEY_LEFT_WINDOWS)
                        or _windows_key_down(_VIRTUAL_KEY_RIGHT_WINDOWS)
                    ),
                    alt_graph=windows_alt_graph_active(),
                )
                if cue:
                    try:
                        state.callback(cue)
                    except Exception:
                        _LOGGER.exception("Windows typing sound callback failed")

        result = _DEFAULT_SUBCLASS_PROC(
            window_handle,
            message,
            virtual_key,
            message_flags,
        )
        if int(message) == _MESSAGE_NC_DESTROY:
            _SUBCLASS_STATES.pop(int(subclass_id), None)
        return result

    _SUBCLASS_PROC = _typing_subclass_proc


class WindowsTextInputObserver:
    """Observe native Windows text-control keys without consuming messages."""

    def __init__(
        self,
        window_handle: int,
        callback: Callable[[TypingSoundCue], None],
    ) -> None:
        self._window_handle = int(window_handle or 0)
        self._subclass_id = id(self)
        self._installed = False
        if (
            sys.platform != "win32"
            or not self._window_handle
            or _SET_SUBCLASS is None
            or _SUBCLASS_PROC is None
        ):
            return
        _SUBCLASS_STATES[self._subclass_id] = _SubclassState(callback=callback)
        self._installed = bool(
            _SET_SUBCLASS(
                self._window_handle,
                _SUBCLASS_PROC,
                self._subclass_id,
                0,
            )
        )
        if not self._installed:
            _SUBCLASS_STATES.pop(self._subclass_id, None)
            _LOGGER.warning(
                "Could not install native typing observer for window handle %s",
                self._window_handle,
            )

    @property
    def installed(self) -> bool:
        return self._installed

    @property
    def window_handle(self) -> int:
        return self._window_handle if self._installed else 0

    def close(self) -> None:
        if (
            self._installed
            and _REMOVE_SUBCLASS is not None
            and _SUBCLASS_PROC is not None
        ):
            _REMOVE_SUBCLASS(
                self._window_handle,
                _SUBCLASS_PROC,
                self._subclass_id,
            )
        self._installed = False
        _SUBCLASS_STATES.pop(self._subclass_id, None)
