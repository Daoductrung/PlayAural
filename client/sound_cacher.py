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
             # Check if it's "already initialized" (BASS_ERROR_ALREADY = 14)
             # sound_lib raises BassError. logic: if str(e) contains "14" or similar
             error_str = str(e)
             if "14" in error_str or "already initialized" in error_str:
                 import logging
                 logging.getLogger("playaural").info("SoundCacher: BASS already initialized, proceeding.")
                 # If already initialized, we don't need to do anything, 
                 # BUT we might need an Output object? 
                 # sound_lib.output.Output() calls BASS_Init. 
                 # If we can't create it, we might be fine if BASS is already live.
                 pass
             else:
                 import logging
                 logging.getLogger("playaural").error(f"Failed to initialize sound_lib Output: {e}")
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
        self.clean()
        self.refs.append(sound)
        return sound

    def clean(self):
        for sound in self.refs[:]:
            if not sound.is_playing:
                self.refs.remove(sound)
