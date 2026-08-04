import asyncio
import struct
import threading
from types import SimpleNamespace

import pytest
import voice_manager

from voice_manager import (
    VOICE_INPUT_QUEUE_FRAMES,
    VOICE_IO_BLOCK_FRAMES,
    VOICE_MIXER_QUEUE_FRAMES,
    VOICE_PREFERRED_OUTPUT_CHANNELS,
    VOICE_REMOTE_STREAM_QUEUE_FRAMES,
    _BoundedPcmBuffer,
    _RealtimeOutputPlayer,
    _downmix_to_mono,
    VoiceManager,
)


def _pcm_samples(*values: int) -> bytes:
    return struct.pack(f"<{len(values)}h", *values)


def _unpack_samples(data: bytes) -> tuple[int, ...]:
    return struct.unpack(f"<{len(data) // 2}h", data)


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
    assert VOICE_MIXER_QUEUE_FRAMES == 10
    assert _RealtimeOutputPlayer._buffer_size(1) == 24_000
    assert _RealtimeOutputPlayer._buffer_size(2) == 48_000


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
        player.buffer.extend(stereo)
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


def test_echo_cancellation_receives_mono_copy_in_ten_ms_frames() -> None:
    class APM:
        def __init__(self) -> None:
            self.frames = []

        def process_reverse_stream(self, frame) -> None:
            self.frames.append(frame)

    loop = asyncio.new_event_loop()
    try:
        player = _RealtimeOutputPlayer(loop=loop, get_volume=lambda: 1.0)
        apm = APM()
        player.apm = apm
        stereo_frame = _pcm_samples(3_000, 1_000)
        stereo = stereo_frame * VOICE_IO_BLOCK_FRAMES
        player.buffer.extend(stereo)
        outdata = bytearray(len(stereo))

        player._output_callback(
            outdata,
            frame_count=VOICE_IO_BLOCK_FRAMES,
            time_info=SimpleNamespace(outputBufferDacTime=0.02, currentTime=0.0),
            status=None,
        )

        assert bytes(outdata) == stereo
        assert len(apm.frames) == 2
        assert all(frame.num_channels == 1 for frame in apm.frames)
        assert all(frame.samples_per_channel == 480 for frame in apm.frames)
        assert _unpack_samples(apm.frames[0].data.tobytes()) == (2_000,) * 480
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
        async def __anext__(self):
            raise StopAsyncIteration

        async def aclose(self) -> None:
            pass

    def make_stream(track, **kwargs):
        captured.update(kwargs)
        return Stream()

    class Mixer:
        def add_stream(self, iterator) -> None:
            captured["iterator"] = iterator

    monkeypatch.setattr(voice_manager.rtc, "AudioStream", make_stream)
    player = _RealtimeOutputPlayer(
        loop=asyncio.get_running_loop(),
        get_volume=lambda: 1.0,
    )
    player.running = True
    player.mixer = Mixer()

    await player.add_track(SimpleNamespace(sid="stereo-track"))

    assert captured["sample_rate"] == 48_000
    assert captured["num_channels"] == 2
    assert captured["frame_size_ms"] == 20
    assert captured["capacity"] == VOICE_REMOTE_STREAM_QUEUE_FRAMES
    assert captured["noise_cancellation"] is None


@pytest.mark.asyncio
async def test_livekit_mixer_preserves_single_track_stereo_samples() -> None:
    stereo = _pcm_samples(1_234, -4_321) * VOICE_IO_BLOCK_FRAMES
    frame = voice_manager.rtc.AudioFrame(
        stereo,
        48_000,
        2,
        VOICE_IO_BLOCK_FRAMES,
    )

    class Frames:
        def __init__(self) -> None:
            self.sent = False

        async def __anext__(self):
            if self.sent:
                raise StopAsyncIteration
            self.sent = True
            return frame

    mixer = voice_manager.rtc.AudioMixer(
        sample_rate=48_000,
        num_channels=2,
        blocksize=VOICE_IO_BLOCK_FRAMES,
        capacity=1,
    )
    mixer.add_stream(Frames())
    try:
        mixed = await asyncio.wait_for(mixer.__anext__(), timeout=1.0)
        assert mixed.num_channels == 2
        assert mixed.data.tobytes() == stereo
    finally:
        await mixer.aclose()


