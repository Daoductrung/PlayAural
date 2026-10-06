"""Cards Against Humanity game implementation for PlayAural."""

import html
import json
import random
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import cache
from pathlib import Path

from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.menu_management_mixin import MenuBuild
from ...game_utils.options import (
    IntOption,
    MenuOption,
    MultiSelectOption,
    multi_select_field,
    option_field,
)
from ...game_utils.sequence_runner_mixin import SequenceBeat, SequenceOperation
from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ...users.base import MenuItem
from ..base import Game, GameOptions, Player
from ..registry import register_game

# ==========================================================================
# Pack loading (cached globally)
# ==========================================================================

_humanity_packs: dict[str, list[dict]] = {}
CAH_SOUND_DIR = "game_humanitycards"
CARD_LANGUAGES = ("en", "es", "pt-BR")
DEFAULT_ENGLISH_PACK = "CAH Main Deck: US v3.0"
MIN_PLAYERS = 3
MAX_PLAYERS = 10
DEFAULT_WINNING_SCORE = 7
MIN_WINNING_SCORE = 3
MAX_WINNING_SCORE = 20
DEFAULT_HAND_SIZE = 10
MIN_HAND_SIZE = 5
MAX_HAND_SIZE = 15
DEFAULT_JUDGE_COUNT = 1
MIN_JUDGE_COUNT = 1
MAX_JUDGE_COUNT = 3
DIRECT_CARD_KEY_COUNT = 10
TICKS_PER_SECOND = 20
NEXT_ROUND_DELAY_SECONDS = 5
NEXT_ROUND_DELAY_TICKS = NEXT_ROUND_DELAY_SECONDS * TICKS_PER_SECOND
BOT_SUBMISSION_DELAY_TICKS = (TICKS_PER_SECOND, 2 * TICKS_PER_SECOND)
BOT_JUDGE_DELAY_TICKS = (
    3 * TICKS_PER_SECOND // 2,
    5 * TICKS_PER_SECOND // 2,
)
NEXT_ROUND_SEQUENCE_ID = "humanitycards_next_round"
NEXT_ROUND_SEQUENCE_TAG = "humanitycards_round_transition"
_REPEAT_DIRECTIVE_RE = re.compile(
    r"_?\s*\((?:same\s+card\s+again|repeat)\)\s*_?",
    re.IGNORECASE,
)
_REPEAT_TOKEN = "\N{OBJECT REPLACEMENT CHARACTER}repeat\N{OBJECT REPLACEMENT CHARACTER}"
_MECHANIC_DIRECTIVE_RE = re.compile(
    r"(?:"
    r"pick\s+(?P<pick_first>\d+)\s*,?\s*draw\s+(?P<draw_second>\d+)"
    r"|"
    r"draw\s+(?P<draw_first>\d+)\s*,?\s*pick\s+(?P<pick_second>\d+)"
    r")\)?\.?$",
    re.IGNORECASE,
)
_BREAK_TAG_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)
_SOFT_HYPHEN_BLANK_RE = re.compile("\N{SOFT HYPHEN}{2,}")
_STRIKETHROUGH_TAG_RE = re.compile(
    r"<(?:s|strike|strikethrough)>(.*?)</(?:s|strike|strikethrough)>",
    re.IGNORECASE | re.DOTALL,
)
_EMPHASIS_TAG_RE = re.compile(r"</?(?:em|i)>", re.IGNORECASE)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_HTML_ENTITY_RE = re.compile(r"&(?:[A-Za-z]+|#\d+|#x[0-9A-Fa-f]+);")
_INVALID_CARD_TEXT_RE = re.compile(r"[\u00AD\uFFFD\x00-\x09\x0B-\x1F]")
_LEGACY_ENGLISH_PACK_ALIASES = {
    "Bad Campaign, The Presidential Party Game!": "Bad Campaign",
    "Black Box Press Kit": "Cards Against Humanity: Blackbox Press Kit",
    "CAH Base Set": "Cards Against Humanity: Main Deck (All Versions)",
    "CAH: Main Deck": "Cards Against Humanity: Main Deck (All Versions)",
    "CAH: Box Expansion": "Cards Against Humanity: Bigger Blacker Box/Box Expansion",
    "Cads About Maternity - A game for bad mommies": "Cads About Maternity",
    "Crabs Adjust Humidity: Volume 1": (
        "Crabs Adjust Humidity: Volume 1 (also in Omniclaw)"
    ),
    "Crabs Adjust Humidity: Volume 2": (
        "Crabs Adjust Humidity: Volume 2 (also in Omniclaw)"
    ),
    "Crabs Adjust Humidity: Volume 3": (
        "Crabs Adjust Humidity: Volume 3 (also in Asylum Pack)"
    ),
    "Crabs Adjust Humidity: Volume 4": (
        "Crabs Adjust Humidity: Volume 4 (also in Omniclaw)"
    ),
    "Crabs Adjust Humidity: Volume 5": (
        "Crabs Adjust Humidity: Volume 5 (also in Omniclaw)"
    ),
    "Dirty Nasty Filthy": "Dirty Nasty Filthy - A Card Game for Twisted Minds",
    "Disgruntled Decks: Marine Corps/Jarhead Edition": (
        "Disgrunteld Decks: Marine Corps/Jarhead Edition"
    ),
    "Gen Con 2018 Midterm Election Pack": (
        "Cards Against Humanity: Gen Con 2018 Midterm Elections Pack"
    ),
    "Guards Against Insanity, Edition 1": (
        "Guards Against Insanity, Edition 1 (also in Asylum Pack)"
    ),
    "Guards Against Insanity, Edition 2": (
        "Guards Against Insanity, Edition 2 (also in Asylum Pack)"
    ),
    "Guards Against Insanity, Edition 3": (
        "Guards Against Insanity, Edition 3 (also in Asylum Pack)"
    ),
    "Guards Against Insanity, Edition 4": (
        "Guards Against Insanity, Edition 4 (also in Asylum Pack)"
    ),
    "KinderPerfect (Commercial Set)": "KinderPerfect (Commerical Set)",
    "KinderPerfect: A Timeout For Parents (Kickstarter Set)": (
        "KinderPerfect (Kickstarter Set)"
    ),
    'PAX 2010 "Oops" Kit': 'Cards Against Humanity: PAX 2012 "Oops" Kit',
    "Personally Incorrect - Expansion 2 [Yellow Box]": (
        "Personally Incorrect - Expansion 2"
    ),
    "Personally Incorrect - Expansion [Red Box]": ("Personally Incorrect - Expansion"),
    "Retail Mini Pack": "Cards Against Humanity: Retail Promo/Mini Pack",
    "The Catholic Card Game: Base Deck": "The Catholic Card Game: Base Set",
    "The Catholic Card Game: Life Teen Expansion Pack": (
        "The Catholic Card Game: Teen Life Expansion Pack"
    ),
    "Trumped UpCards: Astonishlingly Excellent Wealthcare! Expansion Pack": (
        "Trumped UpCards: Astonishingly Excellent Wealthcare! Expansion Pack"
    ),
}


def _read_card_json(filename: str) -> object:
    path = Path(__file__).parent / filename
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _plain_card_text(value: object) -> object:
    """Decode source text and convert supported presentation tags to plain text."""
    if not isinstance(value, str):
        return value
    text = html.unescape(value).replace("\r\n", "\n").replace("\r", "\n")
    text = _BREAK_TAG_RE.sub("\n", text)
    text = _SOFT_HYPHEN_BLANK_RE.sub("_", text)
    text = _STRIKETHROUGH_TAG_RE.sub(lambda match: f"{match.group(1).strip()},", text)
    return _EMPHASIS_TAG_RE.sub("", text)


def _card_mechanics(card: dict) -> tuple[object, object]:
    """Return structured pick/draw counts, honoring explicit printed directives."""
    pick = card.get("pick")
    draw = card.get("draw", 0)
    text = card.get("text")
    if isinstance(text, str) and (match := _MECHANIC_DIRECTIVE_RE.search(text)):
        pick = int(match.group("pick_first") or match.group("pick_second"))
        draw = int(match.group("draw_first") or match.group("draw_second"))
    return pick, draw


