"""LiveKit voice chat lifecycle for the desktop client."""

from __future__ import annotations

import asyncio
import queue
import struct
import threading
import time
import traceback
from collections import deque
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np

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
VOICE_OUTPUT_BUFFER_MS = 250
VOICE_OUTPUT_STARTUP_MS = 40
VOICE_OUTPUT_IDLE_RESET_MS = 200
VOICE_ECHO_REFERENCE_QUEUE_FRAMES = 3
VOICE_REMOTE_TRACK_DRAIN_MS = 60
VOICE_MIC_DRAIN_TIMEOUT_MS = 250


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
    """Apply gain to int16 PCM without stalling the receive event loop."""
    if gain == 1.0:
        return
    samples = np.frombuffer(data, dtype="<i2")
    scaled = samples.astype(np.float32) * gain
    np.clip(scaled, -32_768, 32_767, out=scaled)
    samples[:] = scaled


@dataclass(slots=True)
class _CapturedInputFrame:
    pcm: bytes
    input_delay: float
    captured_at: float


class _BoundedInputFrameBuffer:
    """Thread-safe callback-to-async buffer that keeps the newest mic frames."""

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        *,
        capacity: int,
    ) -> None:
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self._loop = loop
        self._capacity = capacity
        self._frames: deque[_CapturedInputFrame] = deque()
        self._lock = threading.Lock()
        self._event = asyncio.Event()
        self._wake_pending = False
        self._closed = False
        self.dropped_frames = 0

    def put(self, frame: _CapturedInputFrame) -> None:
        with self._lock:
            if self._closed:
                return
            if len(self._frames) >= self._capacity:
                self._frames.popleft()
                self.dropped_frames += 1
            self._frames.append(frame)
            self._schedule_wake_locked()

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._schedule_wake_locked()

    def discard(self) -> None:
        with self._lock:
            self._frames.clear()

    def _schedule_wake_locked(self) -> None:
        if self._wake_pending:
            return
        self._wake_pending = True
        try:
            self._loop.call_soon_threadsafe(self._wake)
        except RuntimeError:
            self._wake_pending = False

    def _wake(self) -> None:
        with self._lock:
            self._wake_pending = False
        self._event.set()

    async def get(self) -> _CapturedInputFrame | None:
        while True:
            # Clear before inspecting the queue so a producer can never set the
            # event between our empty check and the clear operation.
            self._event.clear()
            with self._lock:
                if self._frames:
                    return self._frames.popleft()
                if self._closed:
                    return None
            await self._event.wait()


