"""Tests for the Lounge chat room."""

from pathlib import Path
from unittest.mock import patch

from ..core.server import Server
from ..games.lounge.game import (
    EMOTE_ORDER,
    MAX_TOPIC_LENGTH,
    TICKS_PER_SECOND,
    LoungeGame,
    LoungeOptions,
)
from ..games.registry import GameRegistry
from ..users.test_user import MockUser


def make_room(
    *,
    player_count: int = 3,
    spectators: int = 0,
    touch_first: bool = False,
    locale: str = "en",
    **option_overrides,
) -> tuple[LoungeGame, list[MockUser]]:
    game = LoungeGame(options=LoungeOptions(**option_overrides))
    game.setup_keybinds()
    users: list[MockUser] = []
    for index in range(player_count):
        user = MockUser(
            f"Player{index + 1}",
            locale=locale,
            uuid=f"lounge-p{index + 1}",
        )
        if touch_first and index == 0:
            user.client_type = "mobile"
        users.append(user)
        game.add_player(user.username, user)
    for index in range(spectators):
        user = MockUser(
            f"Watcher{index + 1}",
            locale=locale,
            uuid=f"lounge-s{index + 1}",
        )
        users.append(user)
        game.add_spectator(user.username, user)
    game.host = users[0].username
    for user in users:
        user.clear_messages()
    return game, users


def visible_action_ids(game: LoungeGame, index: int) -> list[str]:
    return [
        resolved.action.id
        for resolved in game.get_all_visible_actions(game.players[index])
    ]


def test_room_registered_with_chat_first_metadata() -> None:
    assert GameRegistry.get("lounge") is LoungeGame
    game = LoungeGame()

    assert game.get_name() == "Lounge"
    assert game.get_type() == "lounge"
    assert game.get_category() == "misc"
    assert game.get_min_players() == 1
    assert game.get_max_players() == 20
    assert game.get_supported_leaderboards() == []
    assert game.supports_score_actions() is False
    assert game.options.allow_emotes is True
    assert game.options.allow_nudges is True
    assert game.options.allow_party_tools is True
    assert game.options.action_cooldown == 3


def test_room_stays_open_and_never_starts() -> None:
    game, users = make_room(player_count=1)
    host = game.players[0]

    assert game.status == "waiting"
    assert game.prestart_validate() == ["lounge-cannot-start"]
    assert game._is_start_game_enabled(host) == "lounge-cannot-start"
    assert "start_game" not in visible_action_ids(game, 0)

    game.execute_action(host, "start_game")

    assert game.status == "waiting"
    assert users[0].get_last_spoken() == (
        "The Lounge is always open, so there is no game to start. Chat, emotes and "
        "room tools are available to everyone the moment they sit down."
    )

    # Even a direct start must not flip the table into a gameplay status, which
    # would turn every later arrival into a spectator.
    game.on_start()
    assert game.status == "waiting"


def test_bots_and_saving_are_refused_with_reasons() -> None:
    game, users = make_room(player_count=1)
    host = game.players[0]

    game.execute_action(host, "add_bot")
    assert users[0].get_last_spoken() == (
        "The Lounge is a room for people, so bots cannot be added here. Invite "
        "someone from the players list instead."
    )
    assert len(game.players) == 1

    users[0].clear_messages()
    game.execute_action(host, "save_table")
    assert users[0].get_last_spoken() == (
        "A Lounge is a live room, so there is nothing to save. The room closes on "
        "its own when the last person leaves."
    )


def test_arrival_is_greeted_and_hears_the_current_topic() -> None:
    game, users = make_room(player_count=1)
    game.execute_action(game.players[0], "change_topic", "Audio games night")

    latecomer = MockUser("Player2", uuid="lounge-p2")
    game.add_player(latecomer.username, latecomer)

    assert latecomer.get_spoken_messages() == [
        "Welcome to the Lounge. This table is only for talking: use table chat, "
        "play emotes, and open the room tools from your menu.",
        "Room topic, set by Player1: Audio games night",
    ]

    watcher = MockUser("Watcher1", uuid="lounge-s1")
    game.add_spectator(watcher.username, watcher)
    assert watcher.get_spoken_messages()[0] == (
        "Welcome to the Lounge. You are watching, so you can read the room and "
        "follow the chat, but emotes and room tools stay with the people seated."
    )


