# Third-party software notices

PlayAural-authored source code is distributed under the GNU General Public
License, version 2 only. See [LICENSE](LICENSE). That grant does not cover or
relicense third-party software, audio, or other assets. Each third-party work
remains under its own license or permission.

This file identifies the direct libraries used by the first-party components
and the complete notices for source or binary artifacts that are checked into
this repository. The lockfiles are the authoritative inventory of exact and
transitive package versions:

- Python desktop: [client/uv.lock](client/uv.lock)
- Python server: [server/uv.lock](server/uv.lock)
- Rust/Cosmos: [cosmos/Cargo.lock](cosmos/Cargo.lock)
- Web: [web_client/package-lock.json](web_client/package-lock.json)
- Mobile: [mobile_client/package-lock.json](mobile_client/package-lock.json)

Release builders must retain the license and notice files supplied by resolved
transitive packages. When a dependency or lockfile changes, its licensing must
be reviewed before publishing the resulting source or binary distribution.
Every resolved Web and mobile npm package currently declares its license in the
corresponding lockfile; repository tests fail if that metadata is omitted.

## Compatibility and distribution warning

This file is an inventory, not a legal opinion or a declaration that every
possible binary combination is license-compatible. In particular, the Apache
Software Foundation and the Free Software Foundation state that Apache-2.0 is
compatible with GPLv3 but not GPLv2 for a combined derivative work. PlayAural
is GPL-2.0-only and uses Apache-2.0 components, including Steam Audio and
LiveKit. Before publishing a combined application binary, distributors must
determine whether their specific packaging creates a combined derivative work
and obtain qualified legal advice, an additional permission, or another valid
licensing solution where required.

References:

- [Apache License 2.0 and GPL compatibility](https://www.apache.org/licenses/GPL-compatibility)
- [GNU license compatibility and relicensing](https://www.gnu.org/licenses/license-compatibility.html)

## Audio and other assets

The GPL-2.0-only grant for PlayAural-authored software does not automatically
cover sound files, music, artwork, game data, or other third-party assets in
the repository. No repository-wide, per-asset provenance and permission
inventory currently exists for the checked-in sound packs. A file's presence
in the repository must not be interpreted as a license grant beyond permission
recorded by its copyright holder. Maintainers must verify and document the
origin and redistribution rights of every asset before a public source or
binary release that includes it.

## Checked-in and binary-bundled software

| Software | Use | License and notices |
| --- | --- | --- |
| Cosmos | PlayAural's vendored Rust audio and accessibility library | MIT, preserving the license metadata in the original repository import; [cosmos/LICENSE](cosmos/LICENSE) |
| miniaudio 0.11.23 | Audio devices, decoding, mixing, and source graphs | Public domain or MIT No Attribution; [cosmos/miniaudio-sys/miniaudio/LICENSE](cosmos/miniaudio-sys/miniaudio/LICENSE) |
| stb_vorbis | Ogg Vorbis decoding embedded by miniaudio | MIT or public domain; [cosmos/miniaudio-sys/miniaudio/STB_LICENSE](cosmos/miniaudio-sys/miniaudio/STB_LICENSE) |
| Steam Audio 4.8.1 | HRTF binaural rendering on Windows, Android, and iOS | Apache-2.0; [license](cosmos/steamaudio-sys/phonon/LICENSE.md), [third-party notices](cosmos/steamaudio-sys/phonon/THIRDPARTY.md), [trademark terms](cosmos/steamaudio-sys/phonon/TRADEMARK_RIGHTS.md), and [pinned artifact manifest](cosmos/steamaudio-sys/phonon/UPSTREAM.json) |
| Expo Speech 55.0.17 | Reviewed Android lifecycle source used by the guarded mobile patch | MIT; [mobile_client/patches/expo-speech/LICENSE](mobile_client/patches/expo-speech/LICENSE) |
| LiveKit JavaScript client 2.18.2 UMD bundle | Browser table voice chat | Apache-2.0 plus bundled dependency licenses; [web_client/vendor/THIRD_PARTY_NOTICES.md](web_client/vendor/THIRD_PARTY_NOTICES.md) |
| stb-vorbis 0.0.6 | Lazy browser fallback for Ogg Vorbis decoding | Apache-2.0 wrapper with embedded MIT-or-public-domain stb_vorbis; [web client notices](web_client/vendor/THIRD_PARTY_NOTICES.md) |

Steam Audio is a Valve Corporation product. The Valve and Steam marks are not
licensed for endorsement or affiliation; the checked-in trademark terms govern
their descriptive use. Steam Audio's own third-party notice file covers the
libraries incorporated into its official binaries.

## Direct runtime dependencies

The names below match the component manifests. Exact resolved versions are in
the lockfiles listed above.

### Server

| Dependencies | License |
| --- | --- |
| argon2-cffi, OpenSkill | MIT |
| Babel, websockets | BSD-3-Clause |
| Fluent Runtime, Mashumaro | Apache-2.0 |

### Desktop client

| Dependencies | License |
| --- | --- |
| Accessible Output 2, keyring, python-sounddevice | MIT |
| Fluent Runtime, LiveKit Python SDK, Requests | Apache-2.0 |
| psutil, websockets | BSD-3-Clause |
| NumPy | BSD-3-Clause with additional licenses for bundled components; retain the notices shipped by the resolved wheel |
| wxPython | wxWindows Library Licence |

### Web client

| Dependency | License |
| --- | --- |
| LiveKit JavaScript client | Apache-2.0 |
| stb-vorbis wrapper | Apache-2.0; embedded stb_vorbis is MIT or public domain |

### Mobile client

| Dependencies | License |
| --- | --- |
| Expo and the direct Expo modules, React, React DOM, React Native, React Native Web, React Native Async Storage, React Native Safe Area Context, React Native WebRTC and its Expo config plugin, RN Foreground Service | MIT |
| LiveKit client, LiveKit React Native, LiveKit React Native Expo plugin | Apache-2.0 |

The mobile lockfile maps all resolved packages to their license expressions.
Those expressions currently include 0BSD, Apache-2.0, BSD-2-Clause,
BSD-3-Clause, BlueOak-1.0.0, CC-BY-4.0, CC0-1.0, ISC, MIT, MPL-2.0,
Python-2.0, Unlicense, Apache-2.0 AND BSD-3-Clause, BSD-3-Clause OR
GPL-2.0, MIT OR Apache-2.0, and MIT OR CC0-1.0.

### Cosmos build and runtime crates

| Dependencies | License |
| --- | --- |
| cc, PyO3, thiserror, windows-sys | MIT or Apache-2.0 |
| bindgen | BSD-3-Clause |
| winit | Apache-2.0 |

## Development dependencies

pytest and pytest-xdist are MIT licensed; pytest-asyncio is Apache-2.0.
TypeScript is Apache-2.0, `@types/react` is MIT, and Babel Preset Expo is MIT.
PyInstaller is GPL-2.0-or-later with its documented exception for distributing
bundled applications. Platform SDKs and build tools are acquired separately
and remain under the terms supplied by Apple, Google, Microsoft, and their
respective licensors.
