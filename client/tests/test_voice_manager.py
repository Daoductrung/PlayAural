import asyncio
import struct
import threading
from types import SimpleNamespace

import pytest
import voice_manager
from voice_manager import (
    VOICE_ECHO_REFERENCE_QUEUE_FRAMES,
    VOICE_INPUT_QUEUE_FRAMES,
    VOICE_IO_BLOCK_FRAMES,
    VOICE_MIC_DRAIN_TIMEOUT_MS,
    VOICE_OUTPUT_IDLE_RESET_MS,
    VOICE_OUTPUT_STARTUP_MS,
    VOICE_PREFERRED_OUTPUT_CHANNELS,
    VOICE_REMOTE_STREAM_QUEUE_FRAMES,
    VOICE_REMOTE_TRACK_DRAIN_MS,
    VoiceManager,
    _BoundedPcmBuffer,
    _downmix_to_mono,
    _RealtimeOutputPlayer,
)


def _pcm_samples(*values: int) -> bytes:
    return struct.pack(f"<{len(values)}h", *values)


def _unpack_samples(data: bytes) -> tuple[int, ...]:
    return struct.unpack(f"<{len(data) // 2}h", data)


def _set_output_buffers(
    player: _RealtimeOutputPlayer,
    *buffers: _BoundedPcmBuffer,
) -> None:
    with player._track_buffers_lock:
        player._track_buffers = buffers


def test_voice_buffer_keeps_newest_complete_samples() -> None:
    buffer = _BoundedPcmBuffer(lambda: 1.0, max_bytes=12, frame_bytes=4)

    buffer.extend(_pcm_samples(1, 2, 3, 4))
    buffer.extend(_pcm_samples(5, 6, 7, 8))

    assert len(buffer) == 12
    assert _unpack_samples(buffer.read(12)) == (3, 4, 5, 6, 7, 8)

    buffer.extend(_pcm_samples(9, 10, 11, 12, 13, 14, 15, 16))

    assert len(buffer) == 12
    assert _unpack_samples(buffer.read(12)) == (11, 12, 13, 14, 15, 16)


def test_voice_buffer_applies_current_gain_without_losing_its_cap() -> None:
    gain = 0.5
    buffer = _BoundedPcmBuffer(lambda: gain, max_bytes=4, frame_bytes=2)

    buffer.extend(_pcm_samples(1_000, -1_000, 2_000))

    assert len(buffer) == 4
    assert _unpack_samples(buffer.read(4)) == (-500, 1_000)

    gain = 2.0
    buffer.extend(_pcm_samples(20_000, -20_000))
    assert _unpack_samples(buffer.read(4)) == (32_767, -32_768)


def test_voice_buffer_remains_bounded_during_callback_thread_reads() -> None:
    buffer = _BoundedPcmBuffer(lambda: 1.0, max_bytes=4_800, frame_bytes=4)
    stereo_block = _pcm_samples(1_000, -1_000) * 96
    start = threading.Event()

    def produce() -> None:
        start.wait()
        for _ in range(2_000):
            buffer.extend(stereo_block)

    def consume() -> None:
        start.wait()
        for _ in range(2_000):
            data = buffer.read(len(stereo_block))
            assert len(data) % 4 == 0

    producer = threading.Thread(target=produce)
    consumer = threading.Thread(target=consume)
    producer.start()
    consumer.start()
    start.set()
    producer.join(timeout=2.0)
    consumer.join(timeout=2.0)

    assert not producer.is_alive()
    assert not consumer.is_alive()
    assert len(buffer) <= 4_800
    assert len(buffer) % 4 == 0


def test_desktop_voice_buffers_are_bounded_for_realtime_audio() -> None:
    assert VOICE_IO_BLOCK_FRAMES == 960
    assert VOICE_INPUT_QUEUE_FRAMES == 20
    assert VOICE_REMOTE_STREAM_QUEUE_FRAMES == 15
    assert VOICE_OUTPUT_STARTUP_MS == 40
    assert VOICE_OUTPUT_IDLE_RESET_MS == 200
    assert VOICE_ECHO_REFERENCE_QUEUE_FRAMES == 3
    assert VOICE_REMOTE_TRACK_DRAIN_MS == 60
    assert VOICE_MIC_DRAIN_TIMEOUT_MS == 250
    assert _RealtimeOutputPlayer._buffer_size(1) == 24_000
    assert _RealtimeOutputPlayer._buffer_size(2) == 48_000


