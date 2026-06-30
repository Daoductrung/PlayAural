"""Localization system using Mozilla Fluent."""

import json
from dataclasses import dataclass
from pathlib import Path

from babel import Locale
from babel.core import UnknownLocaleError
from fluent.runtime import FluentBundle, FluentResource
from babel.lists import format_list


DEFAULT_LOCALE = "en"
PINNED_LOCALES = (DEFAULT_LOCALE, "vi")
LOCALE_METADATA_FILENAME = "metadata.json"


@dataclass(frozen=True)
class LocaleMetadata:
    """Translator and display metadata for one installed locale."""

    code: str
    name: str = ""
    native_name: str = ""
    translators: tuple[str, ...] = ()
    official: bool = False
    available: bool = False


class Localization:
    """
    Localization system using Mozilla Fluent via fluent.runtime.

    Loads .ftl files from the locales directory and provides message
    rendering with variable substitution.

    We use the interpreting ``fluent.runtime`` rather than the codegen-based
    ``fluent_compiler``: the latter compiles every message to a Python function
    at load time, an O(n²) name-reservation pass that took ~16 s *per locale*
    for our ~4 000-message bundles. The interpreter merely parses the FTL
    (~0.2 s per locale) and walks the AST at format time (a few µs per call),
    which is comfortably fast for a server formatting a handful of strings per
    event. See the migration discussion for the full benchmark.
    """

    _bundles: dict[str, FluentBundle] = {}
    _bundle_cache_by_dir: dict[Path, dict[str, FluentBundle]] = {}
    _locales_dir: Path | None = None

    @classmethod
    def init(cls, locales_dir: Path | str) -> None:
        """Initialize the localization system with a locales directory."""
        cls._locales_dir = Path(locales_dir).resolve()
        cls._bundles = cls._bundle_cache_by_dir.setdefault(cls._locales_dir, {})

    @classmethod
    def preload_bundles(cls) -> None:
        """Pre-load all locale bundles at startup."""
        if cls._locales_dir is None:
            return

        for locale_code in cls.available_locale_codes():
            cls._get_bundle(locale_code)

    @classmethod
    def _sanitize_locale(cls, locale: str | None) -> str:
        """Return a safe normalized locale code suitable for lookup only."""
        if not isinstance(locale, str):
            return DEFAULT_LOCALE
        normalized = locale.strip().replace("_", "-").lower()
        if not normalized or "\x00" in normalized:
            return DEFAULT_LOCALE
        if any(ch in normalized for ch in ("/", "\\", ".")):
            return DEFAULT_LOCALE
        if not all(ch.isalnum() or ch == "-" for ch in normalized):
            return DEFAULT_LOCALE
        return normalized

    @classmethod
    def available_locale_codes(cls) -> list[str]:
        """Return available locale directory names in stable display order."""
        if cls._locales_dir is None or not cls._locales_dir.exists():
            return []
        codes = sorted(
            locale_dir.name
            for locale_dir in cls._locales_dir.iterdir()
            if locale_dir.is_dir()
        )
        pinned = [code for code in PINNED_LOCALES if code in codes]
        community = [code for code in codes if code not in PINNED_LOCALES]
        return pinned + community

    @classmethod
    def _coerce_string_tuple(cls, value) -> tuple[str, ...]:
        """Normalize string/list metadata fields into a clean tuple."""
        if isinstance(value, str):
            cleaned = value.strip()
            return (cleaned,) if cleaned else ()
        if not isinstance(value, list):
            return ()
        result = []
        for item in value:
            if isinstance(item, str):
                cleaned = item.strip()
                if cleaned:
                    result.append(cleaned)
        return tuple(result)

    @classmethod
    def get_locale_metadata(cls, locale_code: str) -> LocaleMetadata:
        """Return translator metadata for one locale directory."""
        code = cls._sanitize_locale(locale_code)
        if cls._locales_dir is None:
            return LocaleMetadata(code=code)
        locale_dir = cls._locales_dir / code
        metadata_path = locale_dir / LOCALE_METADATA_FILENAME
        if not locale_dir.is_dir() or not metadata_path.is_file():
            return LocaleMetadata(code=code)
        try:
            data = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return LocaleMetadata(code=code)
        if not isinstance(data, dict):
            return LocaleMetadata(code=code)
        name = data.get("name", "")
        native_name = data.get("native_name", data.get("nativeName", ""))
        translators = cls._coerce_string_tuple(
            data.get("translators", data.get("contributors", []))
        )
        return LocaleMetadata(
            code=code,
            name=name.strip() if isinstance(name, str) else "",
            native_name=native_name.strip() if isinstance(native_name, str) else "",
            translators=translators,
            official=bool(data.get("official", False)),
            available=True,
        )

    @classmethod
    def resolve_locale(
        cls, locale: str | None, *, fallback: str = DEFAULT_LOCALE
    ) -> str:
        """Resolve a requested locale to an installed locale code."""
        available = set(cls.available_locale_codes())
        if not available:
            return DEFAULT_LOCALE

        requested = cls._sanitize_locale(locale)
        if requested in available:
            return requested

        language = requested.split("-", 1)[0]
        if language in available:
            return language

        fallback_code = cls._sanitize_locale(fallback)
        if fallback_code in available:
            return fallback_code
        fallback_language = fallback_code.split("-", 1)[0]
        if fallback_language in available:
            return fallback_language
        if DEFAULT_LOCALE in available:
            return DEFAULT_LOCALE
        return sorted(available)[0]

    @classmethod
    def _get_bundle(cls, locale: str) -> FluentBundle:
        """Get or create a bundle for a locale."""
        if cls._locales_dir is None:
            raise RuntimeError(
                "Localization not initialized. Call Localization.init() first."
            )

        requested_locale = cls._sanitize_locale(locale)
        if requested_locale in cls._bundles:
            return cls._bundles[requested_locale]

        actual_locale = cls.resolve_locale(requested_locale)
        if actual_locale in cls._bundles:
            cls._bundles[requested_locale] = cls._bundles[actual_locale]
            return cls._bundles[actual_locale]

        locale_dir = cls._locales_dir / actual_locale
        if not locale_dir.exists():
            default_dir = cls._locales_dir / DEFAULT_LOCALE
            if default_dir.exists():
                locale_dir = default_dir
                actual_locale = DEFAULT_LOCALE
            else:
                raise RuntimeError(
                    f"No locale files found for {locale} or {DEFAULT_LOCALE}"
                )

        # Load all .ftl files in the locale directory. Each file is added as a
        # separate resource so a parse error is attributed to one file rather
        # than poisoning the whole bundle.
        ftl_files = sorted(locale_dir.glob("*.ftl"))
        if not ftl_files:
            raise RuntimeError(f"No .ftl files found in {locale_dir}")

        # use_isolating=True matches the previous fluent_compiler default; the
        # bidi isolation characters it inserts are stripped in get().
        bundle = FluentBundle([actual_locale], use_isolating=True)
        for ftl_file in ftl_files:
            bundle.add_resource(
                FluentResource(ftl_file.read_text(encoding="utf-8"))
            )
        cls._bundles[actual_locale] = bundle
        cls._bundles[requested_locale] = bundle
        return bundle

    # Unicode bidi isolation characters that Fluent adds around variables
    _BIDI_CHARS = "\u2068\u2069"  # FIRST STRONG ISOLATE, POP DIRECTIONAL ISOLATE

    @classmethod
    def _format_from_bundle(
        cls, locale: str, message_id: str, kwargs: dict
    ) -> str | None:
        """Format one message from one bundle, returning None when unavailable."""
        bundle = cls._get_bundle(locale)
        base_id, _, attribute = message_id.partition(".")
        try:
            message = bundle.get_message(base_id)
        except KeyError:
            return None
        if message is None:
            return None
        pattern = message.attributes.get(attribute) if attribute else message.value
        if pattern is None:
            return None
        result, _errors = bundle.format_pattern(pattern, kwargs)
        for char in cls._BIDI_CHARS:
            result = result.replace(char, "")
        return result

    @classmethod
    def get(cls, locale: str, message_id: str, **kwargs) -> str:
        """
        Get a localized message.

        Args:
            locale: The locale code (e.g., 'en', 'es').
            message_id: The message ID from the .ftl file.
            **kwargs: Variables to substitute into the message.

        Returns:
            The formatted message string.
        """
        try:
            resolved_locale = cls.resolve_locale(locale)
            result = cls._format_from_bundle(resolved_locale, message_id, kwargs)
            if result is not None:
                return result
            if resolved_locale != DEFAULT_LOCALE:
                result = cls._format_from_bundle(DEFAULT_LOCALE, message_id, kwargs)
                if result is not None:
                    return result
        except Exception:
            pass
        return message_id

    @classmethod
    def _babel_locale(cls, locale: str) -> str:
        """Return a Babel-safe locale code with English fallback."""
        resolved = cls.resolve_locale(locale)
        babel_locale = resolved.replace("-", "_")
        try:
            Locale.parse(babel_locale)
            return babel_locale
        except (UnknownLocaleError, ValueError):
            return DEFAULT_LOCALE

    @classmethod
    def format_list(cls, locale: str, items: list[str]) -> str:
        """
        Format a list using standard style (e.g. 'A, B, and C').

        Args:
            locale: The locale code.
            items: List of items to format.

        Returns:
            Formatted list string.
        """
        return format_list(items, style="standard", locale=cls._babel_locale(locale))

    @classmethod
    def format_list_and(cls, locale: str, items: list[str]) -> str:
        """
        Format a list with 'and' conjunction using Babel.

        Args:
            locale: The locale code.
            items: List of items to format.

        Returns:
            Formatted list string (e.g., "A, B, and C").
        """
        return format_list(items, style="standard", locale=cls._babel_locale(locale))

    @classmethod
    def format_list_or(cls, locale: str, items: list[str]) -> str:
        """
        Format a list with 'or' conjunction using Babel.

        Args:
            locale: The locale code.
            items: List of items to format.

        Returns:
            Formatted list string (e.g., "A, B, or C").
        """
        return format_list(items, style="or", locale=cls._babel_locale(locale))

    @classmethod
    def _language_display_name(cls, locale_code: str, display_language: str) -> str:
        """Return a localized language name with Fluent and Babel fallbacks."""
        message_id = f"language-{locale_code}"
        lookup_locale = display_language or locale_code
        name = cls.get(lookup_locale, message_id)
        if name != message_id:
            return name
        if display_language:
            name = cls.get(locale_code, message_id)
            if name != message_id:
                return name
        metadata = cls.get_locale_metadata(locale_code)
        if display_language == DEFAULT_LOCALE and metadata.name:
            return metadata.name
        if metadata.native_name:
            return metadata.native_name
        if metadata.name:
            return metadata.name
        try:
            language = Locale.parse(locale_code.replace("-", "_"))
            display_locale = Locale.parse(
                cls.resolve_locale(display_language or locale_code).replace("-", "_")
            )
            return language.get_display_name(display_locale)
        except (UnknownLocaleError, ValueError):
            return locale_code

    @classmethod
    def get_available_languages(
        cls, display_language: str = "", *, fallback: str = DEFAULT_LOCALE
    ) -> dict[str, str]:
        """
        Get a dictionary of available languages.

        Args:
            display_language: The locale to use for displaying language names.
                              If empty, each language name is shown in its own
                              language (e.g., "English" for en, "中文" for zh).
            fallback: The locale to use if a language name is not found
                             in the display language. Defaults to "en".

        Returns:
            Dictionary mapping language codes to language names.
        """
        if cls._locales_dir is None:
            raise RuntimeError(
                "Localization not initialized. Call Localization.init() first."
            )

        result = {}
        display_locale = cls.resolve_locale(display_language, fallback=fallback)

        for locale_code in cls.available_locale_codes():
            result[locale_code] = cls._language_display_name(
                locale_code,
                display_locale if display_language else "",
            )

        return result


def get_message(locale: str, message_id: str, **kwargs) -> str:
    """Convenience function to get a localized message."""
    return Localization.get(locale, message_id, **kwargs)
