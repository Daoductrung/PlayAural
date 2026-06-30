"""
Client-side localization system using Fluent.
"""

import logging
from pathlib import Path
from fluent.runtime import FluentBundle, FluentResource


LOGGER = logging.getLogger("playaural.localization")


class Localization:
    _bundle = None
    _locale = "en"
    _fallback_locale = "en"
    _locales_dir: Path | None = None
    _message_aliases = {
        "voice-unavailable": "voice-chat-unavailable",
    }

    @classmethod
    def init(cls, locales_dir: Path | None = None, locale: str = "en"):
        """Initialize the localization system."""
        if locales_dir is None:
            # Default to 'locales' next to this file
            locales_dir = Path(__file__).parent / "locales"

        cls._locales_dir = Path(locales_dir)
        cls.set_locale(locale)

    @classmethod
    def current_locale(cls) -> str:
        """Return the currently active client locale."""
        return cls._locale

    @classmethod
    def set_locale(cls, locale: str | None, locales_dir: Path | None = None) -> bool:
        """Switch the active locale and reload Fluent resources immediately."""
        if locales_dir is not None:
            cls._locales_dir = Path(locales_dir)
        if cls._locales_dir is None:
            cls._locales_dir = Path(__file__).parent / "locales"

        normalized_locale = str(locale or cls._fallback_locale).strip() or cls._fallback_locale
        changed = normalized_locale != cls._locale
        cls._locale = normalized_locale
        cls._load_bundle(cls._locales_dir)
        return changed

    @classmethod
    def _load_bundle(cls, locales_dir: Path):
        """Load Fluent bundle."""
        # Try target locale first, then fallback
        locales = [cls._locale]
        if cls._locale != cls._fallback_locale:
            locales.append(cls._fallback_locale)

        cls._bundle = FluentBundle(locales, use_isolating=False)

        # Load the fallback first, then the target locale so translated keys can
        # override fallback keys while missing keys remain readable.
        filename = "client.ftl"

        for loc in reversed(locales):
            path = locales_dir / loc / filename
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        resource = FluentResource(content)
                        cls._bundle.add_resource(resource, allow_overrides=True)
                except Exception as e:
                    LOGGER.warning("Error loading locale %s from %s: %s", loc, path, e)
            else:
                LOGGER.debug("Locale file not found: %s", path.absolute())

    @classmethod
    def get(cls, message_id: str, **kwargs) -> str:
        """Get a localized message."""
        if not cls._bundle:
            return message_id

        lookup_id = cls._message_aliases.get(message_id, message_id)
        if not cls._bundle.has_message(lookup_id):
            return message_id
            
        try:
            message = cls._bundle.get_message(lookup_id)
            if message and message.value:
                val, errors = cls._bundle.format_pattern(message.value, kwargs)
                if errors:
                    LOGGER.warning("Fluent errors for %s: %s", lookup_id, errors)
                    return val or message_id
                return val
            return message_id
        except Exception as e:
            LOGGER.warning("Error formatting %s: %s", lookup_id, e)
            return message_id