def test_voice_buffer_resumes_immediately_after_temporary_starvation() -> None:
    buffer = _BoundedPcmBuffer(
        lambda: 1.0,
        max_bytes=24,
        frame_bytes=4,
    )
    first = _pcm_samples(1, 2)
    second = _pcm_samples(3, 4)

    buffer.extend(first)
    assert buffer.read(4) == first
    assert buffer.read(4) == b""

    buffer.extend(second)
    assert buffer.read(4) == second


def test_voice_buffer_uses_startup_cushion_only_once() -> None:
    buffer = _BoundedPcmBuffer(
        lambda: 1.0,
        max_bytes=24,
        frame_bytes=4,
        startup_bytes=8,
    )
    first = _pcm_samples(1, 2)
    second = _pcm_samples(3, 4)
    resumed = _pcm_samples(5, 6)

    buffer.extend(first)
    assert buffer.read(4) == b""
    buffer.extend(second)
    assert buffer.read(4) == first
    assert buffer.read(4) == second
    assert buffer.read(4) == b""

    buffer.extend(resumed)
    assert buffer.read(4) == resumed


def test_voice_buffer_rearms_startup_only_after_sustained_idle() -> None:
    buffer = _BoundedPcmBuffer(
        lambda: 1.0,
        max_bytes=24,
        frame_bytes=4,
        startup_bytes=8,
        idle_reset_bytes=8,
    )
    first = _pcm_samples(1, 2)
    second = _pcm_samples(3, 4)
    brief_resume = _pcm_samples(5, 6)

    buffer.extend(first + second)
    assert buffer.read(4) == first
    assert buffer.read(4) == second
    assert buffer.read(4) == b""
    buffer.extend(brief_resume)
    assert buffer.read(4) == brief_resume

    assert buffer.read(4) == b""
    assert buffer.read(4) == b""
    buffer.extend(first)
    assert buffer.read(4) == b""
    buffer.extend(second)
    assert buffer.read(4) == first


def test_stereo_downmix_is_only_a_copy_for_echo_cancellation() -> None:
    stereo = _pcm_samples(1_000, -1_000, 3_000, 1_000)

    mono = _downmix_to_mono(stereo, 2)

    assert _unpack_samples(mono) == (0, 2_000)
    assert _unpack_samples(stereo) == (1_000, -1_000, 3_000, 1_000)


def test_output_callback_preserves_stereo_channels() -> None:
    loop = asyncio.new_event_loop()
    try:
        player = _RealtimeOutputPlayer(loop=loop, get_volume=lambda: 1.0)
        player.apm = None
        stereo = _pcm_samples(1_000, -1_000, 2_000, -2_000)
        buffer = _BoundedPcmBuffer(lambda: 1.0, max_bytes=16, frame_bytes=4)
        buffer.extend(stereo)
        _set_output_buffers(player, buffer)
        outdata = bytearray(len(stereo))

        player._output_callback(
            outdata,
            frame_count=2,
            time_info=SimpleNamespace(outputBufferDacTime=0.0, currentTime=0.0),
            status=None,
        )

        assert bytes(outdata) == stereo
    finally:
        loop.close()


def test_echo_cancellation_runs_off_callback_and_receives_ten_ms_mono_frames() -> None:
    class APM:
        def __init__(self) -> None:
            self.frames = []
            self.thread_ids = []
            self.complete = threading.Event()

        def process_reverse_stream(self, frame) -> None:
            self.frames.append(frame)
            self.thread_ids.append(threading.get_ident())
            if len(self.frames) == 2:
                self.complete.set()

    loop = asyncio.new_event_loop()
    try:
        player = _RealtimeOutputPlayer(loop=loop, get_volume=lambda: 1.0)
        apm = APM()
        player._start_echo_worker()
        player.set_echo_processor(apm, None)
        stereo_frame = _pcm_samples(3_000, 1_000)
        stereo = stereo_frame * VOICE_IO_BLOCK_FRAMES
        buffer = _BoundedPcmBuffer(
            lambda: 1.0,
            max_bytes=len(stereo),
            frame_bytes=4,
        )
        buffer.extend(stereo)
        _set_output_buffers(player, buffer)
        outdata = bytearray(len(stereo))
        callback_thread_id = threading.get_ident()

        player._output_callback(
            outdata,
            frame_count=VOICE_IO_BLOCK_FRAMES,
            time_info=SimpleNamespace(outputBufferDacTime=0.02, currentTime=0.0),
            status=None,
        )

        assert bytes(outdata) == stereo
        assert apm.complete.wait(timeout=1.0)
        assert len(apm.frames) == 2
        assert all(thread_id != callback_thread_id for thread_id in apm.thread_ids)
        assert all(frame.num_channels == 1 for frame in apm.frames)
        assert all(frame.samples_per_channel == 480 for frame in apm.frames)
        assert _unpack_samples(apm.frames[0].data.tobytes()) == (2_000,) * 480
    finally:
        player.clear_echo_processor(apm, None)
        player._stop_echo_worker()
        loop.close()