def _normalize_pack_text(packs: list[object]) -> list[dict]:
    """Return pack copies with readable text while retaining source metadata."""
    normalized: list[dict] = []
    for pack in packs:
        if not isinstance(pack, dict):
            raise TypeError(f"Card pack must be an object, not {type(pack).__name__}")
        normalized_pack = dict(pack)
        normalized_pack["name"] = _plain_card_text(pack.get("name"))
        for color in ("white", "black"):
            cards = pack.get(color, [])
            if not isinstance(cards, list):
                normalized_pack[color] = cards
                continue
            normalized_cards = []
            for card in cards:
                if not isinstance(card, dict):
                    normalized_cards.append(card)
                    continue
                normalized_card = dict(card)
                normalized_card["text"] = _plain_card_text(card.get("text"))
                if color == "black":
                    pick, draw = _card_mechanics(normalized_card)
                    normalized_card["pick"] = pick
                    normalized_card["draw"] = draw
                normalized_cards.append(normalized_card)
            normalized_pack[color] = normalized_cards
        normalized.append(normalized_pack)
    return normalized


def _load_english_packs() -> list[dict]:
    data = _read_card_json("humanity_packs.json")
    if not isinstance(data, list):
        raise TypeError("English Cards Against Humanity data must be a pack list")
    return _normalize_pack_text(data)


def _load_spanish_packs() -> list[dict]:
    data = _read_card_json("humanity_packs_es.json")
    if not isinstance(data, dict):
        raise TypeError("Spanish Cards Against Humanity data must be an object")
    white_cards = data.get("whiteCards")
    black_cards = data.get("blackCards")
    if not isinstance(white_cards, list) or not isinstance(black_cards, list):
        raise TypeError("Spanish Cards Against Humanity card lists are invalid")
    return _normalize_pack_text(
        [
            {
                "name": data.get("name", "Cartas contra la humanidad"),
                "official": False,
                "white": [{"text": text} for text in white_cards],
                "black": [
                    {
                        "text": card.get("text"),
                        "pick": card.get("pick"),
                        "draw": card.get("draw", 0),
                    }
                    if isinstance(card, dict)
                    else card
                    for card in black_cards
                ],
            }
        ]
    )


def _load_brazilian_portuguese_packs() -> list[dict]:
    black_data = _read_card_json("humanity_black_cards_pt_br.json")
    white_data = _read_card_json("humanity_white_cards_pt_br.json")
    if not isinstance(black_data, dict) or not isinstance(white_data, dict):
        raise TypeError("Brazilian Portuguese Cards Against Humanity data is invalid")
    questions = black_data.get("questions")
    answers = white_data.get("answers")
    if not isinstance(questions, list) or not isinstance(answers, list):
        raise TypeError("Brazilian Portuguese card lists are invalid")
    return _normalize_pack_text(
        [
            {
                "name": "Cartas Contra a Humanidade (Brasil)",
                "official": False,
                "white": [{"text": text} for text in answers],
                "black": [
                    {
                        "text": (
                            card.get("text", "").replace("$", "_")
                            if isinstance(card.get("text"), str)
                            else card.get("text")
                        ),
                        "pick": card.get("pick"),
                        "draw": card.get("draw", 0),
                    }
                    if isinstance(card, dict)
                    else card
                    for card in questions
                ],
            }
        ]
    )


_PACK_LOADERS = {
    "en": _load_english_packs,
    "es": _load_spanish_packs,
    "pt-BR": _load_brazilian_portuguese_packs,
}


def _validated_source_text(value: object, context: str) -> str:
    """Return clean source text or fail before it can reach a player."""
    if not isinstance(value, str):
        raise TypeError(f"Invalid {context}: {value!r}")
    if not value.strip():
        raise ValueError(f"Empty {context}")
    if value != value.strip():
        raise ValueError(f"Leading or trailing whitespace in {context}")
    if (
        _HTML_TAG_RE.search(value)
        or _HTML_ENTITY_RE.search(value)
        or _INVALID_CARD_TEXT_RE.search(value)
    ):
        raise ValueError(f"Invalid text in {context}")
    return value


def _validate_packs(language: str, packs: list[dict]) -> None:
    """Fail fast when vendored card data is malformed or ambiguous."""
    names: set[str] = set()
    for pack in packs:
        if not isinstance(pack, dict):
            raise TypeError(f"Invalid {language} card pack: {pack!r}")
        name = _validated_source_text(pack.get("name"), f"{language} pack name")
        if name in names:
            raise ValueError(f"Duplicate {language} card pack name: {name!r}")
        names.add(name)
        if not isinstance(pack.get("official"), bool):
            raise TypeError(f"Invalid official flag in {language} pack {name!r}")
        if language == "en":
            _validated_source_text(
                pack.get("sheetName"), f"sheet name in {language} pack {name!r}"
            )
        white_cards = pack.get("white", [])
        black_cards = pack.get("black", [])
        if not isinstance(white_cards, list) or not isinstance(black_cards, list):
            raise TypeError(f"Invalid card lists in {language} pack {name!r}")
        for card in white_cards:
            if not isinstance(card, dict):
                raise TypeError(f"Invalid white card in {language} pack {name!r}")
            _validated_source_text(
                card.get("text"), f"white card in {language} pack {name!r}"
            )
        for card in black_cards:
            if not isinstance(card, dict):
                raise TypeError(f"Invalid black card in {language} pack {name!r}")
            _validated_source_text(
                card.get("text"), f"black card in {language} pack {name!r}"
            )
            pick = card.get("pick")
            draw = card.get("draw")
            if isinstance(pick, bool) or not isinstance(pick, int):
                raise TypeError(f"Invalid pick count in {language} pack {name!r}")
            if pick < 1:
                raise ValueError(f"Invalid pick count in {language} pack {name!r}")
            if isinstance(draw, bool) or not isinstance(draw, int):
                raise TypeError(f"Invalid draw count in {language} pack {name!r}")
            if draw < 0:
                raise ValueError(f"Invalid draw count in {language} pack {name!r}")


def load_humanity_packs(language: str = "en") -> list[dict]:
    """Load and validate one language's vendored card packs once."""
    if language not in _PACK_LOADERS:
        return []
    if language not in _humanity_packs:
        packs = _PACK_LOADERS[language]()
        _validate_packs(language, packs)
        _humanity_packs[language] = packs
    return _humanity_packs[language]


@cache
def get_max_draw_count() -> int:
    """Return the largest temporary hand expansion in any available deck."""
    return max(
        (
            card["draw"]
            for language in CARD_LANGUAGES
            for pack in load_humanity_packs(language)
            for card in pack["black"]
        ),
        default=0,
    )


def get_pack_names() -> list[str]:
    """Get non-empty English pack names for the pack selector."""
    return [
        pack["name"]
        for pack in load_humanity_packs("en")
        if pack.get("white") or pack.get("black")
    ]


def _pack_name_key(name: str) -> str:
    """Normalize historical source prefixes and punctuation for save migration."""
    value = name.casefold()
    for prefix in ("cards against humanity:", "cards against humanity", "cah:"):
        if value.startswith(prefix):
            value = value[len(prefix) :]
            break
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def _resolve_english_pack_names(selected: list[str]) -> list[str]:
    """Map pack names from the previously shipped corpus to current names."""
    current_names = get_pack_names()
    current_set = set(current_names)
    by_key: dict[str, list[str]] = {}
    for name in current_names:
        by_key.setdefault(_pack_name_key(name), []).append(name)

    resolved: list[str] = []
    for original in selected:
        candidate = _LEGACY_ENGLISH_PACK_ALIASES.get(original, original)
        if candidate not in current_set:
            matches = by_key.get(_pack_name_key(candidate), [])
            candidate = matches[0] if len(matches) == 1 else ""
        if candidate and candidate not in resolved:
            resolved.append(candidate)
    return resolved


