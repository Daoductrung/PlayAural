"""Lightweight bot name generation and validation helpers."""

import random
import unicodedata
from collections.abc import Iterable, Sequence

MIN_BOT_NAME_LENGTH = 3
MAX_BOT_NAME_LENGTH = 30

PLAYFUL_BOT_NAMES: tuple[str, ...] = (
    "Pho Pixel",
    "Banh Mi Byte",
    "Mochi Master",
    "Sakura Skip",
    "Chai Champion",
    "Kimchi Combo",
    "Samba Shuffle",
    "Taco Tactician",
    "Lucky Lua",
    "Pixel Pal",
)

PLAYPALACE_BOT_NAMES: tuple[str, ...] = (
    "Smith",
    "Bastardo",
    "Scorpion",
    "Speakertest",
    "Kitana",
    "Assembly_programmer",
    "Liu_kang",
    "Omega-alpha",
    "Alpha-omega",
    "Gama8",
    "Electric-bastard",
    "Yamaha",
    "Jupiter",
    "Mars",
    "Artemis",
    "Fire-lightning",
    "New_play",
    "Y2k-breaker",
    "R2dbag",
    "Subzero",
    "H4mg",
    "4theplaying",
    "@mazing",
    "Virus",
    "Swordswing45",
    "Extremekiller",
    "Tornado26",
    "Legend",
    "Gamesmaster",
    "Angel",
    "Sa",
    "Gamerstorm",
    "Eternalgamer",
    "Sonic_ninja",
    "Summer",
    "Sniper_70",
    "Blindgamer",
    "Nightblade",
    "Darkblade",
    "Dastardo",
    "Boxer",
    "Music_and_lasers",
    "Ak47",
    "Hacker",
    "De_best",
    "Flying_processor",
    "Best_gamer",
    "Destructionmaster",
    "Braillegamer",
    "Braillenote",
    "Lasergun",
    "Michael",
    "Anna",
    "Emma",
    "Matt",
    "Steamtrain",
    "Star06",
    "Cyrus",
    "Godlygamer",
    "Megagaming",
    "Roflgamer_official",
    "Randomuser",
    "Capturer",
    "Commander",
    "Death",
    "Timemaster",
    "Chronos",
    "Titan",
    "Aria",
    "Ares",
    "Assassin",
    "Ball",
    "Master_fighter",
    "Lol",
    "Ultranovagaming",
    "Silva",
    "Lily",
    "Yeet",
    "Mortalkombat",
    "Gun",
    "Kai",
    "Sauce_code",
    "Lasergamer",
    "Still_thinking",
    "Still_existing",
    "Never_existed",
    "Bladethegamer",
    "Bestgame",
)

DEFAULT_BOT_NAME_POOL: tuple[str, ...] = PLAYFUL_BOT_NAMES + PLAYPALACE_BOT_NAMES

_POOL_CHARACTER_REPLACEMENTS: dict[str, str] = {
    "_": " ",
    "-": " ",
    "@": "A",
}


def _capitalize_pool_words(name: str) -> str:
    return " ".join(word[:1].upper() + word[1:] for word in name.split())


def normalize_bot_name(name: str) -> str:
    """Normalize user-visible bot names without changing letter case."""
    return " ".join(unicodedata.normalize("NFC", str(name or "")).strip().split())


def normalize_pool_bot_name(name: str) -> str:
    """Convert configured/generated pool entries into PlayAural-safe display names."""
    normalized = unicodedata.normalize("NFC", str(name or "")).strip()
    for old, new in _POOL_CHARACTER_REPLACEMENTS.items():
        normalized = normalized.replace(old, new)
    normalized = "".join(
        char if char.isalpha() or char.isdigit() or char == " " else " "
        for char in normalized
    )
    return _capitalize_pool_words(normalize_bot_name(normalized))


def bot_name_key(name: str) -> str:
    """Return a case-insensitive comparison key for a bot/player name."""
    return normalize_bot_name(name).casefold()


def _used_name_keys(existing_names: Iterable[str]) -> set[str]:
    return {bot_name_key(name) for name in existing_names if normalize_bot_name(name)}


def _generated_used_name_keys(existing_names: Iterable[str]) -> set[str]:
    used: set[str] = set()
    for name in existing_names:
        normalized = normalize_bot_name(name)
        if normalized:
            used.add(bot_name_key(normalized))
        pool_normalized = normalize_pool_bot_name(name)
        if pool_normalized:
            used.add(bot_name_key(pool_normalized))
    return used


def validate_custom_bot_name(
    name: str,
    existing_names: Iterable[str] = (),
) -> str | None:
    """Return a localization key when a custom bot name is invalid."""
    normalized = normalize_bot_name(name)
    if not MIN_BOT_NAME_LENGTH <= len(normalized) <= MAX_BOT_NAME_LENGTH:
        return "bot-name-invalid-length"
    if not all(char.isalpha() or char.isdigit() or char == " " for char in normalized):
        return "bot-name-invalid-characters"
    if bot_name_key(normalized) in _used_name_keys(existing_names):
        return "bot-name-already-used"
    return None


def get_valid_bot_name_pool(
    name_pool: Sequence[str] = DEFAULT_BOT_NAME_POOL,
) -> tuple[str, ...]:
    """Return the generated-name pool after sanitization, validation, and de-duping."""
    valid_names: list[str] = []
    seen: set[str] = set()
    for name in name_pool:
        normalized = normalize_pool_bot_name(name)
        if validate_custom_bot_name(normalized) is not None:
            continue
        key = bot_name_key(normalized)
        if key in seen:
            continue
        valid_names.append(normalized)
        seen.add(key)
    return tuple(valid_names)


def generate_unique_bot_name(
    existing_names: Iterable[str],
    name_pool: Sequence[str] = DEFAULT_BOT_NAME_POOL,
) -> str:
    """Generate a random unique, valid bot name for a table."""
    used = _generated_used_name_keys(existing_names)
    normalized_pool = get_valid_bot_name_pool(name_pool)
    if not normalized_pool:
        raise ValueError("name_pool must contain at least one valid bot name")

    available_names = [name for name in normalized_pool if bot_name_key(name) not in used]
    if available_names:
        return random.choice(available_names)

    suffixable_names = [
        name for name in normalized_pool if len(f"{name} 2") <= MAX_BOT_NAME_LENGTH
    ]
    if not suffixable_names:
        raise ValueError("name_pool must contain at least one suffixable bot name")

    suffix = 2
    while True:
        suffixed_names = []
        for name in suffixable_names:
            candidate = f"{name} {suffix}"
            if (
                len(candidate) <= MAX_BOT_NAME_LENGTH
                and bot_name_key(candidate) not in used
            ):
                suffixed_names.append(candidate)
        if suffixed_names:
            return random.choice(suffixed_names)
        suffix += 1
