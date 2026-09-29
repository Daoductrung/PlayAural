# Bingo audio provenance

Per-asset record for the eight sound files in `game_bingo/` (identical copies
in `client/sounds/`, `web_client/sounds/` and `mobile_client/sounds/`). The
source pages and license statements below come from the contributor's license
record (verified 27 September 2026) and from the contributor's own statements.
Where a detail was not recorded anywhere, the table says so instead of guessing.

Derivation for every replaced file: the contributor trimmed/edited the
downloaded source into the working file named below, and it was converted to
stereo Ogg Vorbis. The exact edit points inside each source were not recorded.

| Shipped file | Source title | Author / rightsholder | Source URL | License / terms | Working file (edit) |
| --- | --- | --- | --- | --- | --- |
| `call.ogg` | Bingo Spinner | deltaknightone (Freesound) | https://freesound.org/people/deltaknightone/sounds/634197/ | Creative Commons 0 (CC0). Original WAV, 9.079 s. | `Bolas de bingo.wav`, 3.374 s (shortened from the original) |
| `suspense.ogg` | 065391_drumroll.wav (drum roll) | "Freesound Community" (artist name shown on Pixabay) | https://pixabay.com/sound-effects/musical-065391-drumrollwav-88344/ | Pixabay Content License (https://pixabay.com/service/license-summary/). Original MP3, 6 s. | `Suspenso.mp3`, shortened to the shipped 2.083 s edit. |
| `cymbal.ogg` | 065391_drumroll.wav (the cymbal hit that ends the drum roll) | "Freesound Community" (artist name shown on Pixabay) | https://pixabay.com/sound-effects/musical-065391-drumrollwav-88344/ | Pixabay Content License. Same source file as `suspense.ogg`. | `Platillo.mp3`, the shipped 1.835 s edit cut by the contributor from the same drum-roll file (roll and cymbal are the two halves of one effect). |
| `win.ogg` | Victory Bell Success Fanfare | Emand_Edroff (Pixabay) | https://pixabay.com/sound-effects/musical-victory-bell-success-fanfare-576275/ | Pixabay Content License. Pixabay labels this file as AI generated. | Updated supplied edit of `Victoria.mp3`; shipped Ogg is 7.642 s. |
| `error.ogg` | Sad Trumpet | Universfield (Pixabay) | https://pixabay.com/sound-effects/film-special-effects-sad-trumpet-278822/ | Pixabay Content License. Original about 3 s. | `error.mp3`, 2.904 s |
| `daub.ogg` | 10 Click Sound Effects (one of the click variants) | CreatorAssets | https://creatorassets.com/audio/10-clicks | CC0 / public domain. | One click from the pack, used as is; kept, not replaced. |
| `undaub.ogg` | 10 Click Sound Effects (the same click as `daub.ogg`, reversed) | CreatorAssets | https://creatorassets.com/audio/10-clicks | CC0 / public domain. | The same click as `daub.ogg`, played in reverse; kept, not replaced. |
| `music.ogg` | Arcade Fun | The_Mountain (Pixabay) | https://pixabay.com/music/happy-childrens-tunes-arcade-fun-153642/ | Pixabay Content License. The source page labels the track as Content ID registered. | Converted to Ogg Vorbis (48 kHz stereo). |

## Replacing these sounds

These sound effects and the music may be replaced if different assets are
preferred. `call.ogg` and `suspense.ogg` set game timing; see "Timing
dependency" below.

## Terms to be aware of

- The Pixabay files are used under the Pixabay Content License, not CC0. The
  contributor's record states they are used as integrated game audio and not
  as a standalone redistribution of the sound files. Keep this record with the
  public repository and recheck the applicable terms before redistributing or
  replacing the assets.
- A Pixabay page shows the license currently offered for the file; the
  `suspense.ogg` source is credited on Pixabay to "Freesound Community", and
  no separate original Freesound license is assumed.
- Pixabay labels `music.ogg` as Content ID registered. That does not change the
  recorded license, but recordings or streams containing the music may receive
  an automated claim and should retain this source record for disputes.
- "10 Click Sound Effects" by CreatorAssets
  (https://creatorassets.com/audio/10-clicks, CC0) is the source of `daub.ogg`
  and, reversed, `undaub.ogg` -- not a separate interface-click asset.

## Timing dependency

`call.ogg` and `suspense.ogg` lengths drive game timing. `audio.py` measures
the shipped files, so replacing either needs no code change, but
`AUDIO_DURATIONS_TICKS` (the fallback used when a file cannot be read) must be
updated. `test_bingo_timed_audio_is_measured_from_the_shipped_assets` enforces
that requirement.