def test_output_underflow_does_not_stall_available_audio() -> None:
    loop = asyncio.new_event_loop()
    try:
        player = _RealtimeOutputPlayer(loop=loop, get_volume=lambda: 1.0)
        block = _pcm_samples(1_000, -1_000) * VOICE_IO_BLOCK_FRAMES
        buffer = _BoundedPcmBuffer(
            lambda: 1.0,
            max_bytes=len(block) * 3,
            frame_bytes=4,
        )
        buffer.extend(block * 3)
        _set_output_buffers(player, buffer)
        outdata = bytearray(len(block))
        time_info = SimpleNamespace(outputBufferDacTime=0.02, currentTime=0.0)

        player._output_callback(
            outdata,
            frame_count=VOICE_IO_BLOCK_FRAMES,
            time_info=time_info,
            status=SimpleNamespace(output_underflow=True),
        )
        assert bytes(outdata) == block
        assert len(buffer) == len(block) * 2
    finally:
        loop.close()


def test_output_uses_mono_only_when_stereo_device_open_fails(monkeypatch) -> None:
    attempts: list[int] = []

    class Stream:
        def __init__(self, channels: int) -> None:
            self.channels = channels

        def start(self) -> None:
            if self.channels == VOICE_PREFERRED_OUTPUT_CHANNELS:
                raise RuntimeError("stereo unavailable")

        def abort(self) -> None:
            pass

        def close(self) -> None:
            pass

    def open_stream(**kwargs):
        channels = kwargs["channels"]
        attempts.append(channels)
        return Stream(channels)

    monkeypatch.setattr(voice_manager.sd, "RawOutputStream", open_stream)
    loop = asyncio.new_event_loop()
    try:
        player = _RealtimeOutputPlayer(loop=loop, get_volume=lambda: 1.0)

        player._start_output_stream()

        assert attempts == [2, 1]
        assert player.num_channels == 1
    finally:
        player._close_output_stream()
        loop.close()


@pytest.mark.asyncio
async def test_remote_tracks_request_stereo_without_receive_denoising(monkeypatch) -> None:
    captured: dict = {}

    class Stream:
        def __init__(self) -> None:
            self.wait = asyncio.Event()

        def __aiter__(self):
            return self

        async def __anext__(self):
            await self.wait.wait()
            raise StopAsyncIteration

        async def aclose(self) -> None:
            pass

    def make_stream(track, **kwargs):
        captured.update(kwargs)
        return Stream()

    monkeypatch.setattr(voice_manager.rtc, "AudioStream", make_stream)
    player = _RealtimeOutputPlayer(
        loop=asyncio.get_running_loop(),
        get_volume=lambda: 1.0,
    )
    player.running = True

    await player.add_track(SimpleNamespace(sid="stereo-track"))

    assert captured["sample_rate"] == 48_000
    assert captured["num_channels"] == 2
    assert captured["frame_size_ms"] == 20
    assert captured["capacity"] == VOICE_REMOTE_STREAM_QUEUE_FRAMES
    assert captured["noise_cancellation"] is None
    assert len(player.track_streams) == 1
    await player.aclose()


