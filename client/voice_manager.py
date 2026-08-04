"""LiveKit voice chat lifecycle for the desktop client."""

from __future__ import annotations

import asyncio
import struct
import threading
import traceback
from typing import Any, Awaitable, Callable

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
VoiceOperation = Callable[[], Awaitable[None]]


VOICE_SAMPLE_RATE = 48_000
VOICE_INPUT_CHANNELS = 1
VOICE_PREFERRED_OUTPUT_CHANNELS = 2
VOICE_SAMPLE_WIDTH_BYTES = 2
VOICE_IO_BLOCK_MS = 20
VOICE_IO_BLOCK_FRAMES = VOICE_SAMPLE_RATE * VOICE_IO_BLOCK_MS // 1_000
VOICE_INPUT_FRAME_MS = 10
VOICE_INPUT_QUEUE_MS = 200
VOICE_INPUT_QUEUE_FRAMES = VOICE_INPUT_QUEUE_MS // VOICE_INPUT_FRAME_MS
VOICE_REMOTE_STREAM_QUEUE_MS = 300
VOICE_REMOTE_STREAM_QUEUE_FRAMES = VOICE_REMOTE_STREAM_QUEUE_MS // VOICE_IO_BLOCK_MS
VOICE_MIXER_QUEUE_MS = 200
VOICE_MIXER_QUEUE_FRAMES = VOICE_MIXER_QUEUE_MS // VOICE_IO_BLOCK_MS
VOICE_OUTPUT_BUFFER_MS = 250


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


def _apply_pcm_gain(data: bytearray, gain: float) -> None:
    """Apply gain multiplier to int16 PCM samples in a bytearray.

    Pure Python implementation — no numpy required.
    Works in-place on the bytearray to avoid memory allocations.
    """
    if gain == 1.0:
        return
    n = len(data) // 2  # number of int16 samples
    # Process in chunks of 512 samples to avoid excessive struct overhead
    CHUNK = 512
    for chunk_start in range(0, n, CHUNK):
        chunk_end = min(chunk_start + CHUNK, n)
        for i in range(chunk_start, chunk_end):
            sample = struct.unpack_from("<h", data, i * 2)[0]
            scaled = int(sample * gain)
            # Clamp to int16 range
            if scaled > 32767:
                scaled = 32767
            elif scaled < -32768:
                scaled = -32768
            struct.pack_into("<h", data, i * 2, scaled)


class _AudioFrameIterator:
    """Expose only decoded frames from a LiveKit AudioStream."""

    def __init__(self, stream: Any) -> None:
        self.stream = stream

    def __aiter__(self) -> "_AudioFrameIterator":
        return self

    async def __anext__(self) -> Any:
        event = await self.stream.__anext__()
        return event.frame


