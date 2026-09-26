from __future__ import annotations

import hashlib
from pathlib import Path

from client.typing_sounds import TYPING_EXACT_ASSETS, TYPING_SOUND_FAMILY
from server.core.server import SOUNDS_VERSION
from server.moderation.reports import MODERATION_REPORT_NOTIFICATION_SOUND


ROOT = Path(__file__).resolve().parents[2]
SOUND_PACKS = ("client", "web_client", "mobile_client")
TYPING_VARIANT_COUNT = 15


def _sound_path(pack: str, asset: str) -> Path:
    return ROOT / pack / "sounds" / asset


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_sound_pack_versions_are_synchronized() -> None:
    versions = {
        _sound_path(pack, "version.txt").read_text(encoding="utf-8").strip()
        for pack in SOUND_PACKS
    }
    assert versions == {SOUNDS_VERSION}


def test_typing_feedback_assets_are_complete_and_identical_across_clients() -> None:
    variants = tuple(
        f"{TYPING_SOUND_FAMILY}{index}.ogg"
        for index in range(1, TYPING_VARIANT_COUNT + 1)
    )
    assets = (*variants, *TYPING_EXACT_ASSETS)

    for asset in assets:
        paths = tuple(_sound_path(pack, asset) for pack in SOUND_PACKS)
        assert all(path.is_file() for path in paths), asset
        assert all(path.read_bytes().startswith(b"OggS") for path in paths), asset
        assert len({_sha256(path) for path in paths}) == 1, asset

    for pack in SOUND_PACKS:
        discovered = {
            path.name
            for path in (ROOT / pack / "sounds").glob(
                f"{TYPING_SOUND_FAMILY}[0-9]*.ogg"
            )
        }
        assert discovered == set(variants)


def test_moderation_report_sound_is_valid_and_identical_across_clients() -> None:
    paths = tuple(
        _sound_path(pack, MODERATION_REPORT_NOTIFICATION_SOUND)
        for pack in SOUND_PACKS
    )
    assert all(path.is_file() for path in paths)
    assert all(path.read_bytes().startswith(b"OggS") for path in paths)
    assert len({_sha256(path) for path in paths}) == 1
