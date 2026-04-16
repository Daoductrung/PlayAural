"""LiveKit voice chat lifecycle for the desktop client."""

from __future__ import annotations

import asyncio
import threading
import traceback
from typing import Any, Callable

try:
    from livekit import rtc
except Exception:
    rtc = None

try:
    import sounddevice as sd
except Exception:
    sd = None


StatusCallback = Callable[[str, bool], None]
StateCallback = Callable[[str], None]
MicCallback = Callable[[bool], None]
DisconnectCallback = Callable[[str], None]


def _normalize_device_part(value: Any) -> str:
    return str(value or "").strip()


def _build_audio_input_device_id(device_name: str, hostapi_name: str, channel_count: int) -> str:
    return f"{_normalize_device_part(hostapi_name)}|{_normalize_device_part(device_name)}|{int(channel_count)}"


def list_audio_input_devices() -> list[dict[str, Any]]:
    """Return available audio input devices using a stable ID format."""
    if sd is None:
        return []
    try:
        devices = sd.query_devices()
        hostapis = sd.query_hostapis()
        default_device = sd.default.device
    except Exception:
        return []

    default_index = default_device[0] if isinstance(default_device, (list, tuple)) else None
    results: list[dict[str, Any]] = []
    for index, device in enumerate(devices):
        channel_count = int(device.get("max_input_channels", 0) or 0)
        if channel_count < 1:
            continue
        hostapi_index = device.get("hostapi")
        hostapi_name = ""
        if isinstance(hostapi_index, int) and 0 <= hostapi_index < len(hostapis):
            hostapi_name = _normalize_device_part(hostapis[hostapi_index].get("name"))
        device_name = _normalize_device_part(device.get("name")) or f"Input Device {index}"
        results.append(
            {
                "id": _build_audio_input_device_id(device_name, hostapi_name, channel_count),
                "name": f"{device_name} ({hostapi_name})" if hostapi_name else device_name,
                "index": index,
                "is_default": index == default_index,
            }
        )
    return results


def resolve_audio_input_device(device_id: str) -> tuple[int | None, str, str, bool]:
    """Resolve a stored device ID to the current machine's device index."""
    normalized_id = _normalize_device_part(device_id)
    if not normalized_id:
        return None, "", "", True
    for device in list_audio_input_devices():
        if device["id"] == normalized_id:
            return int(device["index"]), str(device["id"]), str(device["name"]), True
    return None, "", "", False


