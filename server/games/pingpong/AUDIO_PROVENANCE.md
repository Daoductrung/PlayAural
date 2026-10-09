# Table Tennis audio provenance

All three shipped effects are excerpts of real table-tennis recordings from
Freesound. Their authors released them under Creative Commons CC0 1.0, which
permits copying, modification, and redistribution, including commercially.

| Shipped asset | Source recording | Author | License | Edits |
| --- | --- | --- | --- | --- |
| `paddle.ogg` | [Ping pong ball hit, sound 269718](https://freesound.org/s/269718/) | michorvath | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) | A 0.20-second impact excerpt beginning at 0.065 seconds; mixed to mono, gain and limiter applied, with a short 32 ms room reflection and fade. |
| `table.ogg` | [Ping pong impact the table.WAV, sound 418555](https://freesound.org/s/418555/) | 14FPanskaBubik_Lukas | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) | A table-bounce excerpt beginning at 1.99 seconds; mixed to mono with gain and limiting. A delayed reflection was removed so the shipped 0.16-second effect contains one impact followed by a short attenuated decay and fade. |
| `net.ogg` | [tabletennis_outdoors, sound 555202](https://freesound.org/s/555202/) | pillonoise | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) | A 0.48-second net-contact excerpt beginning at 33.40 seconds; mixed to mono, high-pass filtered at 120 Hz, and faded. |

The same encoded files are copied unchanged into the desktop, web, and mobile
sound trees. Spatial position and stereo pan are applied by the game at
runtime; the source effects themselves remain mono to avoid conflicting
direction cues.
