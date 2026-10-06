"""Tests for Cards Against Humanity data, gameplay, and audio routing."""

import re
from pathlib import Path

from ..games.humanitycards.game import (
    DEFAULT_ENGLISH_PACK,
    NEXT_ROUND_DELAY_TICKS,
    NEXT_ROUND_SEQUENCE_ID,
    HumanityCardsGame,
    HumanityCardsOptions,
    load_humanity_packs,
)
from ..messages.localization import Localization
from ..users.test_user import MockUser

_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


def _add_three_players(game: HumanityCardsGame):
    p1 = game.add_player("Alice", MockUser("Alice", uuid="hc-sound-1"))
    p2 = game.add_player("Bob", MockUser("Bob", uuid="hc-sound-2"))
    judge = game.add_player("Carol", MockUser("Carol", uuid="hc-sound-3"))
    game.host = "Alice"
    return p1, p2, judge


def _white_card(text: str = "a good answer") -> dict:
    return {"text": text, "pack": "test"}


def test_humanitycards_vendored_datasets_are_clean_and_complete() -> None:
    expected_counts = {
        "en": (427, 65_563, 18_743),
        "es": (1, 399, 60),
        "pt-BR": (1, 469, 92),
    }

    for language, (pack_count, white_count, black_count) in expected_counts.items():
        packs = load_humanity_packs(language)
        assert len(packs) == pack_count
        assert sum(len(pack["white"]) for pack in packs) == white_count
        assert sum(len(pack["black"]) for pack in packs) == black_count
        names = [pack["name"] for pack in packs]
        texts = [
            card["text"]
            for pack in packs
            for color in ("white", "black")
            for card in pack[color]
        ]
        all_text = names + texts
        assert all(text.strip() for text in all_text)
        assert not any(
            re.search(r"&(?:[A-Za-z]+|#\d+|#x[0-9A-Fa-f]+);", text) for text in all_text
        )
        assert not any(re.search(r"<[^>]+>", text) for text in all_text)
        assert not any(
            re.search(r"[\u00AD\uFFFD\x00-\x09\x0B-\x1F]", text) for text in all_text
        )


def test_humanitycards_converts_source_presentation_tags_to_readable_text() -> None:
    texts = {
        card["text"] for pack in load_humanity_packs("en") for card in pack["white"]
    }

    assert "Humperdink!\nHumperdink!\nHumperdink!" in texts
    assert "Being weirdly proud of your blisters, battle wounds." in texts
    assert "That guy from True Blood." in texts

    prompts = {
        card["text"] for pack in load_humanity_packs("en") for card in pack["black"]
    }
    assert "Where do house-elves draw the line? _" in prompts


def test_humanitycards_uses_declared_pick_count_without_guessing_from_blanks() -> None:
    spanish_prompts = load_humanity_packs("es")[0]["black"]
    special_prompt = next(
        card
        for card in spanish_prompts
        if card["pick"] == 3 and "_" not in card["text"]
    )

    assert special_prompt["pick"] == 3


def test_humanitycards_preserves_draw_and_printed_pick_mechanics() -> None:
    english_prompts = [
        card for pack in load_humanity_packs("en") for card in pack["black"]
    ]
    printed_directive = next(
        card
        for card in english_prompts
        if card["text"] == "Fuck, marry, kill. PICK 3 DRAW 2."
    )
    portuguese_prompt = next(
        card
        for card in load_humanity_packs("pt-BR")[0]["black"]
        if card["text"] == "_ + _ = _"
    )

    assert (printed_directive["pick"], printed_directive["draw"]) == (3, 2)
    assert (portuguese_prompt["pick"], portuguese_prompt["draw"]) == (3, 2)


def test_humanitycards_card_language_selects_the_matching_deck() -> None:
    game = HumanityCardsGame(
        options=HumanityCardsOptions(
            card_language="es", card_packs=[DEFAULT_ENGLISH_PACK]
        )
    )

    assert not game.options.is_option_visible("card_packs")
    assert game._get_active_packs() == [load_humanity_packs("es")[0]["name"]]
    assert game._selected_pack_stats() == {
        "selected": 1,
        "white": 399,
        "black": 60,
        "max_pick": 3,
        "max_draw": 0,
    }

    game._build_decks()
    assert {card["pack"] for card in game.white_deck} == set(game._get_active_packs())
    assert {card["pack"] for card in game.black_deck} == set(game._get_active_packs())