def test_emote_splits_actor_and_observer_forms_and_plays_its_sound() -> None:
    game, users = make_room(player_count=3)

    game.execute_action(game.players[0], "emote_applaud")

    assert users[0].get_last_spoken() == "You applaud."
    assert users[1].get_last_spoken() == "Player1 applauds."
    assert users[2].get_last_spoken() == "Player1 applauds."
    assert users[1].get_sounds_played() == ["game_uno/winround.ogg"]
    assert game.emote_count == 1


def test_every_emote_has_a_sound_and_both_announcement_forms() -> None:
    game, users = make_room(player_count=2, action_cooldown=0)

    for emote_id in EMOTE_ORDER:
        for user in users:
            user.clear_messages()
        game.execute_action(game.players[0], f"emote_{emote_id}")

        actor_line = users[0].get_last_spoken()
        observer_line = users[1].get_last_spoken()
        assert actor_line and not actor_line.startswith("lounge-")
        assert observer_line and not observer_line.startswith("lounge-")
        assert actor_line != observer_line
        assert observer_line.startswith("Player1")
        assert len(users[1].get_sounds_played()) == 1

    assert game.emote_count == len(EMOTE_ORDER)


def test_cooldown_blocks_the_next_room_action_until_it_expires() -> None:
    game, users = make_room(player_count=2, action_cooldown=2)

    game.execute_action(game.players[0], "emote_wave")
    users[0].clear_messages()

    game.execute_action(game.players[0], "emote_laugh")
    assert users[0].get_last_spoken() == (
        "Wait 2 more seconds before your next emote, nudge, dice roll or coin flip."
    )
    assert game.emote_count == 1

    # The rows stay in the menu while disabled so client focus keeps its anchor.
    assert "emote_laugh" in visible_action_ids(game, 0)

    for _ in range(2 * TICKS_PER_SECOND):
        game.on_tick()

    users[0].clear_messages()
    game.execute_action(game.players[0], "emote_laugh")
    assert users[0].get_last_spoken() == "You burst out laughing."
    assert game.emote_count == 2


def test_zero_cooldown_allows_back_to_back_room_actions() -> None:
    game, users = make_room(player_count=2, action_cooldown=0)

    game.execute_action(game.players[0], "emote_wave")
    game.execute_action(game.players[0], "emote_boo")

    assert game.emote_count == 2
    assert users[0].get_last_spoken() == "You boo."


def test_disabled_options_explain_which_tool_is_off() -> None:
    game, users = make_room(
        player_count=2,
        allow_emotes=False,
        allow_nudges=False,
        allow_party_tools=False,
    )

    game.execute_action(game.players[0], "emote_wave")
    assert users[0].get_last_spoken() == (
        "Emotes are turned off in this room. The host can turn them back on in the "
        "room settings."
    )

    game.execute_action(game.players[0], "nudge", game.players[1].id)
    assert users[0].get_last_spoken() == (
        "Nudges are turned off in this room. The host can turn them back on in the "
        "room settings."
    )

    game.execute_action(game.players[0], "roll_dice")
    assert users[0].get_last_spoken() == (
        "Dice and coin flips are turned off in this room. The host can turn them "
        "back on in the room settings."
    )
    assert game.emote_count == 0


def test_nudge_is_targeted_and_reported_from_three_perspectives() -> None:
    game, users = make_room(player_count=3)

    game.execute_action(game.players[0], "nudge", game.players[1].id)

    assert users[0].get_last_spoken() == "You nudge Player2."
    assert users[1].get_last_spoken() == "Player1 nudges you."
    assert users[2].get_last_spoken() == "Player1 nudges Player2."
    assert users[1].get_sounds_played() == ["mention.ogg"]
    assert users[0].get_sounds_played() == []
    assert users[2].get_sounds_played() == []


def test_nudge_rejects_self_and_departed_targets() -> None:
    game, users = make_room(player_count=2)

    game.execute_action(game.players[0], "nudge", game.players[0].id)
    assert users[0].get_last_spoken() == (
        "You cannot nudge yourself. Pick another person in the room."
    )

    users[0].clear_messages()
    game.execute_action(game.players[0], "nudge", "lounge-ghost")
    assert users[0].get_last_spoken() == (
        "lounge-ghost is no longer in the room, so the nudge was not sent."
    )