class _AudioDelayEstimator:
    """Share the latest PortAudio render delay with microphone processing."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._output_delay = 0.0

    def set_output_delay(self, delay: float) -> None:
        with self._lock:
            self._output_delay = max(float(delay), 0.0)

    def get_output_delay(self) -> float:
        with self._lock:
            return self._output_delay


@dataclass(slots=True)
class _RealtimeInputCapture:
    source: Any
    input_stream: Any
    task: asyncio.Task[None]
    frames: _BoundedInputFrameBuffer
    apm: Any
    delay_estimator: _AudioDelayEstimator
    processing_lock: threading.Lock = field(default_factory=threading.Lock)
    closed: bool = False

    async def aclose(self) -> None:
        if self.closed:
            return
        self.closed = True
        await asyncio.to_thread(self._close_input_stream)
        self.frames.close()
        try:
            await asyncio.wait_for(
                asyncio.shield(self.task),
                timeout=VOICE_MIC_DRAIN_TIMEOUT_MS / 1_000,
            )
        except asyncio.TimeoutError:
            self.task.cancel()
            await asyncio.gather(self.task, return_exceptions=True)
            self.frames.discard()

    def _close_input_stream(self) -> None:
        try:
            self.input_stream.stop()
        except Exception:
            pass
        try:
            self.input_stream.close()
        except Exception:
            pass


async def _open_input_capture(
    *,
    loop: asyncio.AbstractEventLoop,
    input_device: int | None,
) -> _RealtimeInputCapture:
    """Open microphone capture without scheduling fallible Queue.put callbacks."""
    if rtc is None or sd is None:
        raise RuntimeError("Voice input dependencies are unavailable")
    source = rtc.AudioSource(
        VOICE_SAMPLE_RATE,
        VOICE_INPUT_CHANNELS,
        queue_size_ms=VOICE_INPUT_QUEUE_MS,
        loop=loop,
    )
    apm = rtc.AudioProcessingModule(
        echo_cancellation=True,
        noise_suppression=True,
        high_pass_filter=True,
        auto_gain_control=True,
    )
    delay_estimator = _AudioDelayEstimator()
    processing_lock = threading.Lock()
    frames = _BoundedInputFrameBuffer(loop, capacity=VOICE_INPUT_QUEUE_FRAMES)

    def input_callback(indata: Any, frame_count: int, time_info: Any, status: Any) -> None:
        try:
            input_delay = max(
                float(time_info.currentTime - time_info.inputBufferAdcTime),
                0.0,
            )
        except Exception:
            input_delay = 0.0
        captured_at = time.monotonic()
        frame_samples = VOICE_SAMPLE_RATE * VOICE_INPUT_FRAME_MS // 1_000
        for start in range(0, frame_count - frame_samples + 1, frame_samples):
            end = start + frame_samples
            frames.put(
                _CapturedInputFrame(
                    pcm=indata[start:end, 0].tobytes(),
                    input_delay=input_delay,
                    captured_at=captured_at,
                )
            )

    def open_stream() -> Any:
        input_stream = sd.InputStream(
            callback=input_callback,
            dtype="int16",
            channels=VOICE_INPUT_CHANNELS,
            device=input_device,
            samplerate=VOICE_SAMPLE_RATE,
            blocksize=VOICE_IO_BLOCK_FRAMES,
        )
        try:
            input_stream.start()
        except Exception:
            try:
                input_stream.close()
            except Exception:
                pass
            raise
        return input_stream

    try:
        input_stream = await asyncio.to_thread(open_stream)
    except Exception:
        frames.close()
        await source.aclose()
        raise

    async def pump() -> None:
        frame_samples = VOICE_SAMPLE_RATE * VOICE_INPUT_FRAME_MS // 1_000
        while True:
            captured = await frames.get()
            if captured is None:
                return
            frame = rtc.AudioFrame(
                captured.pcm,
                VOICE_SAMPLE_RATE,
                VOICE_INPUT_CHANNELS,
                frame_samples,
            )
            queue_delay = max(time.monotonic() - captured.captured_at, 0.0)
            total_delay_ms = int(
                (
                    captured.input_delay
                    + delay_estimator.get_output_delay()
                    + queue_delay
                )
                * 1_000
            )
            try:
                with processing_lock:
                    apm.set_stream_delay_ms(total_delay_ms)
                    apm.process_stream(frame)
            except Exception:
                pass
            try:
                await source.capture_frame(frame)
            except Exception:
                pass

    task = asyncio.create_task(pump())
    return _RealtimeInputCapture(
        source=source,
        input_stream=input_stream,
        task=task,
        frames=frames,
        apm=apm,
        delay_estimator=delay_estimator,
        processing_lock=processing_lock,
    )


@dataclass(slots=True)
class _RemoteTrackPlayback:
    """Runtime resources for one independently decoded remote audio track."""

    stream: Any
    buffer: _BoundedPcmBuffer
    task: asyncio.Task[None]


class _RealtimeOutputPlayer:
    """Render independent remote tracks without receive-side processing.

    LiveKit's Python ``AudioMixer`` waits on every registered stream and treats
    normal quiet periods as timeouts. Per-track buffers let PortAudio's device
    clock decide the playout cadence, so a quiet participant cannot stall one
    who is speaking.
    """

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
        self.output_stream = None
        self.track_streams: dict[str, _RemoteTrackPlayback] = {}
        self._track_lock = asyncio.Lock()
        self._track_buffers_lock = threading.Lock()
        self._track_buffers: tuple[_BoundedPcmBuffer, ...] = ()
        self._mix_scratch = np.zeros(
            VOICE_IO_BLOCK_FRAMES * self.num_channels,
            dtype=np.int32,
        )
        self.running = False
        self.apm = None
        self.delay_estimator = None
        self.apm_processing_lock = None
        self._echo_processor_lock = threading.Lock()
        self._echo_queue: queue.Queue[tuple[bytes, float | None] | None] = queue.Queue(
            maxsize=VOICE_ECHO_REFERENCE_QUEUE_FRAMES
        )
        self._echo_stop = threading.Event()
        self._echo_thread: threading.Thread | None = None

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
        self._mix_scratch = np.zeros(
            VOICE_IO_BLOCK_FRAMES * num_channels,
            dtype=np.int32,
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
                self._start_echo_worker()
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
        self._render_remote_audio(outdata, bytes_needed)
        if self.apm is not None:
            self._queue_echo_reference(bytes(outdata[:bytes_needed]), time_info)

    def _render_remote_audio(self, outdata: Any, bytes_needed: int) -> None:
        """Mix ready tracks at the device deadline without waiting on quiet tracks."""
        sample_count = bytes_needed // VOICE_SAMPLE_WIDTH_BYTES
        output_samples = np.frombuffer(outdata, dtype="<i2", count=sample_count)
        output_samples.fill(0)
        with self._track_buffers_lock:
            track_buffers = self._track_buffers
        chunks = [buffer.read(bytes_needed) for buffer in track_buffers]
        chunks = [chunk for chunk in chunks if chunk]
        if not chunks:
            return
        if len(chunks) == 1:
            samples = np.frombuffer(chunks[0], dtype="<i2")
            output_samples[: samples.size] = samples
            return
        if self._mix_scratch.size < sample_count:
            self._mix_scratch = np.zeros(sample_count, dtype=np.int32)
        mixed = self._mix_scratch[:sample_count]
        mixed.fill(0)
        for chunk in chunks:
            samples = np.frombuffer(chunk, dtype="<i2")
            mixed[: samples.size] += samples
        np.clip(mixed, -32_768, 32_767, out=mixed)
        output_samples[:] = mixed

    def _queue_echo_reference(self, rendered_pcm: bytes, time_info: Any) -> None:
        """Queue rendered PCM without doing signal processing in PortAudio's callback."""
        if self.apm is None:
            return
        try:
            output_delay = max(
                float(time_info.outputBufferDacTime - time_info.currentTime),
                0.0,
            )
        except Exception:
            output_delay = None
        item = (rendered_pcm, output_delay)
        try:
            self._echo_queue.put_nowait(item)
        except queue.Full:
            try:
                self._echo_queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self._echo_queue.put_nowait(item)
            except queue.Full:
                pass

    def _start_echo_worker(self) -> None:
        if self._echo_thread is not None and self._echo_thread.is_alive():
            return
        self._discard_echo_references()
        self._echo_stop.clear()
        self._echo_thread = threading.Thread(
            target=self._echo_worker_loop,
            name="PlayAuralVoiceEchoReference",
            daemon=True,
        )
        self._echo_thread.start()

    def _echo_worker_loop(self) -> None:
        while not self._echo_stop.is_set():
            try:
                item = self._echo_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            if item is None:
                break
            rendered_pcm, output_delay = item
            with self._echo_processor_lock:
                apm = self.apm
                if apm is None or rtc is None:
                    continue
                estimator = self.delay_estimator
                if estimator is not None and output_delay is not None:
                    try:
                        estimator.set_output_delay(output_delay)
                    except Exception:
                        pass
                processing_lock = self.apm_processing_lock
                if processing_lock is None:
                    self._process_echo_reference(apm, rendered_pcm)
                else:
                    with processing_lock:
                        self._process_echo_reference(apm, rendered_pcm)

    def _process_echo_reference(self, apm: Any, rendered_pcm: bytes) -> None:
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

    def _discard_echo_references(self) -> None:
        while True:
            try:
                self._echo_queue.get_nowait()
            except queue.Empty:
                return

    def _stop_echo_worker(self) -> None:
        self._echo_stop.set()
        self._discard_echo_references()
        try:
            self._echo_queue.put_nowait(None)
        except queue.Full:
            pass
        echo_thread = self._echo_thread
        self._echo_thread = None
        if echo_thread is not None and echo_thread.is_alive():
            echo_thread.join(timeout=1.0)

    def set_echo_processor(
        self,
        apm: Any,
        delay_estimator: Any,
        processing_lock: threading.Lock | None = None,
    ) -> None:
        """Provide a mono render reference for microphone-side echo cancellation."""
        self._discard_echo_references()
        with self._echo_processor_lock:
            self.apm = apm
            self.delay_estimator = delay_estimator
            self.apm_processing_lock = processing_lock

    def clear_echo_processor(
        self,
        apm: Any,
        delay_estimator: Any,
        processing_lock: threading.Lock | None = None,
    ) -> None:
        with self._echo_processor_lock:
            if self.apm is apm:
                self.apm = None
            if self.delay_estimator is delay_estimator:
                self.delay_estimator = None
            if self.apm_processing_lock is processing_lock:
                self.apm_processing_lock = None
        self._discard_echo_references()

    async def start(self) -> None:
        if self.running:
            raise RuntimeError("Voice output is already running")
        try:
            await asyncio.to_thread(self._start_output_stream)
            self.running = True
        except Exception:
            await asyncio.to_thread(self._close_output_stream)
            raise

    async def _consume_track(
        self,
        stream: Any,
        buffer: _BoundedPcmBuffer,
    ) -> None:
        try:
            async for event in stream:
                if not self.running:
                    break
                buffer.extend(event.frame.data.tobytes())
        except asyncio.CancelledError:
            raise
        except Exception:
            traceback.print_exc()

    def _refresh_track_buffers(self) -> None:
        with self._track_buffers_lock:
            self._track_buffers = tuple(
                playback.buffer for playback in self.track_streams.values()
            )

    async def add_track(self, track: Any) -> None:
        async with self._track_lock:
            if not self.running:
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
            buffer = _BoundedPcmBuffer(
                self.get_volume,
                max_bytes=self._buffer_size(self.num_channels),
                frame_bytes=self.num_channels * VOICE_SAMPLE_WIDTH_BYTES,
                startup_bytes=(
                    VOICE_SAMPLE_RATE
                    * self.num_channels
                    * VOICE_SAMPLE_WIDTH_BYTES
                    * VOICE_OUTPUT_STARTUP_MS
                    // 1_000
                ),
                idle_reset_bytes=(
                    VOICE_SAMPLE_RATE
                    * self.num_channels
                    * VOICE_SAMPLE_WIDTH_BYTES
                    * VOICE_OUTPUT_IDLE_RESET_MS
                    // 1_000
                ),
            )
            try:
                task = asyncio.create_task(self._consume_track(stream, buffer))
            except Exception:
                try:
                    await stream.aclose()
                except Exception:
                    pass
                raise
            self.track_streams[track_sid] = _RemoteTrackPlayback(
                stream=stream,
                buffer=buffer,
                task=task,
            )
            self._refresh_track_buffers()

    async def remove_track(self, track: Any) -> None:
        track_sid = getattr(track, "sid", "")
        async with self._track_lock:
            playback = self.track_streams.get(track_sid)
            if playback is None:
                return
            # Give already-decoded speech a brief chance to reach the output before
            # retiring an unpublished track. This protects sentence endings without
            # retaining stale audio or adding steady-state latency.
            await asyncio.sleep(VOICE_REMOTE_TRACK_DRAIN_MS / 1_000)
            self.track_streams.pop(track_sid, None)
            self._refresh_track_buffers()
            playback.task.cancel()
            try:
                await playback.task
            except asyncio.CancelledError:
                pass
            try:
                await playback.stream.aclose()
            except Exception:
                pass

    def clear_buffer(self) -> None:
        with self._track_buffers_lock:
            track_buffers = self._track_buffers
        for buffer in track_buffers:
            buffer.clear()

    def _close_output_stream(self) -> None:
        output_stream = self.output_stream
        self.output_stream = None
        if output_stream is not None:
            try:
                output_stream.abort()
            except Exception:
                pass
            try:
                output_stream.close()
            except Exception:
                pass
        self._stop_echo_worker()

    async def aclose(self) -> None:
        self.running = False
        self.clear_buffer()
        await asyncio.to_thread(self._close_output_stream)
        async with self._track_lock:
            entries = list(self.track_streams.values())
            self.track_streams.clear()
            self._refresh_track_buffers()
            for playback in entries:
                playback.task.cancel()
            if entries:
                await asyncio.gather(
                    *(playback.task for playback in entries),
                    return_exceptions=True,
                )
                await asyncio.gather(
                    *(playback.stream.aclose() for playback in entries),
                    return_exceptions=True,
                )
        with self._echo_processor_lock:
            self.apm = None
            self.delay_estimator = None
            self.apm_processing_lock = None


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
            if self.room is not room:
                return
            if getattr(track, "kind", None) != rtc.TrackKind.KIND_AUDIO:
                return
            asyncio.run_coroutine_threadsafe(self._add_remote_track(track), self.loop)

        @room.on("track_unsubscribed")
        def on_track_unsubscribed(track: Any, publication: Any, participant: Any) -> None:
            if self.room is not room:
                return
            asyncio.run_coroutine_threadsafe(self._remove_remote_track(track), self.loop)

        @room.on("track_muted")
        def on_track_muted(publication: Any, participant: Any) -> None:
            if self.room is not room:
                return
            track = getattr(publication, "track", None)
            if track is not None and getattr(track, "kind", None) == rtc.TrackKind.KIND_AUDIO:
                asyncio.run_coroutine_threadsafe(
                    self._remove_remote_track(track),
                    self.loop,
                )

        @room.on("track_unmuted")
        def on_track_unmuted(publication: Any, participant: Any) -> None:
            if self.room is not room:
                return
            track = getattr(publication, "track", None)
            if track is not None and getattr(track, "kind", None) == rtc.TrackKind.KIND_AUDIO:
                asyncio.run_coroutine_threadsafe(
                    self._add_remote_track(track),
                    self.loop,
                )

        @room.on("disconnected")
        def on_disconnected(reason: Any) -> None:
            if self.room is not room:
                return
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
                if (
                    track
                    and not bool(getattr(publication, "muted", False))
                    and getattr(track, "kind", None) == rtc.TrackKind.KIND_AUDIO
                ):
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
                self.input_capture = await _open_input_capture(
                    loop=self.loop,
                    input_device=input_device,
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
            getattr(capture, "processing_lock", None),
        )

    def _unlink_input_processing_from_output(self, capture: Any) -> None:
        if not self.output_player or not capture:
            return
        self.output_player.clear_echo_processor(
            getattr(capture, "apm", None),
            getattr(capture, "delay_estimator", None),
            getattr(capture, "processing_lock", None),
        )

    async def _disable_microphone(self) -> None:
        capture = self.input_capture
        publication = self.local_publication
        source = getattr(capture, "source", None)
        self.input_capture = None
        self.local_publication = None
        self.local_track = None
        self._unlink_input_processing_from_output(capture)
        if capture:
            try:
                await capture.aclose()
            except Exception:
                pass
        if source:
            wait_for_playout = getattr(source, "wait_for_playout", None)
            if callable(wait_for_playout):
                try:
                    await asyncio.wait_for(
                        wait_for_playout(),
                        timeout=VOICE_MIC_DRAIN_TIMEOUT_MS / 1_000,
                    )
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
                source.clear_queue()
            except Exception:
                pass
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
    """Thread-safe latency-bounded PCM FIFO with per-frame volume gain."""

    def __init__(
        self,
        get_volume: Callable[[], float],
        *,
        max_bytes: int,
        frame_bytes: int,
        startup_bytes: int = 0,
        idle_reset_bytes: int = 0,
    ) -> None:
        if frame_bytes < VOICE_SAMPLE_WIDTH_BYTES:
            raise ValueError("frame_bytes must hold at least one PCM sample")
        self._frame_bytes = frame_bytes
        self._max_bytes = max_bytes - (max_bytes % frame_bytes)
        if self._max_bytes < frame_bytes:
            raise ValueError("max_bytes must hold at least one PCM frame")
        self._startup_bytes = min(
            self._max_bytes,
            max(0, startup_bytes - (startup_bytes % frame_bytes)),
        )
        self._idle_reset_bytes = max(
            0,
            idle_reset_bytes - (idle_reset_bytes % frame_bytes),
        )
        self._idle_bytes = 0
        self._playout_started = self._startup_bytes == 0
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
            if not self._playout_started:
                if len(self._inner) < max(self._startup_bytes, max_bytes):
                    return b""
                self._playout_started = True
            take = min(max_bytes, len(self._inner))
            take -= take % self._frame_bytes
            data = bytes(self._inner[:take])
            del self._inner[:take]
            if take:
                self._idle_bytes = 0
            elif self._playout_started and self._idle_reset_bytes:
                self._idle_bytes = min(
                    self._idle_bytes + max_bytes,
                    self._idle_reset_bytes,
                )
                if self._idle_bytes >= self._idle_reset_bytes:
                    self._playout_started = False
        return data

    def __len__(self) -> int:
        with self._lock:
            return len(self._inner)

    def clear(self) -> None:
        with self._lock:
            self._inner.clear()
            self._idle_bytes = 0
            self._playout_started = self._startup_bytes == 0