def test_humanitycards_current_main_deck_is_complete_default() -> None:
    game = HumanityCardsGame()

    assert game.options.card_packs == [DEFAULT_ENGLISH_PACK]
    assert game._selected_pack_stats() == {
        "selected": 1,
        "white": 500,
        "black": 100,
        "max_pick": 3,
        "max_draw": 0,
    }


def test_humanitycards_draw_prompt_deals_only_to_answering_players(monkeypatch) -> None:
    monkeypatch.setattr("server.games.humanitycards.game.random.randrange", lambda _: 2)
    game = HumanityCardsGame(options=HumanityCardsOptions(hand_size=5))
    game.setup_keybinds()
    player, other, judge = _add_three_players(game)
    game.status = "playing"
    game.game_active = True
    game.white_deck = [_white_card(f"card {index}") for index in range(30)]
    game.black_deck = [{"text": "_ + _ = _", "pick": 3, "draw": 2, "pack": "test"}]

    game._start_round()

    assert game.judge_indices == [2]
    assert len(player.hand) == 7
    assert len(other.hand) == 7
    assert len(judge.hand) == 5
    assert "Draw 2 extra cards first." in game.get_user(player).get_spoken_messages()
    turn_set = game.get_action_set(player, "turn")
    assert turn_set is not None
    assert turn_set.get_action("toggle_card_16") is not None


def test_humanitycards_speaks_prompt_mechanics_in_card_language() -> None:
    expected = {
        "en": "blank, then same card again",
        "es": "espacio en blanco, then la misma carta otra vez",
        "pt-BR": "espaço em branco, then a mesma carta novamente",
    }

    for language, spoken in expected.items():
        game = HumanityCardsGame(options=HumanityCardsOptions(card_language=language))
        assert game._speech_friendly_black("_, then _(repeat)_") == spoken


def test_humanitycards_overlapping_packs_do_not_duplicate_cards() -> None:
    game = HumanityCardsGame(
        options=HumanityCardsOptions(
            card_packs=["CAH Main Deck: US v2.4", "CAH Main Deck: US v3.0"]
        )
    )

    stats = game._selected_pack_stats()
    assert stats["selected"] == 2
    assert stats["white"] < 1_000
    assert stats["black"] < 200


def test_humanitycards_migrates_previous_english_pack_names() -> None:
    game = HumanityCardsGame(
        options=HumanityCardsOptions(
            card_packs=["CAH Base Set", "2012 Holiday Pack", "Fantasy Pack"]
        )
    )

    assert game.options.card_packs == [
        "Cards Against Humanity: Main Deck (All Versions)",
        "Cards Against Humanity: 2012 Holiday Pack",
        "Cards Against Humanity: Fantasy Pack",
    ]


def test_humanitycards_old_options_default_to_english_card_content() -> None:
    options = HumanityCardsOptions.from_dict(
        {
            "winning_score": 7,
            "hand_size": 10,
            "card_packs": ["CAH Base Set"],
            "czar_selection": "Rotating",
            "num_judges": 1,
        }
    )
    game = HumanityCardsGame(options=options)

    assert game.options.card_language == "en"
    assert game.options.card_packs == [
        "Cards Against Humanity: Main Deck (All Versions)"
    ]


def test_humanitycards_unavailable_legacy_pack_falls_back_to_current_deck() -> None:
    game = HumanityCardsGame(options=HumanityCardsOptions(card_packs=["Evil Apples"]))

    assert game.options.card_packs == [DEFAULT_ENGLISH_PACK]


def test_humanitycards_preserves_card_punctuation_when_building_decks() -> None:
    game = HumanityCardsGame()
    game._build_decks()
    source_texts = {
        card["text"]
        for pack in load_humanity_packs("en")
        if pack["name"] == DEFAULT_ENGLISH_PACK
        for card in pack["white"]
    }

    assert {card["text"] for card in game.white_deck} == source_texts
    assert game._fill_in_blanks("Why _?", ["Because."]) == "Why Because?"
    assert game._fill_in_blanks("Why _?", ["Just waiting..."]) == (
        "Why Just waiting...?"
    )
    assert game._fill_in_blanks("Make a haiku.", ["One.", "Two.", "Three."]) == (
        "Make a haiku. One. Two. Three."
    )