def get_pack_groups() -> dict[str, list[str]]:
    """Group the English catalog by source metadata rather than name guesses."""
    packs = [
        pack
        for pack in load_humanity_packs("en")
        if pack.get("white") or pack.get("black")
    ]
    current = [pack["name"] for pack in packs if pack["name"] == DEFAULT_ENGLISH_PACK]
    main_decks = [
        pack["name"] for pack in packs if pack.get("sheetName") == "CAH Main Deck"
    ]
    family = [
        pack["name"] for pack in packs if pack.get("sheetName") == "CAH Family Edition"
    ]
    official_add_ons = [
        pack["name"]
        for pack in packs
        if pack.get("official")
        and pack.get("sheetName") not in {"CAH Main Deck", "CAH Family Edition"}
    ]
    community = [pack["name"] for pack in packs if not pack.get("official")]
    return {
        "current": current,
        "main_decks": main_decks,
        "official_add_ons": official_add_ons,
        "family": family,
        "community": community,
        "all": [pack["name"] for pack in packs],
    }


def _get_default_packs() -> list[str]:
    """Use the newest complete US main deck by default."""
    names = get_pack_names()
    return [DEFAULT_ENGLISH_PACK] if DEFAULT_ENGLISH_PACK in names else names[:1]


# ==========================================================================
# Player and Options
# ==========================================================================


@dataclass
class HumanityCardsPlayer(Player):
    """Player state for Humanity Cards game."""

    score: int = 0
    hand: list[dict] = field(default_factory=list)  # {"text": str, "pack": str}
    submitted_cards: list[str] | None = (
        None  # Text of submitted cards (None = not submitted)
    )
    selected_indices: list[int] = field(default_factory=list)  # Indices into hand


@dataclass
class HumanityCardsOptions(GameOptions):
    """Options for Humanity Cards game."""

    winning_score: int = option_field(
        IntOption(
            default=DEFAULT_WINNING_SCORE,
            min_val=MIN_WINNING_SCORE,
            max_val=MAX_WINNING_SCORE,
            value_key="score",
            label="hc-set-winning-score",
            prompt="hc-enter-winning-score",
            change_msg="hc-option-changed-winning-score",
            description="hc-desc-winning-score",
        )
    )
    hand_size: int = option_field(
        IntOption(
            default=DEFAULT_HAND_SIZE,
            min_val=MIN_HAND_SIZE,
            max_val=MAX_HAND_SIZE,
            value_key="count",
            label="hc-set-hand-size",
            prompt="hc-enter-hand-size",
            change_msg="hc-option-changed-hand-size",
            description="hc-desc-hand-size",
        )
    )
    card_language: str = option_field(
        MenuOption(
            default="en",
            choices=list(CARD_LANGUAGES),
            value_key="language",
            label="hc-set-card-language",
            prompt="hc-select-card-language",
            change_msg="hc-option-changed-card-language",
            description="hc-desc-card-language",
            choice_labels={
                "en": "language-en",
                "es": "language-es",
                "pt-BR": "hc-card-language-pt-br",
            },
        )
    )
    card_packs: list[str] = multi_select_field(
        MultiSelectOption(
            default=_get_default_packs(),
            choices=get_pack_names,
            label="hc-set-card-packs",
            change_msg="hc-option-changed-card-packs",
            description="hc-desc-card-packs",
            min_selected=1,
            show_bulk_actions=True,
            groups=get_pack_groups,
            group_labels={
                "current": "hc-pack-group-current",
                "main_decks": "hc-pack-group-main-decks",
                "official_add_ons": "hc-pack-group-official-add-ons",
                "family": "hc-pack-group-family",
                "community": "hc-pack-group-community",
                "all": "hc-pack-group-all",
            },
        )
    )
    czar_selection: str = option_field(
        MenuOption(
            default="Rotating",
            choices=["Rotating", "Random", "Most Recent Winner"],
            value_key="mode",
            label="hc-set-czar-selection",
            prompt="hc-select-czar-selection",
            change_msg="hc-option-changed-czar-selection",
            description="hc-desc-czar-selection",
            choice_labels={
                "Rotating": "hc-czar-rotating",
                "Random": "hc-czar-random",
                "Most Recent Winner": "hc-czar-winner",
            },
        )
    )
    num_judges: int = option_field(
        IntOption(
            default=DEFAULT_JUDGE_COUNT,
            min_val=MIN_JUDGE_COUNT,
            max_val=MAX_JUDGE_COUNT,
            value_key="count",
            label="hc-set-num-judges",
            prompt="hc-enter-num-judges",
            change_msg="hc-option-changed-num-judges",
            description="hc-desc-num-judges",
        )
    )

    def is_option_visible(self, name: str) -> bool:
        if name == "card_packs" and self.card_language != "en":
            return False
        return super().is_option_visible(name)


# ==========================================================================
# Game
# ==========================================================================