@pytest.mark.asyncio
async def test_output_start_and_close_release_device_and_mixer(monkeypatch) -> None:
    events: list[str] = []

    class OutputStream:
        def start(self) -> None:
            events.append("start_device")

        def abort(self) -> None:
            events.append("abort_device")

        def close(self) -> None:
            events.append("close_device")

    class Mixer:
        def __aiter__(self):
            return self

        async def __anext__(self):
            await asyncio.Event().wait()

        async def aclose(self) -> None:
            events.append("close_mixer")

    monkeypatch.setattr(
        voice_manager.sd,
        "RawOutputStream",
        lambda **kwargs: OutputStream(),
    )
    monkeypatch.setattr(
        voice_manager.rtc,
        "AudioMixer",
        lambda **kwargs: Mixer(),
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
        "close_mixer",
    ]
    assert player.output_stream is None
    assert player.mixer is None
    assert player.play_task is None


@pytest.mark.asyncio
async def test_microphone_processing_is_confined_to_mono_input(monkeypatch) -> None:
    created: dict = {}
    capture = SimpleNamespace(
        source=object(),
        apm=object(),
        delay_estimator=object(),
    )

    class MediaDevices:
        def __init__(self, **kwargs) -> None:
            created["device_options"] = kwargs

        def open_input(self, **kwargs):
            created["input_options"] = kwargs
            return capture

    class LocalAudioTrack:
        @staticmethod
        def create_audio_track(name, source):
            return SimpleNamespace(name=name, source=source)

    class TrackPublishOptions:
        source = None

    fake_rtc = SimpleNamespace(
        MediaDevices=MediaDevices,
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
        def set_echo_processor(self, apm, delay_estimator) -> None:
            created["echo_processor"] = (apm, delay_estimator)

    manager = VoiceManager.__new__(VoiceManager)
    manager.loop = asyncio.get_running_loop()
    manager.room = SimpleNamespace(local_participant=Participant())
    manager.connected = True
    manager._mic_busy = False
    manager.mic_enabled = False
    manager.input_devices = None
    manager.input_capture = None
    manager.local_track = None
    manager.local_publication = None
    manager.output_player = OutputPlayer()
    manager.on_mic_state = lambda enabled: None
    manager.on_status = lambda key, speak: None

    await manager._set_microphone_enabled(True, input_device=7)

    assert created["device_options"]["num_channels"] == 1
    assert created["input_options"] == {
        "input_device": 7,
        "enable_aec": True,
        "noise_suppression": True,
        "high_pass_filter": True,
        "auto_gain_control": True,
        "queue_capacity": VOICE_INPUT_QUEUE_FRAMES,
    }
    assert created["echo_processor"] == (capture.apm, capture.delay_estimator)
    assert manager.mic_enabled is True


@pytest.mark.asyncio
async def test_microphone_cleanup_discards_queued_audio_before_unpublishing() -> None:
    events: list[str] = []

    class Source:
        def clear_queue(self) -> None:
            events.append("clear_queue")

        async def aclose(self) -> None:
            events.append("source_close")

    source = Source()

    class Capture:
        apm = object()
        delay_estimator = object()

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

        def clear_echo_processor(self, apm, delay_estimator) -> None:
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

    assert events == ["clear_queue", "capture_close", "unpublish", "source_close"]
    assert manager.input_capture is None
    assert manager.local_publication is None
    assert manager.local_track is None
    assert manager.output_player.apm is None
    assert manager.output_player.delay_estimator is None
    assert manager.mic_enabled is False
    assert mic_states == [False]


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
    manager.input_devices = object()
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