def test_humanitycards_fills_repeated_answer_slots_without_mutating_answer_text() -> (
    None
):
    game = HumanityCardsGame()

    assert (
        game._fill_in_blanks(
            "A curse upon thee: _ shall turn into _.",
            ["my _private_ answer."],
        )
        == "A curse upon thee: my _private_ answer shall turn into my _private_ answer."
    )
    assert (
        game._fill_in_blanks(
            "You want _? You can't handle _(SAME CARD AGAIN)_!",
            ["the truth."],
        )
        == "You want the truth? You can't handle the truth!"
    )
    assert (
        game._fill_in_blanks(
            "Whatever happens in _, stays in _(repeat)_. Except _.",
            ["Vegas.", "herpes."],
        )
        == "Whatever happens in Vegas, stays in Vegas. Except herpes."
    )


def test_humanitycards_selection_sounds_use_humanitycards_pack() -> None:
    game = HumanityCardsGame()
    game.setup_keybinds()
    player, _, _ = _add_three_players(game)
    user = game.get_user(player)
    assert user is not None

    game.status = "playing"
    game.phase = "submitting"
    game.judge_indices = [2]
    game.current_black_card = {"text": "_", "pick": 1, "pack": "test"}
    player.hand = [_white_card()]

    game.execute_action(player, "toggle_card_0")
    game.execute_action(player, "toggle_card_0")

    assert user.get_sounds_played()[-2:] == [
        "game_humanitycards/cardselect.ogg",
        "game_humanitycards/cardunselect.ogg",
    ]


def test_humanitycards_multi_card_selection_exposes_order_and_never_replaces_silently() -> (
    None
):
    game = HumanityCardsGame()
    game.setup_keybinds()
    player, _, _ = _add_three_players(game)
    user = game.get_user(player)
    assert user is not None

    game.status = "playing"
    game.phase = "submitting"
    game.judge_indices = [2]
    game.current_black_card = {"text": "_ then _", "pick": 2, "pack": "test"}
    player.hand = [_white_card("first"), _white_card("second"), _white_card("third")]

    game.execute_action(player, "toggle_card_1")
    game.execute_action(player, "toggle_card_0")
    assert game._get_toggle_card_label(player, "toggle_card_1") == (
        "second, selected as answer 1"
    )
    assert game._get_toggle_card_label(player, "toggle_card_0") == (
        "first, selected as answer 2"
    )

    game.execute_action(player, "toggle_card_2")

    assert player.selected_indices == [1, 0]
    assert user.get_last_spoken() == (
        "You already selected 2 cards. Deselect one before choosing another."
    )


def test_humanitycards_review_hand_remains_available_after_submission() -> None:
    game = HumanityCardsGame()
    game.setup_keybinds()
    player, _, _ = _add_three_players(game)
    user = game.get_user(player)
    assert user is not None

    game.status = "playing"
    game.phase = "judging"
    game.judge_indices = [2]
    player.hand = [_white_card("one"), _white_card("two")]
    player.submitted_cards = ["already played"]

    game.execute_action(player, "review_hand")

    items = user.get_current_menu_items("status_box")
    assert items is not None
    assert [item.text for item in items] == [
        "1. one",
        "2. two",
    ]


def test_humanitycards_judge_prompt_is_read_only_menu_information() -> None:
    game = HumanityCardsGame()
    game.setup_keybinds()
    _, _, judge = _add_three_players(game)
    judge_user = game.get_user(judge)
    assert judge_user is not None

    game.status = "playing"
    game.phase = "judging"
    game.judge_indices = [2]
    game.current_black_card = {"text": "Why _?", "pick": 1, "pack": "test"}
    game.submissions = [{"player_id": "hc-sound-1", "cards": ["because"]}]
    game.submission_order = [0]

    items = game.build_menu_items(judge, judge_user).items
    header = next(item for item in items if item.id == "judge_prompt_header")

    assert header.read_only is True
    assert header.text == "Choose the best card that matches: Why blank?"
    turn_set = game.get_action_set(judge, "turn")
    assert turn_set is not None
    assert turn_set.get_action("judge_prompt_header") is None


def test_humanitycards_rotating_mode_randomizes_the_first_judge(monkeypatch) -> None:
    monkeypatch.setattr("server.games.humanitycards.game.random.randrange", lambda _: 1)
    game = HumanityCardsGame()
    _add_three_players(game)

    game._select_judges()

    assert game.judge_indices == [1]


