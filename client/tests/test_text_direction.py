import wx

from ui.text_direction import apply_text_layout_direction, locale_layout_direction


def test_locale_direction_uses_wx_locale_metadata_with_region_fallback():
    assert locale_layout_direction("fa") == wx.Layout_RightToLeft
    assert locale_layout_direction("fa-IR") == wx.Layout_RightToLeft
    assert locale_layout_direction("en-US") == wx.Layout_LeftToRight
    assert locale_layout_direction("unsupported-locale") == wx.Layout_LeftToRight


def test_text_direction_changes_controls_without_mirroring_the_window():
    app = wx.GetApp() or wx.App(False)
    frame = wx.Frame(None)
    panel = wx.Panel(frame)
    label = wx.StaticText(panel, label="فارسی")
    history = wx.TextCtrl(panel, value="پیام")
    initial_frame_direction = frame.GetLayoutDirection()

    try:
        apply_text_layout_direction(frame, "fa")

        assert label.GetLayoutDirection() == wx.Layout_RightToLeft
        assert history.GetLayoutDirection() == wx.Layout_RightToLeft
        assert frame.GetLayoutDirection() == initial_frame_direction

        apply_text_layout_direction(frame, "en")
        assert label.GetLayoutDirection() == wx.Layout_LeftToRight
        assert history.GetLayoutDirection() == wx.Layout_LeftToRight
    finally:
        frame.Destroy()
        app.ProcessPendingEvents()
