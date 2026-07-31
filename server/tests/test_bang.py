"""Rules, accessibility, persistence, and bot tests for BANG! The Bullet."""

import math
import random
import re
import struct
import wave
from collections import Counter
from collections.abc import Callable
from pathlib import Path

import pytest

from server.game_utils.actions import Visibility
from server.game_utils.sequence_runner_mixin import SequenceBeat
from server.games.bang import audio as bang_audio
from server.games.bang import bot as bang_bot
from server.games.bang import cards
from server.games.bang.cards import BangCard, BangInPlayCard
from server.games.bang.characters import ALL_CHARACTERS, character_name
from server.games.bang.events import (
    ALL_EVENTS,
    COMBINED_EVENTS,
    FISTFUL_OF_CARDS,
    FISTFUL_SET,
    HIGH_NOON,
    HIGH_NOON_SET,
    NO_EVENTS,
    build_event_deck,
    event_description,
    event_name,
)
from server.games.bang.game import (
    BOT_CHOICE_DELAY_TICKS,
    BOT_TURN_DELAY_TICKS,
    ROLE_DEPUTY,
    ROLE_OUTLAW,
    ROLE_RENEGADE,
    ROLE_SHERIFF,
    BangGame,
)
from server.games.bang.state import (
    PHASE_DISCARD,
    PHASE_GAME_OVER,
    PHASE_PLAY,
    PHASE_RESOLVING,
    PHASE_STARTING,
    PHASE_START_TURN,
    BangDecision,
    BangEffect,
    BangPlayIntent,
    DamageSource,
    ResolvingCard,
)
from server.games.registry import GameRegistry
from server.messages.localization import Localization
from server.ui.keybinds import KeybindState
from server.users.bot import Bot
from server.users.test_user import MockUser

ROOT = Path(__file__).resolve().parents[2]


def audio_duration_ticks(path: Path) -> int:
    """Read an OGG Vorbis or WAV duration without requiring a codec."""

    if path.suffix.lower() == ".wav":
        with wave.open(str(path), "rb") as wav_file:
            return math.ceil(
                wav_file.getnframes()
                * bang_audio.TICKS_PER_SECOND
                / wav_file.getframerate()
            )
    data = path.read_bytes()
    identification = data.find(b"\x01vorbis")
    assert identification >= 0, f"Missing Vorbis identification header: {path}"
    sample_rate = struct.unpack_from("<I", data, identification + 12)[0]
    offset = 0
    final_granule = 0
    while True:
        page = data.find(b"OggS", offset)
        if page < 0:
            break
        segment_count = data[page + 26]
        header_size = 27 + segment_count
        body_size = sum(data[page + 27 : page + header_size])
        granule = struct.unpack_from("<Q", data, page + 6)[0]
        if granule != 0xFFFFFFFFFFFFFFFF:
            final_granule = max(final_granule, granule)
        offset = page + header_size + body_size
    assert sample_rate > 0 and final_granule > 0, f"Invalid Vorbis timing: {path}"
    return math.ceil(
        final_granule * bang_audio.TICKS_PER_SECOND / sample_rate
    )


def make_card(
    card_id: int,
    kind: str,
    *,
    suit: str = cards.CLUBS,
    rank: str = "2",
    border: str = cards.BROWN,
) -> BangCard:
    return BangCard(
        id=card_id,
        kind=kind,
        suit=suit,
        rank=rank,
        border=border,
    )


def make_game(
    player_count: int = 4,
    *,
    bots: bool = False,
    touch: bool = False,
) -> BangGame:
    game = BangGame()
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        if bots:
            user = Bot(name)
            player = game.create_player(user.uuid, name, is_bot=True)
            game.players.append(player)
            game.attach_user(player.id, user)
            game.setup_player_actions(player)
        else:
            user = MockUser(name, uuid=f"p{index + 1}")
            if touch:
                user.client_type = "mobile"
            game.add_player(name, user)
    game.host = game.players[0].name
    return game


def start_game(
    player_count: int = 4,
    *,
    seed: int = 1,
    bots: bool = False,
    touch: bool = False,
    event_mode: str = NO_EVENTS,
) -> BangGame:
    random.seed(seed)
    game = make_game(player_count, bots=bots, touch=touch)
    game.options.event_rules = event_mode
    game.on_start()
    game.sound_scheduler_tick = bang_audio.GAME_START_DELAY_TICKS
    game.process_sequences()
    game.on_tick()
    return game


def speech_texts(game: BangGame, player_index: int) -> list[str]:
    user = game.get_user(game.players[player_index])
    if not isinstance(user, MockUser):
        return []
    return [
        message.data["text"]
        for message in user.messages
        if message.type == "speak"
    ]


def sound_names(game: BangGame, player_index: int = 0) -> list[str]:
    user = game.get_user(game.players[player_index])
    if not isinstance(user, MockUser):
        return []
    return user.get_sounds_played()


def clear_user_messages(game: BangGame) -> None:
    for player in game.players:
        user = game.get_user(player)
        if isinstance(user, MockUser):
            user.clear_messages()


def tick_until(
    game: BangGame,
    predicate: Callable[[], bool],
    *,
    limit: int = 1000,
) -> None:
    """Advance deterministic server ticks until an asynchronous effect settles."""

    for _ in range(limit):
        if predicate():
            return
        game.on_tick()
    assert predicate(), "BANG! state did not settle before the test tick limit"


def turn_menu_items(game: BangGame, player_index: int) -> dict[str, str]:
    user = game.get_user(game.players[player_index])
    assert isinstance(user, MockUser)
    return {
        item.id: item.text
        for item in user.menus["turn_menu"]["items"]
        if item.id
    }