@pytest.mark.asyncio
async def test_remote_track_starts_after_two_frames_without_losing_audio(
    monkeypatch,
) -> None:
    first = _pcm_samples(1_000, -1_000) * VOICE_IO_BLOCK_FRAMES
    second = _pcm_samples(2_000, -2_000) * VOICE_IO_BLOCK_FRAMES

    class Stream:
        def __init__(self) -> None:
            self.events = [
                SimpleNamespace(
                    frame=SimpleNamespace(data=SimpleNamespace(tobytes=lambda: first))
                ),
                SimpleNamespace(
                    frame=SimpleNamespace(data=SimpleNamespace(tobytes=lambda: second))
                ),
            ]
            self.wait = asyncio.Event()

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.events:
                return self.events.pop(0)
            await self.wait.wait()
            raise StopAsyncIteration

        async def aclose(self) -> None:
            pass

    monkeypatch.setattr(voice_manager.rtc, "AudioStream", lambda *args, **kwargs: Stream())
    player = _RealtimeOutputPlayer(
        loop=asyncio.get_running_loop(),
        get_volume=lambda: 1.0,
    )
    player.running = True
    await player.add_track(SimpleNamespace(sid="speech"))
    await asyncio.sleep(0)
    outdata = bytearray(len(first))

    player._output_callback(
        outdata,
        VOICE_IO_BLOCK_FRAMES,
        SimpleNamespace(outputBufferDacTime=0.02, currentTime=0.0),
        None,
    )
    assert bytes(outdata) == first

    player._output_callback(
        outdata,
        VOICE_IO_BLOCK_FRAMES,
        SimpleNamespace(outputBufferDacTime=0.02, currentTime=0.0),
        None,
    )
    assert bytes(outdata) == second
    await player.aclose()


@pytest.mark.asyncio
async def test_remote_track_removal_yields_before_discarding_tail() -> None:
    events: list[str] = []

    class Stream:
        def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                await asyncio.Event().wait()
            finally:
                events.append("consumer_stopped")

        async def aclose(self) -> None:
            events.append("stream_close")

    player = _RealtimeOutputPlayer(
        loop=asyncio.get_running_loop(),
        get_volume=lambda: 1.0,
    )
    player.running = True
    stream = Stream()
    buffer = _BoundedPcmBuffer(lambda: 1.0, max_bytes=8, frame_bytes=4)
    task = asyncio.create_task(player._consume_track(stream, buffer))
    player.track_streams["remote-track"] = voice_manager._RemoteTrackPlayback(
        stream=stream,
        buffer=buffer,
        task=task,
    )
    player._refresh_track_buffers()
    await asyncio.sleep(0)

    async def observe_drain_window() -> None:
        await asyncio.sleep(0)
        events.append("tail_drain_window")

    observer = asyncio.create_task(observe_drain_window())
    await player.remove_track(SimpleNamespace(sid="remote-track"))
    await observer

    assert events == ["tail_drain_window", "consumer_stopped", "stream_close"]


@pytest.mark.asyncio
async def test_muted_tracks_leave_playback_until_unmuted() -> None:
    handlers: dict[str, object] = {}
    events: list[tuple[str, str]] = []

    class Room:
        def on(self, event_name: str):
            def register(handler):
                handlers[event_name] = handler
                return handler

            return register

    async def add_track(track) -> None:
        events.append(("add", track.sid))

    async def remove_track(track) -> None:
        events.append(("remove", track.sid))

    manager = VoiceManager.__new__(VoiceManager)
    manager.loop = asyncio.get_running_loop()
    manager.connected = True
    manager._local_disconnect_requested = False
    manager._add_remote_track = add_track
    manager._remove_remote_track = remove_track
    manager.on_mic_state = lambda enabled: None
    manager.on_state = lambda state: None
    manager.on_disconnect = lambda reason: None
    manager.on_status = lambda key, speak: None
    manager._bind_room_events(Room())

    track = SimpleNamespace(
        sid="remote-track",
        kind=voice_manager.rtc.TrackKind.KIND_AUDIO,
    )
    publication = SimpleNamespace(track=track)
    handlers["track_muted"](publication, None)
    await asyncio.sleep(0.01)
    handlers["track_unmuted"](publication, None)
    await asyncio.sleep(0.01)

    assert events == [("remove", "remote-track"), ("add", "remote-track")]


@pytest.mark.asyncio
async def test_existing_muted_tracks_are_not_attached() -> None:
    attached: list[str] = []
    audible_track = SimpleNamespace(
        sid="audible",
        kind=voice_manager.rtc.TrackKind.KIND_AUDIO,
    )
    muted_track = SimpleNamespace(
        sid="muted",
        kind=voice_manager.rtc.TrackKind.KIND_AUDIO,
    )
    participant = SimpleNamespace(
        track_publications={
            "audible": SimpleNamespace(track=audible_track, muted=False),
            "muted": SimpleNamespace(track=muted_track, muted=True),
        }
    )
    manager = VoiceManager.__new__(VoiceManager)
    manager.room = SimpleNamespace(remote_participants={"participant": participant})

    async def add_track(track) -> None:
        attached.append(track.sid)

    manager._add_remote_track = add_track

    await manager._attach_existing_tracks()

    assert attached == ["audible"]


