import ctypes
from sound_lib import output, stream

class SoundCacher:
    def __init__(self):
        self.cache = {}
        self.refs = []  # so sound objects don't get eaten by the gc
        # Initialize Output here, lazily
        try:
             # Store output reference to keep it alive
             self.output = output.Output()
        except Exception as e:
             import logging
             logging.getLogger("playaural").error(f"Failed to initialize sound_lib Output: {e}")
             # We might want to re-raise or handle graceful degradation
             # For an audio game, maybe re-raise?
             # But at least we can log it now.
             raise e

    def play(self, file_name, pan=0.0, volume=1.0, pitch=1.0):
        if file_name not in self.cache:
            with open(file_name, "rb") as f:
                self.cache[file_name] = ctypes.create_string_buffer(f.read())
        sound = stream.FileStream(
            mem=True, file=self.cache[file_name], length=len(self.cache[file_name])
        )
        if pan:
            sound.pan = pan
        if volume != 1.0:
            sound.volume = volume
        if pitch != 1.0:
            sound.set_frequency(int(sound.get_frequency() * pitch))
        sound.play()
        self.refs.append(sound)
        return sound