class _RealtimeOutputPlayer:
    """Mix remote audio without receive denoising or stereo channel collapse."""

    def __init__(
        self,
        *,
        loop: asyncio.AbstractEventLoop,
        get_volume: Callable[[], float],
        output_device: int | None = None,
    ) -> None:
        self.loop = loop
        self.get_volume = get_volume
        self.output_device = output_device
        self.num_channels = VOICE_PREFERRED_OUTPUT_CHANNELS
        self.buffer = _BoundedPcmBuffer(
            get_volume,
            max_bytes=self._buffer_size(self.num_channels),
            frame_bytes=self.num_channels * VOICE_SAMPLE_WIDTH_BYTES,
        )
        self.output_stream = None
        self.mixer = None
        self.play_task: asyncio.Task | None = None
        self.track_streams: dict[str, tuple[Any, _AudioFrameIterator]] = {}
        self.running = False
        self.apm = None
        self.delay_estimator = None

    @staticmethod
    def _buffer_size(num_channels: int) -> int:
        return (
            VOICE_SAMPLE_RATE
            * num_channels
            * VOICE_SAMPLE_WIDTH_BYTES
            * VOICE_OUTPUT_BUFFER_MS
            // 1_000
        )

    def _configure_channels(self, num_channels: int) -> None:
        self.num_channels = num_channels
        self.buffer = _BoundedPcmBuffer(
            self.get_volume,
            max_bytes=self._buffer_size(num_channels),
            frame_bytes=num_channels * VOICE_SAMPLE_WIDTH_BYTES,
        )

    def _start_output_stream(self) -> None:
        if sd is None:
            raise RuntimeError("sounddevice is unavailable")
        last_error: Exception | None = None
        for num_channels in (VOICE_PREFERRED_OUTPUT_CHANNELS, 1):
            output_stream = None
            self._configure_channels(num_channels)
            try:
                output_stream = sd.RawOutputStream(
                    samplerate=VOICE_SAMPLE_RATE,
                    blocksize=VOICE_IO_BLOCK_FRAMES,
                    device=self.output_device,
                    channels=num_channels,
                    dtype="int16",
                    callback=self._output_callback,
                )
                output_stream.start()
                self.output_stream = output_stream
                return
            except Exception as error:
                last_error = error
                if output_stream is not None:
                    try:
                        output_stream.close()
                    except Exception:
                        pass
        raise RuntimeError("No compatible audio output device is available") from last_error

    def _output_callback(
        self, outdata: Any, frame_count: int, time_info: Any, status: Any
    ) -> None:
        bytes_needed = frame_count * self.num_channels * VOICE_SAMPLE_WIDTH_BYTES
        chunk = self.buffer.read(bytes_needed)
        copied = len(chunk)
        if copied:
            outdata[:copied] = chunk
        if copied < bytes_needed:
            outdata[copied:bytes_needed] = b"\x00" * (bytes_needed - copied)
        if self.apm is not None:
            self._feed_echo_cancellation(bytes(outdata[:bytes_needed]), time_info)

    def _feed_echo_cancellation(self, rendered_pcm: bytes, time_info: Any) -> None:
        apm = self.apm
        if apm is None or rtc is None:
            return
        estimator = self.delay_estimator
        if estimator is not None:
            try:
                estimator.set_output_delay(
                    max(float(time_info.outputBufferDacTime - time_info.currentTime), 0.0)
                )
            except Exception:
                pass
        try:
            mono_pcm = _downmix_to_mono(rendered_pcm, self.num_channels)
            frame_bytes = (
                VOICE_SAMPLE_RATE
                * VOICE_SAMPLE_WIDTH_BYTES
                * VOICE_INPUT_FRAME_MS
                // 1_000
            )
            frame_samples = VOICE_SAMPLE_RATE * VOICE_INPUT_FRAME_MS // 1_000
            for offset in range(0, len(mono_pcm) - frame_bytes + 1, frame_bytes):
                render_frame = rtc.AudioFrame(
                    mono_pcm[offset : offset + frame_bytes],
                    VOICE_SAMPLE_RATE,
                    VOICE_INPUT_CHANNELS,
                    frame_samples,
                )
                apm.process_reverse_stream(render_frame)
        except Exception:
            pass

    def set_echo_processor(self, apm: Any, delay_estimator: Any) -> None:
        """Provide a mono render reference for microphone-side echo cancellation."""
        self.apm = apm
        self.delay_estimator = delay_estimator

    def clear_echo_processor(self, apm: Any, delay_estimator: Any) -> None:
        if self.apm is apm:
            self.apm = None
        if self.delay_estimator is delay_estimator:
            self.delay_estimator = None

    async def start(self) -> None:
        if self.running:
            raise RuntimeError("Voice output is already running")
        await asyncio.to_thread(self._start_output_stream)
        try:
            self.mixer = rtc.AudioMixer(
                sample_rate=VOICE_SAMPLE_RATE,
                num_channels=self.num_channels,
                blocksize=VOICE_IO_BLOCK_FRAMES,
                stream_timeout_ms=40,
                capacity=VOICE_MIXER_QUEUE_FRAMES,
            )
            self.running = True
            self.play_task = asyncio.create_task(self._playback_loop())
        except Exception:
            await asyncio.to_thread(self._close_output_stream)
            raise

    async def _playback_loop(self) -> None:
        try:
            async for frame in self.mixer:
                if not self.running:
                    break
                self.buffer.extend(frame.data.tobytes())
        except asyncio.CancelledError:
            raise
        except Exception:
            traceback.print_exc()
        finally:
            self.running = False

    async def add_track(self, track: Any) -> None:
        if not self.running or self.mixer is None:
            raise RuntimeError("Voice output is not running")
        track_sid = getattr(track, "sid", "")
        if not track_sid or track_sid in self.track_streams:
            return
        # Receive processing stays transparent: microphone cleanup belongs to the
        # publisher, while speech, stereo music, and future media tracks retain
        # their decoded channel content here.
        stream = rtc.AudioStream(
            track,
            loop=self.loop,
            capacity=VOICE_REMOTE_STREAM_QUEUE_FRAMES,
            sample_rate=VOICE_SAMPLE_RATE,
            num_channels=self.num_channels,
            frame_size_ms=VOICE_IO_BLOCK_MS,
            noise_cancellation=None,
        )
        iterator = _AudioFrameIterator(stream)
        try:
            self.mixer.add_stream(iterator)
        except Exception:
            try:
                await stream.aclose()
            except Exception:
                pass
            raise
        self.track_streams[track_sid] = (stream, iterator)

    async def remove_track(self, track: Any) -> None:
        track_sid = getattr(track, "sid", "")
        entry = self.track_streams.pop(track_sid, None)
        if entry is None:
            return
        stream, iterator = entry
        if self.mixer is not None:
            self.mixer.remove_stream(iterator)
        try:
            await stream.aclose()
        except Exception:
            pass

    def clear_buffer(self) -> None:
        self.buffer.clear()

    def _close_output_stream(self) -> None:
        output_stream = self.output_stream
        self.output_stream = None
        if output_stream is None:
            return
        try:
            output_stream.abort()
        except Exception:
            pass
        try:
            output_stream.close()
        except Exception:
            pass

    async def aclose(self) -> None:
        self.running = False
        self.buffer.clear()
        await asyncio.to_thread(self._close_output_stream)
        if self.play_task is not None and not self.play_task.done():
            self.play_task.cancel()
            try:
                await self.play_task
            except asyncio.CancelledError:
                pass
        self.play_task = None
        entries = list(self.track_streams.values())
        self.track_streams.clear()
        for stream, iterator in entries:
            if self.mixer is not None:
                self.mixer.remove_stream(iterator)
        if entries:
            await asyncio.gather(
                *(stream.aclose() for stream, _ in entries),
                return_exceptions=True,
            )
        if self.mixer is not None:
            try:
                await self.mixer.aclose()
            except Exception:
                pass
        self.mixer = None
        self.apm = None
        self.delay_estimator = None


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
        self._lifecycle_lock: asyncio.Lock | None = None
        self.thread: threading.Thread | None = None
        self.ready = threading.Event()
        self.room = None
        self.input_devices = None
        self.output_player = None
        self.input_capture = None
        self.local_publication = None
        self.local_track = None
        self.connected = False
        self.mic_enabled = False
        self._mic_busy = False
        self._local_disconnect_requested = False
        self._intent_lock = threading.Lock()
        self._intent = 0
        # Voice volume: 0.1–1.0, read by audio thread and main thread
        self._voice_volume: float = 0.8
        self._volume_lock = threading.Lock()
        self._start_loop()

    @property
    def supported(self) -> bool:
        return rtc is not None and sd is not None

    def _start_loop(self) -> None:
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        self.ready.wait(timeout=5.0)

    def _run_loop(self) -> None:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._lifecycle_lock = asyncio.Lock()
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

    def _submit_operation(self, operation: VoiceOperation) -> None:
        self._submit(self._run_operation(operation))

    async def _run_operation(self, operation: VoiceOperation) -> None:
        """Serialize room and microphone lifecycle mutations on the voice loop."""
        if self._lifecycle_lock is None:
            await operation()
            return
        async with self._lifecycle_lock:
            await operation()

    def join(self, packet: dict[str, Any]) -> None:
        intent = self._next_intent()
        voice_packet = dict(packet)
        self._submit_operation(lambda: self._join(voice_packet, intent))

    def leave(self, *, notify: bool = True) -> None:
        self._next_intent()
        self._submit_operation(lambda: self._leave(notify=notify))

    def set_microphone_enabled(
        self, enabled: bool, *, input_device: int | None = None
    ) -> None:
        self._submit_operation(
            lambda: self._set_microphone_enabled(enabled, input_device=input_device)
        )

    def set_voice_volume(self, volume: float) -> None:
        """Set remote voice playback gain (0.1–1.0).

        Changes apply immediately to all active and future audio.
        Thread-safe for concurrent calls.
        """
        clamped = max(0.1, min(1.0, float(volume)))
        with self._volume_lock:
            self._voice_volume = clamped

    def _get_voice_volume(self) -> float:
        with self._volume_lock:
            return self._voice_volume

    def shutdown(self) -> None:
        if self.loop and self.loop.is_running():
            self._next_intent()
            future = asyncio.run_coroutine_threadsafe(
                self._run_operation(lambda: self._leave(notify=False)), self.loop
            )
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
            self.output_player = _RealtimeOutputPlayer(
                loop=self.loop,
                get_volume=self._get_voice_volume,
            )
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
        if not track_sid:
            return
        try:
            await self.output_player.add_track(track)
        except Exception:
            traceback.print_exc()

    async def _remove_remote_track(self, track: Any) -> None:
        if not self.output_player or not track:
            return
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
                if not self.input_devices:
                    self.input_devices = rtc.MediaDevices(
                        loop=self.loop,
                        input_sample_rate=VOICE_SAMPLE_RATE,
                        output_sample_rate=VOICE_SAMPLE_RATE,
                        num_channels=VOICE_INPUT_CHANNELS,
                        blocksize=VOICE_IO_BLOCK_FRAMES,
                    )
                self.input_capture = self.input_devices.open_input(
                    input_device=input_device,
                    enable_aec=True,
                    noise_suppression=True,
                    high_pass_filter=True,
                    auto_gain_control=True,
                    queue_capacity=VOICE_INPUT_QUEUE_FRAMES,
                )
                self._link_input_processing_to_output(self.input_capture)
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

    def _link_input_processing_to_output(self, capture: Any) -> None:
        """Give an already-open output device the microphone's AEC state."""
        if not self.output_player or not capture:
            return
        self.output_player.set_echo_processor(
            getattr(capture, "apm", None),
            getattr(capture, "delay_estimator", None),
        )

    def _unlink_input_processing_from_output(self, capture: Any) -> None:
        if not self.output_player or not capture:
            return
        self.output_player.clear_echo_processor(
            getattr(capture, "apm", None),
            getattr(capture, "delay_estimator", None),
        )

    async def _disable_microphone(self) -> None:
        capture = self.input_capture
        publication = self.local_publication
        source = getattr(capture, "source", None)
        self.input_capture = None
        self.local_publication = None
        self.local_track = None
        self._unlink_input_processing_from_output(capture)
        if source:
            try:
                source.clear_queue()
            except Exception:
                pass
        if capture:
            try:
                await capture.aclose()
            except Exception:
                pass
        if publication and self.room:
            sid = getattr(publication, "sid", "")
            if sid:
                try:
                    await self.room.local_participant.unpublish_track(sid)
                except Exception:
                    pass
        if source:
            try:
                await source.aclose()
            except Exception:
                pass
        self.mic_enabled = False
        self.on_mic_state(False)

    async def _leave(self, *, notify: bool = True) -> None:
        was_connected = self.connected
        await self._disable_microphone()
        output_player = self.output_player
        self.output_player = None
        if output_player:
            try:
                output_player.clear_buffer()
            except Exception:
                pass
        if self.room:
            try:
                self._local_disconnect_requested = True
                await asyncio.wait_for(self.room.disconnect(), timeout=5.0)
            except Exception:
                pass
            finally:
                self._local_disconnect_requested = False
        self.room = None
        if output_player:
            try:
                await output_player.aclose()
            except Exception:
                pass
        self.input_devices = None
        self.connected = False
        self.on_mic_state(False)
        self.on_state("disconnected")
        if notify and was_connected:
            self.on_status("voice-chat-left", True)