def test_output_mixes_tracks_without_waiting_for_a_quiet_track() -> None:
    loop = asyncio.new_event_loop()
    try:
        player = _RealtimeOutputPlayer(loop=loop, get_volume=lambda: 1.0)
        audible = _BoundedPcmBuffer(lambda: 1.0, max_bytes=8, frame_bytes=4)
        quiet = _BoundedPcmBuffer(lambda: 1.0, max_bytes=8, frame_bytes=4)
        audible.extend(_pcm_samples(1_234, -4_321, 2_345, -5_432))
        _set_output_buffers(player, quiet, audible)
        outdata = bytearray(8)

        player._output_callback(
            outdata,
            frame_count=2,
            time_info=SimpleNamespace(outputBufferDacTime=0.0, currentTime=0.0),
            status=None,
        )

        assert bytes(outdata) == _pcm_samples(1_234, -4_321, 2_345, -5_432)
    finally:
        loop.close()


def test_output_mix_clips_overlapping_stereo_tracks() -> None:
    loop = asyncio.new_event_loop()
    try:
        player = _RealtimeOutputPlayer(loop=loop, get_volume=lambda: 1.0)
        first = _BoundedPcmBuffer(lambda: 1.0, max_bytes=4, frame_bytes=4)
        second = _BoundedPcmBuffer(lambda: 1.0, max_bytes=4, frame_bytes=4)
        first.extend(_pcm_samples(20_000, -20_000))
        second.extend(_pcm_samples(20_000, -20_000))
        _set_output_buffers(player, first, second)
        outdata = bytearray(4)

        player._output_callback(
            outdata,
            frame_count=1,
            time_info=SimpleNamespace(outputBufferDacTime=0.0, currentTime=0.0),
            status=None,
        )

        assert _unpack_samples(outdata) == (32_767, -32_768)
    finally:
        loop.close()


@pytest.mark.asyncio
async def test_output_start_and_close_release_device(monkeypatch) -> None:
    events: list[str] = []

    class OutputStream:
        def start(self) -> None:
            events.append("start_device")

        def abort(self) -> None:
            events.append("abort_device")

        def close(self) -> None:
            events.append("close_device")

    monkeypatch.setattr(
        voice_manager.sd,
        "RawOutputStream",
        lambda **kwargs: OutputStream(),
    )
    monkeypatch.setattr(
        voice_manager.rtc,
        "AudioMixer",
        lambda **kwargs: pytest.fail("desktop playback must not use timeout mixing"),
    )
    player = _RealtimeOutputPlayer(
        loop=asyncio.get_running_loop(),
        get_volume=lambda: 1.0,
    )

    await player.start()
    await player.aclose()

    assert events == [
        "start_device",
        "abort_device",
        "close_device",
    ]
    assert player.output_stream is None
    assert player.track_streams == {}