def test_humanitycards_submit_and_judging_sounds_use_humanitycards_pack() -> None:
    game = HumanityCardsGame()
    game.setup_keybinds()
    player, other_submitter, _ = _add_three_players(game)
    user = game.get_user(player)
    assert user is not None

    game.status = "playing"
    game.phase = "submitting"
    game.judge_indices = [2]
    game.current_black_card = {"text": "_", "pick": 1, "pack": "test"}
    player.hand = [_white_card()]
    player.selected_indices = [0]
    other_submitter.submitted_cards = ["already in"]

    game.execute_action(player, "submit_cards")

    sounds = user.get_sounds_played()
    assert "game_humanitycards/submit" in sounds
    assert "game_humanitycards/judging.ogg" in sounds


def test_humanitycards_judging_turn_sound_respects_preference(monkeypatch) -> None:
    monkeypatch.setattr(
        "server.games.humanitycards.game.random.shuffle", lambda items: None
    )
    game = HumanityCardsGame()
    game.setup_keybinds()
    player, other_submitter, judge = _add_three_players(game)
    judge_user = game.get_user(judge)
    assert judge_user is not None

    game.status = "playing"
    game.phase = "submitting"
    game.judge_indices = [2]
    game.current_black_card = {"text": "_", "pick": 1, "pack": "test"}
    player.submitted_cards = ["first answer"]
    other_submitter.submitted_cards = ["second answer"]

    judge_user.preferences.play_turn_sound = True
    game._start_judging()

    assert judge_user.get_sounds_played() == [
        "game_humanitycards/judging.ogg",
        "turn.ogg",
    ]

    judge_user.clear_messages()
    game.phase = "submitting"
    game.submissions = []
    judge_user.preferences.play_turn_sound = False

    game._start_judging()

    assert judge_user.get_sounds_played() == ["game_humanitycards/judging.ogg"]


def test_humanitycards_judging_announces_and_reviews_anonymous_answers(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "server.games.humanitycards.game.random.shuffle", lambda items: None
    )
    game = HumanityCardsGame()
    game.setup_keybinds()
    player, other, judge = _add_three_players(game)
    player_user = game.get_user(player)
    judge_user = game.get_user(judge)
    assert player_user is not None
    assert judge_user is not None

    game.status = "playing"
    game.phase = "submitting"
    game.judge_indices = [2]
    game.current_black_card = {"text": "Why _?", "pick": 1, "pack": "test"}
    player.submitted_cards = ["the first answer"]
    other.submitted_cards = ["the second answer"]

    game._start_judging()

    expected = [
        "Answer 1: Why the first answer?",
        "Answer 2: Why the second answer?",
    ]
    announced = [
        line for line in player_user.get_spoken_messages() if line.startswith("Answer ")
    ]
    assert announced == expected
    assert all("Alice" not in line and "Bob" not in line for line in announced)

    game.execute_action(player, "review_answers")
    items = player_user.get_current_menu_items("status_box")
    assert items is not None
    assert [item.text for item in items] == expected


def test_humanitycards_judge_pick_and_win_sounds_use_humanitycards_pack() -> None:
    game = HumanityCardsGame(options=HumanityCardsOptions(winning_score=1))
    game.setup_keybinds()
    player, _, judge = _add_three_players(game)
    judge_user = game.get_user(judge)
    assert judge_user is not None

    game.status = "playing"
    game.phase = "judging"
    game.judge_indices = [2]
    game.current_black_card = {"text": "_", "pick": 1, "pack": "test"}
    game.submissions = [{"player_id": player.id, "cards": ["the winner"]}]
    game.submission_order = [0]

    game.execute_action(judge, "judge_pick_0")

    sounds = judge_user.get_sounds_played()
    assert "game_humanitycards/judgechoice" in sounds
    assert "game_humanitycards/win.ogg" in sounds


def test_humanitycards_round_transition_uses_serialized_sequence() -> None:
    game = HumanityCardsGame(options=HumanityCardsOptions(winning_score=2))
    game.setup_keybinds()
    player, _, judge = _add_three_players(game)

    game.status = "playing"
    game.game_active = True
    game.phase = "judging"
    game.judge_indices = [2]
    game.current_black_card = {"text": "_", "pick": 1, "pack": "test"}
    game.submissions = [{"player_id": player.id, "cards": ["winner"]}]
    game.submission_order = [0]
    game.white_deck = [_white_card(f"card {index}") for index in range(30)]
    game.black_deck = [{"text": "Next _", "pick": 1, "pack": "test"}]

    game.execute_action(judge, "judge_pick_0")

    assert game.phase == "round_end"
    assert game.round_end_ticks == 0
    assert game.has_active_sequence(sequence_id=NEXT_ROUND_SEQUENCE_ID)

    for _ in range(NEXT_ROUND_DELAY_TICKS):
        game.on_tick()

    assert game.phase == "submitting"
    assert not game.has_active_sequence(sequence_id=NEXT_ROUND_SEQUENCE_ID)