def test_nudge_needs_someone_else_in_the_room() -> None:
    game, users = make_room(player_count=1)
    host = game.players[0]

    assert game._nudge_options(host) == []
    assert game._nudge_pre_input_check(host, "nudge") == "lounge-nudge-no-targets"

    game.handle_event(host, {"type": "action", "action": "nudge"})
    assert users[0].get_last_spoken() == (
        "There is nobody else in the room to nudge yet. Wait for someone to sit down."
    )

    watcher = MockUser("Watcher1", uuid="lounge-s1")
    game.add_spectator(watcher.username, watcher)
    assert game._nudge_options(host) == [watcher.uuid]
    assert game._nudge_option_label(host, watcher.uuid) == "Watcher1"


def test_dice_and_coin_report_their_results_to_the_room() -> None:
    game, users = make_room(player_count=2, action_cooldown=0)

    with patch("server.games.lounge.game.random.randint", side_effect=[4, 5]):
        game.execute_action(game.players[0], "roll_dice")

    assert users[0].get_last_spoken() == "You roll 4 and 5, for a total of 9."
    assert users[1].get_last_spoken() == "Player1 rolls 4 and 5, for a total of 9."
    assert users[1].get_sounds_played() == ["game_dice/dieThrow1.ogg"]

    with patch("server.games.lounge.game.random.choice", return_value=True):
        game.execute_action(game.players[0], "flip_coin")

    assert users[0].get_last_spoken() == "You flip a coin and it lands on heads."
    assert users[1].get_last_spoken() == "Player1 flips a coin and it lands on heads."


def test_away_toggle_announces_and_relabels_only_the_actor_row() -> None:
    game, users = make_room(player_count=2)
    host = game.players[0]

    game.execute_action(host, "toggle_away")

    assert host.away is True
    assert users[0].get_last_spoken() == (
        "You are now marked as away. You keep your seat, and everyone can see you "
        "stepped out."
    )
    assert users[1].get_last_spoken() == "Player1 is now away."
    assert game._get_room_action_label(host, "toggle_away") == (
        "Come back from away"
    )
    assert game._get_room_action_label(game.players[1], "toggle_away") == (
        "Mark yourself away"
    )

    game.execute_action(host, "toggle_away")
    assert host.away is False
    assert users[0].get_last_spoken() == "You are back from away."
    assert users[1].get_last_spoken() == "Player1 is back."


def test_only_the_host_sets_the_topic() -> None:
    game, users = make_room(player_count=2)

    game.execute_action(game.players[1], "change_topic", "Takeover")

    assert game.topic == ""
    assert users[1].get_last_spoken() == (
        "Only the host can set the room topic. Ask Player1 to change it."
    )

    game.execute_action(game.players[0], "change_topic", "Weekly audio games chat")

    assert game.topic == "Weekly audio games chat"
    assert game.topic_author == "Player1"
    assert users[0].get_last_spoken() == (
        "You set the room topic to: Weekly audio games chat"
    )
    assert users[1].get_last_spoken() == (
        "Player1 set the room topic to: Weekly audio games chat"
    )


def test_topic_input_is_cleaned_bounded_and_deduplicated() -> None:
    game, users = make_room(player_count=1)
    host = game.players[0]

    game.execute_action(host, "change_topic", "  Board   games\ttonight \r\n")
    assert game.topic == "Board games tonight"

    users[0].clear_messages()
    game.execute_action(host, "change_topic", "Board games tonight")
    assert users[0].get_last_spoken() == (
        "The room topic already says exactly that, so nothing changed."
    )

    users[0].clear_messages()
    too_long = "x" * (MAX_TOPIC_LENGTH + 5)
    game.execute_action(host, "change_topic", too_long)
    assert game.topic == "Board games tonight"
    assert users[0].get_last_spoken() == (
        f"That topic is too long. Keep it to {MAX_TOPIC_LENGTH} characters or "
        f"fewer; yours had {MAX_TOPIC_LENGTH + 5}."
    )

    users[0].clear_messages()
    game.execute_action(host, "change_topic", "\x07\x01")
    assert game.topic == "Board games tonight"
    assert users[0].get_last_spoken() == (
        "That topic had no readable text in it, so the room topic was left as it was."
    )


