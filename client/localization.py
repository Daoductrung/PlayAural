"""
Client-side localization system using Fluent.
"""

import os
from pathlib import Path
import os
from pathlib import Path
from fluent.runtime import FluentBundle, FluentResource

class Localization:
    _bundle = None
    _locale = "en"
    _fallback_locale = "en"

    @classmethod
    def init(cls, locales_dir: Path | None = None, locale: str = "en"):
        """Initialize the localization system."""
        cls._locale = locale
        if locales_dir is None:
            # Default to 'locales' next to this file
            locales_dir = Path(__file__).parent / "locales"
        
        cls._load_bundle(locales_dir)

    @classmethod
    def _load_bundle(cls, locales_dir: Path):
        """Load Fluent bundle."""
        # Try target locale first, then fallback
        locales = [cls._locale]
        if cls._locale != cls._fallback_locale:
            locales.append(cls._fallback_locale)

        cls._bundle = FluentBundle(locales, use_isolating=False)
        
        # Load files
        # We assume a single 'client.ftl' for now for simplicity
        filename = "client.ftl"
        
        for loc in locales:
            path = locales_dir / loc / filename
            print(f"[Localization] Trying to load: {path}")
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        print(f"[Localization] Read {len(content)} bytes from {path}")
                        resource = FluentResource(content)
                        cls._bundle.add_resource(resource)
                        print(f"[Localization] Loaded {loc}")
                except Exception as e:
                    print(f"Error loading locale {loc}: {e}")
            else:
                print(f"[Localization] File not found: {path.absolute()}")

    @classmethod
    def get(cls, message_id: str, **kwargs) -> str:
        """Get a localized message."""
        if not cls._bundle:
            return message_id
            
        if not cls._bundle.has_message(message_id):
            return message_id
            
        try:
            message = cls._bundle.get_message(message_id)
            if message and message.value:
                val, errors = cls._bundle.format_pattern(message.value, kwargs)
                if errors:
                    print(f"Fluent errors for {message_id}: {errors}")
                    return val or message_id
                return val
            return message_id
        except Exception as e:
            print(f"Error formatting {message_id}: {e}")
            return message_id