def test_humanitycards_migrates_legacy_round_countdown() -> None:
    game = HumanityCardsGame(
        status="playing",
        game_active=True,
        phase="round_end",
        round_end_ticks=25,
    )

    assert game.round_end_ticks == 0
    assert game.has_active_sequence(sequence_id=NEXT_ROUND_SEQUENCE_ID)


def test_humanitycards_prestart_blocks_too_many_judges() -> None:
    game = HumanityCardsGame(options=HumanityCardsOptions(num_judges=3))
    _add_three_players(game)

    assert (
        "hc-error-too-many-judges",
        {"judges": 3, "players": 3, "required": 4},
    ) in game.prestart_validate()


def test_humanitycards_prestart_reserves_cards_for_largest_extra_draw(
    monkeypatch,
) -> None:
    game = HumanityCardsGame(options=HumanityCardsOptions(hand_size=5))
    _add_three_players(game)
    monkeypatch.setattr(
        game,
        "_selected_pack_stats",
        lambda: {
            "selected": 1,
            "white": 18,
            "black": 1,
            "max_pick": 3,
            "max_draw": 2,
        },
    )

    errors = game.prestart_validate()

    assert (
        "hc-error-not-enough-white-cards",
        {
            "players": 3,
            "hand_size": 5,
            "needed": 19,
            "available": 18,
        },
    ) in errors


def test_humanitycards_judge_announcement_uses_personal_context() -> None:
    game = HumanityCardsGame(options=HumanityCardsOptions(num_judges=2))
    game.setup_keybinds()
    judge, _, _ = _add_three_players(game)
    judge_user = game.get_user(judge)
    assert judge_user is not None
    game.status = "playing"
    game.judge_indices = [0, 2]

    game._action_whose_judge(judge, "whose_judge")

    assert (
        judge_user.get_last_spoken() == "You and Carol are the Card Czars this round."
    )


def test_humanitycards_disabled_submit_speaks_parameterized_reason() -> None:
    game = HumanityCardsGame()
    game.setup_keybinds()
    player, _, _ = _add_three_players(game)
    user = game.get_user(player)
    assert user is not None

    game.status = "playing"
    game.phase = "submitting"
    game.judge_indices = [2]
    game.current_black_card = {"text": "_ and _", "pick": 2, "pack": "test"}
    player.hand = [_white_card(), _white_card()]
    player.selected_indices = [0]

    game.execute_action(player, "submit_cards")

    assert user.get_spoken_messages()[-1] == "You need to select exactly 2 cards."


def test_humanitycards_submit_and_reveal_use_personal_broadcasts() -> None:
    game = HumanityCardsGame(options=HumanityCardsOptions(winning_score=2))
    game.setup_keybinds()
    player, other, judge = _add_three_players(game)
    player_user = game.get_user(player)
    other_user = game.get_user(other)
    judge_user = game.get_user(judge)
    assert player_user is not None
    assert other_user is not None
    assert judge_user is not None

    game.status = "playing"
    game.phase = "submitting"
    game.judge_indices = [2]
    game.current_black_card = {"text": "_", "pick": 1, "pack": "test"}
    player.hand = [_white_card("winner")]
    other.hand = [_white_card("runner up")]
    player.selected_indices = [0]
    other.submitted_cards = ["runner up"]

    game.execute_action(player, "submit_cards")

    assert "You submitted your cards." in player_user.get_spoken_messages()
    assert "Alice submitted their cards." in other_user.get_spoken_messages()
    assert "Alice submitted their cards." in judge_user.get_spoken_messages()

    game.submission_order = [0, 1]
    game.execute_action(judge, "judge_pick_0")

    assert (
        "You win the round! Your score is now 1." in player_user.get_spoken_messages()
    )
    assert "Your winning answer: winner" in player_user.get_spoken_messages()
    assert "Alice wins the round! Score: 1." in judge_user.get_spoken_messages()
    assert "Alice's winning answer: winner" in judge_user.get_spoken_messages()