def test_topic_can_be_cleared_and_read_back() -> None:
    game, users = make_room(player_count=2)
    host = game.players[0]

    game.execute_action(game.players[1], "read_topic")
    assert users[1].get_last_spoken() == (
        "This room has no topic yet. The host can set one from the room tools."
    )

    game.execute_action(host, "change_topic", "Late night talk")
    users[1].clear_messages()
    game.execute_action(game.players[1], "read_topic")
    assert users[1].get_last_spoken() == (
        "Room topic, set by Player1: Late night talk"
    )

    users[0].clear_messages()
    users[1].clear_messages()
    game.execute_action(host, "change_topic", "   ")
    assert game.topic == ""
    assert game.topic_author == ""
    assert users[0].get_last_spoken() == "You cleared the room topic."
    assert users[1].get_last_spoken() == "Player1 cleared the room topic."

    users[0].clear_messages()
    game.execute_action(host, "change_topic", "")
    assert users[0].get_last_spoken() == "The room has no topic to clear."


def test_room_information_lists_topic_people_and_settings() -> None:
    game, users = make_room(player_count=2, spectators=1, action_cooldown=1)
    host = game.players[0]

    game.execute_action(host, "change_topic", "Coffee break")
    game.execute_action(game.players[1], "toggle_away")

    game.execute_action(host, "room_info")
    items = users[0].menus["status_box"]["items"]
    assert [item.id for item in items] == [
        "host",
        "topic",
        "topic_author",
        "people",
        "spectators",
        "away",
        "emotes",
        "settings",
        "player:lounge-p1",
        "player:lounge-p2",
        "player:lounge-s1",
    ]
    assert items[0].text == "Host: Player1."
    assert items[1].text == "Topic: Coffee break"
    assert items[3].text == "Seated: 2 people."
    assert items[4].text == "Watching: 1."
    assert items[5].text == "Away right now: 1."
    assert items[7].text == (
        "Room settings: emotes On, nudges On, dice and coin On, waiting time "
        "between room actions 1 second."
    )
    assert items[8].text == "Player1 (host)"
    assert items[9].text == "Player2 (away)"
    assert items[10].text == "Watcher1 (watching)"


def test_room_information_stays_current_while_open() -> None:
    game, users = make_room(player_count=2, action_cooldown=0)
    host = game.players[0]

    game.execute_action(host, "room_info")
    before = users[0].menus["status_box"]["items"]
    assert any(item.text == "Emotes played in this room: 0." for item in before)

    game.execute_action(game.players[1], "emote_celebrate")
    game.flush_menus()

    after = users[0].menus["status_box"]["items"]
    assert [item.id for item in after] == [item.id for item in before]
    assert any(item.text == "Emotes played in this room: 1." for item in after)


def test_spectators_read_the_room_but_cannot_use_seated_tools() -> None:
    game, users = make_room(player_count=1, spectators=1)
    spectator = game.players[1]
    spectator_user = users[1]

    assert spectator.is_spectator is True
    assert visible_action_ids(game, 1) == []

    game.execute_action(spectator, "emote_wave")
    assert spectator_user.get_spoken_messages() == []
    assert game.emote_count == 0

    game.execute_action(spectator, "read_topic")
    assert spectator_user.get_last_spoken() == (
        "This room has no topic yet. The host can set one from the room tools."
    )

    game.execute_action(spectator, "room_info")
    assert "status_box" in spectator_user.menus


def test_room_menu_lists_emotes_first_then_the_other_room_tools() -> None:
    game, users = make_room(player_count=2)

    game.refresh_menus(game.players[0])
    game.flush_menus()
    menu_ids = [
        item.id
        for item in users[0].menus["turn_menu"]["items"]
        if getattr(item, "id", None)
    ]

    expected_start = [f"emote_{emote_id}" for emote_id in EMOTE_ORDER]
    assert menu_ids[: len(expected_start)] == expected_start
    assert menu_ids[len(expected_start) :][:5] == [
        "nudge",
        "roll_dice",
        "flip_coin",
        "toggle_away",
        "change_topic",
    ]
    assert "start_game" not in menu_ids
    # Desktop reaches these through keybinds and the actions menu instead.
    assert "read_topic" not in menu_ids
    assert "room_info" not in menu_ids


