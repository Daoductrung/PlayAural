"""Documentation loading and lightweight markdown rendering."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from ..messages.localization import DEFAULT_LOCALE


@dataclass(frozen=True)
class DocumentationEntry:
    """A top-level documentation page exposed in the Documentation menu."""

    doc_id: str
    label_key: str


TOP_LEVEL_DOCUMENTS: tuple[DocumentationEntry, ...] = (
    DocumentationEntry("intro", "introduction"),
    DocumentationEntry("community_rules", "community-rules"),
    DocumentationEntry("global_keys", "global-keys"),
    DocumentationEntry("changelog", "changelog"),
    DocumentationEntry("donation", "donation"),
    DocumentationEntry("contact", "contact"),
)


class DocumentationManager:
    """Load documentation content with safe IDs, caching, and default fallback."""

    _instance: DocumentationManager | None = None

    @classmethod
    def get_instance(cls) -> DocumentationManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, base_path: Path | None = None):
        self.base_path = base_path or Path(__file__).parent / "content"
        self._content_cache: dict[tuple[str, str], str | None] = {}

    def clear_cache(self) -> None:
        """Clear cached document contents after documentation files change."""
        self._content_cache.clear()

    def get_top_level_documents(self) -> tuple[DocumentationEntry, ...]:
        """Return the ordered top-level documentation pages."""
        return TOP_LEVEL_DOCUMENTS

    def get_all_categories(self, locale: str = DEFAULT_LOCALE) -> dict[str, str]:
        """Backward-compatible mapping of top-level document IDs to label keys."""
        return {
            entry.doc_id: entry.label_key
            for entry in self.get_top_level_documents()
        }

    def get_document(self, doc_id: str, locale: str = DEFAULT_LOCALE) -> str | None:
        """
        Get raw markdown content by canonical document ID.

        Document IDs are extensionless POSIX-style paths such as ``intro`` or
        ``games/scopa``. Localized documents fall back to the default locale
        when missing.
        """
        safe_doc_id = self.normalize_doc_id(doc_id)
        if safe_doc_id is None:
            return None

        locale = self.normalize_locale(locale)
        content = self._load_file(safe_doc_id, locale)
        if content is not None:
            return content
        if locale != DEFAULT_LOCALE:
            return self._load_file(safe_doc_id, DEFAULT_LOCALE)
        return None

    def document_exists(self, doc_id: str, locale: str = DEFAULT_LOCALE) -> bool:
        """Return whether a document exists in the locale or default locale."""
        return self.get_document(doc_id, locale) is not None

    def render_markdown_lines(self, content: str) -> list[str]:
        """Convert project markdown into screen-reader-friendly text lines."""
        rendered: list[str] = []
        for raw_line in content.splitlines():
            text = raw_line.strip()
            if not text:
                continue

            text = self._unescape_project_markdown(text)
            if text.startswith("#"):
                text = text.lstrip("#").strip()
            elif self._starts_with_unordered_marker(text):
                text = text[1:].strip()

            text = self._strip_inline_markdown(text)
            if text:
                rendered.append(text)
        return rendered

    def normalize_doc_id(self, doc_id: str) -> str | None:
        """Return a safe canonical document ID, or None for invalid paths."""
        if not isinstance(doc_id, str):
            return None
        normalized = doc_id.strip().replace("\\", "/").strip("/")
        if normalized.endswith(".md"):
            normalized = normalized[:-3]
        if not normalized or "\x00" in normalized:
            return None

        path = PurePosixPath(normalized)
        if path.is_absolute():
            return None
        if any(part in ("", ".", "..") for part in path.parts):
            return None
        return path.as_posix()

    def normalize_locale(self, locale: str) -> str:
        """Return an installed filesystem-safe locale or the default locale."""
        if not isinstance(locale, str) or not locale:
            return DEFAULT_LOCALE
        normalized = locale.strip().replace("_", "-").lower()
        if any(ch in normalized for ch in ("/", "\\", ".", "\x00")):
            return DEFAULT_LOCALE
        if not all(ch.isalnum() or ch == "-" for ch in normalized):
            return DEFAULT_LOCALE

        installed = self._installed_locales()
        if normalized in installed:
            return normalized
        base = normalized.split("-", 1)[0]
        if base in installed:
            return base
        return DEFAULT_LOCALE

    def _installed_locales(self) -> set[str]:
        if not self.base_path.exists():
            return {DEFAULT_LOCALE}
        return {
            locale_dir.name
            for locale_dir in self.base_path.iterdir()
            if locale_dir.is_dir()
        } or {DEFAULT_LOCALE}

    def _load_file(self, doc_id: str, locale: str) -> str | None:
        """Load a single canonical document file from disk or cache."""
        cache_key = (locale, doc_id)
        if cache_key in self._content_cache:
            return self._content_cache[cache_key]

        locale_root = (self.base_path / locale).resolve()
        file_path = (locale_root / f"{doc_id}.md").resolve()
        try:
            file_path.relative_to(locale_root)
        except ValueError:
            self._content_cache[cache_key] = None
            return None

        if not file_path.is_file():
            self._content_cache[cache_key] = None
            return None

        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Error loading documentation {doc_id} ({locale}): {exc}")
            content = None

        self._content_cache[cache_key] = content
        return content

    def _unescape_project_markdown(self, text: str) -> str:
        """Undo the escaped markdown style used by documentation source files."""
        for char in ("*", "_", "`", ".", "#", "-", "+"):
            text = text.replace(f"\\{char}", char)
        return text.replace("&nbsp;", " ")

    def _starts_with_unordered_marker(self, text: str) -> bool:
        if len(text) < 2:
            return False
        return text[0] in {"-", "*", "+", "\u2022"} and text[1].isspace()

    def _strip_inline_markdown(self, text: str) -> str:
        for marker in ("**", "__", "`"):
            text = text.replace(marker, "")
        return text.strip()
