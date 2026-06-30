"""Compare Fluent locale files for missing, obsolete, and unsafe keys."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_SOURCE_LOCALE = "en"
LOCALE_METADATA_FILENAME = "metadata.json"

SCRIPT_DIR = Path(__file__).parent
SERVER_DIR = SCRIPT_DIR.parent
LOCALES_DIR = SERVER_DIR / "locales"

MESSAGE_RE = re.compile(r"^(-?[A-Za-z][A-Za-z0-9_-]*)\s*=")
ATTRIBUTE_RE = re.compile(r"^\s+\.([A-Za-z][A-Za-z0-9_-]*)\s*=", re.MULTILINE)
VARIABLE_RE = re.compile(r"\{\s*\$([A-Za-z][A-Za-z0-9_-]*)")
VARIANT_RE = re.compile(r"^\s*\*?\[([^\]]+)\]", re.MULTILINE)


@dataclass(frozen=True)
class MessageInfo:
    """Parsed structure that translators must keep compatible."""

    variables: frozenset[str]
    variants: frozenset[str]
    attributes: frozenset[str]


@dataclass
class FileReport:
    """Comparison result for one source/target file pair."""

    relative_path: Path
    duplicate_keys: list[tuple[str, str, list[int]]] = field(default_factory=list)
    missing_keys: list[str] = field(default_factory=list)
    obsolete_keys: list[str] = field(default_factory=list)
    variable_mismatches: list[tuple[str, list[str], list[str]]] = field(
        default_factory=list
    )
    variant_mismatches: list[tuple[str, list[str], list[str]]] = field(
        default_factory=list
    )
    attribute_mismatches: list[tuple[str, list[str], list[str]]] = field(
        default_factory=list
    )
    read_errors: list[str] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return any(
            (
                self.missing_keys,
                self.obsolete_keys,
                self.duplicate_keys,
                self.variable_mismatches,
                self.attribute_mismatches,
                self.read_errors,
            )
        )

    @property
    def has_warnings(self) -> bool:
        return bool(self.variant_mismatches)


@dataclass
class LocaleReport:
    """Comparison result for one target locale."""

    source_locale: str
    target_locale: str
    missing_files: list[Path] = field(default_factory=list)
    obsolete_files: list[Path] = field(default_factory=list)
    metadata_errors: list[str] = field(default_factory=list)
    duplicate_keys: list[tuple[str, str, list[str]]] = field(default_factory=list)
    file_reports: list[FileReport] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(
            self.missing_files
            or self.obsolete_files
            or self.metadata_errors
            or self.duplicate_keys
            or any(report.has_issues for report in self.file_reports)
        )

    @property
    def has_warnings(self) -> bool:
        return any(report.has_warnings for report in self.file_reports)


def parse_messages(file_path: Path) -> dict[str, MessageInfo]:
    """Parse top-level Fluent messages and basic structural requirements."""
    messages: dict[str, list[str]] = {}
    current_key: str | None = None

    with file_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            match = MESSAGE_RE.match(line)
            if match:
                current_key = match.group(1)
                messages.setdefault(current_key, []).append(line)
                continue
            if current_key is not None:
                messages[current_key].append(line)

    parsed: dict[str, MessageInfo] = {}
    for key, lines in messages.items():
        body = "".join(lines)
        attributes = frozenset(
            attribute_match.group(1)
            for attribute_match in ATTRIBUTE_RE.finditer(body)
        )
        parsed[key] = MessageInfo(
            variables=frozenset(VARIABLE_RE.findall(body)),
            variants=frozenset(
                variant.strip() for variant in VARIANT_RE.findall(body)
            ),
            attributes=attributes,
        )
    return parsed


def find_duplicate_message_ids(
    file_path: Path, label: str
) -> list[tuple[str, str, list[int]]]:
    """Return duplicate top-level Fluent message ids with their line numbers."""
    line_numbers: dict[str, list[int]] = {}
    with file_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            match = MESSAGE_RE.match(line)
            if match:
                line_numbers.setdefault(match.group(1), []).append(line_number)
    return [
        (label, key, lines)
        for key, lines in sorted(line_numbers.items())
        if len(lines) > 1
    ]


def find_cross_file_duplicate_message_ids(
    locale_dir: Path, label: str
) -> list[tuple[str, str, list[str]]]:
    """Return message ids defined in more than one Fluent file."""
    locations: dict[str, list[str]] = {}
    for ftl_file in sorted(locale_dir.rglob("*.ftl")):
        relative = ftl_file.relative_to(locale_dir).as_posix()
        with ftl_file.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                match = MESSAGE_RE.match(line)
                if match:
                    locations.setdefault(match.group(1), []).append(
                        f"{relative}:{line_number}"
                    )

    duplicates: list[tuple[str, str, list[str]]] = []
    for key, key_locations in sorted(locations.items()):
        files = {location.rsplit(":", 1)[0] for location in key_locations}
        if len(files) > 1:
            duplicates.append((label, key, key_locations))
    return duplicates


def compare_file(source_file: Path, target_file: Path, relative_path: Path) -> FileReport:
    """Compare one Fluent file."""
    report = FileReport(relative_path=relative_path)
    try:
        report.duplicate_keys.extend(find_duplicate_message_ids(source_file, "source"))
        source_messages = parse_messages(source_file)
    except OSError as exc:
        report.read_errors.append(f"Could not read source file: {exc}")
        return report
    try:
        report.duplicate_keys.extend(find_duplicate_message_ids(target_file, "target"))
        target_messages = parse_messages(target_file)
    except OSError as exc:
        report.read_errors.append(f"Could not read target file: {exc}")
        return report

    source_keys = set(source_messages)
    target_keys = set(target_messages)
    report.missing_keys = sorted(source_keys - target_keys)
    report.obsolete_keys = sorted(target_keys - source_keys)

    for key in sorted(source_keys & target_keys):
        source_info = source_messages[key]
        target_info = target_messages[key]
        if source_info.variables != target_info.variables:
            report.variable_mismatches.append(
                (
                    key,
                    sorted(source_info.variables),
                    sorted(target_info.variables),
                )
            )
        if source_info.variants != target_info.variants:
            report.variant_mismatches.append(
                (
                    key,
                    sorted(source_info.variants),
                    sorted(target_info.variants),
                )
            )
        if source_info.attributes != target_info.attributes:
            report.attribute_mismatches.append(
                (
                    key,
                    sorted(source_info.attributes),
                    sorted(target_info.attributes),
                )
            )

    return report


def validate_locale_metadata(locale_dir: Path, locale_code: str) -> list[str]:
    """Validate translator metadata required for every server locale."""
    metadata_path = locale_dir / LOCALE_METADATA_FILENAME
    if not metadata_path.is_file():
        return [f"{LOCALE_METADATA_FILENAME} is missing."]
    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{LOCALE_METADATA_FILENAME} could not be read: {exc}"]
    if not isinstance(data, dict):
        return [f"{LOCALE_METADATA_FILENAME} must contain a JSON object."]

    errors: list[str] = []
    declared_code = data.get("code")
    if isinstance(declared_code, str) and declared_code and declared_code != locale_code:
        errors.append(
            f"{LOCALE_METADATA_FILENAME} code is {declared_code!r}, expected {locale_code!r}."
        )
    translators = data.get("translators", data.get("contributors"))
    if isinstance(translators, str):
        has_translators = bool(translators.strip())
    elif isinstance(translators, list):
        has_translators = any(
            isinstance(translator, str) and translator.strip()
            for translator in translators
        )
    else:
        has_translators = False
    if not has_translators:
        errors.append(
            f"{LOCALE_METADATA_FILENAME} must include at least one translator."
        )
    return errors


def compare_locale(
    source_dir: Path, target_dir: Path, source_locale: str, target_locale: str
) -> LocaleReport:
    """Compare one target locale directory against the source locale."""
    report = LocaleReport(source_locale=source_locale, target_locale=target_locale)
    report.metadata_errors = validate_locale_metadata(target_dir, target_locale)
    report.duplicate_keys.extend(
        find_cross_file_duplicate_message_ids(source_dir, "source")
    )
    if target_dir.exists():
        report.duplicate_keys.extend(
            find_cross_file_duplicate_message_ids(target_dir, "target")
        )
    source_files = {
        path.relative_to(source_dir): path
        for path in sorted(source_dir.rglob("*.ftl"))
    }
    target_files = {
        path.relative_to(target_dir): path
        for path in sorted(target_dir.rglob("*.ftl"))
    } if target_dir.exists() else {}

    report.missing_files = sorted(source_files.keys() - target_files.keys())
    report.obsolete_files = sorted(target_files.keys() - source_files.keys())

    for relative_path in sorted(source_files.keys() & target_files.keys()):
        file_report = compare_file(
            source_files[relative_path],
            target_files[relative_path],
            relative_path,
        )
        if file_report.has_issues or file_report.has_warnings:
            report.file_reports.append(file_report)

    return report


def locale_dirs(locales_dir: Path, source_locale: str) -> list[str]:
    """Return target locale directory names, excluding the source locale."""
    if not locales_dir.exists():
        return []
    return sorted(
        path.name
        for path in locales_dir.iterdir()
        if path.is_dir() and path.name != source_locale
    )


def print_report(report: LocaleReport) -> None:
    """Print a screen-reader-friendly report for one locale."""
    print(f"\nLocale: {report.target_locale} (source: {report.source_locale})")
    print("-" * 60)
    if report.missing_files:
        print(f"Missing files ({len(report.missing_files)}):")
        for path in report.missing_files:
            print(f"  - {path.as_posix()}")
    if report.obsolete_files:
        print(f"Obsolete files ({len(report.obsolete_files)}):")
        for path in report.obsolete_files:
            print(f"  - {path.as_posix()}")
    if report.metadata_errors:
        print(f"Metadata errors ({len(report.metadata_errors)}):")
        for error in report.metadata_errors:
            print(f"  - {error}")
    if report.duplicate_keys:
        print(f"Cross-file duplicate keys ({len(report.duplicate_keys)}):")
        for label, key, locations in report.duplicate_keys:
            joined_locations = ", ".join(locations)
            print(f"  - {key} in {label} locale at {joined_locations}")

    for file_report in report.file_reports:
        print(f"\n{file_report.relative_path.as_posix()}:")
        for error in file_report.read_errors:
            print(f"  Read error: {error}")
        if file_report.missing_keys:
            print(f"  Missing keys ({len(file_report.missing_keys)}):")
            for key in file_report.missing_keys:
                print(f"    - {key}")
        if file_report.obsolete_keys:
            print(f"  Obsolete keys ({len(file_report.obsolete_keys)}):")
            for key in file_report.obsolete_keys:
                print(f"    - {key}")
        if file_report.duplicate_keys:
            print(f"  Duplicate keys ({len(file_report.duplicate_keys)}):")
            for label, key, lines in file_report.duplicate_keys:
                joined_lines = ", ".join(str(line) for line in lines)
                print(f"    - {key} in {label} file at lines {joined_lines}")
        for label, mismatches in (
            ("Variable mismatches", file_report.variable_mismatches),
            ("Attribute mismatches", file_report.attribute_mismatches),
        ):
            if not mismatches:
                continue
            print(f"  {label} ({len(mismatches)}):")
            for key, source_values, target_values in mismatches:
                print(
                    "    - "
                    f"{key}: source={source_values or '[]'}, "
                    f"target={target_values or '[]'}"
                )
        if file_report.variant_mismatches:
            print(
                "  Select/plural variant differences "
                f"({len(file_report.variant_mismatches)}; review warning):"
            )
            for key, source_values, target_values in file_report.variant_mismatches:
                print(
                    "    - "
                    f"{key}: source={source_values or '[]'}, "
                    f"target={target_values or '[]'}"
                )

    if not report.has_issues and not report.has_warnings:
        print(
            "No missing, obsolete, duplicate, metadata, or structurally unsafe "
            "strings found."
        )
    elif not report.has_issues:
        print(
            "No blocking missing, obsolete, duplicate, metadata, variable, or "
            "attribute issues found."
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare PlayAural Fluent locale files for missing keys, obsolete "
            "keys, duplicate keys, variables, attributes, and select/plural "
            "review warnings."
        )
    )
    parser.add_argument(
        "locales",
        nargs="*",
        help="Target locale codes. When omitted, all non-source locales are checked.",
    )
    parser.add_argument(
        "--source",
        default=DEFAULT_SOURCE_LOCALE,
        help=f"Source locale code. Defaults to {DEFAULT_SOURCE_LOCALE}.",
    )
    parser.add_argument(
        "--locales-dir",
        type=Path,
        default=LOCALES_DIR,
        help="Directory containing locale subdirectories.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    locales_dir = args.locales_dir.resolve()
    source_dir = locales_dir / args.source
    if not source_dir.exists():
        print(f"Error: source locale directory not found: {source_dir}")
        return 2

    targets = args.locales or locale_dirs(locales_dir, args.source)
    if not targets:
        print("No target locales found.")
        return 0

    print("PlayAural Fluent locale comparison")
    print(f"Locale root: {locales_dir}")
    print(f"Source locale: {args.source}")

    reports = [
        compare_locale(source_dir, locales_dir / target, args.source, target)
        for target in targets
    ]
    for report in reports:
        print_report(report)

    return 1 if any(report.has_issues for report in reports) else 0


if __name__ == "__main__":
    sys.exit(main())