@pytest.mark.asyncio
async def test_microphone_callback_burst_drops_stale_frames_without_queue_errors(
    monkeypatch,
) -> None:
    created: dict = {}
    captured_frames = []
    processed_frames = []

    class AudioSource:
        def __init__(self, *args, **kwargs) -> None:
            created["source_options"] = (args, kwargs)

        async def capture_frame(self, frame) -> None:
            captured_frames.append(frame)

        async def aclose(self) -> None:
            pass

    class AudioProcessingModule:
        def __init__(self, **kwargs) -> None:
            created["apm_options"] = kwargs

        def set_stream_delay_ms(self, delay: int) -> None:
            created["stream_delay"] = delay

        def process_stream(self, frame) -> None:
            processed_frames.append(frame)

    class AudioFrame:
        def __init__(
            self,
            data,
            sample_rate,
            num_channels,
            samples_per_channel,
        ) -> None:
            self.data = data
            self.sample_rate = sample_rate
            self.num_channels = num_channels
            self.samples_per_channel = samples_per_channel

    class InputStream:
        def __init__(self, **kwargs) -> None:
            created["input_options"] = kwargs

        def start(self) -> None:
            created["input_started"] = True

        def stop(self) -> None:
            created["input_stopped"] = True

        def close(self) -> None:
            created["input_closed"] = True

    monkeypatch.setattr(
        voice_manager,
        "rtc",
        SimpleNamespace(
            AudioSource=AudioSource,
            AudioProcessingModule=AudioProcessingModule,
            AudioFrame=AudioFrame,
        ),
    )
    monkeypatch.setattr(
        voice_manager,
        "sd",
        SimpleNamespace(InputStream=InputStream),
    )
    loop = asyncio.get_running_loop()
    loop_errors = []
    previous_exception_handler = loop.get_exception_handler()
    loop.set_exception_handler(lambda active_loop, context: loop_errors.append(context))
    capture = await voice_manager._open_input_capture(loop=loop, input_device=7)
    callback = created["input_options"]["callback"]
    time_info = SimpleNamespace(currentTime=0.02, inputBufferAdcTime=0.0)
    try:
        def produce_burst() -> None:
            for value in range(50):
                callback(
                    voice_manager.np.full(
                        (VOICE_IO_BLOCK_FRAMES, 1),
                        value,
                        dtype=voice_manager.np.int16,
                    ),
                    VOICE_IO_BLOCK_FRAMES,
                    time_info,
                    None,
                )

        producer = threading.Thread(target=produce_burst)
        producer.start()
        producer.join(timeout=1.0)
        assert not producer.is_alive()

        assert capture.frames.dropped_frames == 80
        for _ in range(50):
            if len(captured_frames) == VOICE_INPUT_QUEUE_FRAMES:
                break
            await asyncio.sleep(0)

        assert loop_errors == []
        assert len(captured_frames) == VOICE_INPUT_QUEUE_FRAMES
        assert len(processed_frames) == VOICE_INPUT_QUEUE_FRAMES
        assert _unpack_samples(captured_frames[0].data)[0] == 40
        assert _unpack_samples(captured_frames[-1].data)[0] == 49
        assert created["source_options"][1]["queue_size_ms"] == 200
        assert created["apm_options"] == {
            "echo_cancellation": True,
            "noise_suppression": True,
            "high_pass_filter": True,
            "auto_gain_control": True,
        }
        assert created["input_options"]["channels"] == 1
        assert created["input_options"]["blocksize"] == VOICE_IO_BLOCK_FRAMES
        assert created["input_options"]["device"] == 7
    finally:
        await capture.aclose()
        loop.set_exception_handler(previous_exception_handler)

    assert created["input_started"] is True
    assert created["input_stopped"] is True
    assert created["input_closed"] is True


@pytest.mark.asyncio
async def test_microphone_capture_shutdown_is_bounded(monkeypatch) -> None:
    events: list[str] = []

    class InputStream:
        def stop(self) -> None:
            events.append("stop")

        def close(self) -> None:
            events.append("close")

    async def stalled_pump() -> None:
        await asyncio.Event().wait()

    monkeypatch.setattr(voice_manager, "VOICE_MIC_DRAIN_TIMEOUT_MS", 1)
    frames = voice_manager._BoundedInputFrameBuffer(
        asyncio.get_running_loop(),
        capacity=1,
    )
    frames.put(
        voice_manager._CapturedInputFrame(
            pcm=_pcm_samples(1),
            input_delay=0.0,
            captured_at=0.0,
        )
    )
    task = asyncio.create_task(stalled_pump())
    capture = voice_manager._RealtimeInputCapture(
        source=object(),
        input_stream=InputStream(),
        task=task,
        frames=frames,
        apm=object(),
        delay_estimator=voice_manager._AudioDelayEstimator(),
    )

    await capture.aclose()

    assert events == ["stop", "close"]
    assert task.cancelled()
    assert await frames.get() is None


@pytest.mark.asyncio
async def test_microphone_buffer_cannot_lose_a_wakeup_during_empty_check() -> None:
    loop = asyncio.get_running_loop()
    frames = voice_manager._BoundedInputFrameBuffer(loop, capacity=1)
    captured = voice_manager._CapturedInputFrame(
        pcm=_pcm_samples(1),
        input_delay=0.0,
        captured_at=0.0,
    )

    class RacingEvent:
        def __init__(self) -> None:
            self.injected = False
            self.wait_calls = 0

        def clear(self) -> None:
            if not self.injected:
                self.injected = True
                frames.put(captured)
                frames._wake()

        def set(self) -> None:
            pass

        async def wait(self) -> None:
            self.wait_calls += 1

    event = RacingEvent()
    frames._event = event

    assert await frames.get() is captured
    assert event.wait_calls == 0


