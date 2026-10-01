"""Voice authorization package."""

from .service import VoiceAuthorizationError, VoiceContext, VoiceService
from .settings import (
    MAX_VOICE_SETTINGS_IDENTITIES,
    VOICE_PERSONAL_VOLUME_DEFAULT,
    VOICE_PERSONAL_VOLUME_MAX,
    VOICE_PERSONAL_VOLUME_MIN,
    VOICE_PERSONAL_VOLUME_STEP,
    VOICE_SETTINGS_PROTOCOL_VERSION,
    normalize_personal_voice_volume,
    normalize_voice_identity,
    personal_voice_volume_choices,
    validate_voice_settings_snapshot,
)

__all__ = [
    "MAX_VOICE_SETTINGS_IDENTITIES",
    "VOICE_PERSONAL_VOLUME_DEFAULT",
    "VOICE_PERSONAL_VOLUME_MAX",
    "VOICE_PERSONAL_VOLUME_MIN",
    "VOICE_PERSONAL_VOLUME_STEP",
    "VOICE_SETTINGS_PROTOCOL_VERSION",
    "VoiceAuthorizationError",
    "VoiceContext",
    "VoiceService",
    "normalize_personal_voice_volume",
    "normalize_voice_identity",
    "personal_voice_volume_choices",
    "validate_voice_settings_snapshot",
]