def ftl_entries(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    current = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^[a-z0-9][a-z0-9-]*\s*=", line):
            current, value = line.split("=", 1)
            current = current.strip()
            entries[current] = value
        elif current and line[:1].isspace():
            entries[current] += f"\n{line}"
    return entries


def all_card_ids(game: BangGame) -> list[int]:
    ids = [card.id for card in game.deck]
    ids.extend(card.id for card in game.discard_pile)
    ids.extend(card.id for card in game.revealed_cards)
    ids.extend(card.id for card in game.general_store_cards)
    if game.resolving_card:
        ids.append(game.resolving_card.card.id)
    for player in game.players:
        ids.extend(card.id for card in player.hand)
        ids.extend(held.card.id for held in player.in_play)
    return ids


def test_registration_metadata_options_and_catalog_count():
    assert GameRegistry.get("bang") is BangGame
    assert len(GameRegistry.get_all()) == 44
    assert BangGame.get_name() == "BANG! The Bullet"
    assert BangGame.get_category() == "cards"
    assert (BangGame.get_min_players(), BangGame.get_max_players()) == (3, 8)
    assert BangGame().supports_score_actions() is False
    assert BangGame.get_supported_leaderboards() == [
        "wins",
        "rating",
        "games_played",
    ]
    options = BangGame().options
    assert options.expanded_cards is True
    assert options.event_rules == COMBINED_EVENTS


def test_lobby_option_labels_show_localized_current_values():
    game = make_game(4)
    player = game.players[0]
    expanded = game.options.get_option_metas()["expanded_cards"]
    events = game.options.get_option_metas()["event_rules"]

    assert expanded.get_label("en", True).endswith("On")
    assert expanded.get_label("en", False).endswith("Off")
    assert expanded.get_label("vi", True).endswith("Bật")
    assert expanded.get_label("vi", False).endswith("Tắt")
    assert "Mixed set — 12 events" in events.get_label("en", COMBINED_EVENTS)
    assert "Trộn hai nhóm — 12 biến cố" in events.get_label(
        "vi", COMBINED_EVENTS
    )

    action_set = game.options.create_options_action_set(game, player)
    assert "On" in action_set.get_action("toggle_expanded_cards").label
    assert "Mixed set — 12 events" in action_set.get_action(
        "set_event_rules"
    ).label


def test_vietnamese_title_and_distance_sentence_are_polished():
    assert (
        Localization.get("vi", "game-name-bang")
        == "BANG! Miền Tây Khói Lửa"
    )
    distance = Localization.get(
        "vi",
        "bang-distance-line",
        player="Hacker",
        distance=1,
        range=5,
    )
    report = Localization.get(
        "vi",
        "bang-your-distances",
        distances=distance,
        weapon="Winchester, tầm 5; Colt .45 nằm bên dưới",
    )
    assert ".." not in report
    assert report.endswith(".")
    assert cards.card_name(cards.CANTEEN, "vi") == "Bi đông"
    assert cards.card_name(cards.HOWITZER, "vi") == "Pháo lựu"
    assert cards.card_name(cards.PEPPERBOX, "vi") == "Súng lục nhiều nòng"
    assert cards.card_name(cards.PONY_EXPRESS, "vi") == "Kỵ mã chuyển thư"
    assert event_name(HIGH_NOON, "vi") == "Giữa trưa quyết đấu"
    assert event_name("the_judge", "vi") == "Thẩm phán"


def test_card_labels_reuse_platform_rank_and_suit_terminology():
    rank_keys = {
        "2": "rank-two",
        "10": "rank-ten",
        "J": "rank-jack",
        "Q": "rank-queen",
        "K": "rank-king",
        "A": "rank-ace",
    }
    suit_keys = {
        cards.CLUBS: "suit-clubs",
        cards.DIAMONDS: "suit-diamonds",
        cards.HEARTS: "suit-hearts",
        cards.SPADES: "suit-spades",
    }
    for locale in ("en", "vi"):
        for rank, key in rank_keys.items():
            assert cards.rank_name(rank, locale) == Localization.get(locale, key)
        for suit, key in suit_keys.items():
            assert cards.suit_name(suit, locale) == Localization.get(locale, key)

    ace = make_card(900, cards.BANG, rank="A", suit=cards.SPADES)
    jack = make_card(901, cards.MISSED, rank="J", suit=cards.CLUBS)
    assert cards.card_label(ace, "en") == "BANG!, ace of spades"
    assert cards.card_label(ace, "vi") == "BANG!, Át bích"
    assert cards.card_label(jack, "vi") == "Trượt!, J tép"


def test_prestart_validation_enforces_base_and_event_constraints():
    game = make_game(3)
    game.options.expanded_cards = False
    assert "bang-error-base-player-count" in game.prestart_validate()
    game.options.expanded_cards = True
    game.options.event_rules = "invented"
    assert "bang-error-event-mode" in game.prestart_validate()


def test_exact_deck_counts_unique_ids_and_expansion_split():
    base = cards.build_deck(include_extended_cards=False)
    bullet = cards.build_deck(include_extended_cards=True)
    assert len(base) == 80
    assert len(bullet) == 120
    assert len({card.id for card in bullet}) == 120
    assert Counter(card.expansion for card in bullet) == {
        cards.BASE: 80,
        cards.DODGE_CITY: 40,
    }
    assert Counter(card.kind for card in base)[cards.BANG] == 25
    assert Counter(card.kind for card in base)[cards.MISSED] == 12
    assert Counter(card.kind for card in bullet)[cards.DODGE] == 2
    assert Counter(card.border for card in bullet)[cards.GREEN] == 14


def test_every_card_has_detailed_english_and_vietnamese_ui_text():
    kinds = {
        spec[0]
        for spec in cards.BASE_CARD_SPECS + cards.DODGE_CITY_CARD_SPECS
    }
    assert len(kinds) == 44
    for locale in ("en", "vi"):
        for index, kind in enumerate(sorted(kinds), 1):
            key = f"bang-card-{kind.replace('_', '-')}-description"
            assert Localization.has_message(locale, key)
            detail = cards.card_detail_label(make_card(index, kind), locale)
            assert cards.card_name(kind, locale) in detail
            assert Localization.get(locale, key) in detail


def test_hand_hotkey_is_concise_while_card_rows_keep_full_descriptions():
    game = start_game(4, seed=80)
    player = game.current_player
    bang = make_card(
        1001,
        cards.BANG,
        suit=cards.SPADES,
        rank="A",
    )
    weapon = make_card(
        1002,
        cards.WINCHESTER,
        suit=cards.CLUBS,
        rank="8",
        border=cards.BLUE,
    )
    player.hand = [bang, weapon]
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    user.messages.clear()

    game._handle_keybind_event(player, {"key": "h"})

    spoken = " ".join(speech_texts(game, game.players.index(player)))
    assert "BANG!, ace of spades" in spoken
    assert "Winchester, 8 of clubs" in spoken
    assert "Brown shot card" not in spoken
    assert "Blue Weapon" not in spoken

    game.refresh_menus(player)
    game.flush_menus()
    items = turn_menu_items(game, game.players.index(player))
    assert "Brown shot card" in items[f"play_card_{bang.id}"]
    assert "Blue Weapon" in items[f"play_card_{weapon.id}"]


@pytest.mark.parametrize("locale", ["en", "vi"])
def test_bang_strings_and_nested_readouts_have_no_double_periods(locale):
    catalog = ROOT / "server" / "locales" / locale / "bang.ftl"
    assert ".." not in catalog.read_text(encoding="utf-8")

    rendered = []
    for index, event in enumerate(ALL_EVENTS):
        name = event_name(event.id, locale)
        description = event_description(event.id, locale)
        rendered.extend(
            [
                Localization.get(
                    locale,
                    "bang-current-event",
                    event=name,
                    description=description,
                    remaining=index,
                ),
                Localization.get(
                    locale,
                    "bang-event-revealed",
                    event=name,
                    description=description,
                ),
            ]
        )
    rendered.extend(
        cards.card_detail_label(card, locale)
        for card in cards.build_deck(include_extended_cards=True)
    )
    assert all(".." not in text for text in rendered)


@pytest.mark.parametrize(
    ("locale", "expected"),
    [
        ("en", "New event: High Noon."),
        ("vi", "Biến cố mới: Giữa trưa quyết đấu."),
    ],
)
def test_event_reveal_tts_names_event_without_reading_full_description(
    locale,
    expected,
):
    event = event_name(HIGH_NOON, locale)
    description = event_description(HIGH_NOON, locale)
    spoken = Localization.get(locale, "bang-event-revealed", event=event)

    assert spoken == expected
    assert description not in spoken


def test_character_and_event_content_counts_are_complete():
    assert len(ALL_CHARACTERS) == 34
    assert len({character.id for character in ALL_CHARACTERS}) == 34
    assert len(build_event_deck(HIGH_NOON_SET)) == 15
    assert len(build_event_deck(FISTFUL_SET)) == 15
    assert build_event_deck(NO_EVENTS) == []


def test_bullet_promotional_characters_remain_without_dodge_city():
    game = make_game(4)
    game.options.expanded_cards = False
    game.options.event_rules = NO_EVENTS
    random.seed(47)
    game.on_start()
    eligible = [
        character.id
        for character in ALL_CHARACTERS
        if character.expansion != cards.DODGE_CITY
    ]
    assert {"claus_the_saint", "johnny_kisch", "uncle_will"} <= set(eligible)
    assert len(eligible) == 19
    assert all(
        player.character in eligible and player.alternate_character in eligible
        for player in game.players
    )


def test_event_decks_put_a_final_event_last():
    random.seed(8)
    high_noon = build_event_deck(HIGH_NOON_SET)
    fistful = build_event_deck(FISTFUL_SET)
    combined = build_event_deck(COMBINED_EVENTS)
    assert high_noon[-1] == HIGH_NOON
    assert fistful[-1] == FISTFUL_OF_CARDS
    assert len(set(high_noon)) == 15
    assert len(set(fistful)) == 15
    assert len(combined) == 13
    assert combined[-1] in {HIGH_NOON, FISTFUL_OF_CARDS}
    assert len(set(combined[:-1])) == 12
    assert combined[-1] not in combined[:-1]


def test_vendetta_extra_turn_does_not_check_for_another_extra_turn():
    game = start_game(4, seed=74)
    actor = game.current_player
    actor.character = "bart_cassidy"
    game.effect_stack.clear()
    game.decision = None
    game.play_intent = None
    game.phase = PHASE_PLAY
    game.current_event = "vendetta"
    game.event_deck = []
    game.deck = [
        make_card(1301, cards.BEER, suit=cards.HEARTS),
        make_card(1302, cards.BANG),
        make_card(1303, cards.MISSED),
        make_card(1304, cards.BEER, suit=cards.HEARTS),
        make_card(1305, cards.BANG),
        make_card(1306, cards.MISSED),
    ]

    game._finish_turn(actor)

    assert game.current_player is actor
    assert actor.vendetta_extra_turn

    game._finish_turn(actor)

    assert game.current_player is not actor
    assert not actor.vendetta_extra_turn
    assert all(card.id != 1304 for card in game.discard_pile)


def test_abandoned_mine_redirects_kit_carlsons_draw_without_using_his_ability():
    game = make_game(4)
    player = game.players[0]
    player.character = "kit_carlson"
    player.alternate_character = "bart_cassidy"
    player.life = player.max_life = 4
    player.hand.clear()
    game.game_active = True
    game.set_turn_players(game.players)
    game.current_player = player
    game.current_event = "abandoned_mine"
    deck_card = make_card(1310, cards.BANG)
    lower_discard = make_card(1311, cards.MISSED)
    second_draw = make_card(1312, cards.BEER)
    first_draw = make_card(1313, cards.DUEL)
    game.deck = [deck_card]
    game.discard_pile = [lower_discard, second_draw, first_draw]

    game._start_draw_phase(player)

    assert game.decision is None
    assert {card.id for card in player.hand} == {1312, 1313}
    assert [card.id for card in game.discard_pile] == [1311]
    assert [card.id for card in game.deck] == [1310]
    assert player.abandoned_mine_draw_from_discard
    restored = BangGame.from_json(game.to_json())
    restored_player = restored.get_player_by_id(player.id)
    assert restored_player.abandoned_mine_draw_from_discard

    first_discard = player.hand[0]
    game.phase = PHASE_DISCARD
    game.decision = BangDecision(
        kind="discard_excess",
        player_id=player.id,
        card_ids=[card.id for card in player.hand],
        selected_card_ids=[first_discard.id],
        required=1,
    )
    game.game_active = False
    game._finish_discard_selection(player)

    assert game.deck[0] is first_discard
    assert first_discard not in game.discard_pile
    assert not player.abandoned_mine_draw_from_discard


def test_abandoned_mine_falls_back_wholly_when_discards_are_insufficient():
    game = make_game(4)
    player = game.players[0]
    player.character = "bart_cassidy"
    player.life = player.max_life = 4
    player.hand.clear()
    game.game_active = True
    game.set_turn_players(game.players)
    game.current_player = player
    game.current_event = "abandoned_mine"
    first_draw = make_card(1314, cards.BANG)
    second_draw = make_card(1315, cards.MISSED)
    deck_tail = make_card(1316, cards.BEER)
    lone_discard = make_card(1317, cards.DUEL)
    game.deck = [first_draw, second_draw, deck_tail]
    game.discard_pile = [lone_discard]

    game._start_draw_phase(player)

    assert {card.id for card in player.hand} == {1314, 1315}
    assert game.deck == [deck_tail]
    assert game.discard_pile == [lone_discard]
    assert not player.abandoned_mine_draw_from_discard


def test_abandoned_mine_uses_claus_full_draw_as_its_source_requirement():
    game = make_game(4)
    player = game.players[0]
    player.character = "claus_the_saint"
    player.life = player.max_life = 3
    player.hand.clear()
    game.game_active = True
    game.set_turn_players(game.players)
    game.current_player = player
    game.current_event = "abandoned_mine"
    deck_cards = [make_card(1320 + index, cards.BANG) for index in range(6)]
    discards = [make_card(1330 + index, cards.MISSED) for index in range(3)]
    game.deck = list(deck_cards)
    game.discard_pile = list(discards)

    game._start_draw_phase(player)

    assert game.decision and game.decision.kind == "claus_give"
    assert game.general_store_cards == deck_cards[:5]
    assert game.deck == deck_cards[5:]
    assert game.discard_pile == discards
    assert not player.abandoned_mine_draw_from_discard


def test_three_player_deputy_is_the_event_reveal_anchor():
    game = start_game(3, seed=49)
    deputy = next(player for player in game.players if player.role == ROLE_DEPUTY)
    game.effect_stack.clear()
    game.decision = None
    game.play_intent = None
    game.phase = PHASE_PLAY
    game.current_player = deputy
    game.sheriff_turns_started = 1
    game.event_deck = ["blessing"]
    game._begin_turn()
    assert game.current_event == "blessing"
    assert game.event_deck == []


@pytest.mark.parametrize(
    ("player_count", "expected"),
    [
        (3, Counter({ROLE_DEPUTY: 1, ROLE_OUTLAW: 1, ROLE_RENEGADE: 1})),
        (
            4,
            Counter({ROLE_SHERIFF: 1, ROLE_OUTLAW: 2, ROLE_RENEGADE: 1}),
        ),
        (
            5,
            Counter(
                {
                    ROLE_SHERIFF: 1,
                    ROLE_DEPUTY: 1,
                    ROLE_OUTLAW: 2,
                    ROLE_RENEGADE: 1,
                }
            ),
        ),
        (
            6,
            Counter(
                {
                    ROLE_SHERIFF: 1,
                    ROLE_DEPUTY: 1,
                    ROLE_OUTLAW: 3,
                    ROLE_RENEGADE: 1,
                }
            ),
        ),
        (
            7,
            Counter(
                {
                    ROLE_SHERIFF: 1,
                    ROLE_DEPUTY: 2,
                    ROLE_OUTLAW: 3,
                    ROLE_RENEGADE: 1,
                }
            ),
        ),
        (
            8,
            Counter(
                {
                    ROLE_SHERIFF: 1,
                    ROLE_DEPUTY: 2,
                    ROLE_OUTLAW: 3,
                    ROLE_RENEGADE: 2,
                }
            ),
        ),
    ],
)
def test_official_role_distributions(player_count, expected):
    game = BangGame()
    assert Counter(game._roles_for_count(player_count)) == expected


@pytest.mark.parametrize("player_count", range(3, 9))
def test_setup_life_hands_role_visibility_and_card_conservation(player_count):
    game = start_game(player_count, seed=player_count)
    assert game.phase == PHASE_PLAY
    assert len(all_card_ids(game)) == 120
    assert len(set(all_card_ids(game))) == 120
    for player in game.players:
        assert player.max_life in {3, 4, 5}
        assert player.life == player.max_life
        # Phase one has already added the normal opening-turn draws.
        if player is game.current_player:
            assert len(player.hand) >= player.max_life
        else:
            assert len(player.hand) == player.max_life
        if player_count == 3:
            assert player.role_revealed
        else:
            assert player.role_revealed == (player.role == ROLE_SHERIFF)
    starter = game.current_player
    assert starter.role == (ROLE_DEPUTY if player_count == 3 else ROLE_SHERIFF)
    for index, listener in enumerate(game.players):
        spoken = speech_texts(game, index)
        public_roles = next(
            text for text in spoken if text.startswith("Public role")
        )
        for subject in game.players:
            entry = (
                f"{subject.name}: "
                f"{Localization.get('en', f'bang-role-{subject.role}')}"
            )
            assert (entry in public_roles) is subject.role_revealed
        private_setup = next(
            text
            for text in spoken
            if text.startswith(
                f"You are {character_name(listener.character, 'en')}"
            )
        )
        assert Localization.get(
            "en",
            f"bang-role-{listener.role}",
        ) in private_setup
        assert "Objective:" in private_setup
        assert character_name(listener.alternate_character, "en") not in private_setup
        assert not any(
            re.match(r"Your (?:card is|\d+ cards are)", text)
            for text in spoken
        )


def test_sheriff_extra_life_is_not_a_character_ability():
    game = start_game(4, seed=11)
    sheriff = next(player for player in game.players if player.role == ROLE_SHERIFF)
    base_life = next(
        character.life
        for character in ALL_CHARACTERS
        if character.id == sheriff.character
    )
    assert sheriff.max_life == base_life + 1
    game.current_event = "hangover"
    assert sheriff.max_life == base_life + 1


def test_directed_distance_compresses_dead_seats_and_applies_modifiers():
    game = make_game(5)
    actor, neighbor, target, _, _ = game.players
    for player in game.players:
        player.character = "bart_cassidy"
        player.life = player.max_life = 4
    assert game.distance(actor, target) == 2
    neighbor.eliminated = True
    assert game.distance(actor, target) == 1
    neighbor.eliminated = False

    target.character = "paul_regret"
    target.in_play = [
        BangInPlayCard(
            make_card(1001, cards.MUSTANG, border=cards.BLUE)
        )
    ]
    assert game.distance(actor, target) == 4
    assert game.distance(target, actor) == 2

    actor.character = "rose_doolan"
    actor.in_play = [
        BangInPlayCard(
            make_card(1002, cards.SCOPE, border=cards.BLUE)
        )
    ]
    assert game.distance(actor, target) == 2


def test_ambush_lasso_belle_star_and_hangover_distance_rules():
    game = make_game(5)
    actor, _, target, _, _ = game.players
    for player in game.players:
        player.character = "bart_cassidy"
        player.life = player.max_life = 4
    actor.character = "rose_doolan"
    target.character = "paul_regret"
    actor.in_play = [
        BangInPlayCard(make_card(1101, cards.SCOPE, border=cards.BLUE))
    ]
    target.in_play = [
        BangInPlayCard(make_card(1102, cards.MUSTANG, border=cards.BLUE))
    ]
    game.current_event = "ambush"
    assert game.distance(actor, target) == 1
    game.current_event = "lasso"
    assert game.distance(actor, target) == 2
    game.current_event = "hangover"
    assert game.distance(actor, target) == 2
    game.current_event = ""
    actor.character = "belle_star"
    game.set_turn_players(game.players)
    game.current_player = actor
    assert game.distance(actor, target) == 2


def test_lasso_suspends_dynamite_and_jail_without_discarding_them():
    game = start_game(4, seed=177)
    player = game.current_player
    player.character = "bart_cassidy"
    dynamite = make_card(1110, cards.DYNAMITE, border=cards.BLUE)
    jail = make_card(1111, cards.JAIL, border=cards.BLUE)
    player.in_play = [BangInPlayCard(dynamite), BangInPlayCard(jail)]
    game.current_event = "lasso"
    deck_before = list(game.deck)
    frame = BangEffect(
        kind="turn_start",
        actor_id=player.id,
        stage="dynamite",
    )

    game._continue_turn_start(frame)
    assert frame.stage == "jail"
    assert game.decision is None
    assert game.deck == deck_before
    assert [held.card for held in player.in_play] == [dynamite, jail]

    game._continue_turn_start(frame)
    assert frame.stage == "vera"
    assert game.decision is None
    assert game.deck == deck_before
    assert [held.card for held in player.in_play] == [dynamite, jail]


def test_weapon_range_replacement_and_volcanic_bang_limit():
    game = make_game(4)
    player = game.players[0]
    player.character = "bart_cassidy"
    assert game.weapon_range(player) == 1
    player.in_play = [
        BangInPlayCard(
            make_card(1201, cards.WINCHESTER, border=cards.BLUE)
        )
    ]
    assert game.weapon_range(player) == 5
    assert game._bang_limit(player) == 1
    player.in_play = [
        BangInPlayCard(
            make_card(1202, cards.VOLCANIC, border=cards.BLUE)
        )
    ]
    assert game._bang_limit(player) is None
    game.current_event = "lasso"
    assert game.weapon_range(player) == 1
    assert game._bang_limit(player) == 1


def test_every_bang_audio_asset_exists_in_all_shipped_sound_packs():
    assert len(bang_audio.BANG_ASSET_PATHS) == 67
    assert len(set(bang_audio.BANG_ASSET_PATHS)) == 67
    assert all(
        bang_audio.AUDIO_DURATIONS_TICKS[path] > 0
        for path in bang_audio.BANG_ASSET_PATHS
    )
    reference_bytes: dict[str, bytes] = {}
    for pack_root in (
        ROOT / "client" / "sounds",
        ROOT / "web_client" / "sounds",
        ROOT / "mobile_client" / "sounds",
    ):
        bang_root = pack_root / "game_bang"
        assert {
            f"game_bang/{path.name}"
            for path in bang_root.iterdir()
            if path.is_file()
        } == set(bang_audio.BANG_ASSET_PATHS)
        assert all(
            (pack_root / path).is_file()
            for path in bang_audio.BANG_ASSET_PATHS
        )
        for path in bang_audio.BANG_ASSET_PATHS:
            data = (pack_root / path).read_bytes()
            if path in reference_bytes:
                assert data == reference_bytes[path], path
            else:
                reference_bytes[path] = data

    for sound, expected_ticks in bang_audio.AUDIO_DURATIONS_TICKS.items():
        path = ROOT / "client" / "sounds" / sound
        assert path.is_file(), sound
        assert audio_duration_ticks(path) == expected_ticks
    assert bang_audio.sound_ticks(
        bang_audio.SOUND_FIRE_GATLING[0]
    ) == bang_audio.AUDIO_DURATIONS_TICKS[
        bang_audio.SOUND_FIRE_GATLING[0]
    ]


def test_audio_overlap_profiles_stay_in_the_requested_cinematic_band():
    standard_ratios = (
        bang_audio.WAIT_RATIO_LONG_EFFECT,
        bang_audio.WAIT_RATIO_GUNSHOT,
        bang_audio.WAIT_RATIO_CASING,
        bang_audio.WAIT_RATIO_REACTION,
        bang_audio.WAIT_RATIO_IMPACT,
        bang_audio.WAIT_RATIO_SHORT_CUE,
    )

    assert all(0.05 <= ratio <= 0.15 for ratio in standard_ratios)
    assert 0.30 <= bang_audio.WAIT_RATIO_FAILED_DEFENSE <= 0.60
    assert bang_audio.WAIT_RATIO_BARRAGE_LEAD == 0.0
    assert bang_audio.WAIT_RATIO_FULL_CUE == 1.0
    assert bang_audio.LETHAL_FALL_TRIGGER_RATIO == pytest.approx(0.30)
    assert bang_audio.ELIMINATION_FALL_STAGGER_TICKS == 1


def test_game_intro_delays_the_first_turn_by_ten_seconds():
    game = make_game(4)
    game.options.event_rules = NO_EVENTS
    clear_user_messages(game)

    game.on_start()
    game.flush_menus()

    assert bang_audio.GAME_START_DELAY_TICKS == 10 * bang_audio.TICKS_PER_SECOND
    assert game.phase == PHASE_STARTING
    assert game.is_sequence_gameplay_locked()
    assert game.has_active_sequence(tag="bang_game_intro")
    assert sound_names(game)[0] == bang_audio.SOUND_GAME_INTRO
    user = game.get_user(game.players[0])
    assert isinstance(user, MockUser)
    assert any(
        message.type == "play_ambience"
        and message.data["loop"] == bang_audio.SOUND_AMBIENCE_WESTERN
        for message in user.messages
    )
    assert "input_prompt" not in turn_menu_items(game, 0)
    intro_history = [
        message
        for message in user.messages
        if message.type == "speak"
        and "High noon settles over the town" in message.data["text"]
    ]
    assert len(intro_history) == 1
    assert intro_history[0].data == {
        "text": "High noon settles over the town; every hand drifts toward a holster.",
        "buffer": "game",
    }
    assert not any(
        "BANG! begins." in text for text in speech_texts(game, 0)
    )

    for _ in range(bang_audio.GAME_START_DELAY_TICKS - 1):
        game.on_tick()
    assert game.phase == PHASE_STARTING
    assert game.is_sequence_gameplay_locked()

    game.on_tick()

    assert game.phase == PHASE_PLAY
    assert not game.is_sequence_gameplay_locked()
    assert any("BANG! begins." in text for text in speech_texts(game, 0))
    user = game.get_user(game.players[0])
    assert isinstance(user, MockUser)
    assert any(
        message.type == "play_music"
        and message.data["name"] == bang_audio.SOUND_MUSIC_GAMEPLAY
        for message in user.messages
    )


def test_lobby_music_is_stopped_before_bang_intro_and_delayed_bgm():
    game = make_game(4)
    game.options.event_rules = NO_EVENTS
    game.play_music("test/waiting_music.ogg")
    clear_user_messages(game)

    game._start_game_from_lobby()

    user = game.get_user(game.players[0])
    assert isinstance(user, MockUser)
    stop_index = next(
        index
        for index, message in enumerate(user.messages)
        if message.type == "stop_music"
    )
    intro_index = next(
        index
        for index, message in enumerate(user.messages)
        if (
            message.type == "play_sound"
            and message.data.get("name") == bang_audio.SOUND_GAME_INTRO
        )
    )
    assert stop_index < intro_index
    assert not [
        message
        for message in user.messages
        if (
            message.type == "play_music"
            and message.data.get("name") == bang_audio.SOUND_MUSIC_GAMEPLAY
        )
    ]

    for _ in range(bang_audio.GAME_START_DELAY_TICKS):
        game.on_tick()

    assert any(
        message.type == "play_music"
        and message.data.get("name") == bang_audio.SOUND_MUSIC_GAMEPLAY
        for message in user.messages
    )


def test_intro_delay_survives_json_round_trip():
    game = make_game(4)
    game.options.event_rules = NO_EVENTS
    game.on_start()

    restored = BangGame.from_json(game.to_json())
    restored.rebuild_runtime_state()

    assert restored.phase == PHASE_STARTING
    assert restored.has_active_sequence(tag="bang_game_intro")
    for _ in range(bang_audio.GAME_START_DELAY_TICKS):
        restored.on_tick()
    assert restored.phase == PHASE_PLAY
    assert not restored.has_active_sequence(tag="bang_game_intro")


def test_event_reveal_announcement_is_tts_only():
    game = start_game(4, seed=100)
    clear_user_messages(game)

    game._announce_event_revealed("curse")

    assert not sound_names(game)
    assert any(
        "Curse" in text
        for text in speech_texts(game, 0)
    )


def test_delayed_green_card_placement_uses_card_feedback_not_effect_audio():
    game = start_game(4, seed=101)
    actor = game.current_player
    canteen = make_card(1189, cards.CANTEEN, border=cards.GREEN)
    actor.hand = [canteen]
    clear_user_messages(game)

    game._start_card_intent(actor, canteen)

    assert any(in_play.card is canteen for in_play in actor.in_play)
    sounds = set(sound_names(game))
    assert sounds & set(bang_audio.SOUND_CARD_PLAY)
    assert bang_audio.SOUND_DRINK_CANTEEN not in sounds


def test_targeted_green_card_is_placed_without_target_then_targets_when_used():
    game = start_game(4, seed=103)
    actor = game.current_player
    others = game._clockwise_after(actor, exclude_actor=True)
    can_can = make_card(1194, cards.CAN_CAN, border=cards.GREEN)
    actor.hand = [can_can]
    for target in others:
        target.hand.clear()
        target.in_play.clear()

    assert game._normal_card_error(actor, can_can) is None
    game._start_card_intent(actor, can_can)

    assert game.play_intent is None
    assert can_can not in actor.hand
    placed = next(
        in_play for in_play in actor.in_play if in_play.card.id == can_can.id
    )
    assert placed.usable_after_turn == game.turn_serial + 1

    first_card = make_card(1195, cards.BEER)
    second_card = make_card(1196, cards.MISSED)
    others[0].hand = [first_card]
    others[1].hand = [second_card]
    placed.usable_after_turn = game.turn_serial

    game._action_use_in_play(actor, f"use_in_play_{can_can.id}")

    assert game.play_intent is not None
    assert game.play_intent.kind == "green"
    assert game.play_intent.stage == "target"
    assert first_card in others[0].hand
    assert second_card in others[1].hand

    game._action_choose_player(actor, f"choose_player_{others[1].id}")

    assert game.play_intent is None
    assert all(in_play.card.id != can_can.id for in_play in actor.in_play)
    assert first_card in others[0].hand
    assert second_card not in others[1].hand
    assert {can_can.id, second_card.id} <= {
        card.id for card in game.discard_pile
    }


def test_stealing_a_card_has_card_transfer_audio():
    game = start_game(4, seed=102)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    panic = make_card(1192, cards.PANIC)
    stolen = make_card(1193, cards.BEER)
    actor.hand = [panic]
    for player in game.players:
        if player is not actor:
            player.hand = []
            player.in_play = []
    target.hand = [stolen]
    clear_user_messages(game)

    game._start_card_intent(actor, panic)

    assert stolen in actor.hand
    assert set(sound_names(game)) & set(bang_audio.SOUND_CARD_DRAW)


@pytest.mark.parametrize(
    ("weapon_kind", "expected_sounds"),
    [
        ("colt45", bang_audio.SOUND_FIRE_COLT45),
        *list(bang_audio.WEAPON_FIRE_SOUNDS.items()),
    ],
)
def test_bang_shot_uses_the_effective_weapon_sound(
    weapon_kind,
    expected_sounds,
):
    game = start_game(4, seed=91)
    actor = game.current_player
    target = next(player for player in game.players if player is not actor)
    target.hand.clear()
    target.in_play.clear()
    if weapon_kind != "colt45":
        actor.in_play = [
            BangInPlayCard(
                make_card(1190, weapon_kind, border=cards.BLUE)
            )
        ]
    else:
        actor.in_play.clear()
    clear_user_messages(game)

    game._start_shot(
        actor,
        target,
        source_kind="bang_card",
        required=1,
    )

    assert set(sound_names(game)) & set(expected_sounds)
    assert not (
        set(sound_names(game))
        & {
            sound
            for kind, sounds in bang_audio.WEAPON_FIRE_SOUNDS.items()
            if kind != weapon_kind
            for sound in sounds
        }
    )


def test_named_attack_sound_overrides_the_equipped_weapon():
    game = start_game(4, seed=92)
    actor = game.current_player
    target = next(player for player in game.players if player is not actor)
    actor.in_play = [
        BangInPlayCard(
            make_card(1191, cards.WINCHESTER, border=cards.BLUE)
        )
    ]
    target.hand.clear()
    target.in_play.clear()
    clear_user_messages(game)

    game._start_shot(
        actor,
        target,
        source_kind=cards.BUFFALO_RIFLE,
        required=1,
    )

    sounds = set(sound_names(game))
    assert sounds & set(bang_audio.SOUND_FIRE_BUFFALO_RIFLE)
    assert not sounds & set(bang_audio.SOUND_FIRE_WINCHESTER)


def test_gatling_plays_one_barrage_while_all_targets_resolve():
    game = start_game(4, seed=118)
    actor = game.current_player
    targets = game._clockwise_after(actor, exclude_actor=True)
    starting_life = {target.id: target.life for target in targets}
    for target in targets:
        target.character = "bart_cassidy"
        target.hand.clear()
        target.in_play.clear()
    missed = make_card(1194, cards.MISSED)
    targets[0].hand = [missed]
    clear_user_messages(game)

    game._start_multi_shot(actor, kind=cards.GATLING)

    assert game.decision and game.decision.kind == "missed"
    assert game.decision.player_id == targets[0].id
    assert sound_names(game).count(bang_audio.SOUND_FIRE_GATLING[0]) == 1
    assert all(target.life == starting_life[target.id] for target in targets)

    game._use_decision_card(targets[0], missed)

    tick_until(
        game,
        lambda: not game.effect_stack and not game.active_sequences,
    )

    assert targets[0].life == starting_life[targets[0].id]
    assert all(
        target.life == starting_life[target.id] - 1
        for target in targets[1:]
    )
    assert sound_names(game).count(bang_audio.SOUND_FIRE_GATLING[0]) == 1


def test_howitzer_plays_one_cannon_blast_for_the_table_attack():
    game = start_game(4, seed=120)
    actor = game.current_player
    targets = game._clockwise_after(actor, exclude_actor=True)
    starting_life = {target.id: target.life for target in targets}
    for target in targets:
        target.character = "bart_cassidy"
        target.hand.clear()
        target.in_play.clear()
    clear_user_messages(game)

    game._start_multi_shot(actor, kind=cards.HOWITZER)
    assert sound_names(game).count(bang_audio.SOUND_FIRE_HOWITZER[0]) == 1

    tick_until(
        game,
        lambda: not game.effect_stack and not game.active_sequences,
    )

    assert all(
        target.life == starting_life[target.id] - 1
        for target in targets
    )
    assert sound_names(game).count(bang_audio.SOUND_FIRE_HOWITZER[0]) == 1


def test_indians_failure_uses_generic_damage_impact():
    game = start_game(4, seed=167)
    actor = game.current_player
    actor.character = "willy_the_kid"
    for target in game._clockwise_after(actor, exclude_actor=True):
        target.character = "willy_the_kid"
        target.hand.clear()
        target.in_play.clear()
    clear_user_messages(game)

    game._start_indians(actor)

    assert bang_audio.SOUND_IMPACT_GENERIC in sound_names(game)
    assert any(
        "loses 1 life" in text
        for text in speech_texts(game, 0)
    )


def test_indians_bang_response_uses_the_defenders_weapon():
    game = start_game(4, seed=168)
    actor = game.current_player
    defender = game._clockwise_after(actor, exclude_actor=True)[0]
    response = make_card(2750, cards.BANG)
    defender.hand = [response]
    defender.in_play = [
        BangInPlayCard(
            make_card(2751, cards.WINCHESTER, border=cards.BLUE)
        )
    ]
    clear_user_messages(game)

    game._start_indians(actor)

    assert game.decision and game.decision.player_id == defender.id
    game._use_decision_card(defender, response)

    assert set(sound_names(game)) & set(
        bang_audio.SOUND_FIRE_WINCHESTER
    )
    assert bang_audio.SOUND_IMPACT_GENERIC not in sound_names(game)


def test_gunshot_impact_starts_after_proportional_audio_lead():
    game = start_game(4, seed=119)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    target.hand.clear()
    target.in_play.clear()
    starting_life = target.life
    clear_user_messages(game)

    game._start_shot(
        actor,
        target,
        source_kind="bang_card",
        required=1,
    )

    fire_sound = next(
        sound
        for sound in sound_names(game)
        if sound in bang_audio.SOUND_FIRE_COLT45
    )
    wait_ticks = SequenceBeat.audio_delay_ticks(
        bang_audio.sound_ticks(fire_sound),
        wait_ratio=bang_audio.WAIT_RATIO_GUNSHOT,
    )
    assert target.life == starting_life
    assert not set(sound_names(game)) & set(
        bang_audio.SOUND_IMPACT_BULLET_BODY
    )

    for _ in range(wait_ticks - 1):
        game.on_tick()
    assert target.life == starting_life

    game.on_tick()
    assert target.life == starting_life - 1
    assert set(sound_names(game)) & set(
        bang_audio.SOUND_IMPACT_BULLET_BODY
    )


def test_weapon_and_bang_menu_labels_distinguish_equipping_from_firing():
    bang = make_card(1203, cards.BANG)
    weapon = make_card(1204, cards.WINCHESTER, border=cards.BLUE)

    assert cards.card_play_label(bang, "en").startswith("Shot card:")
    assert "Fire at one player" in cards.card_play_label(bang, "en")
    assert cards.card_play_label(weapon, "en").startswith("Weapon to equip:")
    assert "Equip it for range 5" in cards.card_play_label(weapon, "en")
    assert "permanent Colt" not in cards.card_play_label(weapon, "en")
    assert cards.card_play_label(bang, "vi").startswith("Lá khai hỏa:")
    assert cards.card_play_label(weapon, "vi").startswith("Trang bị súng:")
    assert not cards.card_detail_label(weapon, "en").startswith(
        "Weapon to equip:"
    )


def test_equipping_weapon_announces_range_and_replacement_to_all_audiences():
    game = start_game(4, seed=63)
    actor = game.current_player
    observer = next(player for player in game.players if player is not actor)
    actor_index = game.players.index(actor)
    observer_index = game.players.index(observer)
    old_weapon = make_card(1205, cards.SCHOFIELD, border=cards.BLUE)
    new_weapon = make_card(1206, cards.WINCHESTER, border=cards.BLUE)
    actor.in_play = [BangInPlayCard(old_weapon)]
    actor.hand = [new_weapon]
    for listener in (actor, observer):
        user = game.get_user(listener)
        assert isinstance(user, MockUser)
        user.messages.clear()

    game._start_card_intent(actor, new_weapon)

    assert game.weapon_range(actor) == 5
    assert old_weapon in game.discard_pile
    assert actor.in_play[0].card is new_weapon
    assert any(
        "You discard Schofield and equip Winchester" in text
        and "range 5" in text
        for text in speech_texts(game, actor_index)
    )
    assert any(
        f"{actor.name} discards Schofield and equips Winchester" in text
        and "range 5" in text
        for text in speech_texts(game, observer_index)
    )
    assert not any("fire" in text.lower() for text in speech_texts(game, actor_index))


def test_weapon_equipping_and_reverting_to_colt_use_matching_draw_sounds():
    game = start_game(4, seed=163)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    weapon = make_card(1209, cards.WINCHESTER, border=cards.BLUE)
    actor.hand = [weapon]
    clear_user_messages(game)

    game._start_card_intent(actor, weapon)

    assert bang_audio.SOUND_EQUIP_WINCHESTER in sound_names(game)

    panic = make_card(1210, cards.PANIC)
    stolen_weapon = make_card(1214, cards.SCHOFIELD, border=cards.BLUE)
    actor.hand = [panic]
    for player in game.players:
        if player is not actor:
            player.hand.clear()
            player.in_play.clear()
    target.in_play = [BangInPlayCard(stolen_weapon)]
    clear_user_messages(game)

    game._start_card_intent(actor, panic)

    assert not target.in_play
    assert stolen_weapon in actor.hand
    assert bang_audio.SOUND_EQUIP_COLT45 in sound_names(game)


def test_dynamite_and_jail_use_dedicated_state_transition_sounds():
    game = start_game(4, seed=164)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    dynamite = make_card(1211, cards.DYNAMITE, border=cards.BLUE)
    jail = make_card(1212, cards.JAIL, border=cards.BLUE)
    clear_user_messages(game)

    game._put_card_in_play(actor, dynamite, None)
    game._put_card_in_play(actor, jail, target)

    sounds = sound_names(game)
    assert bang_audio.SOUND_DYNAMITE_PLACE in sounds
    assert bang_audio.SOUND_JAIL_CLOSE in sounds

    game.current_player = target
    game.deck = [
        make_card(1213, cards.BANG, suit=cards.HEARTS, rank="4")
    ]
    game.phase = PHASE_START_TURN
    game.effect_stack = [
        BangEffect(
            kind="turn_start",
            actor_id=target.id,
            stage="jail",
        )
    ]
    game.decision = None
    clear_user_messages(game)

    game._continue_effects()

    assert bang_audio.SOUND_JAIL_OPEN in sound_names(game)
    assert all(in_play.card is not jail for in_play in target.in_play)


def test_equipped_weapon_reports_when_lasso_keeps_it_inactive():
    game = start_game(4, seed=72)
    actor = game.current_player
    weapon = make_card(1207, cards.WINCHESTER, border=cards.BLUE)
    actor.hand = [weapon]
    actor.in_play = []
    game.current_event = "lasso"
    actor_user = game.get_user(actor)
    assert isinstance(actor_user, MockUser)
    actor_user.messages.clear()

    game._start_card_intent(actor, weapon)

    assert actor.in_play[0].card is weapon
    assert game.weapon_range(actor) == 1
    assert any(
        "equip Winchester, but Lasso disables it" in text
        and "Colt .45 remains active, range 1" in text
        for text in speech_texts(game, game.players.index(actor))
    )


def test_first_weapon_names_the_colt_it_covers_for_all_audiences():
    game = start_game(4, seed=73)
    actor = game.current_player
    observer = next(player for player in game.players if player is not actor)
    weapon = make_card(1208, cards.REMINGTON, border=cards.BLUE)
    actor.hand = [weapon]
    actor.in_play = []
    for listener in (actor, observer):
        user = game.get_user(listener)
        assert isinstance(user, MockUser)
        user.messages.clear()

    game._start_card_intent(actor, weapon)

    actor_texts = speech_texts(game, game.players.index(actor))
    observer_texts = speech_texts(game, game.players.index(observer))
    assert any(
        "You equip Remington; range 3" in text
        for text in actor_texts
    )
    assert any(
        f"{actor.name} equips Remington; range 3" in text
        for text in observer_texts
    )


def test_public_status_always_identifies_effective_and_equipped_weapon():
    game = make_game(4)
    player = game.players[0]
    player.role = ROLE_SHERIFF
    player.role_revealed = True
    player.character = "bart_cassidy"
    player.alternate_character = "black_jack"
    player.life = player.max_life = 4
    user = game.get_user(player)
    assert isinstance(user, MockUser)

    default_status = game._build_table_status(player, user)
    default_line = next(
        item.text for item in default_status.items if item.id == f"player:{player.id}"
    )
    assert "weapon: Colt .45, range 1" in default_line

    player.in_play = [
        BangInPlayCard(make_card(1209, cards.WINCHESTER, border=cards.BLUE))
    ]
    equipped_status = game._build_table_status(player, user)
    equipped_line = next(
        item.text for item in equipped_status.items if item.id == f"player:{player.id}"
    )
    assert "weapon: Winchester, range 5" in equipped_line

    game.current_event = "lasso"
    inactive_status = game._build_table_status(player, user)
    inactive_line = next(
        item.text for item in inactive_status.items if item.id == f"player:{player.id}"
    )
    assert (
        "weapon: Colt .45, range 1; Winchester inactive"
        in inactive_line
    )


def test_public_status_distinguishes_an_active_ghost_from_elimination():
    game = make_game(4)
    player = game.players[0]
    player.role = ROLE_OUTLAW
    player.role_revealed = True
    player.character = "bart_cassidy"
    player.life = player.max_life = 4
    player.eliminated = True
    player.ghost_active = True
    user = game.get_user(player)
    assert isinstance(user, MockUser)

    status = game._build_table_status(player, user)
    line = next(
        item.text for item in status.items if item.id == f"player:{player.id}"
    )

    assert "status: active as a Ghost Town ghost" in line


def test_calamity_janet_can_play_missed_as_bang():
    game = start_game(4, seed=4)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    actor.character = "calamity_janet"
    converted = make_card(2001, cards.MISSED)
    actor.hand = [converted]
    actor.bangs_played = 0
    target.hand = []
    target.in_play = []
    target.life = 3
    assert game._normal_card_error(actor, converted) is None
    game._start_card_intent(actor, converted)
    assert game.play_intent
    assert game.play_intent.stage == "target"
    assert game.play_intent.data["as_bang"] is True
    game._action_choose_player(actor, f"choose_player_{target.id}")
    tick_until(game, lambda: target.life == 2)
    assert target.life == 2
    assert game.play_intent is None
    assert actor.bangs_played == 1
    tick_until(game, lambda: converted in game.discard_pile)
    assert converted in game.discard_pile


def test_calamity_janet_can_answer_with_bang_and_elena_with_any_card():
    game = make_game(4)
    calamity, elena = game.players[:2]
    calamity.character = "calamity_janet"
    elena.character = "elena_fuente"
    assert game._card_can_miss(calamity, make_card(2101, cards.BANG))
    assert game._card_can_be_bang_response(
        calamity,
        make_card(2102, cards.MISSED),
    )
    assert game._card_can_miss(elena, make_card(2103, cards.BEER))


def test_calamity_missed_cards_pay_sniper_and_ricochet_bang_costs():
    game = start_game(4, seed=41)
    actor = game.current_player
    actor.character = "calamity_janet"
    actor.hand = [
        make_card(2111, cards.MISSED),
        make_card(2112, cards.MISSED),
    ]
    game.current_event = "sniper"
    assert game._is_sniper_enabled(actor) is None
    game.current_event = "ricochet"
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    target.in_play = [
        BangInPlayCard(make_card(2113, cards.BARREL, border=cards.BLUE))
    ]
    assert game._is_ricochet_enabled(actor) is None


def test_forged_or_wrong_additional_cost_is_rejected_without_consumption():
    game = start_game(4, seed=5)
    actor = game.current_player
    first = make_card(2201, cards.BANG)
    second = make_card(2202, cards.BANG)
    wrong = make_card(2203, cards.BEER)
    actor.hand = [first, second, wrong]
    game.current_event = "sniper"
    game.play_intent = BangPlayIntent(
        kind="sniper",
        actor_id=actor.id,
        required=2,
        stage="cost",
        selected_card_ids=[first.id, wrong.id],
        data={"allowed_card_ids": [first.id, second.id]},
    )
    assert game._is_play_card_enabled(
        actor,
        action_id=f"play_card_{wrong.id}",
    ) == "bang-error-card-not-valid-cost"
    game._commit_intent()
    assert game.play_intent is None
    assert actor.hand == [first, second, wrong]
    assert game.discard_pile == []


def test_multi_cost_picker_announces_toggle_state_and_enforces_exact_limit():
    game = start_game(4, seed=52)
    actor = game.current_player
    first = make_card(2204, cards.BANG)
    second = make_card(2205, cards.MISSED)
    third = make_card(2206, cards.BEER)
    actor.hand = [first, second, third]
    game.decision = None
    game.effect_stack.clear()
    game.phase = PHASE_PLAY
    game.play_intent = BangPlayIntent(
        kind="doc_holyday",
        actor_id=actor.id,
        required=2,
        stage="cost",
        data={"allowed_card_ids": [first.id, second.id, third.id]},
    )

    game._action_play_card(actor, f"play_card_{first.id}")
    assert game.play_intent.selected_card_ids == [first.id]
    game._action_play_card(actor, f"play_card_{second.id}")
    assert game.play_intent.selected_card_ids == [first.id, second.id]
    game._action_play_card(actor, f"play_card_{third.id}")
    assert game.play_intent.selected_card_ids == [first.id, second.id]

    actor_index = game.players.index(actor)
    game.flush_menus()
    items = turn_menu_items(game, actor_index)
    assert list(items)[-2:] == ["confirm_selection", "cancel_selection"]
    spoken = speech_texts(game, actor_index)
    assert any("Selected BANG!" in text for text in spoken)
    assert any("Only 2 cards" in text for text in spoken)


def test_single_cost_advances_immediately_without_confirm():
    game = start_game(4, seed=54)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    rag_time = make_card(2207, cards.RAG_TIME)
    cost = make_card(2208, cards.BEER)
    actor.hand = [rag_time, cost]
    target.hand = [make_card(2209, cards.BANG)]
    game.decision = None
    game.effect_stack.clear()
    game.phase = PHASE_PLAY

    game._start_card_intent(actor, rag_time)
    assert game.play_intent and game.play_intent.stage == "cost"
    assert game._is_confirm_hidden(actor) is Visibility.HIDDEN
    game.flush_menus()
    items = turn_menu_items(game, game.players.index(actor))
    assert list(items)[-1] == "cancel_selection"
    assert "confirm_selection" not in items
    assert "Choose 1 card for Rag Time" in items["input_prompt"]
    game._action_play_card(actor, f"play_card_{cost.id}")

    assert game.play_intent is not None
    assert game.play_intent.stage == "target"
    assert game.play_intent.selected_card_ids == [cost.id]
    assert rag_time in actor.hand and cost in actor.hand

    game._action_cancel_selection(actor, "cancel_selection")
    assert game.play_intent is None
    assert rag_time in actor.hand and cost in actor.hand
    assert any(
        "Canceled Rag Time; all cards remain in place." in text
        for text in speech_texts(game, game.players.index(actor))
    )


def test_single_target_commits_immediately_with_cancel_last():
    game = start_game(4, seed=55)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    actor_index = game.players.index(actor)
    cat_balou = make_card(2208, cards.CAT_BALOU)
    target.hand = [make_card(2209, cards.BEER)]
    target.in_play = []
    actor.hand = [cat_balou]
    game.decision = None
    game.effect_stack.clear()
    game.phase = PHASE_PLAY

    game._start_card_intent(actor, cat_balou)
    assert game.play_intent is not None
    assert cat_balou in actor.hand
    assert game.decision is None
    game.flush_menus()
    items = turn_menu_items(game, actor_index)
    assert list(items)[-1] == "cancel_selection"
    assert "confirm_selection" not in items
    assert "choose a target, or Cancel" in items["input_prompt"]
    assert target.name in items[f"choose_player_{target.id}"]

    game._action_choose_player(actor, f"choose_player_{target.id}")
    assert game.play_intent is None
    assert cat_balou not in actor.hand
    assert game.decision is None
    assert target.hand == []
    assert any(card.id == 2209 for card in game.discard_pile)


def test_only_legal_target_and_only_target_card_are_selected_automatically():
    game = start_game(4, seed=91)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    cat_balou = make_card(2212, cards.CAT_BALOU)
    discarded = make_card(2213, cards.BEER)
    actor.hand = [cat_balou]
    for other in game.players:
        if other is not actor:
            other.hand = []
            other.in_play = []
    target.hand = [discarded]
    game.decision = None
    game.effect_stack.clear()
    game.phase = PHASE_PLAY

    game._start_card_intent(actor, cat_balou)

    assert game.play_intent is None
    assert game.decision is None
    assert cat_balou in game.discard_pile
    assert discarded in game.discard_pile
    assert target.hand == []


def test_discard_menu_shows_instruction_progress_and_both_toggle_states():
    game = start_game(4, seed=53)
    actor = game.current_player
    actor_index = game.players.index(actor)
    first = make_card(2206, cards.BANG)
    second = make_card(2207, cards.BEER)
    third = make_card(2210, cards.MISSED)
    actor.hand = [first, second, third]
    game.phase = PHASE_DISCARD
    game.decision = BangDecision(
        kind="discard_excess",
        player_id=actor.id,
        prompt_key="bang-prompt-discard-excess",
        card_ids=[first.id, second.id, third.id],
        required=2,
    )
    game.refresh_menus(actor)
    game.flush_menus()

    items = turn_menu_items(game, actor_index)
    assert next(iter(items)) == "input_prompt"
    assert "Next:" in items["input_prompt"]
    assert "Discard 2 excess cards in order: select the first" in items[
        "input_prompt"
    ]
    assert "0 of 2" not in items["input_prompt"]
    assert "Not selected for discard:" in items[f"play_card_{first.id}"]
    assert "Fire at one player within your current weapon range" in items[
        f"play_card_{first.id}"
    ]
    assert "Shot card:" not in items[f"play_card_{first.id}"]

    actor_user = game.get_user(actor)
    assert isinstance(actor_user, MockUser)
    actor_user.clear_messages()
    game._action_play_card(actor, f"play_card_{first.id}")
    game.flush_menus()
    items = turn_menu_items(game, actor_index)
    assert "1 selected; choose 1 more" in items["input_prompt"]
    assert "Selected for discard:" in items[f"play_card_{first.id}"]
    assert "choose 1 more card" in items["confirm_selection"]
    turn_updates = [
        message
        for message in actor_user.messages
        if message.type == "show_menu"
        and message.data["menu_id"] == "turn_menu"
    ]
    assert turn_updates
    assert turn_updates[-1].data["selection_id"] is None
    assert speech_texts(game, actor_index) == [
        "Will discard BANG!, 2 of clubs. Choose 1 more."
    ]

    game._action_play_card(actor, f"play_card_{second.id}")
    game.flush_menus()
    items = turn_menu_items(game, actor_index)
    assert "Ready to Confirm or change the selection" in items["input_prompt"]
    assert "Selected for discard:" in items[f"play_card_{first.id}"]
    assert "2 selected" in items["confirm_selection"]
    assert any(
        "Will discard BANG!, 2 of clubs. Choose 1 more." in text
        for text in speech_texts(game, actor_index)
    )

    game._action_play_card(actor, f"play_card_{first.id}")
    game.flush_menus()
    items = turn_menu_items(game, actor_index)
    assert "Not selected for discard:" in items[f"play_card_{first.id}"]
    assert any(
        "Will keep BANG!, 2 of clubs. Choose 1 more card to discard."
        in text
        for text in speech_texts(game, actor_index)
    )


def test_single_excess_discard_commits_immediately():
    game = start_game(4, seed=56)
    actor = game.current_player
    actor_index = game.players.index(actor)
    excess = make_card(2211, cards.BANG)
    actor.hand = [excess]
    game.phase = PHASE_DISCARD
    game.decision = BangDecision(
        kind="discard_excess",
        player_id=actor.id,
        prompt_key="bang-prompt-discard-excess",
        card_ids=[excess.id],
        required=1,
    )

    assert game._is_confirm_hidden(actor) is Visibility.HIDDEN
    game._action_play_card(actor, f"play_card_{excess.id}")

    assert not (
        game.decision
        and game.decision.kind == "discard_excess"
        and game.decision.player_id == actor.id
    )
    assert excess not in actor.hand
    assert excess in game.discard_pile
    assert any(
        "You discard BANG!, 2 of clubs and end your turn." in text
        for text in speech_texts(game, actor_index)
    )


def test_law_of_the_west_card_cannot_be_spent_as_an_ability_cost():
    game = start_game(4, seed=42)
    actor = game.current_player
    actor.character = "doc_holyday"
    forced = make_card(2211, cards.BEER, suit=cards.HEARTS)
    other = make_card(2212, cards.BANG)
    third = make_card(2213, cards.MISSED)
    actor.hand = [forced, other, third]
    actor.life = max(1, actor.max_life - 1)
    actor.law_card_id = forced.id
    game.effect_stack.clear()
    game.decision = None
    game.phase = PHASE_PLAY
    assert game._law_card_must_be_played(actor, forced.id)
    game._action_doc_holyday(actor, "doc_holyday")
    assert game.play_intent
    assert forced.id not in game.play_intent.data["allowed_card_ids"]
    assert game._is_play_card_enabled(
        actor,
        action_id=f"play_card_{forced.id}",
    ) == "bang-error-law-card-as-cost"


def test_diamond_duel_is_the_apache_kid_exception():
    game = start_game(4, seed=43)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    target.character = "apache_kid"
    duel = make_card(
        2221,
        cards.DUEL,
        suit=cards.DIAMONDS,
    )
    target.hand = [make_card(2222, cards.BANG)]
    actor.hand = [duel]
    game._start_card_intent(actor, duel)
    game._action_choose_player(actor, f"choose_player_{target.id}")
    assert game.decision is not None
    assert game.decision.kind == "duel"
    assert game.decision.player_id == target.id


def test_apache_kid_immunity_names_the_blocked_bang_for_each_audience():
    game = start_game(4, seed=70)
    actor = game.current_player
    target, observer = game._clockwise_after(actor, exclude_actor=True)[:2]
    target.character = "apache_kid"
    bang = make_card(2220, cards.BANG, suit=cards.DIAMONDS)
    actor.hand = [bang]
    before = target.life
    for listener in (actor, target, observer):
        user = game.get_user(listener)
        assert isinstance(user, MockUser)
        user.messages.clear()

    game._start_card_intent(actor, bang)
    game._action_choose_player(actor, f"choose_player_{target.id}")

    assert target.life == before
    actor_text = " ".join(speech_texts(game, game.players.index(actor)))
    target_text = " ".join(speech_texts(game, game.players.index(target)))
    observer_text = " ".join(speech_texts(game, game.players.index(observer)))
    assert f"protects {target.name} from your BANG!" in actor_text
    assert f"protects you from {actor.name}'s BANG!" in target_text
    assert (
        f"protects {target.name} from {actor.name}'s BANG!" in observer_text
    )


def test_apache_kid_ignores_a_two_diamond_sniper_attack():
    game = start_game(4, seed=50)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    target.character = "apache_kid"
    first = make_card(2223, cards.BANG, suit=cards.DIAMONDS)
    second = make_card(2224, cards.BANG, suit=cards.DIAMONDS)
    actor.hand = [first, second]
    target.hand = []
    before = target.life
    game.play_intent = BangPlayIntent(
        kind="sniper",
        actor_id=actor.id,
        selected_card_ids=[first.id, second.id],
        target_id=target.id,
        required=2,
        stage="target",
        data={"allowed_card_ids": [first.id, second.id]},
    )
    game._commit_intent()
    assert target.life == before
    assert first in game.discard_pile and second in game.discard_pile
    assert game.effect_stack == []


def test_derringer_draws_even_when_the_shot_resolves_immediately():
    game = start_game(4, seed=44)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    derringer = make_card(
        2231,
        cards.DERRINGER,
        border=cards.GREEN,
    )
    actor.hand = []
    target.hand = []
    target.in_play = []
    target.life = 3
    game.resolving_card = ResolvingCard(
        card=derringer,
        actor_id=actor.id,
        from_in_play=True,
    )
    before = len(actor.hand)
    game._resolve_committed_card(actor, derringer, target)
    tick_until(
        game,
        lambda: target.life == 2 and len(actor.hand) == before + 1,
    )
    assert target.life == 2
    tick_until(game, lambda: len(actor.hand) == before + 1)
    assert len(actor.hand) == before + 1
    assert derringer in game.discard_pile


def test_ricochet_auto_selects_the_only_card_of_the_selected_owner():
    game = start_game(4, seed=51)
    actor = game.current_player
    first, second = game._clockwise_after(actor, exclude_actor=True)[:2]
    cost = make_card(2240, cards.BANG)
    first_card = make_card(2241, cards.BARREL, border=cards.BLUE)
    second_card = make_card(2242, cards.MUSTANG, border=cards.BLUE)
    actor.hand = [cost]
    first.hand = []
    first.in_play = [BangInPlayCard(first_card)]
    second.in_play = [BangInPlayCard(second_card)]
    game.current_event = "ricochet"
    clear_user_messages(game)
    game._action_ricochet(actor, "ricochet")
    assert game.play_intent and game.play_intent.stage == "cost"
    assert game._is_confirm_hidden(actor) is Visibility.HIDDEN
    game._action_play_card(actor, f"play_card_{cost.id}")

    assert game.play_intent and game.play_intent.stage == "target"
    actor_index = game.players.index(actor)
    game.flush_menus()
    items = turn_menu_items(game, actor_index)
    assert list(items)[-1] == "cancel_selection"
    assert "confirm_selection" not in items
    prompt = game._intent_prompt(actor, "en")
    assert prompt is not None
    assert prompt[0] == "bang-prompt-select-ricochet-owner"
    assert game._is_confirm_hidden(actor) is Visibility.HIDDEN
    game._action_choose_player(actor, f"choose_player_{first.id}")
    assert game.play_intent is None
    assert cost in game.discard_pile
    tick_until(game, lambda: first_card in game.discard_pile)
    assert first_card in game.discard_pile
    assert not first.in_play
    assert second.in_play[0].card.id == second_card.id
    assert set(sound_names(game)) & set(bang_audio.SOUND_IMPACT_RICOCHET)
    assert any(
        f"Your Ricochet discards {first.name}'s Barrel, 2 of clubs" in text
        for text in speech_texts(game, actor_index)
    )
    assert any(
        f"{actor.name}'s Ricochet discards your Barrel, 2 of clubs" in text
        for text in speech_texts(game, game.players.index(first))
    )


def test_ricochet_impact_only_plays_when_the_target_card_is_hit():
    game = start_game(4, seed=52)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    protected = make_card(2243, cards.BARREL, border=cards.BLUE)
    missed = make_card(2244, cards.MISSED)
    target.in_play = [BangInPlayCard(protected)]
    target.hand = [missed]
    game.decision = None
    game.effect_stack.clear()
    game.phase = PHASE_PLAY
    clear_user_messages(game)

    game._start_ricochet(actor, target, protected.id)

    assert game.decision and game.decision.kind == "ricochet"
    assert not set(sound_names(game)) & set(bang_audio.SOUND_IMPACT_RICOCHET)
    clear_user_messages(game)
    game._use_decision_card(target, missed)

    assert target.in_play[0].card == protected
    assert not set(sound_names(game)) & set(bang_audio.SOUND_IMPACT_RICOCHET)


def test_slabs_real_bang_requires_two_missed_effects():
    game = start_game(4, seed=6)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    actor.character = "slab_the_killer"
    response = make_card(2301, cards.MISSED)
    target.hand = [response]
    target.in_play = []
    target.life = 3
    game._start_shot(actor, target, source_kind="bang_card", required=2)
    assert game.decision and game.decision.kind == "missed"
    game._use_decision_card(target, response)
    tick_until(game, lambda: target.life == 2)
    assert target.life == 2
    assert response in game.discard_pile


def test_multi_miss_shot_cannot_use_a_replacement_drawn_mid_response():
    game = start_game(4, seed=62)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    target.character = "molly_stark"
    first = make_card(2302, cards.MISSED)
    replacement = make_card(2303, cards.MISSED)
    target.hand = [first]
    target.in_play = []
    game.deck.insert(0, replacement)
    life = target.life

    game._start_shot(actor, target, source_kind="bang_card", required=2)
    assert game.decision and game.decision.card_ids == [first.id]
    game._use_decision_card(target, first)

    assert game.decision is None
    tick_until(game, lambda: target.life == life - 1)
    assert target.life == life - 1
    assert target.hand == [replacement]
    assert first in game.discard_pile


def test_dodge_draw_can_supply_the_second_missed_against_slab():
    game = start_game(4, seed=75)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    actor.character = "slab_the_killer"
    dodge = make_card(2304, cards.DODGE)
    drawn_missed = make_card(2305, cards.MISSED)
    target.character = "bart_cassidy"
    target.hand = [dodge]
    target.in_play = []
    game.deck.insert(0, drawn_missed)
    life = target.life

    game._start_shot(actor, target, source_kind="bang_card", required=2)
    game._use_decision_card(target, dodge)

    tick_until(game, lambda: game.decision is not None)
    assert game.decision and game.decision.kind == "missed"
    assert game.decision.card_ids == [drawn_missed.id]
    game._use_decision_card(target, drawn_missed)

    assert target.life == life
    assert game.decision is None
    assert dodge in game.discard_pile
    assert drawn_missed in game.discard_pile


def test_bible_draw_can_supply_the_second_missed_against_slab():
    game = start_game(4, seed=178)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    actor.character = "slab_the_killer"
    bible = make_card(2312, cards.BIBLE, border=cards.GREEN)
    drawn_missed = make_card(2313, cards.MISSED)
    target.character = "bart_cassidy"
    target.hand = []
    target.in_play = [
        BangInPlayCard(bible, usable_after_turn=game.turn_serial)
    ]
    game.deck.insert(0, drawn_missed)
    life = target.life

    game._start_shot(actor, target, source_kind="bang_card", required=2)
    assert game.decision
    assert bible.id in game.decision.data["green_card_ids"]
    game._use_green_response(target, target.in_play[0])

    tick_until(game, lambda: game.decision is not None)
    assert game.decision and game.decision.kind == "missed"
    assert game.decision.card_ids == [drawn_missed.id]
    game._use_decision_card(target, drawn_missed)

    assert target.life == life
    assert game.decision is None
    assert bible in game.discard_pile
    assert drawn_missed in game.discard_pile


def test_dodge_response_is_announced_before_its_card_draw():
    game = start_game(4, seed=81)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    dodge = make_card(
        2309,
        cards.DODGE,
        suit=cards.DIAMONDS,
        rank="7",
    )
    target.character = "bart_cassidy"
    target.hand = [dodge]
    target.in_play = []
    game.decision = None
    game.effect_stack.clear()
    game.phase = PHASE_PLAY
    game._start_shot(actor, target, source_kind="bang_card", required=1)
    assert game.decision and game.decision.kind == "missed"
    assert dodge.id in game.decision.card_ids
    for listener in game.players:
        user = game.get_user(listener)
        if isinstance(user, MockUser):
            user.messages.clear()

    game._use_decision_card(target, dodge)

    target_texts = speech_texts(game, game.players.index(target))
    response_index = next(
        index
        for index, text in enumerate(target_texts)
        if "You avoid" in text and "Dodge, 7 of diamonds" in text
    )
    draw_index = next(
        index
        for index, text in enumerate(target_texts)
        if text.startswith("You draw 1 card:")
    )
    assert response_index < draw_index
    observer = next(
        player
        for player in game.players
        if player is not actor and player is not target
    )
    assert any(
        f"{target.name} avoids {actor.name}'s BANG!" in text
        and "Dodge, 7 of diamonds" in text
        for text in speech_texts(game, game.players.index(observer))
    )
    assert set(sound_names(game)) & set(bang_audio.SOUND_DEFENSE_DODGE)


@pytest.mark.parametrize(
    ("attack_kind", "expected_sound"),
    [
        (cards.KNIFE, bang_audio.SOUND_DEFENSE_BLADE_DODGE),
        (cards.PUNCH, bang_audio.SOUND_DEFENSE_BLUNT_DODGE),
    ],
)
def test_successful_dodge_sound_matches_attack_type(
    attack_kind: str,
    expected_sound: str,
):
    game = start_game(4, seed=166)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    missed = make_card(2317, cards.MISSED)
    target.hand = [missed]
    target.in_play.clear()

    game._start_shot(
        actor,
        target,
        source_kind=attack_kind,
        required=1,
    )
    assert game.decision and game.decision.kind == "missed"
    clear_user_messages(game)

    game._use_decision_card(target, missed)

    assert expected_sound in sound_names(game)
    assert not set(sound_names(game)) & set(
        bang_audio.SOUND_DEFENSE_DODGE
    )


def test_hat_defenses_share_the_two_temporary_helmet_variants():
    for offset, kind in enumerate(
        (cards.SOMBRERO, cards.TEN_GALLON_HAT)
    ):
        game = start_game(4, seed=93 + offset)
        actor = game.current_player
        target = game._clockwise_after(actor, exclude_actor=True)[0]
        defense = make_card(
            2311 + offset,
            kind,
            border=cards.GREEN,
        )
        target.hand.clear()
        target.in_play = [
            BangInPlayCard(defense, usable_after_turn=0)
        ]
        clear_user_messages(game)

        game._start_shot(
            actor,
            target,
            source_kind="bang_card",
            required=1,
        )
        game._use_green_response(target, target.in_play[0])

        assert set(sound_names(game)) & set(
            bang_audio.SOUND_DEFENSE_HAT
        )


def test_barrel_success_uses_a_wood_impact_sound():
    game = start_game(4, seed=95)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    target.character = "bart_cassidy"
    target.hand.clear()
    target.in_play = [
        BangInPlayCard(
            make_card(2313, cards.BARREL, border=cards.BLUE)
        )
    ]
    game.deck.insert(
        0,
        make_card(2314, cards.BEER, suit=cards.HEARTS)
    )
    clear_user_messages(game)

    game._start_shot(
        actor,
        target,
        source_kind="bang_card",
        required=1,
    )
    assert game.decision and game.decision.kind == "barrel"
    game._resolve_item_decision(target, "use_barrel")

    assert set(sound_names(game)) & set(
        bang_audio.SOUND_IMPACT_WOOD_BARREL
    )


def test_failed_barrel_cue_is_staggered_before_the_hit_sound():
    game = start_game(4, seed=151)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    target.character = "bart_cassidy"
    target.hand.clear()
    target.in_play = [
        BangInPlayCard(
            make_card(2315, cards.BARREL, border=cards.BLUE)
        )
    ]
    game.deck.insert(
        0,
        make_card(2316, cards.BEER, suit=cards.SPADES),
    )
    game._start_shot(
        actor,
        target,
        source_kind="bang_card",
        required=1,
    )
    assert game.decision and game.decision.kind == "barrel"
    clear_user_messages(game)
    life = target.life

    game._resolve_item_decision(target, "use_barrel")

    initial_sounds = set(sound_names(game))
    assert initial_sounds & set(bang_audio.SOUND_DEFENSE_BARREL_FAIL)
    assert not initial_sounds & set(bang_audio.SOUND_IMPACT_BULLET_BODY)
    assert target.life == life
    assert game.has_active_sequence(tag="bang_effect_gap")

    failure_sound = next(
        sound
        for sound in sound_names(game)
        if sound in bang_audio.SOUND_DEFENSE_BARREL_FAIL
    )
    wait_ticks = SequenceBeat.audio_delay_ticks(
        bang_audio.sound_ticks(failure_sound),
        wait_ratio=bang_audio.WAIT_RATIO_FAILED_DEFENSE,
    )
    for _ in range(wait_ticks - 1):
        game.on_tick()
    assert target.life == life

    game.on_tick()
    assert target.life == life - 1
    assert set(sound_names(game)) & set(
        bang_audio.SOUND_IMPACT_BULLET_BODY
    )
    actor_text = " ".join(
        speech_texts(game, game.players.index(actor))
    )
    target_text = " ".join(
        speech_texts(game, game.players.index(target))
    )
    observer = next(
        player
        for player in game.players
        if player.id not in {actor.id, target.id}
    )
    observer_text = " ".join(
        speech_texts(game, game.players.index(observer))
    )
    assert f"{target.name}'s Barrel check against your shot fails" in actor_text
    assert "Your Barrel check fails" in target_text
    assert f"{target.name} fails a Barrel check" in observer_text
    assert (
        f"Your BANG! costs {target.name} 1 life; they now have {target.life}"
        in actor_text
    )
    assert "You lose 1 life" in target_text
    assert f"{target.name} loses 1 life" in observer_text


def test_lethal_fall_starts_at_thirty_percent_without_blocking_resolution():
    game = start_game(5, seed=152)
    target = next(player for player in game.players if player.role == ROLE_OUTLAW)
    for player in game.players:
        player.character = "bart_cassidy"
    target.life = 1
    target.hand.clear()
    target.in_play.clear()
    clear_user_messages(game)
    game._push_effect(
        BangEffect(
            kind="damage",
            target_id=target.id,
            amount=1,
            source=DamageSource(kind="high_noon"),
        )
    )

    game._continue_effects()

    impact = next(
        sound
        for sound in sound_names(game)
        if sound == bang_audio.SOUND_IMPACT_GENERIC
    )
    assert target.life == 0
    assert not target.eliminated
    assert not set(sound_names(game)) & set(
        bang_audio.SOUND_ELIMINATION_FALLS
    )

    wait_ticks = SequenceBeat.audio_delay_ticks(
        bang_audio.sound_ticks(impact),
        wait_ratio=bang_audio.LETHAL_FALL_TRIGGER_RATIO,
    )
    for _ in range(wait_ticks - 1):
        game.on_tick()
    assert not target.eliminated
    assert not set(sound_names(game)) & set(
        bang_audio.SOUND_ELIMINATION_FALLS
    )

    game.on_tick()
    assert target.eliminated
    fall_sound = next(
        sound
        for sound in sound_names(game)
        if sound in bang_audio.SOUND_ELIMINATION_FALLS
    )
    assert any(
        "eliminated" in text
        for text in speech_texts(game, game.players.index(target))
    )
    assert fall_sound in bang_audio.SOUND_ELIMINATION_FALLS
    assert not game.effect_stack
    assert not game.has_active_sequence(tag="bang_elimination_fall")
    assert not game.is_sequence_gameplay_locked()
    assert not game.is_sequence_bot_paused()


def test_victory_and_elimination_rewards_continue_when_the_fall_starts():
    game = start_game(4, seed=171)
    sheriff = next(
        player for player in game.players if player.role == ROLE_SHERIFF
    )
    target = next(
        player for player in game.players if player.role == ROLE_OUTLAW
    )
    for player in game.players:
        player.character = "bart_cassidy"
        if (
            player.id != target.id
            and player.role in {ROLE_OUTLAW, ROLE_RENEGADE}
        ):
            player.eliminated = True
            player.role_revealed = True
    target.life = 1
    target.hand.clear()
    target.in_play.clear()
    sheriff.hand.clear()
    clear_user_messages(game)
    game._push_effect(
        BangEffect(
            kind="damage",
            target_id=target.id,
            amount=1,
            source=DamageSource(
                player_id=sheriff.id,
                kind="bang_card",
                card_kind=cards.BANG,
            ),
        )
    )

    game._continue_effects()
    impact = next(
        sound
        for sound in sound_names(game)
        if sound in bang_audio.SOUND_IMPACT_BULLET_BODY
    )
    wait_ticks = SequenceBeat.audio_delay_ticks(
        bang_audio.sound_ticks(impact),
        wait_ratio=bang_audio.LETHAL_FALL_TRIGGER_RATIO,
    )
    for _ in range(wait_ticks):
        game.on_tick()

    assert target.eliminated
    assert game.winner_ids
    assert not game.has_active_sequence(tag="bang_elimination_fall")
    assert not game.is_sequence_bot_paused()
    assert bang_audio.SOUND_WIN in sound_names(game)
    assert len(sheriff.hand) == 3
    fall_index = next(
        index
        for index, sound in enumerate(sound_names(game))
        if sound in bang_audio.SOUND_ELIMINATION_FALLS
    )
    win_index = sound_names(game).index(bang_audio.SOUND_WIN)
    assert fall_index < win_index


def test_simultaneous_eliminations_stagger_falls_without_delaying_victory():
    game = start_game(4, seed=172)
    sheriff = next(
        player for player in game.players if player.role == ROLE_SHERIFF
    )
    enemies = [
        player
        for player in game.players
        if player.role in {ROLE_OUTLAW, ROLE_RENEGADE}
    ]
    already_out, first_victim, second_victim = enemies
    already_out.life = 0
    already_out.eliminated = True
    already_out.role_revealed = True
    for player in game.players:
        player.character = "bart_cassidy"
    for victim in (first_victim, second_victim):
        victim.life = 0
        victim.hand.clear()
        victim.in_play.clear()
    game.phase = PHASE_RESOLVING
    game.clear_scheduled_sounds()
    game.effect_stack = [
        BangEffect(
            kind="elimination",
            target_id=second_victim.id,
            source=DamageSource(kind="high_noon"),
            data={"fall_trigger_tick": game.sound_scheduler_tick},
        ),
        BangEffect(
            kind="elimination",
            target_id=first_victim.id,
            source=DamageSource(kind="high_noon"),
            data={"fall_trigger_tick": game.sound_scheduler_tick},
        ),
    ]
    clear_user_messages(game)

    trigger_tick = game.sound_scheduler_tick
    game._continue_effects()

    assert first_victim.eliminated
    assert second_victim.eliminated
    assert game.winner_ids == [sheriff.id]
    assert not game.game_active
    assert not game.effect_stack
    assert not game.has_active_sequence(tag="bang_elimination_fall")
    assert not game.is_sequence_bot_paused()
    assert len(
        [
            sound
            for sound in sound_names(game)
            if sound in bang_audio.SOUND_ELIMINATION_FALLS
        ]
    ) == 1
    pending_falls = [
        scheduled
        for scheduled in game.scheduled_sounds
        if scheduled[1] in bang_audio.SOUND_ELIMINATION_FALLS
    ]
    assert len(pending_falls) == 1
    assert pending_falls[0][0] == (
        trigger_tick + bang_audio.ELIMINATION_FALL_STAGGER_TICKS
    )
    observer_text = " ".join(speech_texts(game, game.players.index(sheriff)))
    assert first_victim.name in observer_text
    assert second_victim.name in observer_text

    game.on_tick()
    assert len(
        [
            sound
            for sound in sound_names(game)
            if sound in bang_audio.SOUND_ELIMINATION_FALLS
        ]
    ) == 1
    game.on_tick()
    assert len(
        [
            sound
            for sound in sound_names(game)
            if sound in bang_audio.SOUND_ELIMINATION_FALLS
        ]
    ) == 2
    assert not [
        scheduled
        for scheduled in game.scheduled_sounds
        if scheduled[1] in bang_audio.SOUND_ELIMINATION_FALLS
    ]


def test_elimination_fall_trigger_survives_json_round_trip():
    game = start_game(5, seed=173)
    target = next(
        player for player in game.players if player.role == ROLE_OUTLAW
    )
    for player in game.players:
        player.character = "bart_cassidy"
    target.life = 1
    target.hand.clear()
    target.in_play.clear()
    game._push_effect(
        BangEffect(
            kind="damage",
            target_id=target.id,
            amount=1,
            source=DamageSource(kind="high_noon"),
        )
    )
    game._continue_effects()

    damage = game.effect_stack[-1]
    assert damage.kind == "damage"
    trigger_tick = int(damage.data["fall_trigger_tick"])
    assert game.sound_scheduler_tick < trigger_tick

    restored = BangGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    restored_target = restored.get_player_by_id(target.id)
    assert restored_target is not None
    assert not restored_target.eliminated
    assert int(restored.effect_stack[-1].data["fall_trigger_tick"]) == trigger_tick

    tick_until(restored, lambda: restored_target.eliminated)

    assert restored.sound_scheduler_tick >= trigger_tick
    assert not restored.has_active_sequence(tag="bang_elimination_fall")
    assert not restored.effect_stack


def test_game_over_preserves_a_pending_staggered_fall():
    game = start_game(4, seed=174)
    winner = next(
        player for player in game.players if player.role == ROLE_SHERIFF
    )
    game.clear_scheduled_sounds()
    game._play_or_schedule_elimination_fall()
    game._play_or_schedule_elimination_fall()
    pending_before = [
        scheduled
        for scheduled in game.scheduled_sounds
        if scheduled[1] in bang_audio.SOUND_ELIMINATION_FALLS
    ]
    assert len(pending_before) == 1

    game._end_game([winner], ROLE_SHERIFF)

    pending_after = [
        scheduled
        for scheduled in game.scheduled_sounds
        if scheduled[1] in bang_audio.SOUND_ELIMINATION_FALLS
    ]
    assert pending_after == pending_before


def test_legacy_blocking_fall_stage_resumes_after_save_upgrade():
    game = start_game(5, seed=175)
    target = next(
        player for player in game.players if player.role == ROLE_OUTLAW
    )
    target.life = 0
    target.eliminated = True
    target.hand.clear()
    target.in_play.clear()
    frame = BangEffect(
        kind="elimination",
        stage="fall",
        target_id=target.id,
        data={"after_fall_stage": "discard"},
    )
    game.effect_stack = [frame]
    game.decision = None
    game.cancel_all_sequences()

    game._continue_elimination(frame)
    assert frame.stage == "discard"
    game._continue_effects()

    assert not game.effect_stack
    assert not game.decision


def test_restore_migrates_pending_elimination_order_to_sequential_choices():
    game = start_game(4, seed=180)
    victim = next(player for player in game.players if player.role == ROLE_OUTLAW)
    hand_card = make_card(2708, cards.BANG)
    in_play_card = make_card(2709, cards.BARREL, border=cards.BLUE)
    victim.hand = [hand_card]
    victim.in_play = [BangInPlayCard(in_play_card)]
    victim.eliminated = True
    game.effect_stack = [
        BangEffect(
            kind="elimination",
            target_id=victim.id,
            stage="discard",
        )
    ]
    game.decision = BangDecision(
        kind="elimination_discard",
        player_id=victim.id,
        card_ids=[hand_card.id],
        item_ids=[f"in_play_{in_play_card.id}"],
        selected_card_ids=[hand_card.id],
    )

    restored = BangGame.from_json(game.to_json())
    restored.rebuild_runtime_state()

    assert restored.decision
    assert restored.decision.card_ids == [hand_card.id]
    assert restored.decision.item_ids == [
        f"in_play_{in_play_card.id}",
        "finish_elimination_discard",
    ]
    assert restored.decision.selected_card_ids == []


def test_eliminated_player_can_interleave_every_card_in_discard_order():
    game = start_game(4, seed=179, touch=True)
    victim = next(player for player in game.players if player.role == ROLE_OUTLAW)
    observer = next(
        player
        for player in game.players
        if player is not victim and player.role != ROLE_OUTLAW
    )
    first_hand = make_card(2710, cards.BANG)
    second_hand = make_card(2711, cards.BEER)
    weapon = make_card(2712, cards.SCHOFIELD, border=cards.BLUE)
    barrel = make_card(2713, cards.BARREL, border=cards.BLUE)
    victim.hand = [first_hand, second_hand]
    victim.in_play = [BangInPlayCard(weapon), BangInPlayCard(barrel)]
    victim.life = 0
    victim.eliminated = True
    victim.role_revealed = True
    game.phase = PHASE_RESOLVING
    game.discard_pile.clear()
    frame = BangEffect(
        kind="elimination",
        target_id=victim.id,
        stage="discard",
        source=DamageSource(kind="high_noon"),
    )
    game.effect_stack = [frame]
    game.decision = None

    game._continue_elimination(frame)
    assert game.decision and game.decision.kind == "elimination_discard"
    game._sync_turn_actions(victim)
    action_set = game.get_action_set(victim, "turn")
    assert action_set
    assert action_set._order == [
        "input_prompt",
        *(f"play_card_{card.id}" for card in victim.hand),
        f"choice_in_play_{weapon.id}",
        f"choice_in_play_{barrel.id}",
        "choice_finish_elimination_discard",
    ]
    assert (
        game._is_play_card_hidden(
            victim,
            action_id=f"play_card_{second_hand.id}",
        )
        is Visibility.VISIBLE
    )
    clear_user_messages(game)

    game._action_play_card(victim, f"play_card_{second_hand.id}")
    game._action_choose_item(victim, f"choice_in_play_{weapon.id}")
    game._action_play_card(victim, f"play_card_{first_hand.id}")
    game._action_choose_item(
        victim,
        "choice_finish_elimination_discard",
    )

    assert game.discard_pile == [second_hand, weapon, first_hand, barrel]
    assert not victim.hand
    assert not victim.in_play
    assert game.decision is None
    victim_text = " ".join(speech_texts(game, game.players.index(victim)))
    observer_text = " ".join(
        speech_texts(game, game.players.index(observer))
    )
    assert "You place Beer" in victim_text
    assert "You place Schofield" in victim_text
    assert "remaining cards in menu order: Barrel" in victim_text
    assert f"{victim.name} places Beer" in observer_text
    assert f"{victim.name} places Schofield" in observer_text
    assert f"{victim.name} discards the remaining cards" in observer_text


def test_bot_finishes_elimination_discard_in_deterministic_menu_order():
    game = make_game(4, bots=True)
    bot = game.players[0]
    game.decision = BangDecision(
        kind="elimination_discard",
        player_id=bot.id,
        card_ids=[card.id for card in bot.hand],
        item_ids=["finish_elimination_discard"],
    )

    assert (
        bang_bot.choose_action(game, bot)
        == "choice_finish_elimination_discard"
    )


def test_partial_shot_response_announces_the_remaining_requirement():
    game = start_game(4, seed=82)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    missed = make_card(2310, cards.MISSED)
    target.character = "bart_cassidy"
    target.hand = [missed]
    target.in_play = []
    game.decision = None
    game.effect_stack.clear()
    game.phase = PHASE_PLAY
    game._start_shot(actor, target, source_kind="bang_card", required=2)
    target_user = game.get_user(target)
    assert isinstance(target_user, MockUser)
    target_user.messages.clear()

    game._use_decision_card(target, missed)

    assert any(
        "You use Missed!, 2 of clubs" in text
        and "1 Missed! effect still required" in text
        for text in speech_texts(game, game.players.index(target))
    )


def test_molly_stark_does_not_gain_a_bonus_draw_from_dodge():
    game = start_game(4, seed=76)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    dodge = make_card(2306, cards.DODGE)
    printed_draw = make_card(2307, cards.BEER)
    target.character = "molly_stark"
    target.hand = [dodge]
    target.in_play = []
    game.deck.insert(0, printed_draw)
    deck_count = len(game.deck)

    game._start_shot(actor, target, source_kind="bang_card", required=1)
    game._use_decision_card(target, dodge)

    assert target.hand == [printed_draw]
    assert len(game.deck) == deck_count - 1


def test_molly_stark_does_not_draw_for_answering_her_own_duel():
    game = start_game(4, seed=77)
    molly = game.current_player
    target = game._clockwise_after(molly, exclude_actor=True)[0]
    molly.character = "molly_stark"
    response = make_card(2308, cards.BANG)
    molly.hand = [response]
    game.effect_stack = [
        BangEffect(
            kind="duel",
            actor_id=molly.id,
            target_id=target.id,
            data={"responder_id": molly.id},
        )
    ]
    game.decision = BangDecision(
        kind="duel",
        player_id=molly.id,
        card_ids=[response.id],
    )

    game._use_decision_card(molly, response)

    assert molly.molly_deferred_draws == 0


def test_duel_response_uses_responder_opponent_and_observer_perspectives():
    game = start_game(4, seed=157)
    initiator = game.current_player
    responder, observer = game._clockwise_after(
        initiator,
        exclude_actor=True,
    )[:2]
    answer = make_card(2320, cards.BANG, rank="6", suit=cards.DIAMONDS)
    frame = BangEffect(
        kind="duel",
        actor_id=initiator.id,
        target_id=responder.id,
    )
    clear_user_messages(game)

    game._announce_duel_response(responder, answer, frame)

    assert any(
        "You discard BANG!, 6 of diamonds in the Duel" in text
        for text in speech_texts(game, game.players.index(responder))
    )
    assert any(
        f"{responder.name} discards BANG!, 6 of diamonds against you"
        in text
        for text in speech_texts(game, game.players.index(initiator))
    )
    assert any(
        f"{responder.name} discards BANG!, 6 of diamonds in the Duel"
        in text
        for text in speech_texts(game, game.players.index(observer))
    )


def test_duel_response_uses_the_responder_weapon_without_replaying_it():
    game = start_game(4, seed=165)
    initiator = game.current_player
    responder = game._clockwise_after(initiator, exclude_actor=True)[0]
    answer = make_card(2321, cards.BANG)
    responder.hand = [answer]
    responder.in_play = [
        BangInPlayCard(
            make_card(2322, cards.WINCHESTER, border=cards.BLUE)
        )
    ]
    frame = BangEffect(
        kind="duel",
        actor_id=initiator.id,
        target_id=responder.id,
        source=DamageSource(
            player_id=initiator.id,
            kind="duel",
            card_kind=cards.DUEL,
        ),
        data={"responder_id": responder.id},
    )
    game.effect_stack = [frame]
    game.decision = BangDecision(
        kind="duel",
        player_id=responder.id,
        card_ids=[answer.id],
        item_ids=["lose_duel"],
    )
    clear_user_messages(game)

    game._use_decision_card(responder, answer)

    assert set(sound_names(game)) & set(
        bang_audio.SOUND_FIRE_WINCHESTER
    )

    tick_until(
        game,
        lambda: (
            game.decision is not None
            and game.decision.player_id == initiator.id
        ),
    )
    game.decision = BangDecision(
        kind="duel",
        player_id=initiator.id,
        item_ids=["lose_duel"],
    )
    starting_life = initiator.life
    winchester_shots = sum(
        sound in bang_audio.SOUND_FIRE_WINCHESTER
        for sound in sound_names(game)
    )

    game._resolve_item_decision(initiator, "lose_duel")

    assert initiator.life == starting_life - 1
    assert sum(
        sound in bang_audio.SOUND_FIRE_WINCHESTER
        for sound in sound_names(game)
    ) == winchester_shots
    assert set(sound_names(game)) & set(
        bang_audio.SOUND_IMPACT_BULLET_BODY
    )


def test_immediate_duel_loss_fires_the_winners_weapon_before_impact():
    game = start_game(4, seed=169)
    initiator = game.current_player
    responder = game._clockwise_after(initiator, exclude_actor=True)[0]
    initiator.in_play = [
        BangInPlayCard(
            make_card(2323, cards.REMINGTON, border=cards.BLUE)
        )
    ]
    frame = BangEffect(
        kind="duel",
        actor_id=initiator.id,
        target_id=responder.id,
        source=DamageSource(
            player_id=initiator.id,
            kind="duel",
            card_kind=cards.DUEL,
        ),
        data={"responder_id": responder.id},
    )
    game.effect_stack = [frame]
    game.decision = BangDecision(
        kind="duel",
        player_id=responder.id,
        item_ids=["lose_duel"],
    )
    starting_life = responder.life
    clear_user_messages(game)

    game._resolve_item_decision(responder, "lose_duel")

    decisive_shot = next(
        sound
        for sound in sound_names(game)
        if sound in bang_audio.SOUND_FIRE_REMINGTON
    )
    assert responder.life == starting_life
    assert not set(sound_names(game)) & set(
        bang_audio.SOUND_IMPACT_BULLET_BODY
    )

    wait_ticks = SequenceBeat.audio_delay_ticks(
        bang_audio.sound_ticks(decisive_shot),
        wait_ratio=bang_audio.WAIT_RATIO_GUNSHOT,
    )
    for _ in range(wait_ticks - 1):
        game.on_tick()
    assert responder.life == starting_life

    game.on_tick()
    assert responder.life == starting_life - 1
    assert set(sound_names(game)) & set(
        bang_audio.SOUND_IMPACT_BULLET_BODY
    )


def test_ghost_town_departure_does_not_play_a_lethal_fall():
    game = start_game(4, seed=170)
    ghost = game._clockwise_after(game.current_player, exclude_actor=True)[0]
    ghost.eliminated = True
    ghost.ghost_active = True
    ghost.life = 1
    ghost.hand.clear()
    ghost.in_play.clear()
    frame = BangEffect(
        kind="elimination",
        target_id=ghost.id,
        source=DamageSource(kind="ghost_town"),
    )
    game.effect_stack = [frame]
    clear_user_messages(game)

    game._continue_elimination(frame)

    assert frame.stage == "discard"
    assert not set(sound_names(game)) & set(
        bang_audio.SOUND_ELIMINATION_FALLS
    )
    assert not game.has_active_sequence(tag="bang_elimination_fall")


def test_molly_does_not_draw_for_a_green_card_already_in_play():
    game = start_game(4, seed=61)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    target.character = "molly_stark"
    target.hand = []
    defense = make_card(2291, cards.IRON_PLATE, border=cards.GREEN)
    target.in_play = [BangInPlayCard(defense, usable_after_turn=0)]
    life = target.life
    deck_count = len(game.deck)

    game._start_shot(actor, target, source_kind="bang_card", required=1)
    assert game.decision and game.decision.kind == "missed"
    game._use_green_response(target, target.in_play[0])

    assert target.life == life
    assert target.hand == []
    assert len(game.deck) == deck_count
    assert defense in game.discard_pile


def test_bible_audio_only_plays_for_a_bound_successful_response():
    game = start_game(4, seed=121)
    actor = game.current_player
    actor.character = "bart_cassidy"
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    bible = make_card(2292, cards.BIBLE, border=cards.GREEN)
    target.hand.clear()
    target.in_play = [
        BangInPlayCard(bible, usable_after_turn=game.turn_serial)
    ]
    starting_life = target.life
    clear_user_messages(game)

    game._start_shot(actor, target, source_kind="bang_card", required=1)
    assert game.decision and game.decision.kind == "missed"
    game._action_use_in_play(target, f"use_in_play_{bible.id}")

    assert target.life == starting_life
    assert bible in game.discard_pile
    assert sound_names(game).count(bang_audio.SOUND_DEFENSE_BIBLE) == 1
    assert any(
        target.name in text and "Bible" in text and "avoids" in text
        for text in speech_texts(game, game.players.index(actor))
    )


def test_stale_bible_response_cannot_consume_card_or_play_audio():
    game = start_game(4, seed=122)
    target = game._clockwise_after(
        game.current_player,
        exclude_actor=True,
    )[0]
    bible = make_card(2293, cards.BIBLE, border=cards.GREEN)
    target.in_play = [
        BangInPlayCard(bible, usable_after_turn=game.turn_serial)
    ]
    game.effect_stack.clear()
    game.decision = BangDecision(
        kind="missed",
        player_id=target.id,
        data={
            "green_card_ids": [bible.id],
            "effect_depth": 1,
        },
    )
    clear_user_messages(game)

    game._action_use_in_play(target, f"use_in_play_{bible.id}")

    assert target.in_play[0].card is bible
    assert bible not in game.discard_pile
    assert bang_audio.SOUND_DEFENSE_BIBLE not in sound_names(game)


@pytest.mark.parametrize(
    "event_id",
    ["blessing", "the_reverend", "the_sermon"],
)
def test_religious_event_reveals_do_not_impersonate_bible_defense(
    event_id: str,
):
    game = start_game(4, seed=123)
    clear_user_messages(game)

    game._announce_event_revealed(event_id)

    assert not sound_names(game)


def test_in_play_use_buttons_match_their_actual_interaction_window():
    game = start_game(4, seed=87)
    actor = game.current_player
    defensive = make_card(2390, cards.BIBLE, border=cards.GREEN)
    proactive = make_card(2391, cards.PONY_EXPRESS, border=cards.GREEN)
    actor.in_play = [
        BangInPlayCard(defensive, usable_after_turn=game.turn_serial),
        BangInPlayCard(proactive, usable_after_turn=game.turn_serial + 1),
    ]
    game.phase = PHASE_PLAY
    game.effect_stack.clear()
    game.decision = None
    game.play_intent = None

    assert game._is_use_in_play_hidden(
        actor,
        action_id=f"use_in_play_{defensive.id}",
    ) is Visibility.HIDDEN
    assert game._is_use_in_play_hidden(
        actor,
        action_id=f"use_in_play_{proactive.id}",
    ) is Visibility.VISIBLE
    assert game._is_use_in_play_enabled(
        actor,
        action_id=f"use_in_play_{proactive.id}",
    ) == "bang-error-green-not-ready"

    game.effect_stack = [
        BangEffect(
            kind="shot",
            stage="response",
            target_id=actor.id,
            data={"misses_remaining": 1},
        )
    ]
    game.decision = BangDecision(
        kind="missed",
        player_id=actor.id,
        data={
            "green_card_ids": [defensive.id],
            "effect_depth": 1,
        },
    )
    assert game._is_use_in_play_hidden(
        actor,
        action_id=f"use_in_play_{defensive.id}",
    ) is Visibility.VISIBLE
    assert game._is_use_in_play_hidden(
        actor,
        action_id=f"use_in_play_{proactive.id}",
    ) is Visibility.HIDDEN


def test_targeted_shot_splits_event_notice_from_one_complete_instruction():
    game = start_game(4, seed=54)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    target.character = "willy_the_kid"
    target.in_play = []
    target.hand = [
        make_card(2611, cards.MISSED),
        make_card(2612, cards.MISSED),
    ]
    target_index = game.players.index(target)
    game.decision = None
    game.effect_stack.clear()
    game.phase = PHASE_PLAY

    game._start_shot(actor, target, source_kind="bang_card", required=2)
    assert game.decision and game.decision.kind == "missed"
    game.flush_menus()

    spoken = speech_texts(game, target_index)
    shot_notice = next(
        text for text in spoken if f"{actor.name} fires BANG! at you" in text
    )
    assert "Provide" not in shot_notice
    assert any(
        f"Respond to {actor.name}'s BANG!" in text
        and "play 2 more Missed! effects" in text
        and "take 1 damage" in text
        for text in spoken
    )
    items = turn_menu_items(game, target_index)
    assert next(iter(items)) == "input_prompt"
    assert f"Respond to {actor.name}'s BANG!" in items["input_prompt"]
    assert "play 2 more Missed! effects" in items["input_prompt"]


def test_bang_play_is_announced_as_firing_to_actor_target_and_observer():
    game = start_game(4, seed=64)
    actor = game.current_player
    target, observer = game._clockwise_after(actor, exclude_actor=True)[:2]
    bang = make_card(2399, cards.BANG)
    actor.hand = [bang]
    target.hand = []
    target.in_play = []
    listeners = (actor, target, observer)
    for listener in listeners:
        user = game.get_user(listener)
        assert isinstance(user, MockUser)
        user.messages.clear()

    game._start_card_intent(actor, bang)
    game._action_choose_player(actor, f"choose_player_{target.id}")

    actor_text = " ".join(speech_texts(game, game.players.index(actor)))
    target_text = " ".join(speech_texts(game, game.players.index(target)))
    observer_text = " ".join(speech_texts(game, game.players.index(observer)))
    assert f"You fire BANG! at {target.name}" in actor_text
    assert f"{actor.name} fires BANG! at you" in target_text
    assert f"{actor.name} fires BANG! at {target.name}" in observer_text
    assert "must provide" not in actor_text
    assert "must provide" not in observer_text
    assert "You play BANG!" not in actor_text


def test_calamity_janet_fires_missed_as_bang_with_explicit_source():
    game = start_game(4, seed=65)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    actor.character = "calamity_janet"
    converted = make_card(2400, cards.MISSED)
    actor.hand = [converted]
    target.hand = []
    target.in_play = []
    actor_user = game.get_user(actor)
    assert isinstance(actor_user, MockUser)
    actor_user.messages.clear()

    game._start_card_intent(actor, converted)
    game._action_choose_player(actor, f"choose_player_{target.id}")

    assert any(
        f"You fire Missed! used as BANG! at {target.name}" in text
        for text in speech_texts(game, game.players.index(actor))
    )


def test_beer_at_maximum_life_is_discarded_with_clear_no_effect_notice():
    game = start_game(4, seed=66)
    actor = game.current_player
    observer = next(player for player in game.players if player is not actor)
    beer = make_card(2402, cards.BEER, suit=cards.HEARTS)
    actor.hand = [beer]
    actor.life = actor.max_life
    for listener in (actor, observer):
        user = game.get_user(listener)
        assert isinstance(user, MockUser)
        user.messages.clear()

    assert game._normal_card_error(actor, beer) is None
    game._start_card_intent(actor, beer)

    assert actor.life == actor.max_life
    assert beer in game.discard_pile
    assert bang_audio.SOUND_DRINK_BEER in sound_names(game)
    assert bang_audio.SOUND_HEAL_SUCCESS not in sound_names(game)
    assert any(
        "You discard Beer" in text
        and "life is already full" in text
        for text in speech_texts(game, game.players.index(actor))
    )
    assert any(
        f"{actor.name} discards Beer at full life" in text
        for text in speech_texts(game, game.players.index(observer))
    )


def test_beer_with_two_players_remaining_is_discarded_without_healing():
    game = start_game(4, seed=67)
    actor = game.current_player
    survivor = game._clockwise_after(actor, exclude_actor=True)[0]
    for player in game.players:
        if player is not actor and player is not survivor:
            player.eliminated = True
    beer = make_card(2403, cards.BEER, suit=cards.HEARTS)
    actor.hand = [beer]
    actor.life = actor.max_life - 1
    actor_user = game.get_user(actor)
    assert isinstance(actor_user, MockUser)
    actor_user.messages.clear()

    game._start_card_intent(actor, beer)

    assert actor.life == actor.max_life - 1
    assert beer in game.discard_pile
    assert bang_audio.SOUND_DRINK_BEER in sound_names(game)
    assert bang_audio.SOUND_HEAL_SUCCESS not in sound_names(game)
    assert any(
        "cannot heal with two players left" in text
        for text in speech_texts(game, game.players.index(actor))
    )


@pytest.mark.parametrize("kind", [cards.WHISKY, cards.CANTEEN])
def test_non_beer_healing_card_at_full_life_reports_no_effect(kind):
    game = start_game(4, seed=85)
    actor = game.current_player
    observer = next(player for player in game.players if player is not actor)
    healing = make_card(
        2410,
        kind,
        border=cards.GREEN if kind == cards.CANTEEN else cards.BROWN,
    )
    actor.life = actor.max_life
    for listener in (actor, observer):
        user = game.get_user(listener)
        assert isinstance(user, MockUser)
        user.messages.clear()

    if kind == cards.WHISKY:
        cost = make_card(2411, cards.MISSED)
        actor.hand = [healing, cost]
        game._start_card_intent(actor, healing)
        game._action_play_card(actor, f"play_card_{cost.id}")
    else:
        actor.in_play = [
            BangInPlayCard(healing, usable_after_turn=game.turn_serial)
        ]
        game._action_use_in_play(actor, f"use_in_play_{healing.id}")

    assert actor.life == actor.max_life
    assert healing in game.discard_pile
    assert bang_audio.SOUND_HEAL_SUCCESS not in sound_names(game)
    assert any(
        f"You use {cards.card_name(kind, 'en')}; your life is already full."
        in text
        for text in speech_texts(game, game.players.index(actor))
    )
    assert any(
        f"{actor.name} uses {cards.card_name(kind, 'en')} at full life."
        in text
        for text in speech_texts(game, game.players.index(observer))
    )


def test_tequila_at_full_target_reports_actor_target_and_observer_context():
    game = start_game(4, seed=86)
    actor = game.current_player
    target, observer = game._clockwise_after(actor, exclude_actor=True)[:2]
    tequila = make_card(2412, cards.TEQUILA)
    cost = make_card(2413, cards.MISSED)
    actor.hand = [tequila, cost]
    target.life = target.max_life
    for listener in (actor, target, observer):
        user = game.get_user(listener)
        assert isinstance(user, MockUser)
        user.messages.clear()

    game._start_card_intent(actor, tequila)
    game._action_play_card(actor, f"play_card_{cost.id}")
    game._action_choose_player(actor, f"choose_player_{target.id}")

    assert target.life == target.max_life
    assert bang_audio.SOUND_DRINK_TEQUILA in sound_names(game)
    assert bang_audio.SOUND_HEAL_SUCCESS not in sound_names(game)
    assert any(
        f"You use Tequila on {target.name}, whose life is already full."
        in text
        for text in speech_texts(game, game.players.index(actor))
    )
    assert any(
        f"{actor.name} uses Tequila on you; your life is already full."
        in text
        for text in speech_texts(game, game.players.index(target))
    )
    assert any(
        f"{actor.name} uses Tequila on {target.name}, whose life is already full."
        in text
        for text in speech_texts(game, game.players.index(observer))
    )


def test_tequila_healing_reports_actor_target_and_observer_outcomes():
    game = start_game(4, seed=156)
    actor = game.current_player
    target, observer = game._clockwise_after(actor, exclude_actor=True)[:2]
    tequila = make_card(2420, cards.TEQUILA)
    cost = make_card(2421, cards.MISSED)
    actor.hand = [tequila, cost]
    target.life = target.max_life - 1
    clear_user_messages(game)

    game._start_card_intent(actor, tequila)
    game._action_play_card(actor, f"play_card_{cost.id}")
    game._action_choose_player(actor, f"choose_player_{target.id}")

    assert target.life == target.max_life
    assert bang_audio.SOUND_DRINK_TEQUILA in sound_names(game)
    assert bang_audio.SOUND_HEAL_SUCCESS in sound_names(game)
    assert any(
        f"{target.name} regains 1 life from your aid" in text
        for text in speech_texts(game, game.players.index(actor))
    )
    assert any(
        f"{actor.name} helps you regain 1 life" in text
        for text in speech_texts(game, game.players.index(target))
    )
    assert any(
        f"{actor.name} helps {target.name} regain 1 life" in text
        for text in speech_texts(game, game.players.index(observer))
    )


def test_tequila_cost_then_target_can_be_canceled_without_consuming_cards():
    game = start_game(4, seed=104)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    tequila = make_card(2414, cards.TEQUILA)
    cost = make_card(2415, cards.MISSED)
    actor.hand = [tequila, cost]
    target.life = target.max_life - 1
    game.decision = None
    game.effect_stack.clear()
    game.phase = PHASE_PLAY

    game._start_card_intent(actor, tequila)
    game._action_play_card(actor, f"play_card_{cost.id}")

    assert game.play_intent is not None
    assert game.play_intent.stage == "target"
    assert game.play_intent.selected_card_ids == [cost.id]
    assert actor.hand == [tequila, cost]
    game.flush_menus()
    items = turn_menu_items(game, game.players.index(actor))
    assert list(items)[-1] == "cancel_selection"
    assert "confirm_selection" not in items

    game._action_cancel_selection(actor, "cancel_selection")

    assert game.play_intent is None
    assert {card.id for card in actor.hand} == {tequila.id, cost.id}
    assert tequila not in game.discard_pile
    assert cost not in game.discard_pile

    game._start_card_intent(actor, tequila)
    game._action_play_card(actor, f"play_card_{cost.id}")
    game._action_choose_player(actor, f"choose_player_{target.id}")

    assert game.play_intent is None
    assert actor.hand == []
    assert target.life == target.max_life
    assert {tequila.id, cost.id} <= {card.id for card in game.discard_pile}


def test_saloon_and_hard_liquor_report_when_no_life_is_recovered():
    game = start_game(4, seed=94)
    actor = game.current_player
    observer = next(player for player in game.players if player is not actor)
    saloon = make_card(2414, cards.SALOON)
    actor.hand = [saloon]
    for player in game.players_in_play:
        player.life = player.max_life
    for listener in (actor, observer):
        user = game.get_user(listener)
        assert isinstance(user, MockUser)
        user.messages.clear()

    game._start_card_intent(actor, saloon)

    assert bang_audio.SOUND_DRINK_BEER not in sound_names(game)
    assert bang_audio.SOUND_DRINK_WHISKY not in sound_names(game)
    assert bang_audio.SOUND_HEAL_SUCCESS not in sound_names(game)
    assert any(
        "You play Saloon; everyone is at full life." in text
        for text in speech_texts(game, game.players.index(actor))
    )
    assert any(
        f"{actor.name} plays Saloon; everyone is at full life." in text
        for text in speech_texts(game, game.players.index(observer))
    )

    for listener in (actor, observer):
        user = game.get_user(listener)
        assert isinstance(user, MockUser)
        user.messages.clear()
    game.current_event = "hard_liquor"
    game.effect_stack = [
        BangEffect(
            kind="draw_phase",
            actor_id=actor.id,
            stage="after_hard_liquor",
        )
    ]
    game.decision = BangDecision(
        kind="hard_liquor",
        player_id=actor.id,
        item_ids=["draw_normally", "skip_draw_heal"],
    )

    game._resolve_item_decision(actor, "skip_draw_heal")

    assert any(
        "You skip drawing for Hard Liquor, but your life is already full." in text
        for text in speech_texts(game, game.players.index(actor))
    )
    assert any(
        f"{actor.name} skips drawing for Hard Liquor at full life." in text
        for text in speech_texts(game, game.players.index(observer))
    )


def test_saloon_spatializes_one_drink_and_success_cue_per_healed_player():
    game = start_game(5, seed=194)
    actor = game.current_player
    saloon = make_card(2416, cards.SALOON)
    actor.hand = [saloon]
    for player in game.players_in_play:
        player.life = player.max_life - 1
    clear_user_messages(game)

    game._start_card_intent(actor, saloon)

    sequence = next(
        sequence
        for sequence in game.active_sequences
        if sequence.tag == "bang_saloon"
    )
    drink_beats = sequence.beats[:-1]
    assert all(
        bang_audio.SALOON_STAGGER_MIN_TICKS
        <= beat.delay_after_ticks
        <= bang_audio.SALOON_STAGGER_MAX_TICKS
        for beat in drink_beats[:-1]
    )
    assert drink_beats[-1].delay_after_ticks == 0

    tick_until(game, lambda: not game.has_active_sequence(tag="bang_saloon"))

    assert all(
        player.life == player.max_life
        for player in game.players_in_play
    )
    user = game.get_user(actor)
    assert isinstance(user, MockUser)
    sound_messages = [
        message.data
        for message in user.messages
        if message.type == "play_sound"
    ]
    drink_messages = [
        data
        for data in sound_messages
        if data["name"]
        in {
            bang_audio.SOUND_DRINK_BEER,
            bang_audio.SOUND_DRINK_WHISKY,
        }
    ]
    assert len(drink_messages) == len(game.players_in_play)
    assert {data["name"] for data in drink_messages} == {
        bang_audio.SOUND_DRINK_BEER,
        bang_audio.SOUND_DRINK_WHISKY,
    }
    assert [data["pan"] for data in drink_messages] == [
        -70,
        -35,
        0,
        35,
        70,
    ]
    assert sum(
        data["name"] == bang_audio.SOUND_HEAL_SUCCESS
        for data in sound_messages
    ) == len(game.players_in_play)


def test_saloon_sequence_survives_json_round_trip_without_repeating_heals():
    game = start_game(4, seed=195)
    actor = game.current_player
    saloon = make_card(2417, cards.SALOON)
    actor.hand = [saloon]
    for player in game.players_in_play:
        player.life = player.max_life - 1

    game._start_card_intent(actor, saloon)
    already_healed = sum(
        player.life == player.max_life
        for player in game.players_in_play
    )
    assert already_healed == 1

    restored = BangGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    tick_until(
        restored,
        lambda: not restored.has_active_sequence(tag="bang_saloon"),
    )

    assert all(
        player.life == player.max_life
        for player in restored.players_in_play
    )
    assert sum(
        card.kind == cards.SALOON
        for card in restored.discard_pile
    ) == 1


def test_lethal_beer_and_tequila_joe_recovery():
    game = start_game(4, seed=7)
    target = game.players[1]
    target.character = "tequila_joe"
    beer = make_card(2401, cards.BEER, suit=cards.HEARTS)
    target.hand = [beer]
    target.life = 0
    game._push_effect(
        BangEffect(
            kind="damage",
            target_id=target.id,
            amount=1,
            source=DamageSource(kind="dynamite"),
        )
    )
    game._continue_effects()
    assert game.decision and beer.id in game.decision.card_ids
    game._use_decision_card(target, beer)
    assert target.life == 1
    assert not target.eliminated


def test_bot_sid_lethal_recovery_completes_without_reopening_forever():
    game = start_game(4, seed=154, bots=True)
    attacker = game.current_player
    target = game._clockwise_after(attacker, exclude_actor=True)[0]
    target.character = "sid_ketchum"
    target.life = 1
    first = make_card(2402, cards.BANG)
    second = make_card(2403, cards.MISSED)
    target.hand = [first, second]
    target.in_play.clear()
    game._push_effect(
        BangEffect(
            kind="damage",
            target_id=target.id,
            amount=1,
            source=DamageSource(
                player_id=attacker.id,
                kind="bang_card",
            ),
        )
    )

    game._continue_effects()
    tick_until(
        game,
        lambda: (
            target.life == 1
            and not target.eliminated
            and game.decision is None
            and game.play_intent is None
        ),
    )

    assert target.hand == []
    assert {first.id, second.id} <= {
        card.id for card in game.discard_pile
    }
    assert not any(
        frame.kind == "damage" and frame.target_id == target.id
        for frame in game.effect_stack
    )


def test_lethal_recovery_does_not_offer_sid_with_a_protected_law_card():
    game = start_game(4, seed=83)
    player = game.current_player
    player.character = "sid_ketchum"
    forced = make_card(2405, cards.STAGECOACH)
    other = make_card(2406, cards.MISSED)
    player.hand = [forced, other]
    player.life = 0
    player.law_card_id = forced.id
    game.current_event = "law_of_the_west"
    game.phase = PHASE_PLAY
    game.decision = None
    game.effect_stack.clear()

    assert game._can_normally_play(player, forced)
    assert not game._open_lethal_recovery(player)
    assert game.decision is None


def test_lethal_recovery_respects_the_active_players_handcuffs_suit():
    game = start_game(4, seed=84)
    player = game.current_player
    player.character = "bart_cassidy"
    wrong_suit = make_card(2407, cards.BEER, suit=cards.HEARTS)
    matching = make_card(2408, cards.BEER, suit=cards.SPADES)
    player.life = 0
    player.hand = [wrong_suit]
    player.handcuffs_suit = cards.SPADES
    game.current_event = "handcuffs"
    game.phase = PHASE_PLAY
    game.decision = None
    game.effect_stack.clear()

    assert not game._open_lethal_recovery(player)
    assert game.decision is None

    player.hand.append(matching)
    assert game._open_lethal_recovery(player)
    assert game.decision
    assert game.decision.card_ids == [matching.id]


def test_handcuffs_restricts_only_the_active_players_duel_response():
    game = start_game(4, seed=85)
    active = game.current_player
    opponent = next(player for player in game.players if player is not active)
    active_match = make_card(2409, cards.BANG, suit=cards.SPADES)
    active_wrong = make_card(2410, cards.BANG, suit=cards.HEARTS)
    opponent_match = make_card(2411, cards.BANG, suit=cards.SPADES)
    opponent_wrong = make_card(2412, cards.BANG, suit=cards.HEARTS)
    active.hand = [active_wrong, active_match]
    opponent.hand = [opponent_wrong, opponent_match]
    active.handcuffs_suit = cards.SPADES
    game.current_event = "handcuffs"

    game._continue_duel(
        BangEffect(kind="duel", data={"responder_id": active.id})
    )
    assert game.decision
    assert game.decision.card_ids == [active_match.id]

    game.decision = None
    game._continue_duel(
        BangEffect(kind="duel", data={"responder_id": opponent.id})
    )
    assert game.decision
    assert game.decision.card_ids == [opponent_wrong.id, opponent_match.id]


def test_insufficient_last_beer_finishes_recovery_with_elimination():
    game = start_game(4, seed=71)
    target = next(
        player
        for player in game.players
        if player is not game.current_player
    )
    target.character = "bart_cassidy"
    beer = make_card(2404, cards.BEER, suit=cards.HEARTS)
    target.hand = [beer]
    target.in_play = []
    target.life = 0
    game.decision = None
    game.effect_stack.clear()
    game._push_effect(
        BangEffect(
            kind="damage",
            target_id=target.id,
            amount=1,
            source=DamageSource(kind="dynamite"),
        )
    )
    game._continue_effects()

    assert target.life == -1
    assert game.decision and game.decision.kind == "lethal_recovery"
    game._use_decision_card(target, beer)

    assert target.life == 0
    assert target.eliminated
    assert game.decision is None
    tick_until(game, lambda: not game.effect_stack)
    assert game.effect_stack == []


def test_three_player_victory_and_wrong_kill_fallback():
    game = start_game(3, seed=9)
    deputy = next(player for player in game.players if player.role == ROLE_DEPUTY)
    renegade = next(
        player for player in game.players if player.role == ROLE_RENEGADE
    )
    outlaw = next(player for player in game.players if player.role == ROLE_OUTLAW)
    assert game._three_player_goal_hit(deputy, renegade)
    assert not game._three_player_goal_hit(deputy, outlaw)
    game.three_player_last_standing = True
    outlaw.eliminated = True
    renegade.eliminated = True
    game._check_victory()
    assert game.phase == PHASE_GAME_OVER
    assert game.winner_ids == [deputy.id]


def test_standard_victory_includes_eliminated_teammates():
    game = start_game(5, seed=10)
    deputy = next(player for player in game.players if player.role == ROLE_DEPUTY)
    deputy.eliminated = True
    for player in game.players:
        if player.role in {ROLE_OUTLAW, ROLE_RENEGADE}:
            player.eliminated = True
    game._check_victory()
    assert game.phase == PHASE_GAME_OVER
    assert deputy.id in game.winner_ids
    sheriff = next(player for player in game.players if player.role == ROLE_SHERIFF)
    assert sheriff.id in game.winner_ids


def test_renegade_killing_sheriff_loses_while_another_player_survives():
    game = start_game(5, seed=181)
    sheriff = next(player for player in game.players if player.role == ROLE_SHERIFF)
    renegade = next(
        player for player in game.players if player.role == ROLE_RENEGADE
    )
    deputy = next(player for player in game.players if player.role == ROLE_DEPUTY)
    outlaws = [player for player in game.players if player.role == ROLE_OUTLAW]
    for outlaw in outlaws:
        outlaw.eliminated = True
    sheriff.life = 0
    sheriff.eliminated = True

    game._apply_elimination_triggers(
        sheriff,
        DamageSource(player_id=renegade.id, kind="bang_card"),
    )

    assert not deputy.eliminated
    assert game.winning_side == ROLE_OUTLAW
    assert game.winner_ids == [outlaw.id for outlaw in outlaws]
    assert renegade.id not in game.winner_ids


def test_renegade_killing_sheriff_wins_as_the_only_survivor():
    game = start_game(4, seed=182)
    sheriff = next(player for player in game.players if player.role == ROLE_SHERIFF)
    renegade = next(
        player for player in game.players if player.role == ROLE_RENEGADE
    )
    for player in game.players:
        if player.id not in {sheriff.id, renegade.id}:
            player.eliminated = True
    sheriff.life = 0
    sheriff.eliminated = True

    game._apply_elimination_triggers(
        sheriff,
        DamageSource(player_id=renegade.id, kind="bang_card"),
    )

    assert game.winning_side == ROLE_RENEGADE
    assert game.winner_ids == [renegade.id]


def test_game_end_discards_the_card_whose_effect_caused_victory():
    game = start_game(4, seed=106)
    actor = game.current_player
    played = actor.hand.pop()
    game.resolving_card = ResolvingCard(card=played, actor_id=actor.id)

    game._end_game([actor], actor.role)

    assert game.resolving_card is None
    assert played in game.discard_pile
    card_ids = all_card_ids(game)
    assert len(card_ids) == 120
    assert len(set(card_ids)) == 120


def test_private_actor_and_public_observer_card_announcements():
    game = start_game(4, seed=12)
    actor = game.current_player
    observer = next(player for player in game.players if player is not actor)
    actor_index = game.players.index(actor)
    observer_index = game.players.index(observer)
    actor_user = game.get_user(actor)
    observer_user = game.get_user(observer)
    assert isinstance(actor_user, MockUser)
    assert isinstance(observer_user, MockUser)
    actor_user.messages.clear()
    observer_user.messages.clear()
    stagecoach = make_card(2501, cards.STAGECOACH)
    actor.hand = [stagecoach]
    game._start_card_intent(actor, stagecoach)
    actor_text = " ".join(speech_texts(game, actor_index))
    observer_text = " ".join(speech_texts(game, observer_index))
    assert "You play Stagecoach" in actor_text
    assert f"{actor.name} plays Stagecoach" in observer_text
    assert f"{actor.name} plays Stagecoach" not in actor_text


def test_observers_hear_the_identity_of_a_stolen_public_card():
    game = start_game(4, seed=78)
    actor = game.current_player
    target, observer = game._clockwise_after(actor, exclude_actor=True)[:2]
    weapon = make_card(
        2502,
        cards.WINCHESTER,
        rank="8",
        suit=cards.SPADES,
        border=cards.BLUE,
    )
    target.in_play = [BangInPlayCard(weapon)]
    game.effect_stack = [
        BangEffect(
            kind="target_card",
            actor_id=actor.id,
            target_id=target.id,
            data={"mode": "steal"},
        )
    ]
    decision = BangDecision(
        kind="target_card",
        player_id=actor.id,
        data={"target_id": target.id, "mode": "steal"},
    )
    game.decision = decision
    target_user = game.get_user(target)
    observer_user = game.get_user(observer)
    assert isinstance(target_user, MockUser)
    assert isinstance(observer_user, MockUser)
    target_user.messages.clear()
    observer_user.messages.clear()

    game._resolve_target_card_item(
        actor,
        decision,
        f"in_play_{weapon.id}",
    )

    observer_text = " ".join(speech_texts(game, game.players.index(observer)))
    assert (
        f"{actor.name} takes Winchester, 8 of spades from {target.name}"
        in observer_text
    )
    assert (
        f"{target.name} loses Winchester; Colt .45 is active, range 1"
        in observer_text
    )
    assert "hidden card" not in observer_text
    target_text = " ".join(speech_texts(game, game.players.index(target)))
    assert (
        "You lose Winchester; Colt .45 is active, range 1"
        in target_text
    )


def test_general_store_reveal_and_each_public_pick_are_announced():
    game = start_game(4, seed=79)
    actor = game.current_player
    observer = next(player for player in game.players if player is not actor)
    store = make_card(2510, cards.GENERAL_STORE)
    revealed = [
        make_card(2511, cards.BANG, rank="2", suit=cards.CLUBS),
        make_card(2512, cards.MISSED, rank="3", suit=cards.SPADES),
        make_card(2513, cards.BEER, rank="4", suit=cards.HEARTS),
        make_card(2514, cards.DUEL, rank="5", suit=cards.DIAMONDS),
    ]
    actor.hand = [store]
    game.deck = [*revealed, *game.deck]
    observer_user = game.get_user(observer)
    assert isinstance(observer_user, MockUser)
    observer_user.messages.clear()

    game._start_card_intent(actor, store)

    reveal_text = " ".join(speech_texts(game, game.players.index(observer)))
    assert "General Store reveals 4 cards" in reveal_text
    assert "BANG!, 2 of clubs" in reveal_text
    assert "Duel, 5 of diamonds" in reveal_text
    observer_user.messages.clear()
    game._resolve_item_decision(actor, f"store_{revealed[0].id}")

    pick_text = " ".join(speech_texts(game, game.players.index(observer)))
    assert (
        f"{actor.name} takes BANG!, 2 of clubs from General Store"
        in pick_text
    )


def test_elimination_and_victory_use_listener_specific_perspectives():
    game = start_game(5, seed=155)
    killer = game.current_player
    victim = next(
        player
        for player in game.players
        if player.role == ROLE_OUTLAW and player.id != killer.id
    )
    observer = next(
        player
        for player in game.players
        if player.id not in {killer.id, victim.id}
    )
    victim.life = 1
    victim.character = "rose_doolan"
    victim.hand.clear()
    victim.in_play.clear()
    game.effect_stack.clear()
    game.decision = None
    game.play_intent = None
    clear_user_messages(game)

    game._push_effect(
        BangEffect(
            kind="damage",
            target_id=victim.id,
            amount=1,
            source=DamageSource(
                player_id=killer.id,
                kind="bang_card",
            ),
        )
    )
    game._continue_effects()
    tick_until(game, lambda: victim.eliminated)

    assert any(
        f"You eliminate {victim.name}, the Outlaw" in text
        for text in speech_texts(game, game.players.index(killer))
    )
    assert any(
        "You are eliminated. Your role was Outlaw" in text
        for text in speech_texts(game, game.players.index(victim))
    )
    assert any(
        f"{victim.name} is eliminated as the Outlaw" in text
        for text in speech_texts(game, game.players.index(observer))
    )

    winner = killer
    loser = victim
    spectator = observer
    spectator.is_spectator = True
    clear_user_messages(game)
    game._end_game([winner], ROLE_SHERIFF)

    assert any(
        "You win. Winning side: Sheriff" in text
        for text in speech_texts(game, game.players.index(winner))
    )
    assert any(
        "You lose. Winning side: Sheriff" in text
        for text in speech_texts(game, game.players.index(loser))
    )
    assert any(
        "The game is over. Winning side: Sheriff" in text
        for text in speech_texts(game, game.players.index(spectator))
    )


@pytest.mark.parametrize("client_type", ["mobile", "web"])
def test_touch_standard_info_order_and_no_score_actions(
    client_type: str,
):
    game = start_game(4, seed=13, touch=True)
    player = game.players[0]
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    user.client_type = client_type
    action_set = game.get_action_set(player, "standard")
    assert action_set is not None
    order = action_set._order
    expected = [
        "read_life",
        "read_role",
        "read_distances",
        "read_piles",
        "read_event",
        "read_table",
        "read_hand",
        "whose_turn",
        "whos_at_table",
    ]
    assert [action_id for action_id in order if action_id in expected] == expected
    visible = [
        resolved.action.id
        for resolved in action_set.get_visible_actions(game, player)
    ]
    assert [
        action_id for action_id in visible if action_id in expected
    ] == expected
    game.refresh_menus(player)
    game.flush_menus()
    rendered = list(turn_menu_items(game, 0))
    assert [
        action_id for action_id in rendered if action_id in expected
    ] == expected
    assert "check_scores" not in order
    assert "check_scores_detailed" not in order


def test_desktop_actions_menu_uses_the_same_bang_info_order():
    game = start_game(4, seed=13)
    player = game.players[0]
    action_set = game.get_action_set(player, "standard")
    assert action_set is not None
    expected = [
        "read_life",
        "read_role",
        "read_distances",
        "read_piles",
        "read_event",
        "read_table",
        "read_hand",
    ]
    enabled = [
        resolved.action.id
        for resolved in action_set.get_enabled_actions(game, player)
    ]
    assert [action_id for action_id in enabled if action_id in expected] == expected
    user = game.get_user(player)
    assert isinstance(user, MockUser)
    game._action_show_actions_menu(player, "show_actions")
    rendered = [
        item.id
        for item in user.menus["actions_menu"]["items"]
        if item.id
    ]
    assert [
        action_id for action_id in rendered if action_id in expected
    ] == expected


def test_read_piles_has_active_public_shortcut():
    game = make_game(4)
    bindings = game._keybinds["p"]

    assert any(
        binding.actions == ["read_piles"]
        and binding.state == KeybindState.ACTIVE
        and binding.include_spectators
        for binding in bindings
    )
    action_set = game.get_action_set(game.players[0], "standard")
    assert action_set is not None
    action = action_set.get_action("read_piles")
    assert action is not None
    assert action.include_spectators


def test_read_life_has_a_shortcut_and_touch_visible_action():
    game = start_game(4, seed=152, touch=True)
    active = game.current_player
    reader = next(player for player in game.players if player is not active)
    reader.life = max(1, reader.max_life - 1)
    binding = game._keybinds["l"]
    assert any(
        item.actions == ["read_life"]
        and item.state == KeybindState.ACTIVE
        and not item.include_spectators
        for item in binding
    )
    action_set = game.get_action_set(reader, "standard")
    assert action_set is not None
    action = action_set.get_action("read_life")
    assert action is not None
    assert not action.include_spectators
    assert game._is_info_hidden(reader) is Visibility.VISIBLE
    clear_user_messages(game)

    game._handle_keybind_event(reader, {"key": "l"})

    assert any(
        f"You have {reader.life} of {reader.max_life} life." == text
        for text in speech_texts(game, game.players.index(reader))
    )


def test_out_of_turn_hand_rows_remain_visible_but_cannot_be_played():
    game = start_game(4, seed=153)
    active = game.current_player
    reader = next(player for player in game.players if player is not active)
    card = make_card(2618, cards.BANG, rank="7", suit=cards.HEARTS)
    reader.hand = [card]
    game.decision = BangDecision(
        kind="handcuffs",
        player_id=active.id,
        prompt_key="bang-prompt-handcuffs",
        item_ids=[cards.CLUBS, cards.DIAMONDS, cards.HEARTS, cards.SPADES],
    )
    game.refresh_menus(reader)
    game.flush_menus()

    action_id = f"play_card_{card.id}"
    items = turn_menu_items(game, game.players.index(reader))
    assert action_id in items
    resolved = next(
        action
        for action in game.get_all_visible_actions(reader)
        if action.action.id == action_id
    )
    assert not resolved.enabled
    before = list(reader.hand)

    game.execute_action(reader, action_id)

    assert reader.hand == before
    assert game.play_intent is None


def test_read_hand_remains_private_and_available_out_of_turn():
    game = start_game(4, seed=147)
    active = game.current_player
    reader = next(player for player in game.players if player is not active)
    reader.hand = [
        make_card(2617, cards.BANG, rank="7", suit=cards.HEARTS),
    ]
    game.decision = BangDecision(
        kind="handcuffs",
        player_id=active.id,
        prompt_key="bang-prompt-handcuffs",
        item_ids=[cards.CLUBS, cards.DIAMONDS, cards.HEARTS, cards.SPADES],
    )
    clear_user_messages(game)

    assert game._is_private_info_enabled(reader) is None
    game._handle_keybind_event(reader, {"key": "h"})

    reader_index = game.players.index(reader)
    assert any(
        "Your card is BANG!, 7 of hearts." in text
        for text in speech_texts(game, reader_index)
    )
    for index, player in enumerate(game.players):
        if player is not reader:
            assert not speech_texts(game, index)


def test_waiting_error_repeats_the_exact_pending_instruction():
    game = start_game(4, seed=148)
    owner = game.current_player
    observer = next(player for player in game.players if player is not owner)
    game.decision = BangDecision(
        kind="handcuffs",
        player_id=owner.id,
        prompt_key="bang-prompt-handcuffs",
        item_ids=[cards.CLUBS, cards.DIAMONDS, cards.HEARTS, cards.SPADES],
    )

    reason = game._phase_error(observer)

    assert isinstance(reason, tuple)
    assert reason[0] == "bang-error-waiting-for-player"
    assert reason[1] == {
        "player": owner.name,
        "action": "Choose the only suit you may play this turn.",
    }


def test_waiting_error_does_not_reveal_an_uncommitted_hand_card():
    game = start_game(4, seed=150)
    owner = game.current_player
    observer = next(player for player in game.players if player is not owner)
    tequila = make_card(2619, cards.TEQUILA)
    owner.hand = [tequila]
    game.decision = None
    game.play_intent = BangPlayIntent(
        kind="card",
        actor_id=owner.id,
        card_id=tequila.id,
        required=1,
        stage="target",
    )

    reason = game._phase_error(observer)

    assert isinstance(reason, tuple)
    assert reason == (
        "bang-error-waiting-for-player",
        {
            "player": owner.name,
            "action": (
                "choose a legal target for the pending action, or cancel."
            ),
        },
    )
    assert "Tequila" not in reason[1]["action"]


def test_public_card_broadcasts_render_for_each_listener_locale():
    game = start_game(4, seed=149)
    actor = game.current_player
    opponent, observer = game._clockwise_after(
        actor,
        exclude_actor=True,
    )[:2]
    observer_user = game.get_user(observer)
    assert isinstance(observer_user, MockUser)
    observer_user._locale = "vi"
    card = make_card(2618, cards.BANG, rank="7", suit=cards.HEARTS)
    clear_user_messages(game)

    game._announce_duel_response(
        actor,
        card,
        BangEffect(
            kind="duel",
            actor_id=opponent.id,
            target_id=actor.id,
        ),
    )

    assert any(
        "You discard BANG!, 7 of hearts in the Duel." in text
        for text in speech_texts(game, game.players.index(actor))
    )
    assert any(
        f"{actor.name} bỏ BANG!, 7 cơ trong màn Quyết đấu." in text
        for text in speech_texts(game, game.players.index(observer))
    )


def test_spacebar_uses_one_contextual_action_and_repeats_target_instruction():
    game = start_game(4, seed=68)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    bang = make_card(2600, cards.BANG)
    actor.hand = [bang]
    actor_user = game.get_user(actor)
    assert isinstance(actor_user, MockUser)
    actor_user.messages.clear()
    game.decision = None
    game.effect_stack.clear()
    game.phase = PHASE_PLAY
    assert [
        keybind.actions for keybind in game._keybinds["space"]
    ] == [["end_or_confirm"]]

    game._start_card_intent(actor, bang)
    assert game.play_intent and game.play_intent.stage == "target"
    game._handle_keybind_event(actor, {"key": "space"})

    assert game.play_intent and game.play_intent.stage == "target"
    assert target.life == target.max_life
    assert any(
        "BANG!: choose a target, or Cancel." in text
        for text in speech_texts(game, game.players.index(actor))
    )


def test_spacebar_reports_incomplete_multi_selection_context():
    game = start_game(4, seed=69)
    actor = game.current_player
    actor_user = game.get_user(actor)
    assert isinstance(actor_user, MockUser)
    actor_user.messages.clear()
    first = make_card(2603, cards.BANG)
    second = make_card(2604, cards.MISSED)
    actor.hand = [first, second]
    game.play_intent = BangPlayIntent(
        kind="sid_ketchum",
        actor_id=actor.id,
        required=2,
        stage="cost",
        selected_card_ids=[first.id],
        data={"allowed_card_ids": [first.id, second.id]},
    )

    game._action_end_or_confirm(actor, "end_or_confirm")

    assert game.play_intent is not None
    assert game.play_intent.selected_card_ids == [first.id]
    assert any(
        "Select the remaining required cards, then confirm" in text
        for text in speech_texts(game, game.players.index(actor))
    )


def test_sid_ketchum_is_available_between_other_players_cards():
    game = start_game(4, seed=45)
    sid = next(player for player in game.players if player is not game.current_player)
    sid.character = "sid_ketchum"
    sid.life = max(1, sid.max_life - 1)
    sid.hand = [
        make_card(2611, cards.BANG),
        make_card(2612, cards.MISSED),
    ]
    assert game._is_sid_hidden(sid).value == "visible"
    assert game._is_sid_enabled(sid) is None
    game._action_sid_ketchum(sid, "sid_ketchum")
    active = game.current_player
    assert active is not sid
    active_action_id = f"play_card_{active.hand[0].id}"
    assert game._is_play_card_hidden(
        active,
        action_id=active_action_id,
    ).value == "visible"
    assert game._is_play_card_enabled(
        active,
        action_id=active_action_id,
    ) is not None


def test_sid_ketchum_completes_and_cancels_safely_out_of_turn():
    game = start_game(4, seed=145)
    active = game.current_player
    sid = next(player for player in game.players if player is not active)
    sid.character = "sid_ketchum"
    sid.life = sid.max_life - 2
    first = make_card(2613, cards.BANG)
    second = make_card(2614, cards.MISSED)
    sid.hand = [first, second]

    game._action_sid_ketchum(sid, "sid_ketchum")
    game._action_play_card(sid, f"play_card_{first.id}")
    game._action_cancel_selection(sid, "cancel_selection")

    assert game.play_intent is None
    assert sid.life == sid.max_life - 2
    assert [card.id for card in sid.hand] == [first.id, second.id]
    assert game.current_player is active

    game._action_sid_ketchum(sid, "sid_ketchum")
    game._action_play_card(sid, f"play_card_{first.id}")
    game._action_play_card(sid, f"play_card_{second.id}")
    game._action_confirm_selection(sid, "confirm_selection")

    assert game.play_intent is None
    assert sid.life == sid.max_life - 1
    assert sid.hand == []
    assert {card.id for card in game.discard_pile[-2:]} == {
        first.id,
        second.id,
    }
    assert game.current_player is active
    assert game.phase == PHASE_PLAY


def test_sid_ketchum_cannot_interrupt_an_unresolved_choice():
    game = start_game(4, seed=146)
    active = game.current_player
    sid = next(player for player in game.players if player is not active)
    sid.character = "sid_ketchum"
    sid.life = sid.max_life - 1
    sid.hand = [
        make_card(2615, cards.BANG),
        make_card(2616, cards.MISSED),
    ]
    game.decision = BangDecision(
        kind="handcuffs",
        player_id=active.id,
        prompt_key="bang-prompt-handcuffs",
        item_ids=[cards.CLUBS, cards.DIAMONDS, cards.HEARTS, cards.SPADES],
    )

    assert game._is_sid_hidden(sid).value == "hidden"
    reason = game._is_sid_enabled(sid)
    assert isinstance(reason, tuple)
    assert reason[0] == "bang-error-waiting-for-player"
    assert reason[1]["player"] == active.name
    assert (
        "Choose the only suit you may play this turn"
        in reason[1]["action"]
    )

    game._action_sid_ketchum(sid, "sid_ketchum")

    assert game.play_intent is None
    assert sid.life == sid.max_life - 1
    assert len(sid.hand) == 2


def test_ghost_town_ghosts_can_heal_and_spend_life_but_ignore_damage():
    game = start_game(4, seed=48)
    ghost = game.players[1]
    ghost.eliminated = True
    ghost.ghost_active = True
    ghost.life = 0
    ghost.hand = []
    game._heal(ghost, 2)
    assert ghost.life == 2
    game._push_effect(
        BangEffect(
            kind="damage",
            target_id=ghost.id,
            amount=3,
            source=DamageSource(kind="dynamite"),
        )
    )
    game._continue_effects()
    assert ghost.life == 2

    ghost.character = "chuck_wengam"
    ghost.life = 1
    deck_count = len(game.deck)
    assert game._is_chuck_enabled(ghost) is None
    game._action_chuck_wengam(ghost, "chuck_wengam")
    assert ghost.life == 0
    assert len(ghost.hand) == 2
    assert len(game.deck) == deck_count - 2
    assert ghost.eliminated
    assert ghost.ghost_active


def test_sniper_is_touch_visible_only_during_its_active_play_window():
    game = start_game(4, seed=14, touch=True)
    actor = game.current_player
    actor.hand = [
        make_card(2601, cards.BANG),
        make_card(2602, cards.BANG),
    ]
    game.current_event = "sniper"
    assert game._is_sniper_hidden(actor).value == "visible"
    game.current_event = ""
    assert game._is_sniper_hidden(actor).value == "hidden"


def test_phase_one_draw_is_spoken_privately_and_counted_publicly():
    game = start_game(4, seed=46)
    actor = game.current_player
    actor_index = game.players.index(actor)
    observer = next(player for player in game.players if player is not actor)
    observer_index = game.players.index(observer)
    assert any("You draw 2 cards:" in text for text in speech_texts(game, actor_index))
    assert any(
        f"{actor.name} draws 2 cards." in text
        for text in speech_texts(game, observer_index)
    )


def test_renegade_bot_target_score_does_not_inspect_hidden_roles():
    game = make_game(5, bots=True)
    actor, first, second = game.players[:3]
    actor.role = ROLE_RENEGADE
    first.role_revealed = False
    second.role_revealed = False
    first.life = second.life = 3
    first.role = ROLE_OUTLAW
    second.role = ROLE_DEPUTY
    first_score = bang_bot._target_score(game, actor, first)
    second_score = bang_bot._target_score(game, actor, second)
    assert first_score[:2] == second_score[:2]
    first.role, second.role = second.role, first.role
    assert bang_bot._target_score(game, actor, first)[:2] == first_score[:2]
    assert bang_bot._target_score(game, actor, second)[:2] == second_score[:2]


def test_bot_targeting_accounts_for_public_threat_without_reading_hand_faces():
    game = make_game(4, bots=True)
    actor, armed, quiet, _ = game.players
    actor.role = ROLE_SHERIFF
    actor.bot_role_suspicion = {armed.id: 1, quiet.id: 1}
    armed.role_revealed = quiet.role_revealed = False
    armed.life = quiet.life = 3
    armed.in_play = [
        BangInPlayCard(
            make_card(2818, cards.WINCHESTER, border=cards.BLUE)
        )
    ]
    armed.hand = [
        make_card(2819, cards.BANG),
        make_card(2820, cards.BEER),
    ]
    quiet.hand = [
        make_card(2821, cards.MISSED),
        make_card(2822, cards.DODGE),
    ]

    assert bang_bot._best_target(
        game,
        actor,
        [quiet.id, armed.id],
    ) == armed.id
    score = bang_bot._target_score(game, actor, armed)
    armed.hand = [
        make_card(2823, cards.DYNAMITE),
        make_card(2824, cards.SALOON),
    ]
    assert bang_bot._target_score(game, actor, armed) == score


def test_bot_global_attacks_protect_public_allies_and_pressure_the_sheriff():
    game = make_game(4, bots=True)
    outlaw, sheriff, unknown, other = game.players
    outlaw.role = ROLE_OUTLAW
    sheriff.role = ROLE_SHERIFF
    sheriff.role_revealed = True
    unknown.role_revealed = other.role_revealed = False
    assert bang_bot._global_attack_is_sensible(game, outlaw)

    deputy = outlaw
    deputy.role = ROLE_DEPUTY
    sheriff.life = 1
    assert not bang_bot._global_attack_is_sensible(game, deputy)


def test_bot_saloon_and_ricochet_choices_trade_cards_for_public_value():
    game = make_game(4, bots=True)
    outlaw, sheriff, attacker, other = game.players
    outlaw.role = ROLE_OUTLAW
    sheriff.role = ROLE_SHERIFF
    sheriff.role_revealed = True
    outlaw.life = outlaw.max_life
    sheriff.life = sheriff.max_life - 1
    attacker.life = attacker.max_life
    other.life = other.max_life
    assert not bang_bot._saloon_is_sensible(game, outlaw)
    sheriff.life = sheriff.max_life
    outlaw.life -= 1
    assert bang_bot._saloon_is_sensible(game, outlaw)

    dynamite = make_card(2825, cards.DYNAMITE, border=cards.BLUE)
    dodge = make_card(2826, cards.DODGE)
    outlaw.in_play = [BangInPlayCard(dynamite)]
    outlaw.hand = [dodge]
    game.effect_stack = [
        BangEffect(
            kind="ricochet",
            stage="response",
            actor_id=attacker.id,
            target_id=outlaw.id,
            card_ids=[dynamite.id],
        )
    ]
    game.decision = BangDecision(
        kind="ricochet",
        player_id=outlaw.id,
        card_ids=[dodge.id],
        item_ids=["lose_in_play"],
    )
    assert bang_bot.choose_action(game, outlaw) == "choice_lose_in_play"


def test_bot_pacing_uses_human_scale_serialized_delays():
    game = start_game(4, seed=88, bots=True)
    assert all(
        BOT_TURN_DELAY_TICKS[0]
        <= player.bot_think_ticks
        <= BOT_TURN_DELAY_TICKS[1]
        for player in game.players
    )
    bot = game.current_player
    bot.bot_pending_action = "end_turn"
    game._pace_bot(bot, choice=True)
    assert (
        BOT_CHOICE_DELAY_TICKS[0]
        <= bot.bot_think_ticks
        <= BOT_CHOICE_DELAY_TICKS[1]
    )
    assert bot.bot_pending_action is None

    restored = BangGame.from_json(game.to_json())
    restored_bot = restored.get_player_by_id(bot.id)
    assert restored_bot.bot_think_ticks == bot.bot_think_ticks


def test_bot_prefers_public_ally_for_blood_brothers():
    game = make_game(4, bots=True)
    deputy, sheriff, unknown, other = game.players
    deputy.role = ROLE_DEPUTY
    sheriff.role = ROLE_SHERIFF
    sheriff.role_revealed = True
    sheriff.max_life = 5
    sheriff.life = 2
    unknown.role = ROLE_OUTLAW
    unknown.role_revealed = False
    unknown.max_life = 4
    unknown.life = 1
    other.max_life = other.life = 4
    game.decision = BangDecision(
        kind="blood_brothers",
        player_id=deputy.id,
        player_ids=[sheriff.id, unknown.id],
        item_ids=["skip_blood_brothers"],
    )

    assert bang_bot.choose_action(game, deputy) == f"choose_player_{sheriff.id}"


def test_blood_brothers_skips_the_choice_when_nobody_can_be_healed():
    game = start_game(4, seed=105)
    actor = game.current_player
    actor.life = max(2, actor.life)
    for player in game.players_in_play:
        if player is not actor:
            player.life = player.max_life
    game.current_event = "blood_brothers"
    game.decision = None
    frame = BangEffect(
        kind="turn_start",
        stage="event_start",
        actor_id=actor.id,
    )

    game._continue_turn_start(frame)

    assert frame.stage == "after_event_start"
    assert game.decision is None


def test_blood_brothers_announces_one_complete_message_per_perspective():
    game = start_game(4, seed=158)
    donor = game.current_player
    target, observer = game._clockwise_after(donor, exclude_actor=True)[:2]
    donor.life = max(2, donor.life)
    target.life = target.max_life - 1
    game.effect_stack = [
        BangEffect(kind="turn_start", actor_id=donor.id)
    ]
    game.decision = BangDecision(
        kind="blood_brothers",
        player_id=donor.id,
        player_ids=[target.id],
        item_ids=["skip_blood_brothers"],
    )
    clear_user_messages(game)

    game._resolve_turn_player_choice(donor, target, game.decision)

    donor_text = " ".join(speech_texts(game, game.players.index(donor)))
    target_text = " ".join(speech_texts(game, game.players.index(target)))
    observer_text = " ".join(speech_texts(game, game.players.index(observer)))
    assert f"You lose one life, give one life to {target.name}" in donor_text
    assert f"{donor.name} loses one life and gives one life to you" in target_text
    assert (
        f"{donor.name} loses one life, gives one life to {target.name}"
        in observer_text
    )
    assert "You regain" not in target_text


def test_bot_uses_ready_green_cards_and_does_not_waste_full_life_whisky():
    game = start_game(4, seed=89, bots=True)
    bot = game.current_player
    game.phase = PHASE_PLAY
    game.effect_stack.clear()
    game.decision = None
    game.play_intent = None
    pony = make_card(2801, cards.PONY_EXPRESS, border=cards.GREEN)
    bot.in_play = [
        BangInPlayCard(pony, usable_after_turn=game.turn_serial)
    ]
    bot.hand = []
    assert bang_bot.choose_action(game, bot) == f"use_in_play_{pony.id}"

    bot.in_play = []
    bot.life = bot.max_life
    bot.hand = [
        make_card(2802, cards.WHISKY),
        make_card(2803, cards.MISSED),
    ]
    assert bang_bot.choose_action(game, bot) == "end_turn"


def test_bot_uses_dodge_before_missed_and_does_not_downgrade_weapon():
    game = start_game(4, seed=90, bots=True)
    bot = game.current_player
    dodge = make_card(2804, cards.DODGE)
    missed = make_card(2805, cards.MISSED)
    bot.hand = [missed, dodge]
    game.decision = BangDecision(
        kind="missed",
        player_id=bot.id,
        card_ids=[missed.id, dodge.id],
        item_ids=["take_hit"],
    )
    assert bang_bot.choose_action(game, bot) == f"play_card_{dodge.id}"

    game.decision = None
    game.phase = PHASE_PLAY
    game.effect_stack.clear()
    winchester = make_card(2806, cards.WINCHESTER, border=cards.BLUE)
    schofield = make_card(2807, cards.SCHOFIELD, border=cards.BLUE)
    bot.in_play = [BangInPlayCard(winchester)]
    bot.hand = [schofield, missed]
    assert bang_bot.choose_action(game, bot) == "end_turn"


def test_bot_keeps_valuable_cards_and_uses_effective_suits():
    game = start_game(4, seed=91, bots=True)
    bot = game.current_player
    barrel = make_card(2808, cards.BARREL, border=cards.BLUE)
    dynamite = make_card(2809, cards.DYNAMITE, border=cards.BLUE)
    bot.in_play = [BangInPlayCard(barrel), BangInPlayCard(dynamite)]
    game.decision = BangDecision(
        kind="daltons",
        player_id=bot.id,
        item_ids=[
            f"in_play_{barrel.id}",
            f"in_play_{dynamite.id}",
        ],
    )
    assert bang_bot.choose_action(game, bot) == f"choice_in_play_{dynamite.id}"

    bot.hand = [
        make_card(2810, cards.BANG, suit=cards.CLUBS),
        make_card(2811, cards.MISSED, suit=cards.DIAMONDS),
    ]
    game.current_event = "blessing"
    game.decision = BangDecision(
        kind="handcuffs",
        player_id=bot.id,
        item_ids=[f"suit_{suit}" for suit in cards.SUITS],
    )
    assert bang_bot.choose_action(game, bot) == "choice_suit_hearts"


def test_elena_bot_does_not_waste_beer_as_a_generic_missed_effect():
    game = start_game(4, seed=92, bots=True)
    bot = game.current_player
    bot.character = "elena_fuente"
    bot.life = bot.max_life - 1
    beer = make_card(2812, cards.BEER)
    expendable = make_card(2813, cards.CAT_BALOU)
    bot.hand = [beer, expendable]
    game.decision = BangDecision(
        kind="missed",
        player_id=bot.id,
        card_ids=[beer.id, expendable.id],
        item_ids=["take_hit"],
    )

    assert bang_bot.choose_action(game, bot) == f"play_card_{expendable.id}"


def test_bot_chooses_useful_character_for_vera_and_new_identity():
    game = start_game(4, seed=93, bots=True)
    bot, weak, strong, _ = game.players
    bot.character = "vera_custer"
    weak.character = "vulture_sam"
    strong.character = "willy_the_kid"
    bot.hand = [
        make_card(2814, cards.BANG),
        make_card(2815, cards.BANG),
    ]
    game.decision = BangDecision(
        kind="vera_custer",
        player_id=bot.id,
        player_ids=[weak.id, strong.id],
    )
    assert bang_bot.choose_action(game, bot) == f"choose_player_{strong.id}"

    bot.character = "vulture_sam"
    bot.alternate_character = "willy_the_kid"
    bot.life = 1
    game.decision = BangDecision(
        kind="new_identity",
        player_id=bot.id,
        item_ids=["keep_identity", "change_identity"],
    )
    assert bang_bot.choose_action(game, bot) == "choice_change_identity"


def test_sniper_sequence_synchronizes_aim_fire_tts_and_casing():
    game = start_game(4, seed=96)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    target.hand = [make_card(2690, cards.MISSED)]
    target.in_play.clear()
    clear_user_messages(game)

    game._start_shot(
        actor,
        target,
        source_kind="sniper",
        required=2,
    )

    assert game.is_sequence_gameplay_locked()
    assert sound_names(game)[0] == bang_audio.SOUND_SNIPER_AIM
    assert any(
        "sniper shot" in text
        for text in speech_texts(game, game.players.index(actor))
    )
    clear_user_messages(game)

    for _ in range(bang_audio.sound_ticks(bang_audio.SOUND_SNIPER_AIM)):
        game.on_tick()

    actor_user = game.get_user(actor)
    assert isinstance(actor_user, MockUser)
    fire_index = next(
        index
        for index, message in enumerate(actor_user.messages)
        if message.type == "play_sound"
        and message.data["name"] in bang_audio.SOUND_FIRE_SNIPER
    )
    speech_index = next(
        index
        for index, message in enumerate(actor_user.messages)
        if message.type == "speak" and "Sniper" in message.data["text"]
    )
    assert speech_index == fire_index + 1
    tick_until(game, lambda: not game.is_sequence_gameplay_locked())
    assert not game.is_sequence_gameplay_locked()
    assert set(sound_names(game)) & set(bang_audio.SOUND_CASING_DROPS)
    assert game.decision and game.decision.kind == "missed"


@pytest.mark.parametrize(
    ("player_count", "expected_role"),
    [(4, ROLE_SHERIFF), (3, ROLE_DEPUTY)],
)
def test_russian_roulette_prepares_fully_before_opening_defense(
    player_count: int,
    expected_role: str,
):
    game = start_game(player_count, seed=97)
    target = game._event_anchor()
    assert target is not None
    assert target.role == expected_role
    missed = make_card(2691, cards.MISSED)
    target.hand = [missed]
    target.in_play.clear()
    game.current_player = target
    game.sheriff_turns_started = 1
    game.event_deck = ["russian_roulette"]
    game.current_event = ""
    game.phase = PHASE_START_TURN
    game.effect_stack = [
        BangEffect(kind="turn_start", actor_id=target.id)
    ]
    game.decision = None
    clear_user_messages(game)

    game._continue_effects()

    assert sound_names(game) == [bang_audio.SOUND_ROULETTE_LOAD]
    assert game.is_sequence_gameplay_locked()

    for _ in range(
        bang_audio.sound_ticks(bang_audio.SOUND_ROULETTE_LOAD) - 1
    ):
        game.on_tick()
    assert sound_names(game) == [bang_audio.SOUND_ROULETTE_LOAD]
    game.on_tick()
    assert sound_names(game)[-1] == bang_audio.SOUND_ROULETTE_SPIN

    for _ in range(
        bang_audio.sound_ticks(bang_audio.SOUND_ROULETTE_SPIN) - 1
    ):
        game.on_tick()
    assert bang_audio.SOUND_ROULETTE_COCK not in sound_names(game)
    game.on_tick()
    assert sound_names(game)[-1] == bang_audio.SOUND_ROULETTE_COCK

    for _ in range(
        bang_audio.sound_ticks(bang_audio.SOUND_ROULETTE_COCK) - 1
    ):
        game.on_tick()
    assert game.decision is None
    game.on_tick()

    assert not game.is_sequence_gameplay_locked()
    assert game.decision and game.decision.kind == "missed"
    assert sound_names(game).count(bang_audio.SOUND_ROULETTE_COCK) == 1

    clear_user_messages(game)
    game._use_decision_card(target, missed)

    assert bang_audio.SOUND_WEAPON_EMPTY in sound_names(game)
    assert set(sound_names(game)) & set(
        bang_audio.SOUND_CARD_DISCARD
    )


def test_russian_roulette_moves_clockwise_and_stops_at_first_failure():
    game = start_game(4, seed=105)
    anchor = game._event_anchor()
    assert anchor is not None
    order = [anchor, *game._clockwise_after(anchor, exclude_actor=True)]
    defender, casualty, spared = order[:3]
    missed = make_card(2696, cards.MISSED)
    defender.hand = [missed]
    for player in order:
        player.in_play.clear()
    casualty.character = "willy_the_kid"
    casualty.hand.clear()
    spared.hand.clear()
    starting_life = {player.id: player.life for player in order}
    game.effect_stack.clear()
    game.decision = None
    game._push_effect(
        BangEffect(
            kind="russian_roulette",
            player_ids=[player.id for player in order],
        )
    )

    game._continue_effects()

    assert game.decision is not None
    assert game.decision.kind == "missed"
    assert game.decision.player_id == defender.id
    game._use_decision_card(defender, missed)
    tick_until(
        game,
        lambda: not game.effect_stack and game.decision is None,
    )

    assert defender.life == starting_life[defender.id]
    assert casualty.life == starting_life[casualty.id] - 2
    assert spared.life == starting_life[spared.id]


def test_dynamite_explosion_and_aftermath_sync_with_damage_tts():
    game = start_game(4, seed=98)
    player = game.current_player
    player.character = "bart_cassidy"
    player.life = player.max_life = 5
    dynamite = make_card(
        2692,
        cards.DYNAMITE,
        border=cards.BLUE,
    )
    player.in_play = [BangInPlayCard(dynamite)]
    game.deck = [
        make_card(
            2693,
            cards.BANG,
            suit=cards.SPADES,
            rank="5",
        )
    ]
    game.phase = PHASE_START_TURN
    game.effect_stack = [
        BangEffect(
            kind="turn_start",
            actor_id=player.id,
            stage="dynamite",
        )
    ]
    game.decision = None
    clear_user_messages(game)

    game._continue_effects()

    assert game.has_active_sequence(tag="bang_dynamite")
    assert player.life == 5
    assert bang_audio.SOUND_DYNAMITE_FUSE not in sound_names(game)
    assert bang_audio.SOUND_DYNAMITE_EXPLOSION not in sound_names(game)
    game.on_tick()
    assert bang_audio.SOUND_DYNAMITE_EXPLOSION in sound_names(game)
    assert bang_audio.SOUND_DYNAMITE_FUSE not in sound_names(game)
    assert game.has_active_sequence(tag="bang_dynamite")
    assert player.life == 5

    wait_ticks = SequenceBeat.audio_delay_ticks(
        bang_audio.sound_ticks(bang_audio.SOUND_DYNAMITE_EXPLOSION),
        wait_ratio=bang_audio.WAIT_RATIO_LONG_EFFECT,
    )
    for _ in range(wait_ticks - 1):
        game.on_tick()
    assert player.life == 5
    assert bang_audio.SOUND_DYNAMITE_AFTERMATH not in sound_names(game)

    game.on_tick()

    assert bang_audio.SOUND_DYNAMITE_AFTERMATH in sound_names(game)
    assert player.life == 2
    assert dynamite in game.discard_pile
    assert any(
        "You lose 3 life" in text
        for text in speech_texts(game, game.players.index(player))
    )


def test_safe_dynamite_transfer_is_the_only_fuse_path():
    game = start_game(4, seed=198)
    player = game.current_player
    recipient = game._clockwise_after(player, exclude_actor=True)[0]
    dynamite = make_card(2694, cards.DYNAMITE, border=cards.BLUE)
    player.in_play = [BangInPlayCard(dynamite)]
    game.deck = [
        make_card(2695, cards.BANG, suit=cards.HEARTS, rank="5")
    ]
    game.phase = PHASE_START_TURN
    game.effect_stack = [
        BangEffect(
            kind="turn_start",
            actor_id=player.id,
            stage="dynamite",
        )
    ]
    game.decision = None
    clear_user_messages(game)

    game._continue_effects()

    assert game.has_active_sequence(tag="bang_dynamite")
    assert bang_audio.SOUND_DYNAMITE_FUSE not in sound_names(game)
    game.on_tick()

    assert bang_audio.SOUND_DYNAMITE_FUSE in sound_names(game)
    assert bang_audio.SOUND_DYNAMITE_EXPLOSION not in sound_names(game)
    assert bang_audio.SOUND_DYNAMITE_AFTERMATH not in sound_names(game)
    assert all(in_play.card is not dynamite for in_play in player.in_play)
    assert any(in_play.card is dynamite for in_play in recipient.in_play)


def test_lethal_dynamite_fall_starts_at_thirty_percent_of_aftermath():
    game = start_game(4, seed=201)
    player = game.current_player
    dynamite = make_card(
        2696,
        cards.DYNAMITE,
        border=cards.BLUE,
    )
    player.life = 3
    player.hand.clear()
    player.in_play = [BangInPlayCard(dynamite)]
    game.deck = [
        make_card(
            2697,
            cards.BANG,
            suit=cards.SPADES,
            rank="5",
        )
    ]
    game.phase = PHASE_START_TURN
    game.effect_stack = [
        BangEffect(
            kind="turn_start",
            actor_id=player.id,
            stage="dynamite",
        )
    ]
    game.decision = None
    clear_user_messages(game)

    game._continue_effects()
    tick_until(
        game,
        lambda: (
            bang_audio.SOUND_DYNAMITE_AFTERMATH
            in sound_names(game)
        ),
    )

    assert player.life == 0
    assert not player.eliminated
    aftermath_started_tick = game.sound_scheduler_tick
    deadline = aftermath_started_tick + SequenceBeat.audio_delay_ticks(
        bang_audio.sound_ticks(bang_audio.SOUND_DYNAMITE_AFTERMATH),
        wait_ratio=bang_audio.LETHAL_FALL_TRIGGER_RATIO,
    )
    while game.sound_scheduler_tick < deadline - 1:
        game.on_tick()
    assert not player.eliminated
    assert not set(sound_names(game)) & set(
        bang_audio.SOUND_ELIMINATION_FALLS
    )

    game.on_tick()
    assert player.eliminated
    assert set(sound_names(game)) & set(
        bang_audio.SOUND_ELIMINATION_FALLS
    )
    assert not game.has_active_sequence(tag="bang_elimination_fall")
    assert not game.is_sequence_bot_paused()


def test_sniper_audio_sequence_survives_json_round_trip():
    game = start_game(4, seed=99)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    target.hand = [make_card(2694, cards.MISSED)]
    target.in_play.clear()
    game._start_shot(
        actor,
        target,
        source_kind="sniper",
        required=2,
    )

    restored = BangGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    assert restored.is_sequence_gameplay_locked()
    assert restored.active_sequences[0].current_index == 1

    tick_until(restored, lambda: restored.decision is not None)

    assert restored.decision and restored.decision.kind == "missed"
    assert restored.effect_stack[-1].source.kind == "sniper"


def test_pending_effect_and_decision_survive_json_round_trip():
    game = start_game(4, seed=15)
    actor = game.current_player
    target = game._clockwise_after(actor, exclude_actor=True)[0]
    response = make_card(2701, cards.MISSED)
    target.hand = [response]
    target.in_play = []
    game._start_shot(actor, target, source_kind="bang_card", required=1)
    assert game.decision and game.effect_stack
    restored = BangGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    assert restored.decision is not None
    assert restored.decision.kind == "missed"
    assert restored.decision.player_id == target.id
    assert restored.effect_stack[-1].kind == "shot"
    assert restored.effect_stack[-1].source.player_id == actor.id
    assert len(all_card_ids(restored)) == len(set(all_card_ids(restored)))


def test_restore_cancels_stale_private_intent_without_consuming_cards():
    game = start_game(4, seed=16)
    actor = game.current_player
    original_ids = [card.id for card in actor.hand]
    game.play_intent = BangPlayIntent(
        kind="card",
        actor_id=actor.id,
        card_id=999999,
        stage="target",
    )
    restored = BangGame.from_json(game.to_json())
    restored.rebuild_runtime_state()
    restored_actor = restored.get_player_by_id(actor.id)
    assert restored.play_intent is None
    assert [card.id for card in restored_actor.hand] == original_ids


@pytest.mark.parametrize(
    ("player_count", "event_mode", "seed", "max_ticks"),
    [
        (3, NO_EVENTS, 31, 12000),
        (4, COMBINED_EVENTS, 32, 25000),
        (6, COMBINED_EVENTS, 33, 35000),
        (8, COMBINED_EVENTS, 34, 50000),
    ],
)
def test_bots_finish_legal_games(player_count, event_mode, seed, max_ticks):
    game = start_game(
        player_count,
        seed=seed,
        bots=True,
        event_mode=event_mode,
    )
    for _ in range(max_ticks):
        if not game.game_active:
            break
        for player in game.players:
            player.bot_think_ticks = 0
        game.on_tick()
    assert not game.game_active
    assert game.phase == PHASE_GAME_OVER
    assert game.winner_ids
    assert game.decision is None
    assert game.play_intent is None
    assert game.effect_stack == []
    card_ids = all_card_ids(game)
    assert len(card_ids) == 120
    assert len(set(card_ids)) == 120
    assert all(player.life <= player.max_life for player in game.players)


def test_locale_keys_variables_and_select_arms_match():
    en = ftl_entries(ROOT / "server" / "locales" / "en" / "bang.ftl")
    vi = ftl_entries(ROOT / "server" / "locales" / "vi" / "bang.ftl")
    assert en.keys() == vi.keys()
    for key in en:
        assert set(re.findall(r"\{\s*\$([a-zA-Z0-9_-]+)", en[key])) == set(
            re.findall(r"\{\s*\$([a-zA-Z0-9_-]+)", vi[key])
        )
        assert set(re.findall(r"^\s*\*?\[([^\]]+)\]", en[key], re.MULTILINE)) == set(
            re.findall(r"^\s*\*?\[([^\]]+)\]", vi[key], re.MULTILINE)
        )


def test_every_explicit_bang_locale_key_used_by_code_exists():
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "server" / "games" / "bang").glob("*.py")
    )
    used = set(re.findall(r'"(bang-[a-z0-9-]+)"', source))
    en = ftl_entries(ROOT / "server" / "locales" / "en" / "bang.ftl")
    assert used <= en.keys()


