"""Shared table-voice settings contract and validation."""

from __future__ import annotations

from typing import Any


VOICE_SETTINGS_PROTOCOL_VERSION = 1
VOICE_PERSONAL_VOLUME_MIN = 10
VOICE_PERSONAL_VOLUME_MAX = 100
VOICE_PERSONAL_VOLUME_STEP = 10
VOICE_PERSONAL_VOLUME_DEFAULT = 100
MAX_VOICE_SETTINGS_IDENTITIES = 256
MAX_VOICE_IDENTITY_LENGTH = 128


def normalize_voice_identity(value: Any) -> str:
    """Return one bounded provider/account identity or an empty value."""
    if not isinstance(value, str):
        return ""
    identity = value.strip()
    if not identity or len(identity) > MAX_VOICE_IDENTITY_LENGTH:
        return ""
    return identity


def normalize_personal_voice_volume(value: Any) -> int | None:
    """Validate one percentage from the protocol's discrete volume scale."""
    if type(value) is not int:
        return None
    if not VOICE_PERSONAL_VOLUME_MIN <= value <= VOICE_PERSONAL_VOLUME_MAX:
        return None
    if (value - VOICE_PERSONAL_VOLUME_MIN) % VOICE_PERSONAL_VOLUME_STEP:
        return None
    return value


def personal_voice_volume_choices() -> range:
    """Return every supported percentage in display order."""
    return range(
        VOICE_PERSONAL_VOLUME_MIN,
        VOICE_PERSONAL_VOLUME_MAX + 1,
        VOICE_PERSONAL_VOLUME_STEP,
    )


def validate_voice_settings_snapshot(payload: Any) -> dict[str, Any] | None:
    """Validate an untrusted server snapshot for client-facing conformance tests.

    First-party clients implement this same small versioned boundary in their
    native language. Keeping the canonical rules here gives server tests one
    authoritative packet validator without coupling clients to Python.
    """
    if not isinstance(payload, dict):
        return None
    if set(payload) != {
        "type",
        "version",
        "context_id",
        "host_muted",
        "participants",
    }:
        return None
    if payload.get("type") != "voice_settings":
        return None
    if payload.get("version") != VOICE_SETTINGS_PROTOCOL_VERSION:
        return None
    raw_context_id = payload.get("context_id")
    context_id = normalize_voice_identity(raw_context_id)
    if (
        not context_id
        or context_id != raw_context_id
        or type(payload.get("host_muted")) is not bool
    ):
        return None
    entries = payload.get("participants")
    if not isinstance(entries, list) or len(entries) > MAX_VOICE_SETTINGS_IDENTITIES:
        return None

    normalized_entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {
            "participant_id",
            "volume",
            "muted",
        }:
            return None
        raw_participant_id = entry.get("participant_id")
        participant_id = normalize_voice_identity(raw_participant_id)
        volume = normalize_personal_voice_volume(entry.get("volume"))
        muted = entry.get("muted")
        if (
            not participant_id
            or participant_id != raw_participant_id
            or participant_id in seen
            or volume is None
            or type(muted) is not bool
        ):
            return None
        seen.add(participant_id)
        normalized_entries.append(
            {
                "participant_id": participant_id,
                "volume": volume,
                "muted": muted,
            }
        )

    return {
        "type": "voice_settings",
        "version": VOICE_SETTINGS_PROTOCOL_VERSION,
        "context_id": context_id,
        "host_muted": payload["host_muted"],
        "participants": normalized_entries,
    }