def _downmix_to_mono(data: bytes, num_channels: int) -> bytes:
    """Create a mono AEC reference without changing rendered receive audio."""
    if num_channels <= 1:
        return data
    frame_bytes = num_channels * VOICE_SAMPLE_WIDTH_BYTES
    frame_count = len(data) // frame_bytes
    mono = bytearray(frame_count * VOICE_SAMPLE_WIDTH_BYTES)
    for frame_index in range(frame_count):
        frame_offset = frame_index * frame_bytes
        total = 0
        for channel_index in range(num_channels):
            total += struct.unpack_from(
                "<h",
                data,
                frame_offset + channel_index * VOICE_SAMPLE_WIDTH_BYTES,
            )[0]
        struct.pack_into(
            "<h",
            mono,
            frame_index * VOICE_SAMPLE_WIDTH_BYTES,
            int(total / num_channels),
        )
    return bytes(mono)


class _BoundedPcmBuffer:
    """Thread-safe newest-first PCM buffer with per-frame volume gain."""

    def __init__(
        self,
        get_volume: Callable[[], float],
        *,
        max_bytes: int,
        frame_bytes: int,
    ) -> None:
        if frame_bytes < VOICE_SAMPLE_WIDTH_BYTES:
            raise ValueError("frame_bytes must hold at least one PCM sample")
        self._frame_bytes = frame_bytes
        self._max_bytes = max_bytes - (max_bytes % frame_bytes)
        if self._max_bytes < frame_bytes:
            raise ValueError("max_bytes must hold at least one PCM frame")
        self._inner = bytearray()
        self._get_volume = get_volume
        self._lock = threading.Lock()

    def extend(self, data: bytes) -> None:
        """Append current PCM and drop stale frames before exceeding the cap."""
        usable_bytes = len(data) - (len(data) % self._frame_bytes)
        if usable_bytes <= 0:
            return
        data = data[:usable_bytes]
        if len(data) > self._max_bytes:
            data = data[-self._max_bytes :]
        gain = self._get_volume()
        if gain != 1.0:
            chunk: bytes | bytearray = bytearray(data)
            _apply_pcm_gain(chunk, gain)
        else:
            chunk = data
        with self._lock:
            overflow = len(self._inner) + len(chunk) - self._max_bytes
            if overflow > 0:
                overflow = (
                    (overflow + self._frame_bytes - 1) // self._frame_bytes
                ) * self._frame_bytes
                del self._inner[:overflow]
            self._inner.extend(chunk)

    def read(self, max_bytes: int) -> bytes:
        """Remove and return up to max_bytes of complete PCM frames."""
        max_bytes -= max_bytes % self._frame_bytes
        if max_bytes <= 0:
            return b""
        with self._lock:
            take = min(max_bytes, len(self._inner))
            take -= take % self._frame_bytes
            data = bytes(self._inner[:take])
            del self._inner[:take]
        return data

    def __len__(self) -> int:
        with self._lock:
            return len(self._inner)

    def clear(self) -> None:
        with self._lock:
            self._inner.clear()
