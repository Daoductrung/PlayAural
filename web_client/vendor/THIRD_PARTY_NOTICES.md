# LiveKit Web bundle notices

`livekit-client.umd.js` is the unmodified LiveKit JavaScript client 2.18.2 UMD
distribution (line endings may be normalized by Git). It is distributed under
Apache-2.0. The complete license is in
[`licenses/Apache-2.0.txt`](licenses/Apache-2.0.txt), and LiveKit's attribution
notice is in [`LIVEKIT_NOTICE`](LIVEKIT_NOTICE).

The bundle package and its resolved dependencies are listed below. Versions
match `../package-lock.json`; each project remains under its own license.

| Package | Version | License and notice |
| --- | --- | --- |
| `livekit-client` | 2.18.2 | [Apache-2.0](licenses/Apache-2.0.txt) and [attribution notice](LIVEKIT_NOTICE) |
| `@bufbuild/protobuf` | 1.10.1 | Apache-2.0 and BSD-3-Clause; [Apache](licenses/Apache-2.0.txt), [Google varint notice](licenses/buf-protobuf-BSD-3-Clause.txt) |
| `@livekit/mutex` | 1.1.1 | [Apache-2.0](licenses/Apache-2.0.txt) |
| `@livekit/protocol` | 1.44.0 | [Apache-2.0](licenses/Apache-2.0.txt) |
| `events` | 3.3.0 | [MIT](licenses/events-MIT.txt) |
| `jose` | 6.2.2 | [MIT](licenses/jose-MIT.txt) |
| `loglevel` | 1.9.2 | [MIT](licenses/loglevel-MIT.txt) |
| `rxjs` | 7.8.2 | [Apache-2.0](licenses/Apache-2.0.txt) |
| `sdp` | 3.2.2 | [MIT](licenses/sdp-MIT.txt) |
| `sdp-transform` | 2.15.0 | [MIT](licenses/sdp-transform-MIT.txt) |
| `tslib` | 2.8.1 | [0BSD](licenses/tslib-0BSD.txt) |
| `typed-emitter` | 2.1.0 | [MIT](licenses/typed-emitter-MIT.txt) |
| `webrtc-adapter` | 9.0.4 | [BSD-3-Clause](licenses/webrtc-adapter-BSD-3-Clause.txt) |

`@types/dom-mediacapture-record` is a type-only package used while building the
upstream client and is not executable code in the UMD bundle.

## Ogg Vorbis fallback

`stb-vorbis.js` is the unmodified `stb-vorbis` 0.0.6 ES module distribution.
It is loaded only when the browser cannot natively decode PlayAural's Ogg
Vorbis assets. The JavaScript/WebAssembly wrapper is distributed under
[Apache-2.0](licenses/Apache-2.0.txt). Its embedded `stb_vorbis` decoder is
available under the player's choice of the
[MIT license or public-domain dedication](licenses/stb_vorbis-MIT-or-Public-Domain.txt).

| Package | Version | License and notice |
| --- | --- | --- |
| `stb-vorbis` | 0.0.6 | [Apache-2.0](licenses/Apache-2.0.txt) wrapper; embedded [stb_vorbis terms](licenses/stb_vorbis-MIT-or-Public-Domain.txt) |