@pytest.mark.asyncio
async def test_microphone_open_failure_closes_partial_resources(monkeypatch) -> None:
    events: list[str] = []

    class AudioSource:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def aclose(self) -> None:
            events.append("source_close")

    class AudioProcessingModule:
        def __init__(self, **kwargs) -> None:
            pass

    class InputStream:
        def __init__(self, **kwargs) -> None:
            pass

        def start(self) -> None:
            events.append("start")
            raise RuntimeError("device failed")

        def close(self) -> None:
            events.append("stream_close")

    monkeypatch.setattr(
        voice_manager,
        "rtc",
        SimpleNamespace(
            AudioSource=AudioSource,
            AudioProcessingModule=AudioProcessingModule,
        ),
    )
    monkeypatch.setattr(
        voice_manager,
        "sd",
        SimpleNamespace(InputStream=InputStream),
    )

    with pytest.raises(RuntimeError, match="device failed"):
        await voice_manager._open_input_capture(
            loop=asyncio.get_running_loop(),
            input_device=None,
        )

    assert events == ["start", "stream_close", "source_close"]


@pytest.mark.asyncio
async def test_microphone_processing_is_confined_to_mono_input(monkeypatch) -> None:
    created: dict = {}
    capture = SimpleNamespace(
        source=object(),
        apm=object(),
        delay_estimator=object(),
        processing_lock=threading.Lock(),
    )

    async def open_input_capture(**kwargs):
        created["capture_options"] = kwargs
        return capture

    monkeypatch.setattr(voice_manager, "_open_input_capture", open_input_capture)

    class LocalAudioTrack:
        @staticmethod
        def create_audio_track(name, source):
            return SimpleNamespace(name=name, source=source)

    class TrackPublishOptions:
        source = None

    fake_rtc = SimpleNamespace(
        LocalAudioTrack=LocalAudioTrack,
        TrackPublishOptions=TrackPublishOptions,
        TrackSource=SimpleNamespace(SOURCE_MICROPHONE="microphone"),
    )
    monkeypatch.setattr(voice_manager, "rtc", fake_rtc)

    class Participant:
        async def publish_track(self, track, options):
            created["track"] = track
            created["publish_options"] = options
            return SimpleNamespace(sid="published")

    class OutputPlayer:
        def set_echo_processor(self, apm, delay_estimator, processing_lock) -> None:
            created["echo_processor"] = (apm, delay_estimator, processing_lock)

    manager = VoiceManager.__new__(VoiceManager)
    manager.loop = asyncio.get_running_loop()
    manager.room = SimpleNamespace(local_participant=Participant())
    manager.connected = True
    manager._mic_busy = False
    manager.mic_enabled = False
    manager.input_capture = None
    manager.local_track = None
    manager.local_publication = None
    manager.output_player = OutputPlayer()
    manager.on_mic_state = lambda enabled: None
    manager.on_status = lambda key, speak: None

    await manager._set_microphone_enabled(True, input_device=7)

    assert created["capture_options"] == {
        "loop": manager.loop,
        "input_device": 7,
    }
    assert created["echo_processor"] == (
        capture.apm,
        capture.delay_estimator,
        capture.processing_lock,
    )
    assert manager.mic_enabled is True