def test_every_dynamic_source_and_draw_requirement_is_localized():
    source_kinds = {
        "bang_card",
        "missed_as_bang",
        "doc_holyday",
        "sniper",
        cards.PUNCH,
        cards.SPRINGFIELD,
        cards.BUFFALO_RIFLE,
        cards.KNIFE,
        cards.PEPPERBOX,
        cards.DERRINGER,
        cards.GATLING,
        cards.HOWITZER,
        "ricochet",
        "russian_roulette",
        "fistful_of_cards",
        "duel",
        "indians",
        "dynamite",
        "high_noon",
    }
    purposes = {"barrel", "dynamite", "jail", "vendetta"}
    for locale in ("en", "vi"):
        for kind in source_kinds:
            key = f"bang-source-{kind.replace('_', '-')}"
            assert Localization.get(locale, key) != key
        for purpose in purposes:
            key = f"bang-draw-requirement-{purpose}"
            assert Localization.get(locale, key) != key


def test_manuals_are_synchronized_and_cover_accessible_play():
    en = (
        ROOT / "server" / "documentation" / "content" / "en" / "games" / "bang.md"
    ).read_text(encoding="utf-8")
    vi = (
        ROOT / "server" / "documentation" / "content" / "vi" / "games" / "bang.md"
    ).read_text(encoding="utf-8")
    assert en.count(r"\*\*") == vi.count(r"\*\*")
    assert en.count("Emiliano Sciarra") == 1
    assert vi.count("Emiliano Sciarra") == 1
    assert "Dodge City" not in en
    assert "Dodge City" not in vi
    for required in ("PlayAural", "Calamity Janet", "Jourdonnais", "Ctrl+U"):
        assert required in en
        assert required in vi
    for required in (
        "The story",
        "Your objective",
        "A turn, step by step",
        "How combat sounds resolve",
        "Expanded cards and characters",
        "Turn-changing events",
        "Choosing a target commits the play immediately",
        "the first turn starts ten seconds",
        "fall begins about one-third",
        "Hear who is currently at the table",
    ):
        assert required in en
    for required in (
        "Chuyện ở miền biên ải",
        "Mục tiêu của bạn",
        "Một lượt, từng bước một",
        "Diễn biến âm thanh khi giao chiến",
        "Bài và nhân vật mở rộng",
        "Biến cố đổi luật",
        "Chọn mục tiêu là chốt nước đi ngay",
        "lượt đầu bắt đầu sau đó 10 giây",
        "tiếng ngã bắt đầu",
        "Nghe danh sách người hiện có ở bàn",
    ):
        assert required in vi
    assert en.index(r"\*\*The story\*\*") < en.index(
        r"\*\*Your objective\*\*"
    ) < en.index(r"\*\*A turn, step by step\*\*")
    assert vi.index(r"\*\*Chuyện ở miền biên ải\*\*") < vi.index(
        r"\*\*Mục tiêu của bạn\*\*"
    ) < vi.index(r"\*\*Một lượt, từng bước một\*\*")
    assert "Toggle table voice chat" not in en
    assert "Bật hoặc tắt đàm thoại bàn" not in vi
    assert "Bồi" not in vi
    assert "Đầm" not in vi
    assert "Già" not in vi
    assert "2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K và Át" in vi
    manuals = {"en": en, "vi": vi}
    card_kinds = {
        card.kind for card in cards.build_deck(include_extended_cards=True)
    }
    for locale, manual in manuals.items():
        for kind in card_kinds:
            assert cards.card_name(kind, locale) in manual
        for character in ALL_CHARACTERS:
            assert character_name(character.id, locale) in manual
        for event in ALL_EVENTS:
            assert event_name(event.id, locale) in manual
