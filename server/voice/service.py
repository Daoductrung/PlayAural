"""Voice room authorization service."""

from __future__ import annotations

from dataclasses import dataclass, field
import os
import re
from typing import Any

from .tokens import generate_livekit_token


SUPPORTED_PROVIDER = "livekit"
DEFAULT_TOKEN_TTL_SECONDS = 900
ROOM_COMPONENT_PATTERN = re.compile(r"[^A-Za-z0-9_.:-]+")


class VoiceAuthorizationError(Exception):
    """Raised when a voice room request cannot be authorized."""


@dataclass(frozen=True)
class VoiceContext:
    scope: str
    context_id: str
    room_label: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VoiceService:
    enabled: bool = False
    provider: str = SUPPORTED_PROVIDER
    public_url: str = ""
    api_key: str = ""
    api_secret: str = ""
    room_prefix: str = "playaural"
    token_ttl_seconds: int = DEFAULT_TOKEN_TTL_SECONDS

    @classmethod
    def from_env(cls) -> "VoiceService":
        enabled = os.environ.get("PLAYAURAL_VOICE_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}
        provider = os.environ.get("PLAYAURAL_VOICE_PROVIDER", SUPPORTED_PROVIDER).strip().lower() or SUPPORTED_PROVIDER
        public_url = os.environ.get("PLAYAURAL_VOICE_URL", "").strip()
        api_key = os.environ.get("PLAYAURAL_VOICE_API_KEY", "").strip()
        api_secret = os.environ.get("PLAYAURAL_VOICE_API_SECRET", "").strip()
        room_prefix = os.environ.get("PLAYAURAL_VOICE_ROOM_PREFIX", "playaural").strip() or "playaural"
        ttl_raw = os.environ.get("PLAYAURAL_VOICE_TOKEN_TTL_SECONDS", str(DEFAULT_TOKEN_TTL_SECONDS)).strip()
        try:
            token_ttl_seconds = max(60, min(86400, int(ttl_raw)))
        except ValueError:
            token_ttl_seconds = DEFAULT_TOKEN_TTL_SECONDS
        return cls(
            enabled=enabled,
            provider=provider,
            public_url=public_url,
            api_key=api_key,
            api_secret=api_secret,
            room_prefix=room_prefix,
            token_ttl_seconds=token_ttl_seconds,
        )

    def capability_packet(self) -> dict[str, Any]:
        return {
            "enabled": self.is_ready(),
            "provider": self.provider,
            "url": self.public_url if self.is_ready() else "",
            "token_ttl_seconds": self.token_ttl_seconds,
        }

    def is_ready(self) -> bool:
        return (
            self.enabled
            and self.provider == SUPPORTED_PROVIDER
            and bool(self.public_url)
            and bool(self.api_key)
            and bool(self.api_secret)
        )

    def build_room_name(self, context: VoiceContext) -> str:
        scope = self._safe_component(context.scope)
        context_id = self._safe_component(context.context_id)
        prefix = self._safe_component(self.room_prefix)
        if not scope or not context_id:
            raise VoiceAuthorizationError("voice-invalid-context")
        return f"{prefix}:{scope}:{context_id}"

    def create_join_packet(
        self,
        *,
        context: VoiceContext,
        identity: str,
        display_name: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.is_ready():
            raise VoiceAuthorizationError("voice-unavailable")
        room = self.build_room_name(context)
        token_metadata = dict(context.metadata)
        if metadata:
            token_metadata.update(metadata)
        token, expires_at = generate_livekit_token(
            api_key=self.api_key,
            api_secret=self.api_secret,
            identity=identity,
            name=display_name,
            room=room,
            ttl_seconds=self.token_ttl_seconds,
            metadata=token_metadata,
        )
        return {
            "type": "voice_join_info",
            "provider": self.provider,
            "scope": context.scope,
            "context_id": context.context_id,
            "url": self.public_url,
            "room": room,
            "room_label": context.room_label,
            "participant": {
                "identity": identity,
                "name": display_name,
            },
            "token": token,
            "expires_at": expires_at,
            "ice_servers": [],
        }

    def _safe_component(self, value: str) -> str:
        normalized = ROOM_COMPONENT_PATTERN.sub("_", value.strip())
        return normalized.strip("_")[:96]