@dataclass
@register_game
class HumanityCardsGame(Game):
    """
    Humanity Cards party game.

    Players take turns as the Card Czar. A black card prompt is read, and
    other players submit white cards to fill in the blanks. The Card Czar
    picks the funniest submission and that player scores a point.
    """

    players: list[HumanityCardsPlayer] = field(default_factory=list)
    options: HumanityCardsOptions = field(default_factory=HumanityCardsOptions)

    # Game state
    phase: str = "waiting"  # waiting, submitting, judging, round_end
    white_deck: list[dict] = field(default_factory=list)
    black_deck: list[dict] = field(default_factory=list)
    white_discard: list[dict] = field(default_factory=list)
    black_discard: list[dict] = field(default_factory=list)
    # {"text": str, "pick": int, "draw": int, "pack": str}
    current_black_card: dict | None = None
    judge_indices: list[int] = field(
        default_factory=list
    )  # Indices into active players
    last_winner_index: int = -1  # For "Most Recent Winner" czar selection
    submissions: list[dict] = field(
        default_factory=list
    )  # [{"player_id": str, "cards": [str]}]
    submission_order: list[int] = field(
        default_factory=list
    )  # Shuffled indices into submissions
    # Retained only to migrate saved matches from the former tick countdown.
    round_end_ticks: int = 0

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.options.card_language == "en" and self.options.card_packs:
            migrated = _resolve_english_pack_names(self.options.card_packs)
            self.options.card_packs = migrated or _get_default_packs()
        if (
            self.phase == "round_end"
            and self.round_end_ticks > 0
            and not self.has_active_sequence(sequence_id=NEXT_ROUND_SEQUENCE_ID)
        ):
            self._schedule_next_round(self.round_end_ticks)
            self.round_end_ticks = 0

    @classmethod
    def get_name(cls) -> str:
        return "Cards Against Humanity"

    @classmethod
    def get_type(cls) -> str:
        return "humanitycards"

    @classmethod
    def get_category(cls) -> str:
        return "cards"

    @classmethod
    def get_min_players(cls) -> int:
        return MIN_PLAYERS

    @classmethod
    def get_max_players(cls) -> int:
        return MAX_PLAYERS

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "total_score", "high_score", "rating", "games_played"]

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> HumanityCardsPlayer:
        return HumanityCardsPlayer(id=player_id, name=name, is_bot=is_bot)

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        """Block impossible judge and deck configurations before play starts."""
        errors: list[str | tuple[str, dict]] = list(super().prestart_validate())
        active_count = len(self.get_active_players())
        if active_count and self.options.num_judges >= active_count:
            errors.append(
                (
                    "hc-error-too-many-judges",
                    {
                        "judges": self.options.num_judges,
                        "players": active_count,
                        "required": self.options.num_judges + 1,
                    },
                )
            )

        stats = self._selected_pack_stats()
        if stats["selected"] == 0:
            errors.append("hc-error-no-valid-packs")
        elif stats["black"] == 0:
            errors.append("hc-error-no-black-cards")

        non_judge_count = max(0, active_count - self.options.num_judges)
        total_whites_needed = (
            active_count * self.options.hand_size + non_judge_count * stats["max_draw"]
        )
        if active_count and stats["white"] < total_whites_needed:
            errors.append(
                (
                    "hc-error-not-enough-white-cards",
                    {
                        "players": active_count,
                        "hand_size": self.options.hand_size,
                        "needed": total_whites_needed,
                        "available": stats["white"],
                    },
                )
            )

        if stats["max_pick"] > self.options.hand_size:
            errors.append(
                (
                    "hc-error-pick-exceeds-hand-size",
                    {
                        "pick": stats["max_pick"],
                        "hand_size": self.options.hand_size,
                    },
                )
            )
        return errors

    def _selected_pack_stats(self) -> dict[str, int]:
        selected_count, white_cards, black_cards = self._selected_pack_cards()
        return {
            "selected": selected_count,
            "white": len(white_cards),
            "black": len(black_cards),
            "max_pick": max(
                (card["pick"] for _, card in black_cards),
                default=0,
            ),
            "max_draw": max(
                (card["draw"] for _, card in black_cards),
                default=0,
            ),
        }

    # ==========================================================================
    # Deck management
    # ==========================================================================

    def _get_active_packs(self) -> list[str]:
        """Get the list of selected pack names."""
        language = self.options.card_language
        if language == "en":
            return list(self.options.card_packs)
        return [pack["name"] for pack in load_humanity_packs(language)]

    def _selected_pack_cards(
        self,
    ) -> tuple[int, list[tuple[str, dict]], list[tuple[str, dict]]]:
        """Collect selected cards, removing exact duplicates across overlapping packs."""
        packs = load_humanity_packs(self.options.card_language)
        active_pack_names = set(self._get_active_packs())
        selected_count = 0
        white_cards: list[tuple[str, dict]] = []
        black_cards: list[tuple[str, dict]] = []
        seen_white: set[str] = set()
        seen_black: set[tuple[str, int, int]] = set()

        for pack in packs:
            pack_name = pack["name"]
            if pack_name not in active_pack_names:
                continue
            selected_count += 1
            for card in pack.get("white", []):
                text = card["text"]
                if text in seen_white:
                    continue
                seen_white.add(text)
                white_cards.append((pack_name, card))
            for card in pack.get("black", []):
                key = (card["text"], card["pick"], card["draw"])
                if key in seen_black:
                    continue
                seen_black.add(key)
                black_cards.append((pack_name, card))

        return selected_count, white_cards, black_cards

    def _build_decks(self) -> None:
        """Build white and black decks from selected packs."""
        _, selected_white, selected_black = self._selected_pack_cards()

        self.white_deck = []
        self.black_deck = []
        self.white_discard = []
        self.black_discard = []

        for pack_name, card in selected_white:
            self.white_deck.append({"text": card["text"], "pack": pack_name})

        for pack_name, card in selected_black:
            self.black_deck.append(
                {
                    "text": card["text"],
                    "pick": card["pick"],
                    "draw": card["draw"],
                    "pack": pack_name,
                }
            )

        random.shuffle(self.white_deck)  # nosec B311
        random.shuffle(self.black_deck)  # nosec B311

    def _draw_white(self, count: int = 1) -> list[dict]:
        """Draw white cards from the deck, reshuffling discard if needed."""
        cards = []
        for _ in range(count):
            if not self.white_deck:
                if self.white_discard:
                    self.white_deck = list(self.white_discard)
                    self.white_discard = []
                    random.shuffle(self.white_deck)  # nosec B311
                    self.broadcast_l("hc-deck-reshuffled", buffer="game")
                else:
                    break  # No cards available
            if self.white_deck:
                cards.append(self.white_deck.pop())
        return cards

    def _draw_black(self) -> dict | None:
        """Draw a black card from the deck, reshuffling discard if needed."""
        if not self.black_deck:
            if self.black_discard:
                self.black_deck = list(self.black_discard)
                self.black_discard = []
                random.shuffle(self.black_deck)  # nosec B311
                self.broadcast_l("hc-black-deck-reshuffled", buffer="game")
            else:
                return None
        return self.black_deck.pop() if self.black_deck else None

    def _deal_to_hand_size(self, player: HumanityCardsPlayer) -> None:
        """Fill a player's hand up to the hand size."""
        needed = self.options.hand_size - len(player.hand)
        if needed > 0:
            cards = self._draw_white(needed)
            player.hand.extend(cards)

    def _fill_in_blanks(self, black_text: str, white_cards: list[str]) -> str:
        """Fill a prompt while preserving the stored card text."""
        prompt = _REPEAT_DIRECTIVE_RE.sub(_REPEAT_TOKEN, black_text)
        card_index = 0
        last_card = ""
        parts: list[str] = []
        position = 0
        slot_pattern = re.compile(rf"_+|{re.escape(_REPEAT_TOKEN)}")

        for match in slot_pattern.finditer(prompt):
            parts.append(prompt[position : match.start()])
            is_repeat = match.group() == _REPEAT_TOKEN
            if is_repeat and last_card:
                card_text = last_card
            elif card_index < len(white_cards):
                card_text = white_cards[card_index]
                card_index += 1
                last_card = card_text
            elif last_card:
                card_text = last_card
            else:
                parts.append(match.group())
                position = match.end()
                continue

            following = prompt[match.end() :]
            insert = card_text
            if following and card_text.endswith(".") and not card_text.endswith(".."):
                insert = card_text[:-1]
            parts.append(insert)
            position = match.end()

        parts.append(prompt[position:])
        result = "".join(parts)

        for card_text in white_cards[card_index:]:
            result = f"{result.rstrip()} {card_text}".strip()
        return result

    def _speech_friendly_black(self, text: str) -> str:
        """Render prompt mechanics in the selected card language for speech."""
        language = self.options.card_language
        repeat = Localization.get(language, "hc-card-same-again")
        blank = Localization.get(language, "hc-card-blank")
        text = _REPEAT_DIRECTIVE_RE.sub(repeat, text)
        return re.sub(r"_+", blank, text)

    # ==========================================================================
    # Judge management (supports multiple judges)
    # ==========================================================================

    def _is_judge(self, player: HumanityCardsPlayer) -> bool:
        """Check if a player is one of the current judges."""
        active = self.get_active_players()
        for idx in self.judge_indices:
            if idx < len(active) and active[idx].id == player.id:
                return True
        return False

    def _get_judges(self) -> list[HumanityCardsPlayer]:
        """Get all current judge players."""
        active = self.get_active_players()
        judges = []
        for idx in self.judge_indices:
            if idx < len(active):
                judges.append(active[idx])
        return judges

    def _get_non_judges(self) -> list[HumanityCardsPlayer]:
        """Get all non-judge active players."""
        judge_ids = {j.id for j in self._get_judges()}
        return [p for p in self.get_active_players() if p.id not in judge_ids]

    def _play_judge_turn_sounds(self) -> None:
        """Play the standard personal turn cue for judges who allow it."""
        for judge in self._get_judges():
            user = self.get_user(judge)
            if user and user.preferences.play_turn_sound:
                user.play_sound("turn.ogg")

    def _select_judges(self) -> None:
        """Select judge(s) for the current round based on czar_selection option."""
        active = self.get_active_players()
        num_judges = min(
            self.options.num_judges, len(active) - 1
        )  # At least 1 non-judge
        if num_judges < 1:
            num_judges = 1

        mode = self.options.czar_selection

        if mode == "Random":
            indices = list(range(len(active)))
            random.shuffle(indices)  # nosec B311
            self.judge_indices = indices[:num_judges]
        elif mode == "Most Recent Winner":
            if self.last_winner_index >= 0 and self.last_winner_index < len(active):
                self.judge_indices = [self.last_winner_index]
                # Fill additional judges rotating from winner
                if num_judges > 1:
                    for offset in range(1, len(active)):
                        if len(self.judge_indices) >= num_judges:
                            break
                        idx = (self.last_winner_index + offset) % len(active)
                        self.judge_indices.append(idx)
            else:
                # Fallback to rotating for first round
                self._select_judges_rotating(active, num_judges)
        else:
            # Rotating (default)
            self._select_judges_rotating(active, num_judges)

    def _select_judges_rotating(
        self, active: list[HumanityCardsPlayer], num_judges: int
    ) -> None:
        """Rotating judge selection: advance from current position."""
        if not self.judge_indices:
            self.judge_indices = [random.randrange(len(active))]  # nosec B311
        else:
            # Advance the first judge index
            first = (self.judge_indices[0] + 1) % len(active)
            self.judge_indices = [first]

        # Fill additional judge slots
        while len(self.judge_indices) < num_judges:
            next_idx = (self.judge_indices[-1] + 1) % len(active)
            if next_idx in self.judge_indices:
                break
            self.judge_indices.append(next_idx)

    # ==========================================================================
    # Action set creation
    # ==========================================================================

    def create_turn_action_set(self, player: HumanityCardsPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # Card toggle actions — non-judges during submitting
        for i in range(MAX_HAND_SIZE + get_max_draw_count()):
            action_set.add(
                Action(
                    id=f"toggle_card_{i}",
                    label=Localization.get(locale, "hc-card-number", number=i + 1),
                    handler="_action_toggle_card",
                    is_enabled="_is_toggle_card_enabled",
                    is_hidden="_is_toggle_card_hidden",
                    get_label="_get_toggle_card_label",
                    show_in_actions_menu=False,
                )
            )

        # At most one fewer submission than the table's maximum player count.
        for i in range(MAX_PLAYERS - 1):
            action_set.add(
                Action(
                    id=f"judge_pick_{i}",
                    label=Localization.get(
                        locale, "hc-submission-number", number=i + 1
                    ),
                    handler="_action_judge_pick",
                    is_enabled="_is_judge_pick_enabled",
                    is_hidden="_is_judge_pick_hidden",
                    get_label="_get_judge_pick_label",
                    show_in_actions_menu=False,
                )
            )

        # View submission (above submit for non-judges)
        action_set.add(
            Action(
                id="view_submission",
                label=Localization.get(locale, "hc-preview-submission"),
                handler="_action_view_submission",
                is_enabled="_is_view_submission_enabled",
                is_hidden="_is_view_submission_hidden",
                get_label="_get_view_submission_label",
                show_in_actions_menu=False,
            )
        )

        # Submit cards
        action_set.add(
            Action(
                id="submit_cards",
                label=Localization.get(
                    locale, "hc-submit-cards", selected=0, required=1
                ),
                handler="_action_submit_cards",
                is_enabled="_is_submit_enabled",
                is_hidden="_is_submit_hidden",
                get_label="_get_submit_label",
                show_in_actions_menu=False,
            )
        )

        return action_set

    def build_menu_items(self, player: Player, user) -> MenuBuild:
        """Add a genuine read-only prompt above a judge's submissions."""
        menu = super().build_menu_items(player, user)
        if (
            self.status != "playing"
            or self.phase != "judging"
            or not isinstance(player, HumanityCardsPlayer)
            or not self._is_judge(player)
        ):
            return menu

        prompt = (
            self._speech_friendly_black(self.current_black_card["text"])
            if self.current_black_card
            else Localization.get(user.locale, "hc-choose-best-card")
        )
        header = MenuItem(
            text=Localization.get(
                user.locale,
                "hc-choose-best-card-for",
                prompt=prompt,
            ),
            id="judge_prompt_header",
            read_only=True,
        )
        insert_at = next(
            (
                index
                for index, item in enumerate(menu.items)
                if item.id and item.id.startswith("judge_pick_")
            ),
            0,
        )
        menu.items.insert(insert_at, header)
        return menu

    def create_standard_action_set(self, player: Player) -> ActionSet:
        """Create standard info actions for Cards Against Humanity."""
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set.add(
            Action(
                id="view_black_card",
                label=Localization.get(locale, "hc-view-black-card"),
                handler="_action_view_black_card",
                is_enabled="_is_view_enabled",
                is_hidden="_is_view_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="whose_judge",
                label=Localization.get(locale, "hc-whose-judge"),
                handler="_action_whose_judge",
                is_enabled="_is_check_scores_enabled",
                is_hidden="_is_whose_judge_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="review_hand",
                label=Localization.get(locale, "hc-review-hand"),
                handler="_action_review_hand",
                is_enabled="_is_review_hand_enabled",
                is_hidden="_is_review_hand_hidden",
            )
        )
        action_set.add(
            Action(
                id="review_answers",
                label=Localization.get(locale, "hc-review-answers"),
                handler="_action_review_answers",
                is_enabled="_is_review_answers_enabled",
                is_hidden="_is_review_answers_hidden",
                include_spectators=True,
            )
        )

        if self.is_touch_client(user):
            self._order_touch_standard_actions(
                action_set,
                [
                    "view_black_card",
                    "review_hand",
                    "review_answers",
                    "whose_judge",
                    "check_scores",
                    "whose_turn",
                    "whos_at_table",
                ],
            )

        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        # Number keys 1-9, 0 for cards 1-10
        for i in range(DIRECT_CARD_KEY_COUNT):
            key = str((i + 1) % 10)  # 1,2,3,...,9,0
            self.define_keybind(
                key,
                Localization.get("en", "hc-toggle-card-keybind", number=i + 1),
                [f"toggle_card_{i}"],
                state=KeybindState.ACTIVE,
            )

        # Space to submit
        self.define_keybind(
            "space",
            Localization.get("en", "hc-submit-cards-keybind"),
            ["submit_cards"],
            state=KeybindState.ACTIVE,
        )

        # C to view black card
        self.define_keybind(
            "c",
            Localization.get("en", "hc-view-black-card"),
            ["view_black_card"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        # V to view/preview submission
        self.define_keybind(
            "v",
            Localization.get("en", "hc-view-submission"),
            ["view_submission"],
            state=KeybindState.ACTIVE,
        )

        # Scores use the standard check_scores keybind ("s"); no custom binding.

        # J to announce judges
        self.define_keybind(
            "j",
            Localization.get("en", "hc-whose-judge"),
            ["whose_judge"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        self.define_keybind(
            "h",
            Localization.get("en", "hc-review-hand"),
            ["review_hand"],
            state=KeybindState.ACTIVE,
        )

        self.define_keybind(
            "shift+v",
            Localization.get("en", "hc-review-answers"),
            ["review_answers"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    # ==========================================================================
    # is_enabled callbacks
    # ==========================================================================

    def _is_toggle_card_enabled(
        self, player: Player, action_id: str
    ) -> str | tuple[str, dict] | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self._is_judge(hcp):
            return "hc-judge-cannot-submit"
        if hcp.submitted_cards is not None:
            return "hc-already-submitted"
        if self.phase != "submitting":
            return "hc-not-submission-phase"
        idx = int(action_id.removeprefix("toggle_card_"))
        if idx >= len(hcp.hand):
            return "hc-card-not-in-hand"
        required = self.current_black_card["pick"] if self.current_black_card else 1
        if idx not in hcp.selected_indices and len(hcp.selected_indices) >= required:
            return ("hc-selection-full", {"count": required})
        return None

    def _is_toggle_card_hidden(self, player: Player, action_id: str) -> Visibility:
        if self.status != "playing" or self.phase != "submitting":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self._is_judge(hcp):
            return Visibility.HIDDEN
        if hcp.submitted_cards is not None:
            return Visibility.HIDDEN
        idx = int(action_id.removeprefix("toggle_card_"))
        if idx >= len(hcp.hand):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_toggle_card_label(self, player: Player, action_id: str) -> str:
        hcp: HumanityCardsPlayer = player  # type: ignore
        idx = int(action_id.removeprefix("toggle_card_"))
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if idx >= len(hcp.hand):
            return Localization.get(locale, "hc-card-number", number=idx + 1)
        card = hcp.hand[idx]
        if idx in hcp.selected_indices:
            required = self.current_black_card["pick"] if self.current_black_card else 1
            if required > 1:
                return Localization.get(
                    locale,
                    "hc-card-selected-position",
                    text=card["text"],
                    position=hcp.selected_indices.index(idx) + 1,
                )
            return Localization.get(locale, "hc-card-selected", text=card["text"])
        return Localization.get(locale, "hc-card-not-selected", text=card["text"])

    def _is_submit_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self._is_judge(hcp):
            return "hc-judge-cannot-submit"
        if hcp.submitted_cards is not None:
            return "hc-already-submitted"
        if self.phase != "submitting":
            return "hc-not-submission-phase"
        required = self.current_black_card["pick"] if self.current_black_card else 1
        if len(hcp.selected_indices) != required:
            return ("hc-wrong-card-count", {"count": required})
        return None

    def _is_submit_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or self.phase != "submitting":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self._is_judge(hcp):
            return Visibility.HIDDEN
        if hcp.submitted_cards is not None:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_submit_label(self, player: Player, action_id: str) -> str:
        hcp: HumanityCardsPlayer = player  # type: ignore
        user = self.get_user(player)
        locale = user.locale if user else "en"
        required = self.current_black_card["pick"] if self.current_black_card else 1
        return Localization.get(
            locale,
            "hc-submit-cards",
            selected=len(hcp.selected_indices),
            required=required,
        )

    # ==========================================================================
    # Judge pick callbacks (inline submission selection)
    # ==========================================================================

    def _is_judge_pick_enabled(self, player: Player, action_id: str) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        hcp: HumanityCardsPlayer = player  # type: ignore
        if not self._is_judge(hcp):
            return "hc-only-judges-pick"
        if self.phase != "judging":
            return "hc-not-judging-phase"
        idx = int(action_id.removeprefix("judge_pick_"))
        if idx >= len(self.submission_order):
            return "hc-submission-not-available"
        return None

    def _is_judge_pick_hidden(self, player: Player, action_id: str) -> Visibility:
        if self.status != "playing" or self.phase != "judging":
            return Visibility.HIDDEN
        hcp: HumanityCardsPlayer = player  # type: ignore
        if not self._is_judge(hcp):
            return Visibility.HIDDEN
        idx = int(action_id.removeprefix("judge_pick_"))
        if idx >= len(self.submission_order):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_judge_pick_label(self, player: Player, action_id: str) -> str:
        idx = int(action_id.removeprefix("judge_pick_"))
        if idx < len(self.submission_order):
            sub_idx = self.submission_order[idx]
            if sub_idx < len(self.submissions):
                sub = self.submissions[sub_idx]
                if self.current_black_card:
                    return self._fill_in_blanks(
                        self.current_black_card["text"], sub["cards"]
                    )
                return ", ".join(sub["cards"])
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "hc-submission-number", number=idx + 1)

    # ==========================================================================
    # Whose judge / whose turn overrides
    # ==========================================================================

    def _is_whose_judge_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        # Keybind-only — always hidden from menu
        return Visibility.HIDDEN

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whose_turn_hidden(player)

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_review_hand_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_review_hand_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if (
            self.status == "playing"
            and not player.is_spectator
            and self.is_touch_client(user)
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_review_answers_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.phase != "judging" or not self.submission_order:
            return "hc-no-answers-to-review"
        return None

    def _is_review_answers_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if (
            self.status == "playing"
            and self.phase == "judging"
            and self.submission_order
            and self.is_touch_client(user)
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _format_names(self, locale: str, names: list[str]) -> str:
        """Format a player-name list with the listener's locale rules."""
        if not names:
            return ""
        return Localization.format_list_and(locale, names)

    def _speak_judge_announcement(self, user) -> None:
        judges = self._get_judges()
        if not judges:
            return
        listener = self.get_player_by_id(user.uuid)
        if listener and listener.id in {judge.id for judge in judges}:
            other_judges = [judge.name for judge in judges if judge.id != listener.id]
            if other_judges:
                user.speak_l(
                    "hc-you-and-others-are-judges",
                    buffer="game",
                    judges=self._format_names(user.locale, other_judges),
                )
            else:
                user.speak_l("hc-you-are-judge", buffer="game")
            return
        user.speak_l(
            "hc-judge-is",
            buffer="game",
            judges=self._format_names(user.locale, [judge.name for judge in judges]),
            count=len(judges),
        )

    def _action_whose_judge(self, player: Player, action_id: str) -> None:
        """Announce who the current judge(s) are."""
        user = self.get_user(player)
        if not user:
            return
        self._speak_judge_announcement(user)

    def _action_whose_turn(self, player: Player, action_id: str) -> None:
        """Override default whose_turn to show submission status."""
        user = self.get_user(player)
        if not user:
            return

        judges = self._get_judges()
        judge_names = self._format_names(user.locale, [j.name for j in judges])

        if self.phase == "submitting":
            # List who hasn't submitted
            waiting = [
                p.name for p in self._get_non_judges() if p.submitted_cards is None
            ]
            if waiting:
                user.speak_l(
                    "hc-waiting-for",
                    buffer="game",
                    names=self._format_names(user.locale, waiting),
                )
            else:
                user.speak_l(
                    "hc-all-submitted-waiting-judge", buffer="game", judge=judge_names
                )
        elif self.phase == "judging":
            user.speak_l(
                "hc-all-submitted-waiting-judge", buffer="game", judge=judge_names
            )
        else:
            user.speak_l("game-no-turn", buffer="game")

    def _is_view_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_view_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or self.current_black_card is None:
            return Visibility.HIDDEN
        user = self.get_user(player)
        if not self.is_touch_client(user):
            return Visibility.HIDDEN
        # Hide for judges during judging — prompt is shown in the header
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self.phase == "judging" and self._is_judge(hcp):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_view_submission_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self._is_judge(hcp):
            return "hc-judge-has-no-submission"
        if self.phase != "submitting" and self.phase != "judging":
            return "hc-no-submission-active"
        # During submitting: enabled if at least one card selected or already submitted
        if hcp.submitted_cards is None and not hcp.selected_indices:
            return "hc-select-cards-first"
        return None

    def _is_view_submission_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.phase not in ("submitting", "judging"):
            return Visibility.HIDDEN
        user = self.get_user(player)
        if not self.is_touch_client(user):
            return Visibility.HIDDEN
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self._is_judge(hcp):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_view_submission_label(self, player: Player, action_id: str) -> str:
        hcp: HumanityCardsPlayer = player  # type: ignore
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if hcp.submitted_cards is not None:
            return Localization.get(locale, "hc-view-submission")
        return Localization.get(locale, "hc-preview-submission")

    # ==========================================================================
    # Card and submission action handlers
    # ==========================================================================

    def _toggle_card(self, player: Player, index: int) -> None:
        """Toggle card selection for submission."""
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self.phase != "submitting" or hcp.submitted_cards is not None:
            return
        if self._is_judge(hcp):
            return
        if index >= len(hcp.hand):
            return

        required = self.current_black_card["pick"] if self.current_black_card else 1

        user = self.get_user(player)
        if index in hcp.selected_indices:
            hcp.selected_indices.remove(index)
            if user:
                user.play_sound(f"{CAH_SOUND_DIR}/cardunselect.ogg")
        else:
            if len(hcp.selected_indices) >= required:
                return
            hcp.selected_indices.append(index)
            if user:
                user.play_sound(f"{CAH_SOUND_DIR}/cardselect.ogg")

        self.refresh_menus(player)

    def _action_toggle_card(self, player: Player, action_id: str) -> None:
        self._toggle_card(player, int(action_id.removeprefix("toggle_card_")))

    def _action_judge_pick(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, int(action_id.removeprefix("judge_pick_")))

    def _action_review_hand(self, player: Player, action_id: str) -> None:
        if not isinstance(player, HumanityCardsPlayer) or player.is_spectator:
            return
        user = self.get_user(player)
        if not user:
            return
        if not player.hand:
            user.speak_l("hc-hand-empty", buffer="game")
            return

        lines: list[str] = []
        for index, card in enumerate(player.hand):
            if index in player.selected_indices:
                lines.append(
                    Localization.get(
                        user.locale,
                        "hc-hand-card-selected",
                        number=index + 1,
                        position=player.selected_indices.index(index) + 1,
                        text=card["text"],
                    )
                )
            else:
                lines.append(
                    Localization.get(
                        user.locale,
                        "hc-hand-card",
                        number=index + 1,
                        text=card["text"],
                    )
                )
        self.status_box(player, lines)

    def _ordered_answer_texts(self) -> list[str]:
        """Complete the anonymous answers in their judging order."""
        if not self.current_black_card:
            return []
        texts: list[str] = []
        for submission_index in self.submission_order:
            if submission_index >= len(self.submissions):
                continue
            texts.append(
                self._fill_in_blanks(
                    self.current_black_card["text"],
                    self.submissions[submission_index]["cards"],
                )
            )
        return texts

    def _answer_lines(self, locale: str) -> list[str]:
        """Localize the current anonymous answers for a status view."""
        return [
            Localization.get(
                locale,
                "hc-answer-line",
                number=number,
                text=text,
            )
            for number, text in enumerate(self._ordered_answer_texts(), 1)
        ]

    def _action_review_answers(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        lines = self._answer_lines(user.locale)
        if not lines:
            user.speak_l("hc-no-answers-to-review", buffer="game")
            return
        self.status_box(player, lines)

    # ==========================================================================
    # Submit / Judge action handlers
    # ==========================================================================

    def _action_submit_cards(self, player: Player, action_id: str) -> None:
        """Submit selected cards."""
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self.phase != "submitting" or hcp.submitted_cards is not None:
            return
        if self._is_judge(hcp):
            return

        required = self.current_black_card["pick"] if self.current_black_card else 1
        if len(hcp.selected_indices) != required:
            user = self.get_user(player)
            if user:
                user.speak_l("hc-wrong-card-count", buffer="game", count=required)
            return

        # Collect submitted card texts
        submitted_texts = []
        # Sort indices in selection order (the order they were picked)
        for idx in hcp.selected_indices:
            if idx < len(hcp.hand):
                card = hcp.hand[idx]
                submitted_texts.append(card["text"])

        hcp.submitted_cards = submitted_texts

        # Remove submitted cards from hand (highest index first to avoid shift)
        for idx in sorted(hcp.selected_indices, reverse=True):
            if idx < len(hcp.hand):
                removed = hcp.hand.pop(idx)
                self.white_discard.append(removed)

        hcp.selected_indices = []

        # Sound + announcement
        self.play_sound_family(f"{CAH_SOUND_DIR}/submit")
        self.broadcast_personal_l(
            player,
            "hc-you-submitted",
            "hc-player-submitted",
            buffer="game",
        )

        # Broadcast progress
        non_judges = self._get_non_judges()
        submitted_count = sum(1 for p in non_judges if p.submitted_cards is not None)
        total = len(non_judges)
        self.broadcast_l(
            "hc-submission-progress",
            buffer="game",
            submitted=submitted_count,
            total=total,
        )

        self.refresh_menus()

        # Check if all have submitted
        if submitted_count >= total:
            self._start_judging()

    def _judge_pick(self, player: Player, pick_index: int) -> None:
        """Judge picks a submission by its display index."""
        if self.phase != "judging":
            return
        hcp: HumanityCardsPlayer = player  # type: ignore
        if not self._is_judge(hcp):
            return
        if pick_index >= len(self.submission_order):
            return
        actual_idx = self.submission_order[pick_index]
        if actual_idx >= len(self.submissions):
            return

        winning_sub = self.submissions[actual_idx]
        winner = self.get_player_by_id(winning_sub["player_id"])
        if not winner:
            return

        hc_winner: HumanityCardsPlayer = winner  # type: ignore

        # Award point
        hc_winner.score += 1
        active = self.get_active_players()
        self.last_winner_index = next(
            (i for i, p in enumerate(active) if p.id == winner.id), -1
        )

        # Announce winner
        winning_text = self._fill_in_blanks(
            self.current_black_card["text"] if self.current_black_card else "",
            winning_sub["cards"],
        )

        # Play judge choice sound
        self.play_sound_family(f"{CAH_SOUND_DIR}/judgechoice")

        self.broadcast_personal_l(
            winner,
            "hc-you-win-round",
            "hc-player-wins-round",
            buffer="game",
            score=hc_winner.score,
        )

        # Announce winner's submission first
        self._broadcast_submission_reveal(winner, winning_text, winning=True)

        # Then announce other submissions
        other_submissions: list[tuple[Player, str]] = []
        for sub in self.submissions:
            if sub["player_id"] == winner.id:
                continue
            sub_player = self.get_player_by_id(sub["player_id"])
            if sub_player:
                filled = self._fill_in_blanks(
                    self.current_black_card["text"] if self.current_black_card else "",
                    sub["cards"],
                )
                other_submissions.append((sub_player, filled))
        if other_submissions:
            self.broadcast_l("hc-all-submissions", buffer="game")
            for sub_player, filled in other_submissions:
                self._broadcast_submission_reveal(sub_player, filled, winning=False)

        # Play draw card sound as players receive new cards
        self.play_sound_family("game_cards/draw")

        # Check win condition
        if hc_winner.score >= self.options.winning_score:
            self._end_game(hc_winner)
        else:
            # Keep the reveal readable before the next prompt begins.
            self.phase = "round_end"

            # Discard current black card
            if self.current_black_card:
                self.black_discard.append(self.current_black_card)
                self.current_black_card = None

            self._schedule_next_round(NEXT_ROUND_DELAY_TICKS)
            self.refresh_menus()

    def _schedule_next_round(self, delay_ticks: int) -> None:
        self.start_sequence(
            NEXT_ROUND_SEQUENCE_ID,
            [
                SequenceBeat.pause(delay_ticks),
                SequenceBeat(ops=[SequenceOperation.callback_op("start_next_round")]),
            ],
            tag=NEXT_ROUND_SEQUENCE_TAG,
            lock_scope=self.SEQUENCE_LOCK_GAMEPLAY,
            pause_bots=True,
        )

    def _action_view_black_card(self, player: Player, action_id: str) -> None:
        """View the current black card prompt."""
        user = self.get_user(player)
        if not user or not self.current_black_card:
            return
        text = self._speech_friendly_black(self.current_black_card["text"])
        user.speak_l("hc-black-card", buffer="game", text=text)

    def _action_view_submission(self, player: Player, action_id: str) -> None:
        """View the player's submitted or in-progress submission."""
        hcp: HumanityCardsPlayer = player  # type: ignore
        user = self.get_user(player)
        if not user:
            return

        if hcp.submitted_cards is not None and self.current_black_card:
            filled = self._fill_in_blanks(
                self.current_black_card["text"], hcp.submitted_cards
            )
            user.speak_l("hc-your-submission", buffer="game", text=filled)
        elif hcp.selected_indices and self.current_black_card:
            # Preview current selection
            cards = [
                hcp.hand[i]["text"] for i in hcp.selected_indices if i < len(hcp.hand)
            ]
            filled = self._fill_in_blanks(self.current_black_card["text"], cards)
            user.speak_l("hc-preview-submission-text", buffer="game", text=filled)
        else:
            user.speak_l("hc-select-cards-first", buffer="game")

    def _broadcast_submission_reveal(
        self, player: Player, text: str, *, winning: bool
    ) -> None:
        """Reveal one submission with personal wording for its owner."""
        if winning:
            self.broadcast_personal_l(
                player,
                "hc-your-winning-answer",
                "hc-winning-answer-player",
                buffer="game",
                text=text,
            )
        else:
            self.broadcast_personal_l(
                player,
                "hc-your-other-submission",
                "hc-other-submission-player",
                buffer="game",
                text=text,
            )

    # ==========================================================================
    # Score overrides
    # ==========================================================================

    def _is_check_scores_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_scores_detailed_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if self.status == "playing" and self.is_touch_client(user):
            return Visibility.VISIBLE
        return super()._is_check_scores_hidden(player)

    def _action_check_scores(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        sorted_players = sorted(
            self.get_active_players(),
            key=lambda p: p.score,  # type: ignore
            reverse=True,
        )
        for p in sorted_players:
            user.speak_l("hc-score-line", buffer="game", player=p.name, score=p.score)  # type: ignore

    def _action_check_scores_detailed(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        self.live_status_box(
            player,
            "humanitycards_scores",
            lambda _player, live_user: self._score_lines(live_user.locale),
        )

    def _score_lines(self, locale: str) -> list[str]:
        sorted_players = sorted(
            self.get_active_players(),
            key=lambda p: p.score,  # type: ignore
            reverse=True,
        )
        return [
            Localization.get(locale, "hc-score-line", player=p.name, score=p.score)  # type: ignore
            for p in sorted_players
        ]

    # ==========================================================================
    # Game lifecycle
    # ==========================================================================

    def on_start(self) -> None:
        """Called when the game starts."""
        errors = self.validate_start()
        if errors:
            for error in errors:
                if isinstance(error, tuple):
                    error_key, kwargs = error
                    self.broadcast_l(error_key, buffer="game", **kwargs)
                else:
                    self.broadcast_l(error, buffer="game")
            return

        self.status = "playing"
        self.game_active = True
        self.cancel_sequences_by_tag(NEXT_ROUND_SEQUENCE_TAG)
        self.round = 0
        self.judge_indices = []
        self.last_winner_index = -1

        # Build decks
        self._build_decks()

        active_players = self.get_active_players()

        # Reset player state
        for p in active_players:
            hp: HumanityCardsPlayer = p  # type: ignore
            hp.score = 0
            hp.hand = []
            hp.submitted_cards = None
            hp.selected_indices = []

        # Deal initial hands
        self.broadcast_l("hc-game-starting", buffer="game")
        self.broadcast_l(
            "hc-dealing-cards", buffer="game", count=self.options.hand_size
        )
        for p in active_players:
            hp: HumanityCardsPlayer = p  # type: ignore
            self._deal_to_hand_size(hp)

        # Play music
        self.play_music("game_3cardpoker/mus.ogg")

        # Start first round
        self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        self.cancel_sequences_by_tag(NEXT_ROUND_SEQUENCE_TAG)
        self.round += 1
        self.phase = "submitting"
        self.submissions = []
        self.submission_order = []

        # Play card shuffle sound at round start
        self.play_sound("game_3cardpoker/roundstart.ogg")

        active_players = self.get_active_players()

        # Reset player submission state
        for p in active_players:
            hp: HumanityCardsPlayer = p  # type: ignore
            hp.submitted_cards = None
            hp.selected_indices = []
            # Refill hand
            self._deal_to_hand_size(hp)

        # Select judge(s)
        self._select_judges()

        # Draw black card
        self.current_black_card = self._draw_black()
        if not self.current_black_card:
            self.broadcast_l("hc-not-enough-cards", buffer="game")
            self.finish_game()
            return

        pick_count = self.current_black_card.get("pick", 1)
        draw_count = self.current_black_card.get("draw", 0)

        if draw_count:
            for player in self._get_non_judges():
                player.hand.extend(self._draw_white(draw_count))

        # Announce round
        self.broadcast_l("hc-round-start", buffer="game", round=self.round)

        # Announce judge(s)
        for p in self.players:
            user = self.get_user(p)
            if user:
                self._speak_judge_announcement(user)

        # Announce black card
        black_text = self._speech_friendly_black(self.current_black_card["text"])
        self.broadcast_l("hc-black-card", buffer="game", text=black_text)
        if draw_count:
            self.broadcast_l("hc-black-card-draw", buffer="game", count=draw_count)
        if pick_count > 1:
            self.broadcast_l("hc-black-card-pick", buffer="game", count=pick_count)

        # Tell non-judges to select cards
        for p in self._get_non_judges():
            user = self.get_user(p)
            if user:
                user.speak_l(
                    "hc-select-cards",
                    buffer="game",
                    history=False,
                    count=pick_count,
                )

        # Jolt bots
        for p in active_players:
            if p.is_bot and not self._is_judge(p):
                BotHelper.jolt_bot(
                    p,
                    ticks=random.randint(*BOT_SUBMISSION_DELAY_TICKS),  # nosec B311
                )

        self.refresh_menus()

    def _start_judging(self) -> None:
        """Transition to judging phase."""
        self.phase = "judging"

        # Collect submissions
        self.submissions = []
        for p in self._get_non_judges():
            if p.submitted_cards is not None:
                self.submissions.append(
                    {
                        "player_id": p.id,
                        "cards": list(p.submitted_cards),
                    }
                )

        # Shuffle presentation order
        self.submission_order = list(range(len(self.submissions)))
        random.shuffle(self.submission_order)  # nosec B311

        self.play_sound(f"{CAH_SOUND_DIR}/judging.ogg")
        self._play_judge_turn_sounds()
        self.broadcast_l("hc-judging-start", buffer="game")
        for number, text in enumerate(self._ordered_answer_texts(), 1):
            self.broadcast_l(
                "hc-answer-line",
                buffer="game",
                number=number,
                text=text,
            )

        # Jolt judge bots
        for j in self._get_judges():
            if j.is_bot:
                BotHelper.jolt_bot(
                    j,
                    ticks=random.randint(*BOT_JUDGE_DELAY_TICKS),  # nosec B311
                )

        self.refresh_menus()

    def _end_game(self, winner: HumanityCardsPlayer) -> None:
        """End the game and announce the winner."""
        self.play_sound(f"{CAH_SOUND_DIR}/win.ogg")
        self.broadcast_personal_l(
            winner,
            "hc-you-win",
            "hc-game-winner",
            buffer="game",
            score=winner.score,
        )
        self.finish_game()

    # ==========================================================================
    # Bot AI
    # ==========================================================================

    def bot_think(self, player: HumanityCardsPlayer) -> str | None:
        """Bot AI decision making."""
        if self.phase == "submitting" and not self._is_judge(player):
            if player.submitted_cards is not None:
                return None
            required = self.current_black_card["pick"] if self.current_black_card else 1

            # Select random cards if not enough selected
            if len(player.selected_indices) < required:
                available = [
                    i
                    for i in range(len(player.hand))
                    if i not in player.selected_indices
                ]
                if available:
                    pick = random.choice(available)  # nosec B311
                    return f"toggle_card_{pick}"

            # Submit when we have enough
            if len(player.selected_indices) == required:
                return "submit_cards"

        return None

    def on_tick(self) -> None:
        """Called every tick."""
        super().on_tick()
        self.process_scheduled_sounds()
        self.process_sequences()

        if not self.game_active:
            return
        if self.is_sequence_bot_paused():
            return

        # Process bot actions
        if self.phase == "submitting":
            self._process_submission_bots()
        elif self.phase == "judging":
            self._process_judging_bots()

    def on_sequence_callback(
        self, sequence_id: str, callback_id: str, payload: dict
    ) -> None:
        if sequence_id == NEXT_ROUND_SEQUENCE_ID and callback_id == "start_next_round":
            self._start_round()
            return
        super().on_sequence_callback(sequence_id, callback_id, payload)

    def _process_submission_bots(self) -> None:
        """Process all bot actions during submission phase."""
        for player in self.players:
            if not player.is_bot or player.is_spectator:
                continue
            hcp: HumanityCardsPlayer = player  # type: ignore
            if self._is_judge(hcp) or hcp.submitted_cards is not None:
                continue

            BotHelper.process_bot_action(
                player,
                think_fn=lambda p=hcp: self.bot_think(p),
                execute_fn=lambda action_id, p=player: self.execute_action(
                    p, action_id
                ),
            )

    def _process_judging_bots(self) -> None:
        """Process judge bot actions during judging phase."""
        for judge in self._get_judges():
            if not judge.is_bot:
                continue

            if judge.bot_think_ticks > 0:
                judge.bot_think_ticks -= 1
                continue

            if judge.bot_pending_action:
                action_id = judge.bot_pending_action
                judge.bot_pending_action = None
                self.execute_action(judge, action_id)
                continue

            # Bot judge picks a random submission
            if self.submission_order:
                pick = random.randint(0, len(self.submission_order) - 1)  # nosec B311
                judge.bot_pending_action = f"judge_pick_{pick}"

    # ==========================================================================
    # Game result
    # ==========================================================================

    def build_game_result(self) -> GameResult:
        """Build the game result."""
        active_players = self.get_active_players()
        sorted_players = sorted(
            active_players,
            key=lambda p: p.score,  # type: ignore
            reverse=True,
        )

        final_scores = {}
        for p in sorted_players:
            hp: HumanityCardsPlayer = p  # type: ignore
            final_scores[p.name] = hp.score

        winner = sorted_players[0] if sorted_players else None
        winner_ids = [
            player.id
            for player in sorted_players
            if winner and player.score == winner.score  # type: ignore
        ]

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[PlayerResult.from_player(p) for p in active_players],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_ids": winner_ids,
                "winner_score": winner.score if winner else 0,  # type: ignore
                "final_scores": final_scores,
                "rounds_played": self.round,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen."""
        lines = [Localization.get(locale, "game-final-scores-header")]

        final_scores = result.custom_data.get("final_scores", {})
        for i, (name, score) in enumerate(final_scores.items(), 1):
            lines.append(
                Localization.get(
                    locale, "hc-final-score-line", rank=i, player=name, score=score
                )
            )

        return lines