def test_touch_clients_get_the_room_info_buttons_in_order() -> None:
    game, users = make_room(player_count=2, touch_first=True)

    action_set = game.create_standard_action_set(game.players[0])
    order = action_set._order
    assert order.index("read_topic") < order.index("room_info")
    assert order.index("room_info") < order.index("whos_at_table")

    game.refresh_menus(game.players[0])
    game.flush_menus()
    menu_ids = [
        item.id
        for item in users[0].menus["turn_menu"]["items"]
        if getattr(item, "id", None)
    ]
    assert menu_ids[-5:] == [
        "read_topic",
        "room_info",
        "whos_at_table",
        "web_actions_menu",
        "web_leave_table",
    ]
    assert "check_scores" not in menu_ids
    assert "whose_turn" not in menu_ids


def test_room_keybinds_reach_the_room_tools() -> None:
    game, users = make_room(player_count=2)
    host = game.players[0]

    game.handle_event(host, {"type": "keybind", "key": "r"})
    assert "status_box" in users[0].menus

    game.handle_event(host, {"type": "keybind", "key": "a"})
    assert host.away is True

    assert game._get_keybind_for_action("read_topic") == "t"
    assert game._get_keybind_for_action("change_topic") == "shift+t"
    assert game._get_keybind_for_action("nudge") == "n"
    assert game._get_keybind_for_action("roll_dice") == "d"
    assert game._get_keybind_for_action("flip_coin") == "f"


def test_room_state_survives_a_save_and_restore_round_trip() -> None:
    game, users = make_room(player_count=2, action_cooldown=5)
    host = game.players[0]

    game.execute_action(host, "change_topic", "Restored talk")
    game.execute_action(game.players[1], "toggle_away")

    restored = LoungeGame.from_json(game.to_json())
    restored.rebuild_runtime_state()

    assert restored.status == "waiting"
    assert restored.topic == "Restored talk"
    assert restored.topic_author == "Player1"
    assert restored.emote_count == 0
    assert restored.options.action_cooldown == 5
    assert [player.away for player in restored.players] == [False, True]


def test_lounge_tables_are_listed_as_an_open_room() -> None:
    server = Server(
        db_path=":memory:",
        locales_dir=Path(__file__).resolve().parents[1] / "locales",
    )
    host = MockUser("Bob")
    viewer = MockUser("Alice")
    server._users = {"Bob": host, "Alice": viewer}
    table = server._tables.create_table("lounge", "Bob", host)
    table.game = LoungeGame()

    assert server._table_status_key(table) == "table-status-open-room"

    server._show_active_tables_menu(viewer)
    texts = [
        item.text if hasattr(item, "text") else item
        for item in (viewer.get_current_menu_items("active_tables_menu") or [])
    ]
    assert any("Lounge [Open room]" in text for text in texts)


def test_latecomers_take_a_seat_instead_of_becoming_spectators() -> None:
    server = Server(
        db_path=":memory:",
        locales_dir=Path(__file__).resolve().parents[1] / "locales",
    )
    server._db.connect()
    host = MockUser("Bob")
    latecomer = MockUser("Alice")
    server._users = {"Bob": host, "Alice": latecomer}
    table = server._tables.create_table("lounge", "Bob", host)
    game = LoungeGame()
    table.game = game
    game._table = table
    game.initialize_lobby("Bob", host)

    server._auto_join_table(latecomer, table, "lounge")

    joined = game.get_player_by_id(latecomer.uuid)
    assert joined is not None
    assert joined.is_spectator is False
    assert table.get_players() == table.members
    assert game.status == "waiting"


def test_vietnamese_room_strings_render_for_each_listener() -> None:
    game, users = make_room(player_count=2, locale="vi")

    game.execute_action(game.players[0], "emote_wave")

    assert users[0].get_last_spoken() == "Bạn vẫy tay chào cả phòng."
    assert users[1].get_last_spoken() == "Player1 vẫy tay chào cả phòng."
