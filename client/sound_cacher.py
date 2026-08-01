import ctypes
from collections import OrderedDict
import logging

from sound_lib import output, stream

MAX_CACHED_SOUNDS = 128
MAX_CACHED_SOUND_BYTES = 96 * 1024 * 1024


class SoundCacher:
    def __init__(self):
        self.cache = OrderedDict()
        self.refs = []  # so sound objects don't get eaten by the gc
        self.ref_files = {}
        self.pinned = set()
        try:
            self.output = output.Output()
        except Exception as e:
            error_text = str(e)
            if "14" in error_text or "already initialized" in error_text:
                logging.getLogger("playaural").info(
                    "SoundCacher: BASS was already initialized; reusing it."
                )
            else:
                logging.getLogger("playaural").error(
                    "Failed to initialize sound_lib output: %s", e
                )
                raise

    def create(
        self,
        file_name,
        pan=0.0,
        volume=1.0,
        pitch=1.0,
        looping=False,
        pinned=False,
    ):
        if file_name not in self.cache:
            with open(file_name, "rb") as f:
                self.cache[file_name] = ctypes.create_string_buffer(f.read())
        else:
            self.cache.move_to_end(file_name)
        sound = stream.FileStream(
            mem=True, file=self.cache[file_name], length=len(self.cache[file_name])
        )
        if pan:
            sound.pan = pan
        if volume != 1.0:
            sound.volume = volume
        if pitch != 1.0:
            sound.set_frequency(int(sound.get_frequency() * pitch))
        sound.looping = bool(looping)
        self.refs.append(sound)
        self.ref_files[id(sound)] = file_name
        if pinned:
            self.pinned.add(id(sound))
        self.clean()
        self._trim_cache()
        return sound

    def play(
        self,
        file_name,
        pan=0.0,
        volume=1.0,
        pitch=1.0,
        looping=False,
        pinned=False,
    ):
        sound = self.create(
            file_name,
            pan=pan,
            volume=volume,
            pitch=pitch,
            looping=looping,
            pinned=pinned,
        )
        sound.play()
        return sound

    def clean(self):
        for sound in self.refs[:]:
            if id(sound) not in self.pinned and not sound.is_playing:
                self.refs.remove(sound)
                self.ref_files.pop(id(sound), None)

    def pin(self, sound):
        self.pinned.add(id(sound))

    def unpin(self, sound):
        self.pinned.discard(id(sound))
        self.clean()
        self._trim_cache()

    def _trim_cache(self):
        active_files = set(self.ref_files.values())
        for file_name in list(self.cache):
            cache_bytes = sum(len(buffer) for buffer in self.cache.values())
            if (
                len(self.cache) <= MAX_CACHED_SOUNDS
                and cache_bytes <= MAX_CACHED_SOUND_BYTES
            ):
                break
            if file_name not in active_files:
                self.cache.pop(file_name, None)