@pytest.mark.asyncio
async def test_microphone_cleanup_drains_queued_audio_before_unpublishing() -> None:
    events: list[str] = []

    class Source:
        def clear_queue(self) -> None:
            events.append("clear_queue")

        async def wait_for_playout(self) -> None:
            events.append("wait_for_playout")

        async def aclose(self) -> None:
            events.append("source_close")

    source = Source()

    class Capture:
        apm = object()
        delay_estimator = object()
        processing_lock = threading.Lock()

        def __init__(self) -> None:
            self.source = source

        async def aclose(self) -> None:
            events.append("capture_close")

    capture = Capture()

    class Participant:
        async def unpublish_track(self, sid: str) -> None:
            assert sid == "mic-track"
            events.append("unpublish")

    class OutputPlayer:
        def __init__(self) -> None:
            self.apm = capture.apm
            self.delay_estimator = capture.delay_estimator

        def clear_echo_processor(self, apm, delay_estimator, processing_lock) -> None:
            if self.apm is apm:
                self.apm = None
            if self.delay_estimator is delay_estimator:
                self.delay_estimator = None

    mic_states: list[bool] = []
    manager = VoiceManager.__new__(VoiceManager)
    manager.input_capture = capture
    manager.local_publication = SimpleNamespace(sid="mic-track")
    manager.local_track = object()
    manager.output_player = OutputPlayer()
    manager.room = SimpleNamespace(local_participant=Participant())
    manager.mic_enabled = True
    manager.on_mic_state = mic_states.append

    await manager._disable_microphone()

    assert events == [
        "capture_close",
        "wait_for_playout",
        "unpublish",
        "clear_queue",
        "source_close",
    ]
    assert manager.input_capture is None
    assert manager.local_publication is None
    assert manager.local_track is None
    assert manager.output_player.apm is None
    assert manager.output_player.delay_estimator is None
    assert manager.mic_enabled is False
    assert mic_states == [False]


@pytest.mark.asyncio
async def test_microphone_tail_drain_is_bounded_when_playout_stalls(monkeypatch) -> None:
    events: list[str] = []

    class Source:
        async def wait_for_playout(self) -> None:
            events.append("wait_started")
            await asyncio.Event().wait()

        def clear_queue(self) -> None:
            events.append("clear_queue")

        async def aclose(self) -> None:
            events.append("source_close")

    source = Source()

    class Capture:
        apm = None
        delay_estimator = None

        def __init__(self) -> None:
            self.source = source

        async def aclose(self) -> None:
            events.append("capture_close")

    class Participant:
        async def unpublish_track(self, sid: str) -> None:
            events.append("unpublish")

    monkeypatch.setattr(voice_manager, "VOICE_MIC_DRAIN_TIMEOUT_MS", 1)
    manager = VoiceManager.__new__(VoiceManager)
    manager.input_capture = Capture()
    manager.local_publication = SimpleNamespace(sid="mic-track")
    manager.local_track = object()
    manager.output_player = None
    manager.room = SimpleNamespace(local_participant=Participant())
    manager.mic_enabled = True
    manager.on_mic_state = lambda enabled: None

    await manager._disable_microphone()

    assert events == [
        "capture_close",
        "wait_started",
        "unpublish",
        "clear_queue",
        "source_close",
    ]


@pytest.mark.asyncio
async def test_leave_disconnects_transport_before_closing_output() -> None:
    events: list[str] = []

    class OutputPlayer:
        def clear_buffer(self) -> None:
            events.append("clear_output")

        async def aclose(self) -> None:
            events.append("close_output")

    class Room:
        async def disconnect(self) -> None:
            events.append("disconnect")

    statuses: list[tuple[str, bool]] = []
    manager = VoiceManager.__new__(VoiceManager)
    manager.input_capture = None
    manager.local_publication = None
    manager.local_track = None
    manager.output_player = OutputPlayer()
    manager.room = Room()
    manager.connected = True
    manager.mic_enabled = False
    manager._local_disconnect_requested = False
    manager.on_mic_state = lambda enabled: None
    manager.on_state = lambda state: None
    manager.on_status = lambda key, speak: statuses.append((key, speak))

    await manager._leave(notify=True)

    assert events == ["clear_output", "disconnect", "close_output"]
    assert manager.output_player is None
    assert manager.room is None
    assert statuses == [("voice-chat-left", True)]


@pytest.mark.asyncio
async def test_voice_lifecycle_operations_do_not_overlap() -> None:
    manager = VoiceManager.__new__(VoiceManager)
    manager._lifecycle_lock = asyncio.Lock()
    first_started = asyncio.Event()
    release_first = asyncio.Event()
    events: list[str] = []

    async def first() -> None:
        events.append("first_start")
        first_started.set()
        await release_first.wait()
        events.append("first_end")

    async def second() -> None:
        events.append("second")

    first_task = asyncio.create_task(manager._run_operation(first))
    await first_started.wait()
    second_task = asyncio.create_task(manager._run_operation(second))
    await asyncio.sleep(0)

    assert events == ["first_start"]

    release_first.set()
    await asyncio.gather(first_task, second_task)

    assert events == ["first_start", "first_end", "second"]
