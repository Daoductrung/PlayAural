"""Locale-aware text direction helpers for native desktop controls."""

import wx


_TEXT_CONTROLS = (
    wx.Button,
    wx.CheckBox,
    wx.Choice,
    wx.ComboBox,
    wx.ListBox,
    wx.SpinCtrl,
    wx.StaticText,
    wx.TextCtrl,
)


def locale_layout_direction(locale: str | None) -> int:
    """Resolve a locale through wxWidgets without hardcoded language lists."""
    normalized = str(locale or "").strip().replace("-", "_")
    candidates = (normalized, normalized.split("_", 1)[0])
    for candidate in candidates:
        if not candidate:
            continue
        info = wx.Locale.FindLanguageInfo(candidate)
        if info is not None:
            return info.LayoutDirection
    return wx.Layout_LeftToRight


def apply_text_layout_direction(root: wx.Window, locale: str | None) -> int:
    """Apply locale direction to text controls without mirroring containers."""
    direction = locale_layout_direction(locale)
    pending = list(root.GetChildren())
    while pending:
        control = pending.pop()
        pending.extend(control.GetChildren())
        if isinstance(control, _TEXT_CONTROLS):
            control.SetLayoutDirection(direction)
    return direction