class VoiceManager:
    """Runs LiveKit voice chat on a dedicated asyncio loop."""

    def __init__(
        self,
        *,
        on_status: StatusCallback,
        on_state: StateCallback,
        on_mic_state: MicCallback,
        on_disconnect: DisconnectCallback,
    ) -> None:
        self.on_status = on_status
        self.on_state = on_state
        self.on_mic_state = on_mic_state
        self.on_disconnect = on_disconnect
        self.loop: asyncio.AbstractEventLoop | None = None
        self.thread: threading.Thread | None = None
        self.ready = threading.Event()
        self.room = None
        self.media_devices = None
        self.output_player = None
        self.input_capture = None
        self.local_publication = None
        self.local_track = None
        self.remote_tracks: dict[str, Any] = {}
        self.connected = False
        self.mic_enabled = False
        self._mic_busy = False
        self._local_disconnect_requested = False
        self._intent_lock = threading.Lock()
        self._intent = 0
        self._start_loop()

    @property
    def supported(self) -> bool:
        return rtc is not None

    def _start_loop(self) -> None:
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        self.ready.wait(timeout=5.0)

    def _run_loop(self) -> None:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.ready.set()
        self.loop.run_forever()
        pending = asyncio.all_tasks(self.loop)
        for task in pending:
            task.cancel()
        if pending:
            self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        self.loop.close()

    def _submit(self, coro: Any) -> None:
        if not self.loop or not self.loop.is_running():
            if hasattr(coro, "close"):
                coro.close()
            self.on_status("voice-chat-connect-failed", True)
            return
        asyncio.run_coroutine_threadsafe(coro, self.loop)

    def join(self, packet: dict[str, Any]) -> None:
        intent = self._next_intent()
        self._submit(self._join(packet, intent))

    def leave(self, *, notify: bool = True) -> None:
        self._next_intent()
        self._submit(self._leave(notify=notify))

    def set_microphone_enabled(
        self, enabled: bool, *, input_device: int | None = None
    ) -> None:
        self._submit(self._set_microphone_enabled(enabled, input_device=input_device))

    def shutdown(self) -> None:
        if self.loop and self.loop.is_running():
            self._next_intent()
            future = asyncio.run_coroutine_threadsafe(self._leave(notify=False), self.loop)
            try:
                future.result(timeout=3.0)
            except Exception:
                pass
            self.loop.call_soon_threadsafe(self.loop.stop)
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=3.0)

    def _next_intent(self) -> int:
        with self._intent_lock:
            self._intent += 1
            return self._intent

    def _is_current_intent(self, intent: int) -> bool:
        with self._intent_lock:
            return self._intent == intent

    async def _join(self, packet: dict[str, Any], intent: int) -> None:
        if rtc is None:
            self.on_status("voice-chat-sdk-missing", True)
            self.on_state("disconnected")
            return
        await self._leave(notify=False)
        if not self._is_current_intent(intent):
            return
        self.on_state("connecting")
        try:
            self.media_devices = rtc.MediaDevices(loop=self.loop)
            self.output_player = self.media_devices.open_output()
            await self.output_player.start()
            self.room = rtc.Room(loop=self.loop)
            self._bind_room_events(self.room)
            await self.room.connect(packet["url"], packet["token"])
            if not self._is_current_intent(intent):
                await self._leave(notify=False)
                return
            self.connected = True
            self.mic_enabled = False
            await self._attach_existing_tracks()
            if not self._is_current_intent(intent):
                await self._leave(notify=False)
                return
            self.on_state("connected")
            self.on_mic_state(False)
            self.on_status("voice-chat-listen-only", True)
        except Exception:
            traceback.print_exc()
            await self._leave(notify=False)
            if self._is_current_intent(intent):
                self.on_status("voice-chat-connect-failed", True)
                self.on_state("disconnected")

    def _bind_room_events(self, room: Any) -> None:
        @room.on("track_subscribed")
        def on_track_subscribed(track: Any, publication: Any, participant: Any) -> None:
            if getattr(track, "kind", None) != rtc.TrackKind.KIND_AUDIO:
                return
            asyncio.run_coroutine_threadsafe(self._add_remote_track(track), self.loop)

        @room.on("track_unsubscribed")
        def on_track_unsubscribed(track: Any, publication: Any, participant: Any) -> None:
            asyncio.run_coroutine_threadsafe(self._remove_remote_track(track), self.loop)

        @room.on("disconnected")
        def on_disconnected(reason: Any) -> None:
            if self.connected:
                self.connected = False
                self.mic_enabled = False
                self.on_mic_state(False)
                self.on_state("disconnected")
                if not self._local_disconnect_requested:
                    self.on_disconnect("connection_lost")
                    self.on_status("voice-chat-left", False)

    async def _attach_existing_tracks(self) -> None:
        if not self.room:
            return
        for participant in self.room.remote_participants.values():
            for publication in participant.track_publications.values():
                track = getattr(publication, "track", None)
                if track and getattr(track, "kind", None) == rtc.TrackKind.KIND_AUDIO:
                    await self._add_remote_track(track)

    async def _add_remote_track(self, track: Any) -> None:
        if not self.output_player or not track:
            return
        track_sid = getattr(track, "sid", "")
        if not track_sid or track_sid in self.remote_tracks:
            return
        try:
            await self.output_player.add_track(track)
            self.remote_tracks[track_sid] = track
        except Exception:
            traceback.print_exc()

    async def _remove_remote_track(self, track: Any) -> None:
        if not self.output_player or not track:
            return
        track_sid = getattr(track, "sid", "")
        if track_sid:
            self.remote_tracks.pop(track_sid, None)
        try:
            await self.output_player.remove_track(track)
        except Exception:
            pass

    async def _set_microphone_enabled(
        self, enabled: bool, input_device: int | None = None
    ) -> None:
        if not self.room or not self.connected:
            self.on_status("voice-chat-not-connected", True)
            return
        if self._mic_busy:
            return
        if enabled == self.mic_enabled:
            return
        self._mic_busy = True
        try:
            if enabled:
                if not self.media_devices:
                    self.media_devices = rtc.MediaDevices(loop=self.loop)
                self.input_capture = self.media_devices.open_input(input_device=input_device)
                self.local_track = rtc.LocalAudioTrack.create_audio_track(
                    "microphone", self.input_capture.source
                )
                options = rtc.TrackPublishOptions()
                options.source = rtc.TrackSource.SOURCE_MICROPHONE
                self.local_publication = await self.room.local_participant.publish_track(
                    self.local_track, options
                )
                self.mic_enabled = True
                self.on_mic_state(True)
                self.on_status("voice-chat-mic-on", True)
            else:
                await self._disable_microphone()
                self.on_status("voice-chat-mic-off", True)
        except Exception:
            traceback.print_exc()
            await self._disable_microphone()
            self.on_status("voice-chat-mic-denied", True)
        finally:
            self._mic_busy = False

    async def _disable_microphone(self) -> None:
        publication = self.local_publication
        if publication and self.room:
            sid = getattr(publication, "sid", "")
            if sid:
                try:
                    await self.room.local_participant.unpublish_track(sid)
                except Exception:
                    pass
        if self.input_capture:
            try:
                await self.input_capture.aclose()
            except Exception:
                pass
        self.input_capture = None
        self.local_publication = None
        self.local_track = None
        self.mic_enabled = False
        self.on_mic_state(False)

    async def _leave(self, *, notify: bool = True) -> None:
        await self._disable_microphone()
        if self.output_player:
            try:
                await self.output_player.aclose()
            except Exception:
                pass
        self.output_player = None
        self.remote_tracks.clear()
        if self.room:
            try:
                self._local_disconnect_requested = True
                await asyncio.wait_for(self.room.disconnect(), timeout=5.0)
            except Exception:
                pass
            finally:
                self._local_disconnect_requested = False
        self.room = None
        self.media_devices = None
        was_connected = self.connected
        self.connected = False
        self.on_mic_state(False)
        self.on_state("disconnected")
        if notify and was_connected:
            self.on_status("voice-chat-left", True)
