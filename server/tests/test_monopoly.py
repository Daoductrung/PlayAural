"""Rules, accessibility, persistence, and bot tests for Monopoly."""

import ast
import random
from dataclasses import replace
from pathlib import Path

import pytest

from server.core.server import SOUNDS_VERSION
from server.game_utils.actions import MenuInput
from server.game_utils.audio_duration import measure_audio_duration_ticks
from server.games.monopoly import audio as monopoly_audio
from server.games.monopoly.boards import (
    get_board,
    get_board_ids,
    register_board,
    validate_board,
)
from server.games.monopoly.bot import (
    cash_reserve,
    landing_weight,
    maximum_auction_bid,
    opponent_rent_pressure,
)
from server.games.monopoly.game import (
    PHASE_AUCTION,
    PHASE_AWAIT_ROLL,
    PHASE_DEBT,
    PHASE_JAIL,
    PHASE_MANAGE,
    PHASE_MORTGAGE_TRANSFER,
    PHASE_PROPERTY,
    PHASE_RENT,
    PHASE_SETUP,
    PHASE_TRADE_BUILD,
    PHASE_TRADE_RESPONSE,
    PHASE_TURN_ACTIONS,
    MonopolyGame,
)
from server.games.monopoly.models import (
    AuctionState,
    BoardDefinition,
    DebtState,
    DevelopmentDefinition,
    MortgageTransferState,
    PropertyState,
    RentState,
    TradeState,
)
from server.games.monopoly.rules import (
    calculate_rent,
    can_build,
    can_sell_building,
    transfer_mortgage_interest,
    unmortgage_cost,
)
from server.games.registry import GameRegistry
from server.messages.localization import Localization
from server.users.bot import Bot
from server.users.test_user import MockUser

ROOT = Path(__file__).resolve().parents[2]
BOARD = get_board("standard")
LONDON_BOARD = get_board("london")
PARIS_BOARD = get_board("paris")
GERMANY_BOARD = get_board("germany")
ITALY_BOARD = get_board("italy")
MADRID_BOARD = get_board("madrid")
TOKYO_BOARD = get_board("tokyo")
AUSTRALIA_BOARD = get_board("australia")
NEW_ZEALAND_BOARD = get_board("new_zealand")
HANOI_BOARD = get_board("hanoi")


def drain_sequence(
    game: MonopolyGame,
    tag: str,
    *,
    max_ticks: int = 2_000,
) -> None:
    for _ in range(max_ticks):
        if not game.has_active_sequence(tag=tag):
            return
        game.on_tick()
    raise AssertionError(f"Monopoly {tag} sequence did not complete")


def make_game(
    player_count: int = 2,
    *,
    start: bool = False,
    touch: bool = False,
    bots: bool = False,
    locale: str = "en",
) -> MonopolyGame:
    game = MonopolyGame()
    game.setup_keybinds()
    for index in range(player_count):
        name = f"Player{index + 1}"
        user = (
            Bot(name, uuid=f"p{index + 1}")
            if bots
            else MockUser(name, locale=locale, uuid=f"p{index + 1}")
        )
        if touch:
            user.client_type = "mobile"
        game.add_player(name, user)
    game.host = "Player1"
    if start:
        game.on_start()
        drain_sequence(game, "monopoly_intro")
        game.flush_menus()
    return game


def force_current(game: MonopolyGame, player_index: int = 0) -> None:
    player = game.players[player_index]
    game.current_player = player
    game.phase = "await_roll"
    game.decision_player_id = player.id
    game.refresh_menus()


def own_group(game: MonopolyGame, owner_id: str, group_id: str) -> None:
    for space in game.board.group_spaces(group_id):
        game.property_states[space.id].owner_id = owner_id


def test_registration_metadata_and_catalog_count() -> None:
    assert GameRegistry.get("monopoly") is MonopolyGame
    assert MonopolyGame.get_name() == "Monopoly"
    assert MonopolyGame.get_type() == "monopoly"
    assert MonopolyGame.get_category() == "board"
    assert MonopolyGame.get_min_players() == 2
    assert MonopolyGame.get_max_players() == 8
    assert MonopolyGame.get_supported_leaderboards() == [
        "wins",
        "rating",
        "games_played",
    ]
    assert len(GameRegistry.get_all()) == 45
    assert get_board_ids() == (
        "australia",
        "germany",
        "hanoi",
        "italy",
        "london",
        "madrid",
        "new_zealand",
        "paris",
        "standard",
        "tokyo",
    )
    board_option = MonopolyGame().options.get_option_metas()["board_id"]
    assert board_option.get_label("en", "standard") == "Board: United States"
    assert board_option.get_label("vi", "standard") == "Bàn cờ: Hoa Kỳ"
    assert board_option.get_label("en", "london") == "Board: London"
    assert board_option.get_label("vi", "london") == "Bàn cờ: Luân Đôn"
    assert board_option.get_label("en", "paris") == "Board: Paris"
    assert board_option.get_label("vi", "paris") == "Bàn cờ: Paris"
    assert board_option.get_label("en", "germany") == "Board: Germany"
    assert board_option.get_label("vi", "germany") == "Bàn cờ: Đức"
    assert board_option.get_label("en", "italy") == "Board: Italy"
    assert board_option.get_label("vi", "italy") == "Bàn cờ: Ý"
    assert board_option.get_label("en", "madrid") == "Board: Madrid"
    assert board_option.get_label("vi", "madrid") == "Bàn cờ: Madrid"
    assert board_option.get_label("en", "tokyo") == "Board: Tokyo"
    assert board_option.get_label("vi", "tokyo") == "Bàn cờ: Tokyo"
    assert board_option.get_label("en", "australia") == "Board: Australia"
    assert board_option.get_label("vi", "australia") == "Bàn cờ: Úc"
    assert board_option.get_label("en", "new_zealand") == "Board: New Zealand"
    assert board_option.get_label("vi", "new_zealand") == "Bàn cờ: New Zealand"
    assert board_option.get_label("en", "hanoi") == "Board: Hanoi, Vietnam"
    assert board_option.get_label("vi", "hanoi") == "Bàn cờ: Hà Nội, Việt Nam"
    assert MonopolyGame.relevant_preferences == ["brief_announcements"]
    game_options = MonopolyGame().options
    assert game_options.free_parking_cash is False
    assert game_options.double_salary_on_go is False
    assert game_options.no_rent_in_jail is False
    assert game_options.buy_after_passing_go is False
    assert game_options.snake_eyes_bonus is False
    metas = game_options.get_option_metas()
    assert "House rule" not in metas["free_parking_cash"].get_label("en", False)
    assert metas["free_parking_cash"].get_label("en", False) == (
        "Rest-space jackpot: Off"
    )
    assert metas["free_parking_cash"].get_label("vi", False) == "Quỹ ô nghỉ: Tắt"
    assert "board's rest space" in metas["free_parking_cash"].get_description(
        "en", False
    )
    snake_description = metas["snake_eyes_bonus"].get_description(
        "en", False, game=MonopolyGame()
    )
    assert "$500" in snake_description
    assert "United States" not in snake_description
    assert "Default: Off" in snake_description
    london_game = MonopolyGame()
    london_game.options.board_id = "london"
    assert "£500" in metas["snake_eyes_bonus"].get_description(
        "en", False, game=london_game
    )
    for board_id in ("paris", "germany", "italy", "madrid"):
        euro_game = MonopolyGame()
        euro_game.options.board_id = board_id
        assert "€500" in metas["snake_eyes_bonus"].get_description(
            "en", False, game=euro_game
        )
    tokyo_game = MonopolyGame()
    tokyo_game.options.board_id = "tokyo"
    assert "$500" in metas["snake_eyes_bonus"].get_description(
        "en", False, game=tokyo_game
    )
    australia_game = MonopolyGame()
    australia_game.options.board_id = "australia"
    assert "A$500" in metas["snake_eyes_bonus"].get_description(
        "en", False, game=australia_game
    )
    new_zealand_game = MonopolyGame()
    new_zealand_game.options.board_id = "new_zealand"
    assert "NZ$500" in metas["snake_eyes_bonus"].get_description(
        "en", False, game=new_zealand_game
    )
    hanoi_game = MonopolyGame()
    hanoi_game.options.board_id = "hanoi"
    assert "500,000 VND" in metas["snake_eyes_bonus"].get_description(
        "en", False, game=hanoi_game
    )


def test_dynamic_option_descriptions_render_through_the_real_menu_hint_path() -> None:
    game = make_game()
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None

    game.options.board_id = "tokyo"
    english = game._option_description_text(player, "toggle_snake_eyes_bonus")
    assert english == (
        "Rolling two ones pays $500, including when rolling for doubles in jail. "
        "Default: Off."
    )
    assert "amount" not in english

    user._locale = "vi"
    vietnamese = game._option_description_text(player, "toggle_snake_eyes_bonus")
    assert vietnamese == (
        "Khi cả hai xúc xắc đều ra mặt một, người tung nhận 500 đô la Monopoly, "
        "kể cả khi tung để tìm đôi trong tù. Mặc định: Tắt."
    )
    assert "amount" not in vietnamese

    action_ids = (
        "set_board_id",
        "toggle_free_parking_cash",
        "toggle_double_salary_on_go",
        "toggle_no_rent_in_jail",
        "toggle_buy_after_passing_go",
        "toggle_snake_eyes_bonus",
    )
    user._locale = "en"
    assert all(
        "Default:" in game._option_description_text(player, action_id)
        for action_id in action_ids
    )
    user._locale = "vi"
    assert all(
        "Mặc định:" in game._option_description_text(player, action_id)
        for action_id in action_ids
    )


def test_unknown_board_ids_are_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported Monopoly board"):
        get_board("unknown")


@pytest.mark.parametrize("board_id", get_board_ids())
def test_each_bundled_board_is_complete_and_valid(board_id: str) -> None:
    board = get_board(board_id)
    validate_board(board)
    assert len(board.spaces) == 40
    assert len(board.chance_cards) == 16
    assert len(board.community_cards) == 16
    assert (
        len(
            [
                space
                for space in board.spaces
                if space.id
                in {
                    item.id
                    for item in board.spaces
                    if item.kind in {"street", "transit", "utility"}
                }
            ]
        )
        == 28
    )
    assert board.starting_cash > 0
    if board.development.finite_supply:
        assert board.bank_houses == 32
        assert board.bank_hotels == 12
    else:
        assert board.bank_houses == 0
        assert board.bank_hotels == 0
    assert len(board.property_groups) == 10
    assert board.property_group("orange").name_key == "monopoly-group-orange"
    assert board.rules.auction_opening_bid > 0


def test_bundled_boards_have_unambiguous_localized_metadata() -> None:
    boards = [get_board(board_id) for board_id in get_board_ids()]
    assert len({board.name_key for board in boards}) == len(boards)
    assert len({board.description_key for board in boards}) == len(boards)


def test_started_boards_keep_runtime_state_isolated() -> None:
    games: list[MonopolyGame] = []
    for board_id in get_board_ids():
        game = make_game()
        game.options.board_id = board_id
        game.on_start()
        games.append(game)

    first_properties = [next(iter(game.property_states.values())) for game in games]
    first_properties[0].owner_id = games[0].players[0].id

    assert all(not state.owner_id for state in first_properties[1:])
    assert len({id(game.property_states) for game in games}) == len(games)
    assert len({id(game.chance_deck) for game in games}) == len(games)
    assert len({id(game.community_deck) for game in games}) == len(games)


def test_london_board_has_authentic_layout_economy_and_card_destinations() -> None:
    assert LONDON_BOARD.currency_key == "monopoly-currency-gbp"
    assert [space.id for space in LONDON_BOARD.spaces] == [
        "go",
        "old_kent_road",
        "community_1",
        "whitechapel_road",
        "income_tax",
        "kings_cross_station",
        "angel_islington",
        "chance_1",
        "euston_road",
        "pentonville_road",
        "jail",
        "pall_mall",
        "electric_company",
        "whitehall",
        "northumberland_avenue",
        "marylebone_station",
        "bow_street",
        "community_2",
        "marlborough_street",
        "vine_street",
        "free_parking",
        "strand",
        "chance_2",
        "fleet_street",
        "trafalgar_square",
        "fenchurch_station",
        "leicester_square",
        "coventry_street",
        "water_works",
        "piccadilly",
        "go_to_jail",
        "regent_street",
        "oxford_street",
        "community_3",
        "bond_street",
        "liverpool_street_station",
        "chance_3",
        "park_lane",
        "super_tax",
        "mayfair",
    ]
    assert LONDON_BOARD.space("old_kent_road").rents == (2, 10, 30, 90, 160, 250)
    assert LONDON_BOARD.space("mayfair").price == 400
    assert LONDON_BOARD.space("super_tax").tax_amount == 100
    assert LONDON_BOARD.property_group("transit").name_key == (
        "monopoly-group-stations"
    )
    assert LONDON_BOARD.card("chance", "chance_red_property").destination_id == (
        "trafalgar_square"
    )
    assert LONDON_BOARD.card("chance", "chance_named_transit").destination_id == (
        "kings_cross_station"
    )


def test_paris_board_has_authentic_layout_economy_and_card_destinations() -> None:
    assert PARIS_BOARD.currency_key == "monopoly-currency-eur"
    assert [space.id for space in PARIS_BOARD.spaces] == [
        "go",
        "boulevard_belleville",
        "community_1",
        "rue_lecourbe",
        "income_tax",
        "gare_montparnasse",
        "rue_vaugirard",
        "chance_1",
        "rue_courcelles",
        "avenue_republique",
        "jail",
        "boulevard_villette",
        "electric_company",
        "avenue_neuilly",
        "rue_paradis",
        "gare_lyon",
        "avenue_mozart",
        "community_2",
        "boulevard_saint_michel",
        "place_pigalle",
        "free_parking",
        "avenue_matignon",
        "chance_2",
        "boulevard_malesherbes",
        "avenue_henri_martin",
        "gare_nord",
        "faubourg_saint_honore",
        "place_bourse",
        "water_company",
        "rue_la_fayette",
        "go_to_jail",
        "avenue_breteuil",
        "avenue_foch",
        "community_3",
        "boulevard_capucines",
        "gare_saint_lazare",
        "chance_3",
        "avenue_champs_elysees",
        "luxury_tax",
        "rue_paix",
    ]
    assert PARIS_BOARD.space("boulevard_belleville").rents == (
        2,
        10,
        30,
        90,
        160,
        250,
    )
    assert PARIS_BOARD.space("rue_paix").price == 400
    assert PARIS_BOARD.space("luxury_tax").tax_amount == 100
    assert PARIS_BOARD.property_group("transit").name_key == ("monopoly-group-stations")
    assert PARIS_BOARD.card("chance", "chance_red_property").destination_id == (
        "avenue_henri_martin"
    )
    assert PARIS_BOARD.card("chance", "chance_named_transit").destination_id == (
        "gare_lyon"
    )


def test_germany_board_has_authentic_layout_economy_and_card_destinations() -> None:
    assert GERMANY_BOARD.currency_key == "monopoly-currency-eur"
    assert [space.id for space in GERMANY_BOARD.spaces] == [
        "go",
        "badstrasse",
        "community_1",
        "turmstrasse",
        "income_tax",
        "suedbahnhof",
        "chausseestrasse",
        "chance_1",
        "elisenstrasse",
        "poststrasse",
        "jail",
        "seestrasse",
        "elektrizitaetswerk",
        "hafenstrasse",
        "neue_strasse",
        "westbahnhof",
        "muenchner_strasse",
        "community_2",
        "wiener_strasse",
        "berliner_strasse",
        "free_parking",
        "theaterstrasse",
        "chance_2",
        "museumstrasse",
        "opernplatz",
        "nordbahnhof",
        "lessingstrasse",
        "schillerstrasse",
        "wasserwerk",
        "goethestrasse",
        "go_to_jail",
        "rathausplatz",
        "hauptstrasse",
        "community_3",
        "bahnhofstrasse",
        "hauptbahnhof",
        "chance_3",
        "parkstrasse",
        "additional_tax",
        "schlossallee",
    ]
    assert GERMANY_BOARD.space("badstrasse").rents == (2, 10, 30, 90, 160, 250)
    assert GERMANY_BOARD.space("schlossallee").price == 400
    assert GERMANY_BOARD.space("additional_tax").tax_amount == 100
    assert GERMANY_BOARD.property_group("transit").name_key == (
        "monopoly-group-stations"
    )
    assert GERMANY_BOARD.card("chance", "chance_red_property").destination_id == (
        "opernplatz"
    )
    assert GERMANY_BOARD.card("chance", "chance_pink_property").destination_id == (
        "seestrasse"
    )
    assert GERMANY_BOARD.card("chance", "chance_named_transit").destination_id == (
        "suedbahnhof"
    )


def test_italy_board_has_authentic_layout_economy_and_card_destinations() -> None:
    assert ITALY_BOARD.currency_key == "monopoly-currency-eur"
    assert [space.id for space in ITALY_BOARD.spaces] == [
        "go",
        "vicolo_corto",
        "community_1",
        "vicolo_stretto",
        "income_tax",
        "stazione_sud",
        "bastioni_gran_sasso",
        "chance_1",
        "viale_monterosa",
        "viale_vesuvio",
        "jail",
        "via_accademia",
        "electric_company",
        "corso_ateneo",
        "piazza_universita",
        "stazione_ovest",
        "via_verdi",
        "community_2",
        "corso_raffaello",
        "piazza_dante",
        "free_parking",
        "via_marco_polo",
        "chance_2",
        "corso_magellano",
        "largo_colombo",
        "stazione_nord",
        "viale_costantino",
        "viale_traiano",
        "water_works",
        "piazza_giulio_cesare",
        "go_to_jail",
        "via_roma",
        "corso_impero",
        "community_3",
        "largo_augusto",
        "stazione_est",
        "chance_3",
        "viale_dei_giardini",
        "luxury_tax",
        "parco_della_vittoria",
    ]
    assert ITALY_BOARD.space("vicolo_corto").rents == (2, 10, 30, 90, 160, 250)
    assert ITALY_BOARD.space("parco_della_vittoria").price == 400
    assert ITALY_BOARD.space("luxury_tax").tax_amount == 100
    assert ITALY_BOARD.property_group("transit").name_key == ("monopoly-group-stations")
    assert ITALY_BOARD.card("chance", "chance_red_property").destination_id == (
        "largo_colombo"
    )
    assert ITALY_BOARD.card("chance", "chance_pink_property").destination_id == (
        "via_accademia"
    )
    assert ITALY_BOARD.card("chance", "chance_named_transit").destination_id == (
        "stazione_sud"
    )


def test_madrid_board_has_authentic_layout_economy_and_card_destinations() -> None:
    assert MADRID_BOARD.currency_key == "monopoly-currency-eur"
    assert [space.id for space in MADRID_BOARD.spaces] == [
        "go",
        "ronda_valencia",
        "community_1",
        "plaza_lavapies",
        "income_tax",
        "estacion_goya",
        "glorieta_cuatro_caminos",
        "chance_1",
        "avenida_reina_victoria",
        "calle_bravo_murillo",
        "jail",
        "glorieta_bilbao",
        "electric_company",
        "calle_alberto_aguilera",
        "calle_fuencarral",
        "estacion_delicias",
        "avenida_felipe_ii",
        "community_2",
        "calle_velazquez",
        "calle_serrano",
        "free_parking",
        "avenida_america",
        "chance_2",
        "calle_maria_molina",
        "calle_cea_bermudez",
        "estacion_mediodia",
        "avenida_reyes_catolicos",
        "calle_bailen",
        "water_works",
        "plaza_espana",
        "go_to_jail",
        "puerta_sol",
        "calle_alcala",
        "community_3",
        "gran_via",
        "estacion_norte",
        "chance_3",
        "paseo_castellana",
        "luxury_tax",
        "paseo_prado",
    ]
    assert MADRID_BOARD.space("ronda_valencia").rents == (2, 10, 30, 90, 160, 250)
    assert MADRID_BOARD.space("paseo_prado").price == 400
    assert MADRID_BOARD.space("luxury_tax").tax_amount == 100
    assert MADRID_BOARD.property_group("transit").name_key == (
        "monopoly-group-stations"
    )
    assert MADRID_BOARD.card("chance", "chance_top_property").destination_id == (
        "paseo_prado"
    )
    assert MADRID_BOARD.card("chance", "chance_red_property").destination_id == (
        "calle_cea_bermudez"
    )
    assert MADRID_BOARD.card("chance", "chance_pink_property").destination_id == (
        "glorieta_bilbao"
    )
    assert MADRID_BOARD.card("chance", "chance_named_transit").destination_id == (
        "estacion_goya"
    )


def test_tokyo_board_has_authentic_layout_economy_and_card_destinations() -> None:
    assert TOKYO_BOARD.currency_key == "monopoly-currency-monopoly-dollar"
    assert [space.id for space in TOKYO_BOARD.spaces] == [
        "go",
        "hachioji",
        "community_1",
        "tachikawa",
        "income_tax",
        "shinjuku_station",
        "yotsuya",
        "chance_1",
        "yoyogi",
        "ichigaya",
        "jail",
        "akihabara",
        "electric_company",
        "ueno",
        "ikebukuro",
        "shinagawa_station",
        "odaiba",
        "community_2",
        "hibiya",
        "shimbashi",
        "free_parking",
        "ebisu",
        "chance_2",
        "harajuku",
        "omotesando",
        "shibuya_station",
        "akasaka",
        "roppongi",
        "water_works",
        "toranomon",
        "go_to_jail",
        "yurakucho",
        "nihonbashi",
        "community_3",
        "otemachi",
        "tokyo_station",
        "chance_3",
        "marunouchi",
        "luxury_tax",
        "ginza",
    ]
    assert TOKYO_BOARD.space("hachioji").rents == (2, 10, 30, 90, 160, 250)
    assert TOKYO_BOARD.space("ginza").price == 400
    assert TOKYO_BOARD.space("luxury_tax").tax_amount == 100
    assert TOKYO_BOARD.property_group("transit").name_key == ("monopoly-group-stations")
    assert TOKYO_BOARD.card("chance", "chance_top_property").destination_id == ("ginza")
    assert TOKYO_BOARD.card("chance", "chance_red_property").destination_id == (
        "omotesando"
    )
    assert TOKYO_BOARD.card("chance", "chance_pink_property").destination_id == (
        "akihabara"
    )
    assert TOKYO_BOARD.card("chance", "chance_named_transit").destination_id == (
        "shinjuku_station"
    )


def test_australia_board_has_authentic_layout_economy_and_card_destinations() -> None:
    assert AUSTRALIA_BOARD.currency_key == "monopoly-currency-aud"
    assert [space.id for space in AUSTRALIA_BOARD.spaces] == [
        "go",
        "todd_street",
        "community_1",
        "smith_street",
        "income_tax",
        "perth_station",
        "salamanca_place",
        "chance_1",
        "davey_street",
        "macquarie_street",
        "jail",
        "william_street",
        "australia_post",
        "barrack_street",
        "hay_street",
        "adelaide_station",
        "north_terrace",
        "community_2",
        "victoria_square",
        "rundle_mall",
        "free_parking",
        "stanley_street",
        "chance_2",
        "petries_bight",
        "wickham_terrace",
        "flinders_street_station",
        "collins_street",
        "elizabeth_street",
        "telecom_australia",
        "bourke_street",
        "go_to_jail",
        "castlereagh_street",
        "george_street",
        "community_3",
        "pitt_street",
        "sydney_station",
        "chance_3",
        "flinders_way",
        "super_tax",
        "kings_avenue",
    ]
    assert AUSTRALIA_BOARD.space("todd_street").rents == (2, 10, 30, 90, 160, 250)
    assert AUSTRALIA_BOARD.space("kings_avenue").price == 400
    assert AUSTRALIA_BOARD.space("super_tax").tax_amount == 100
    assert AUSTRALIA_BOARD.property_group("transit").name_key == (
        "monopoly-group-stations"
    )
    assert AUSTRALIA_BOARD.card("chance", "chance_top_property").destination_id == (
        "kings_avenue"
    )
    assert AUSTRALIA_BOARD.card("chance", "chance_red_property").destination_id == (
        "wickham_terrace"
    )
    assert AUSTRALIA_BOARD.card("chance", "chance_pink_property").destination_id == (
        "william_street"
    )
    assert (
        AUSTRALIA_BOARD.card("chance", "chance_named_transit").destination_id
        == "perth_station"
    )


def test_new_zealand_board_has_authentic_layout_economy_and_card_destinations() -> None:
    assert NEW_ZEALAND_BOARD.currency_key == "monopoly-currency-nzd"
    assert [space.id for space in NEW_ZEALAND_BOARD.spaces] == [
        "go",
        "palmerston_street",
        "community_1",
        "mackay_street",
        "income_tax",
        "balclutha_station",
        "east_street",
        "chance_1",
        "stafford_street",
        "thames_street",
        "jail",
        "gladstone_road",
        "electric_company",
        "marine_parade",
        "bank_street",
        "taumarunui_station",
        "devon_street",
        "community_2",
        "rangitikei_street",
        "victoria_avenue",
        "free_parking",
        "high_street",
        "chance_2",
        "market_street",
        "trafalgar_street",
        "kaikoura_station",
        "cameron_road",
        "fenton_street",
        "water_works",
        "garden_place",
        "go_to_jail",
        "dee_street",
        "princes_street",
        "community_3",
        "cathedral_square",
        "frankton_junction",
        "chance_3",
        "lambton_quay",
        "super_tax",
        "queen_street",
    ]
    assert NEW_ZEALAND_BOARD.space("palmerston_street").rents == (
        2,
        10,
        30,
        90,
        160,
        250,
    )
    assert NEW_ZEALAND_BOARD.space("queen_street").price == 400
    assert NEW_ZEALAND_BOARD.space("super_tax").tax_amount == 100
    assert NEW_ZEALAND_BOARD.property_group("transit").name_key == (
        "monopoly-group-stations"
    )
    assert NEW_ZEALAND_BOARD.card("chance", "chance_top_property").destination_id == (
        "queen_street"
    )
    assert NEW_ZEALAND_BOARD.card("chance", "chance_red_property").destination_id == (
        "trafalgar_street"
    )
    assert NEW_ZEALAND_BOARD.card("chance", "chance_pink_property").destination_id == (
        "gladstone_road"
    )
    assert (
        NEW_ZEALAND_BOARD.card("chance", "chance_named_transit").destination_id
        == "balclutha_station"
    )


def test_hanoi_board_has_authentic_layout_economy_and_rule_values() -> None:
    assert HANOI_BOARD.currency_key == "monopoly-currency-vnd"
    assert [space.id for space in HANOI_BOARD.spaces] == [
        "go",
        "dinh_liet",
        "social_insurance",
        "trang_tien",
        "lottery_1",
        "my_dinh_bus_station",
        "hang_khay",
        "lucky_draw_1",
        "nguyen_huu_huan",
        "ngo_tat_to",
        "jail",
        "hang_ga",
        "lottery_2",
        "hang_gai",
        "hang_ca",
        "nuoc_ngam_bus_station",
        "cau_go",
        "one_pillar_pagoda",
        "bat_dan",
        "thanh_nien",
        "free_parking",
        "nha_tho",
        "lucky_draw_2",
        "ngu_xa",
        "hang_hanh",
        "giap_bat_bus_station",
        "ngo_huyen",
        "nam_ngu",
        "long_bien_bridge",
        "hang_manh",
        "go_to_jail",
        "le_van_huu",
        "giang_vo",
        "lottery_3",
        "hang_chao",
        "gia_lam_bus_station",
        "lucky_draw_3",
        "nha_chung",
        "excise_tax",
        "lo_duc",
    ]
    assert HANOI_BOARD.space("dinh_liet").rents == (
        2_000,
        10_000,
        30_000,
        90_000,
        160_000,
        250_000,
    )
    assert HANOI_BOARD.space("lo_duc").price == 400_000
    assert HANOI_BOARD.space("hang_hanh").building_cost == 150_000
    assert HANOI_BOARD.space("social_insurance").tax_amount == 200_000
    assert HANOI_BOARD.space("excise_tax").tax_amount == 100_000
    assert HANOI_BOARD.space("one_pillar_pagoda").price == 150_000
    assert HANOI_BOARD.space("long_bien_bridge").price == 280_000
    assert HANOI_BOARD.space("long_bien_bridge").mortgage_value == 140_000
    assert HANOI_BOARD.property_group("transit").name_key == (
        "monopoly-group-hanoi-bus-stations"
    )
    assert HANOI_BOARD.property_group("utility").name_key == (
        "monopoly-group-hanoi-landmarks"
    )
    assert HANOI_BOARD.starting_cash == 1_500_000
    assert HANOI_BOARD.go_salary == 200_000
    assert HANOI_BOARD.jail_fine == 100_000
    assert HANOI_BOARD.rules.auction_opening_bid == 10_000
    assert HANOI_BOARD.rules.auction_bid_increment == 5_000
    assert HANOI_BOARD.rules.utility_dice_unit == 1_000
    assert HANOI_BOARD.development.finite_supply is False
    assert len(HANOI_BOARD.development.level_keys) == 5
    assert HANOI_BOARD.card("chance", "chance_dividend").amount == 50_000
    assert HANOI_BOARD.card("chance", "chance_back_three").amount == 3
    assert HANOI_BOARD.card("chance", "chance_red_property").destination_id == (
        "hang_hanh"
    )
    assert HANOI_BOARD.card("chance", "chance_named_transit").destination_id == (
        "my_dinh_bus_station"
    )


def test_hanoi_board_uses_named_unlimited_business_development() -> None:
    game = make_game()
    game.options.board_id = "hanoi"
    game.on_start()
    player = game.players[0]
    player.cash = 10_000_000
    own_group(game, player.id, "brown")
    for space in game.board.group_spaces("brown"):
        game.property_states[space.id].buildings = 4

    assert game.bank_houses == 0
    assert game.bank_hotels == 0
    assert can_build(
        game.board,
        game.property_states,
        "dinh_liet",
        player.id,
        game.bank_houses,
        game.bank_hotels,
    ) is None

    game._apply_build(player, "dinh_liet", announce=False)

    assert game.property_states["dinh_liet"].buildings == 5
    assert game.bank_houses == 0
    assert game.bank_hotels == 0
    assert game._building_text("vi", 5) == "nhà hàng hoặc cửa hàng lớn"
    assert game._get_management_selector_label(
        player, "choose_build_property"
    ) == "Upgrade a business"
    assert "restaurant or large shop" in game._property_description(
        "en", "dinh_liet"
    )

    game._apply_sell_building(player, "dinh_liet", announce=False)

    assert game.property_states["dinh_liet"].buildings == 4
    assert game.bank_houses == 0
    assert game.bank_hotels == 0


def test_hanoi_management_never_formats_impossible_standard_building_actions() -> None:
    game = make_game(locale="vi")
    game.options.board_id = "hanoi"
    game.on_start()
    drain_sequence(game, "monopoly_intro")
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    player.cash = 171_064
    own_group(game, player.id, "brown")
    game.phase = PHASE_MANAGE
    game.decision_player_id = player.id
    game.management_property_id = "dinh_liet"
    game.property_states["dinh_liet"].buildings = 5

    assert game._get_management_action_label(player, "build") == (
        "Nâng cấp kinh doanh"
    )
    build_action = game.find_action(player, "build")
    assert build_action is not None
    build_resolution = game.resolve_action(player, build_action)
    assert build_resolution.enabled is False
    assert build_resolution.description == (
        "Mua cấp phát triển tiếp theo cho bất động sản này. Mọi bất động sản "
        "trong nhóm màu phải được phát triển đều."
    )
    assert build_resolution.description != "Hàng quán này đã đạt bậc cao nhất."
    user.clear_messages()
    game.execute_action(player, "build")
    assert user.get_last_spoken() == "Hàng quán này đã đạt bậc cao nhất."

    game.management_property_id = "hang_manh"
    game.property_states["hang_manh"].owner_id = player.id
    assert game.property_states["hang_manh"].buildings == 0
    assert game._get_management_action_label(player, "sell_building") == (
        "Bán một cấp nâng cấp kinh doanh"
    )
    assert game._get_management_action_label(player, "sell_group_buildings") == (
        "Bán mọi cấp nâng cấp kinh doanh trong nhóm màu này"
    )
    sell_action = game.find_action(player, "sell_building")
    assert sell_action is not None
    sell_resolution = game.resolve_action(player, sell_action)
    assert sell_resolution.enabled is False
    assert sell_resolution.description == (
        "Bán một cấp phát triển cho Ngân hàng với nửa giá mua. Mọi bất động sản "
        "trong nhóm màu phải được bán đều."
    )
    user.clear_messages()
    game.execute_action(player, "sell_building")
    assert user.get_last_spoken() == (
        "Hàng quán này chưa có cấp nâng cấp nào để bán."
    )
    assert "0 đồng" not in game._get_management_action_label(
        player, "sell_group_buildings"
    )
    assert "ngôi nhà" not in " ".join(
        game._get_management_action_label(player, action_id)
        for action_id in ("build", "sell_building", "sell_group_buildings")
    )


def test_management_selector_empty_reasons_identify_the_actual_blocker() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    game.phase = PHASE_MANAGE
    game.decision_player_id = player.id

    assert game._is_management_selector_enabled(
        player, action_id="choose_build_property"
    ) == "monopoly-error-build-none-no-streets"

    game.property_states["mediterranean"].owner_id = player.id
    assert game._is_management_selector_enabled(
        player, action_id="choose_build_property"
    ) == "monopoly-error-build-none-no-color-set"

    game.property_states["baltic"].owner_id = player.id
    game.property_states["baltic"].mortgaged = True
    assert game._is_management_selector_enabled(
        player, action_id="choose_build_property"
    ) == "monopoly-error-build-none-groups-mortgaged"

    game.property_states["baltic"].mortgaged = False
    for property_id in ("mediterranean", "baltic"):
        game.property_states[property_id].buildings = 5
    assert game._is_management_selector_enabled(
        player, action_id="choose_build_property"
    ) == "monopoly-error-build-none-fully-developed"

    for property_id in ("mediterranean", "baltic"):
        game.property_states[property_id].buildings = 0
    player.cash = 0
    build_reason = game._is_management_selector_enabled(
        player, action_id="choose_build_property"
    )
    assert build_reason == (
        "monopoly-error-build-none-needs-cash",
        {"cost": "$50", "cash": "$0"},
    )
    build_action = game.find_action(player, "choose_build_property")
    assert build_action is not None
    build_resolution = game.resolve_action(player, build_action)
    assert build_resolution.enabled is False
    assert build_resolution.description == (
        "Opens a list of properties where you can legally afford the next "
        "development level."
    )
    user.clear_messages()
    game.execute_action(player, "choose_build_property")
    assert user.get_last_spoken() == (
        "The cheapest legal building costs $50, but you have only $0."
    )

    assert game._is_management_selector_enabled(
        player, action_id="choose_unmortgage_property"
    ) == "monopoly-error-no-mortgaged-properties"
    game.property_states["mediterranean"].mortgaged = True
    assert game._is_management_selector_enabled(
        player, action_id="choose_unmortgage_property"
    ) == (
        "monopoly-error-unmortgage-none-needs-cash",
        {"cost": "$33", "cash": "$0"},
    )


def test_hanoi_board_uses_localized_space_deck_and_development_terms() -> None:
    game = make_game()
    game.options.board_id = "hanoi"
    game.on_start()
    player = game.players[0]

    assert game._money("en", 1_500_000) == "1,500,000 VND"
    assert game._money("vi", 1_500_000) == "1.500.000 đồng"
    assert "type: bus station" in game._property_description(
        "en", "my_dinh_bus_station"
    )
    assert "loại: địa danh" in game._property_description(
        "vi", "one_pillar_pagoda"
    )
    english_landmark = game._property_description("en", "one_pillar_pagoda")
    vietnamese_landmark = game._property_description("vi", "one_pillar_pagoda")
    assert "4,000 VND per dice pip" in english_landmark
    assert "10,000 VND per dice pip" in english_landmark
    assert "both landmarks" in english_landmark
    assert "4.000 đồng cho mỗi điểm xúc xắc" in vietnamese_landmark
    assert "10.000 đồng cho mỗi điểm" in vietnamese_landmark
    assert "cả hai địa danh" in vietnamese_landmark
    nearest_landmark = game.board.card("chance", "chance_utility")
    assert "nearest landmark" in game._card_text("en", nearest_landmark)
    assert "10,000 VND per dice pip" in game._card_text("en", nearest_landmark)
    assert "địa danh gần nhất" in game._card_text("vi", nearest_landmark)
    assert "10.000 đồng cho mỗi điểm xúc xắc" in game._card_text(
        "vi", nearest_landmark
    )
    assert "Lucky Draw" in game._jail_card_option_label(
        player, "chance_jail_free"
    )
    assert "Xổ Số Kiến Thiết" in game._jail_card_option_label(
        player, "community_jail_free"
    )
    assert "mảnh nâng cấp kinh doanh" in game._card_text(
        "vi", game.board.card("chance", "chance_repairs")
    )
    assert "Hồ Hoàn Kiếm" in game._card_text(
        "vi", game.board.card("chance", "chance_go")
    )
    assert "Nhà tù Hỏa Lò" in game._card_text(
        "vi", game.board.card("chance", "chance_go_jail")
    )

    user = game.get_user(player)
    assert user is not None
    user._locale = "vi"
    user.clear_messages()
    game._resolve_card(player, game.board.card("chance", "chance_repairs"))
    assert user.get_last_spoken() == (
        "Bạn không có cấp nâng cấp kinh doanh nên không phải trả phí sửa chữa "
        "trên thẻ."
    )


def test_board_validation_rejects_invalid_regional_content() -> None:
    assert register_board(BOARD) is BOARD

    invalid = replace(BOARD, spaces=BOARD.spaces[:-1] + (BOARD.spaces[0],))
    with pytest.raises(ValueError, match="unique ids"):
        validate_board(invalid)

    invalid_group = replace(
        BOARD,
        property_groups=tuple(
            group for group in BOARD.property_groups if group.id != "brown"
        ),
    )
    with pytest.raises(ValueError, match="incomplete deed data"):
        validate_board(invalid_group)

    invalid_deed_data = replace(
        BOARD,
        spaces=(replace(BOARD.spaces[0], price=1), *BOARD.spaces[1:]),
    )
    with pytest.raises(ValueError, match="unused deed data"):
        validate_board(invalid_deed_data)

    invalid_card = replace(
        BOARD.chance_cards[7],
        destination_id=BOARD.go_space_id,
    )
    with pytest.raises(ValueError, match="unused destination"):
        validate_board(
            replace(
                BOARD,
                chance_cards=(
                    *BOARD.chance_cards[:7],
                    invalid_card,
                    *BOARD.chance_cards[8:],
                ),
            )
        )

    invalid_collect_go = replace(BOARD.chance_cards[7], collect_go=True)
    with pytest.raises(ValueError, match="unused collect-Go data"):
        validate_board(
            replace(
                BOARD,
                chance_cards=(
                    *BOARD.chance_cards[:7],
                    invalid_collect_go,
                    *BOARD.chance_cards[8:],
                ),
            )
        )

    with pytest.raises(ValueError, match="localized metadata"):
        validate_board(
            replace(
                BOARD,
                terminology=replace(BOARD.terminology, utility_kind_key=""),
            )
        )
    with pytest.raises(ValueError, match="five levels"):
        validate_board(
            replace(
                BOARD,
                development=DevelopmentDefinition(
                    level_keys=("one", "two", "three", "four"),
                    empty_key="empty",
                ),
            )
        )
    with pytest.raises(ValueError, match="unique and localized"):
        validate_board(
            replace(
                BOARD,
                development=replace(
                    BOARD.development,
                    error_key_overrides=(("same", "one"), ("same", "two")),
                ),
            )
        )
    with pytest.raises(ValueError, match="must contain pieces"):
        validate_board(replace(BOARD, bank_houses=0))
    with pytest.raises(ValueError, match="safe ranges"):
        validate_board(
            replace(
                BOARD,
                rules=replace(BOARD.rules, utility_dice_unit=0),
            )
        )

    with pytest.raises(ValueError, match="name key already registered"):
        register_board(
            replace(
                BOARD,
                id="conflicting_name",
            )
        )
    with pytest.raises(ValueError, match="description key already registered"):
        register_board(
            replace(
                BOARD,
                id="conflicting_description",
                name_key="monopoly-board-conflicting-description",
            )
        )


def test_start_initializes_economy_and_audio() -> None:
    game = make_game(3, start=True)

    assert game.status == "playing"
    assert all(player.cash == 1_500 and player.position == 0 for player in game.players)
    assert len(game.property_states) == 28
    assert game.bank_houses == 32
    assert game.bank_hotels == 12
    assert len(game.chance_deck) == 16
    assert len(game.community_deck) == 16
    for player in game.players:
        user = game.get_user(player)
        assert user is not None
        sounds = [
            message.data["name"]
            for message in user.messages
            if message.type == "play_sound"
        ]
        assert sounds[:2] == [
            monopoly_audio.SOUND_BOARD_SETUP,
            monopoly_audio.SOUND_DECK_SHUFFLE,
        ]
        assert any(
            sound in monopoly_audio.SOUND_OPENING_ROLLS for sound in sounds[2:]
        )
        assert any(
            message.type == "play_music"
            and message.data["name"] == monopoly_audio.SOUND_MUSIC_LOOP
            for message in user.messages
        )


def test_intro_keeps_turn_unassigned_and_blocks_rolls_until_reveal() -> None:
    game = make_game(3)
    game.on_start()
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None

    assert game.phase == PHASE_SETUP
    assert game.current_player is None
    assert game.decision_player_id == ""
    assert game.turn_player_ids == []

    user.clear_messages()
    game._action_whose_turn(player, "whose_turn")
    assert user.get_last_spoken() == Localization.get("en", "game-no-turn")

    game.handle_event(player, {"type": "keybind", "key": "space"})
    assert user.get_last_spoken() == Localization.get(
        "en", "monopoly-error-setup-in-progress"
    )
    assert not game.has_active_sequence(tag="monopoly_roll")
    assert game.current_player is None

    drain_sequence(game, "monopoly_intro")
    assert game.current_player in game.players
    assert game.decision_player_id == game.current_player.id
    assert game.phase == PHASE_AWAIT_ROLL


def test_intro_reveal_and_first_player_survive_save_restore() -> None:
    game = make_game(3)
    game.on_start()
    restored = MonopolyGame.from_json(game.to_json())
    restored.rebuild_runtime_state()

    assert restored.phase == PHASE_SETUP
    assert restored.current_player is None
    drain_sequence(game, "monopoly_intro")
    drain_sequence(restored, "monopoly_intro")

    assert restored.current_player is not None
    assert game.current_player is not None
    assert restored.current_player.id == game.current_player.id
    assert restored.decision_player_id == restored.current_player.id


@pytest.mark.parametrize("jailed", (False, True))
def test_space_shortcut_dispatches_exactly_one_phase_appropriate_roll(
    jailed: bool,
) -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    player.in_jail = jailed
    if jailed:
        player.position = game.board.space_index(game.board.jail_space_id)
        game.phase = PHASE_JAIL
    outcomes = [(1, 2), (6, 6)]
    calls = 0

    def roll_pair() -> tuple[int, int]:
        nonlocal calls
        outcome = outcomes[calls]
        calls += 1
        return outcome

    game._roll_pair = roll_pair  # type: ignore[method-assign]
    user.clear_messages()

    game.handle_event(player, {"type": "keybind", "key": "space"})

    assert calls == 1
    assert (game.last_die_1, game.last_die_2) == (1, 2)
    assert len(
        [sequence for sequence in game.active_sequences if sequence.tag == "monopoly_roll"]
    ) == 1
    assert Localization.get(
        "en", "monopoly-error-roll-resolving"
    ) not in user.get_spoken_messages()


def test_london_board_start_uses_pounds_and_board_specific_station_terms() -> None:
    game = make_game()
    game.options.board_id = "london"
    game.on_start()
    game.flush_menus()
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None

    assert game.board is LONDON_BOARD
    assert game._money("en", 1_500) == "£1,500"
    assert game._money("vi", 1_500) == "1.500 bảng"
    assert "type: station" in game._property_description("en", "kings_cross_station")
    assert "loại: nhà ga" in game._property_description("vi", "kings_cross_station")
    assert any("London board" in message for message in user.get_spoken_messages())


@pytest.mark.parametrize(
    (
        "board_id",
        "board",
        "red_property_id",
        "station_id",
        "english_money",
        "vietnamese_money",
    ),
    (
        (
            "london",
            LONDON_BOARD,
            "trafalgar_square",
            "kings_cross_station",
            "£1,500",
            "1.500 bảng",
        ),
        (
            "paris",
            PARIS_BOARD,
            "avenue_henri_martin",
            "gare_lyon",
            "€1,500",
            "1.500 euro",
        ),
        (
            "germany",
            GERMANY_BOARD,
            "opernplatz",
            "suedbahnhof",
            "€1,500",
            "1.500 euro",
        ),
        (
            "italy",
            ITALY_BOARD,
            "largo_colombo",
            "stazione_sud",
            "€1,500",
            "1.500 euro",
        ),
        (
            "madrid",
            MADRID_BOARD,
            "calle_cea_bermudez",
            "estacion_goya",
            "€1,500",
            "1.500 euro",
        ),
        (
            "tokyo",
            TOKYO_BOARD,
            "omotesando",
            "shinjuku_station",
            "$1,500",
            "1.500 đô la Monopoly",
        ),
        (
            "australia",
            AUSTRALIA_BOARD,
            "wickham_terrace",
            "perth_station",
            "A$1,500",
            "1.500 đô la Úc",
        ),
        (
            "new_zealand",
            NEW_ZEALAND_BOARD,
            "trafalgar_street",
            "balclutha_station",
            "NZ$1,500",
            "1.500 đô la New Zealand",
        ),
    ),
)
def test_regional_boards_use_stations_currency_and_card_destinations(
    board_id: str,
    board: BoardDefinition,
    red_property_id: str,
    station_id: str,
    english_money: str,
    vietnamese_money: str,
) -> None:
    game = make_game()
    game.options.board_id = board_id
    game.on_start()
    drain_sequence(game, "monopoly_intro")
    player = game.players[0]
    force_current(game)
    player.position = game.board.space_index("chance_3")
    game.chance_deck.remove("chance_red_property")
    game.chance_deck.insert(0, "chance_red_property")

    game._draw_card(player, "chance")
    drain_sequence(game, "monopoly_card")

    assert game.board is board
    assert game._money("en", 1_500) == english_money
    assert game._money("vi", 1_500) == vietnamese_money
    assert "type: station" in game._property_description("en", station_id)
    assert "loại: nhà ga" in game._property_description("vi", station_id)
    assert player.position == game.board.space_index(red_property_id)
    assert player.cash == game.board.starting_cash + game.board.go_salary
    assert game.pending_property_id == red_property_id


@pytest.mark.parametrize(
    ("board_id", "expected_text"),
    (
        ("standard", "Collect $50 from the Bank."),
        ("london", "Collect £50 from the Bank."),
        ("paris", "Collect €50 from the Bank."),
        ("germany", "Collect €50 from the Bank."),
        ("italy", "Collect €50 from the Bank."),
        ("madrid", "Collect €50 from the Bank."),
        ("tokyo", "Collect $50 from the Bank."),
        ("australia", "Collect A$50 from the Bank."),
        ("new_zealand", "Collect NZ$50 from the Bank."),
        ("hanoi", "Collect 50,000 VND from the Bank."),
    ),
)
def test_shared_card_templates_use_the_selected_board_currency(
    board_id: str, expected_text: str
) -> None:
    game = make_game()
    game.options.board_id = board_id
    card = game.board.card("chance", "chance_dividend")

    assert game._card_text("en", card) == expected_text


@pytest.mark.parametrize(
    ("board_id", "english_term", "vietnamese_term"),
    (
        ("standard", "nearest railroad", "tuyến đường sắt gần nhất"),
        ("london", "nearest station", "nhà ga gần nhất"),
        ("paris", "nearest station", "nhà ga gần nhất"),
        ("germany", "nearest station", "nhà ga gần nhất"),
        ("italy", "nearest station", "nhà ga gần nhất"),
        ("madrid", "nearest station", "nhà ga gần nhất"),
        ("tokyo", "nearest station", "nhà ga gần nhất"),
        ("australia", "nearest station", "nhà ga gần nhất"),
        ("new_zealand", "nearest station", "nhà ga gần nhất"),
        ("hanoi", "nearest bus station", "bến xe gần nhất"),
    ),
)
def test_shared_card_templates_use_the_selected_transit_term(
    board_id: str, english_term: str, vietnamese_term: str
) -> None:
    game = make_game()
    game.options.board_id = board_id
    card = game.board.card("chance", "chance_transit_1")

    assert english_term in game._card_text("en", card)
    assert vietnamese_term in game._card_text("vi", card)


@pytest.mark.parametrize("board_id", get_board_ids())
def test_every_card_template_renders_for_every_locale(board_id: str) -> None:
    game = make_game()
    game.options.board_id = board_id

    for card in game.board.chance_cards + game.board.community_cards:
        for locale in ("en", "vi"):
            rendered = game._card_text(locale, card)
            assert rendered
            assert card.text_key not in rendered
            assert "{" not in rendered and "}" not in rendered


def test_passing_go_and_go_to_jail() -> None:
    game = make_game(start=True)
    player = game.players[0]
    force_current(game)
    player.position = 39
    cash = player.cash

    game._move_by(player, 2, collect_go=True)

    assert player.position == 1
    assert player.cash == cash + 200
    game._send_to_jail(player)
    assert player.position == BOARD.space_index("jail")
    assert player.in_jail is True


def test_three_consecutive_doubles_send_player_to_jail() -> None:
    game = make_game(start=True)
    player = game.players[0]
    force_current(game)
    game._resolve_landing = lambda *args, **kwargs: None  # type: ignore[method-assign]

    for die in (1, 2, 3):
        game._roll_pair = lambda die=die: (die, die)  # type: ignore[method-assign]
        game._action_roll_dice(player, "roll_dice")
        drain_sequence(game, "monopoly_roll")

    assert player.in_jail is True
    assert player.position == BOARD.space_index("jail")


def test_jail_doubles_move_without_an_extra_roll() -> None:
    game = make_game(start=True)
    player = game.players[0]
    force_current(game)
    player.in_jail = True
    player.position = BOARD.space_index("jail")
    game.phase = PHASE_JAIL
    game.decision_player_id = player.id
    game._roll_pair = lambda: (4, 4)  # type: ignore[method-assign]

    game._action_jail_roll(player, "jail_roll")
    drain_sequence(game, "monopoly_roll")

    assert player.in_jail is False
    assert player.position == 18
    assert game.extra_roll_pending is False


def test_jailed_player_can_manage_property_and_trade_before_rolling() -> None:
    game = make_game(start=True)
    player = game.players[0]
    force_current(game)
    player.in_jail = True
    player.position = BOARD.space_index("jail")
    game.phase = PHASE_JAIL
    game.decision_player_id = player.id
    game.property_states["mediterranean"].owner_id = player.id

    assert game._is_manage_entry_enabled(player) is None
    assert game._is_propose_trade_enabled(player) is None


@pytest.mark.parametrize("touch", (False, True))
def test_manage_properties_stays_available_without_owned_property(touch: bool) -> None:
    game = make_game(start=True, touch=touch)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)

    assert game._manage_property_options(player) == []
    assert game._is_manage_entry_enabled(player) is None
    assert "manage_properties" in {
        item.action.id for item in game.get_all_enabled_actions(player)
    }
    if touch:
        assert "manage_properties" in {
            item.action.id for item in game.get_all_visible_actions(player)
        }
    user.clear_messages()

    game.execute_action(player, "manage_properties")

    assert game.phase == PHASE_AWAIT_ROLL
    assert user.get_last_spoken() == "You do not own any property to manage."


def test_optional_variations_are_opt_in_and_rules_aligned() -> None:
    game = make_game(start=True)
    player, owner = game.players[:2]
    force_current(game)

    game.options.double_salary_on_go = True
    player.position = BOARD.space_index("boardwalk")
    starting_cash = player.cash
    game._move_by(player, 1, collect_go=True)
    assert player.cash == starting_cash + 400
    assert player.passed_go_once is True

    game.options.snake_eyes_bonus = True
    cash_before_bonus = player.cash
    game._move_by = lambda *args, **kwargs: None  # type: ignore[method-assign]
    game._roll_pair = lambda: (1, 1)  # type: ignore[method-assign]
    force_current(game)
    game._action_roll_dice(player, "roll_dice")
    drain_sequence(game, "monopoly_roll")
    assert player.cash == cash_before_bonus + BOARD.snake_eyes_bonus

    game.options.no_rent_in_jail = True
    game.property_states["mediterranean"].owner_id = owner.id
    owner.in_jail = True
    player.position = BOARD.space_index("mediterranean")
    game._resolve_landing(player)
    assert game.rent_state is None
    assert game.phase == PHASE_TURN_ACTIONS


@pytest.mark.parametrize("board_id", get_board_ids())
def test_optional_variations_use_selected_board_values(board_id: str) -> None:
    game = make_game()
    game.options.board_id = board_id
    game.on_start()
    player = game.players[0]
    force_current(game)
    board = get_board(board_id)
    game._resolve_landing = lambda *args, **kwargs: None  # type: ignore[method-assign]

    game.options.double_salary_on_go = True
    player.position = len(board.spaces) - 1
    cash = player.cash
    game._move_by(player, 2, collect_go=True)
    assert player.cash == cash + board.go_salary
    player.position = len(board.spaces) - 1
    cash = player.cash
    game._move_by(player, 1, collect_go=True)
    assert player.cash == cash + board.go_salary * 2

    game.options.snake_eyes_bonus = True
    cash = player.cash
    game._award_snake_eyes_bonus(player, 1, 1)
    assert player.cash == cash + board.snake_eyes_bonus
    game._award_snake_eyes_bonus(player, 1, 2)
    assert player.cash == cash + board.snake_eyes_bonus


def test_no_rent_in_jail_changes_only_jailed_owner_rent() -> None:
    game = make_game(start=True)
    tenant, owner = game.players[:2]
    force_current(game)
    property_id = "mediterranean"
    tenant.position = BOARD.space_index(property_id)
    game.property_states[property_id].owner_id = owner.id
    owner.in_jail = True

    game.options.no_rent_in_jail = False
    game._resolve_landing(tenant)
    assert game.phase == PHASE_RENT
    assert game.rent_state is not None

    game.rent_state = None
    game.options.no_rent_in_jail = True
    game._resolve_landing(tenant)
    assert game.phase == PHASE_TURN_ACTIONS
    assert game.rent_state is None


def test_free_parking_jackpot_excludes_normal_bank_and_player_payments() -> None:
    game = make_game(start=True)
    player, owner = game.players[:2]
    force_current(game)
    game.options.free_parking_cash = True
    player.cash = 1_500

    game._start_debt(
        player,
        owner.id,
        25,
        "monopoly-debt-rent",
        continuation="finish_landing",
    )
    assert game.free_parking_pot == 0
    assert owner.cash == 1_525

    player.in_jail = True
    game.phase = PHASE_JAIL
    game.decision_player_id = player.id
    game._action_jail_pay(player, "jail_pay")
    assert game.free_parking_pot == BOARD.jail_fine


@pytest.mark.parametrize("board_id", get_board_ids())
def test_get_out_of_jail_card_returns_to_its_deck_exactly_once(board_id: str) -> None:
    game = make_game()
    game.options.board_id = board_id
    game.on_start()
    drain_sequence(game, "monopoly_intro")
    player = game.players[0]
    force_current(game)
    card_id = "chance_jail_free"
    game.chance_deck.remove(card_id)
    player.jail_card_ids = [card_id]
    player.in_jail = True
    game.phase = PHASE_JAIL
    game.decision_player_id = player.id

    game._action_jail_card(player, "jail_card")

    assert player.jail_card_ids == []
    assert game.chance_deck.count(card_id) == 1
    assert len(game.chance_deck) == len(game.board.chance_cards)


def test_pass_go_before_buying_filters_purchase_and_auction_eligibility() -> None:
    game = make_game(start=True)
    player, other = game.players[:2]
    force_current(game)
    game.options.buy_after_passing_go = True
    player.position = BOARD.space_index("mediterranean")
    user = game.get_user(player)
    assert user is not None
    portfolio = game._build_my_portfolio_status(player, user)
    assert any("buying-eligibility" in item.id for item in portfolio.items)

    game._resolve_landing(player)

    assert game.phase == PHASE_TURN_ACTIONS
    assert game.auction_state is None
    assert game.property_states["mediterranean"].owner_id == ""

    other.passed_go_once = True
    player.position = BOARD.space_index("baltic")
    game._resolve_landing(player)

    assert game.phase == PHASE_AUCTION
    assert game.auction_state is not None
    assert game.auction_state.bidder_ids == [other.id]


def test_free_parking_jackpot_tracks_only_penalties_and_clears_on_collection() -> None:
    game = make_game(start=True)
    player = game.players[0]
    force_current(game)
    game.options.free_parking_cash = True
    player.cash = 1_000

    game._start_debt(
        player, "", 200, "monopoly-debt-tax", continuation="finish_landing"
    )
    assert player.cash == 800
    assert game.free_parking_pot == 200

    player.position = BOARD.space_index("free_parking")
    game._resolve_landing(player)

    assert player.cash == 1_000
    assert game.free_parking_pot == 0


def test_brief_announcements_are_selected_per_listener() -> None:
    game = make_game(start=True)
    actor, observer = game.players[:2]
    actor_user = game.get_user(actor)
    observer_user = game.get_user(observer)
    assert actor_user is not None and observer_user is not None
    actor_user.preferences.set_game_override("brief_announcements", "monopoly", True)
    actor_user.clear_messages()
    observer_user.clear_messages()
    force_current(game)
    game._move_by = lambda *args, **kwargs: None  # type: ignore[method-assign]
    game._roll_pair = lambda: (3, 4)  # type: ignore[method-assign]

    game._action_roll_dice(actor, "roll_dice")

    assert actor_user.get_last_spoken() == "You: 7."
    assert "3 and 4, totaling 7" in observer_user.get_last_spoken()


def test_brief_purchase_omits_group_and_remaining_cash() -> None:
    game = make_game(start=True)
    buyer = game.players[0]
    user = game.get_user(buyer)
    assert user is not None
    user.preferences.set_game_override("brief_announcements", "monopoly", True)
    force_current(game)
    buyer.position = BOARD.space_index("mediterranean")
    game._resolve_landing(buyer)
    user.clear_messages()

    game._action_buy_property(buyer, "buy_property")

    assert user.get_last_spoken() == "You bought Mediterranean Avenue for $60."


def test_brief_movement_announces_only_the_localized_destination() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    user.preferences.set_game_override("brief_announcements", "monopoly", True)
    user.clear_messages()

    game._announce_move(player, BOARD.space_index("illinois"), 7)

    assert user.get_last_spoken() == "Illinois Avenue."


def test_brief_mode_omits_redundant_no_effect_landing_message() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    user.preferences.set_game_override("brief_announcements", "monopoly", True)
    player.position = BOARD.space_index("free_parking")
    user.clear_messages()

    game._announce_move(player, player.position, 5)
    game._resolve_landing(player)

    assert user.get_last_spoken() == "Free Parking."


def test_unowned_property_purchase_and_decline_auction() -> None:
    game = make_game(start=True)
    buyer = game.players[0]
    force_current(game)
    buyer.position = BOARD.space_index("mediterranean")
    game._resolve_landing(buyer)
    assert game.phase == PHASE_PROPERTY

    game._action_buy_property(buyer, "buy_property")
    assert game.property_states["mediterranean"].owner_id == buyer.id
    assert buyer.cash == 1_440

    buyer.position = BOARD.space_index("baltic")
    game._resolve_landing(buyer)
    game._action_decline_property(buyer, "decline_property")
    assert game.phase == PHASE_AUCTION
    assert game.auction_state is not None
    assert game.auction_state.property_id == "baltic"


def test_auction_allows_declining_player_and_finishes_at_high_bid() -> None:
    game = make_game(start=True)
    first, second = game.players[:2]
    force_current(game)
    game._start_auction(
        "mediterranean", resume_kind="landing", first_bidder_id=first.id
    )

    game._action_place_bid(first, "20", "place_bid")
    assert game.decision_player_id == second.id
    game._action_place_bid(second, "25", "place_bid")
    assert game.decision_player_id == first.id
    game._action_pass_auction(first, "pass_auction")

    assert game.auction_state is None
    assert game.property_states["mediterranean"].owner_id == second.id
    assert second.cash == 1_475


def test_auction_offers_minimum_bid_before_custom_bid() -> None:
    game = make_game(start=True, touch=True)
    first, second = game.players[:2]
    force_current(game)
    game._start_auction(
        "mediterranean", resume_kind="landing", first_bidder_id=first.id
    )

    turn_actions = game.get_action_set(first, "turn")
    assert turn_actions is not None
    assert turn_actions._order.index("bid_minimum") < turn_actions._order.index(
        "place_bid"
    )

    game._action_bid_minimum(first, "bid_minimum")

    assert game.auction_state is not None
    assert game.auction_state.highest_bid == 1
    assert game.auction_state.highest_bidder_id == first.id
    assert game.decision_player_id == second.id


def test_auction_controls_persist_disabled_and_update_for_active_bidders() -> None:
    game = make_game(3, start=True, touch=True)
    first, second, third = game.players
    first_user = game.get_user(first)
    third_user = game.get_user(third)
    assert first_user is not None and third_user is not None
    force_current(game)
    game.property_states["reading_railroad"].owner_id = first.id
    game._start_auction(
        "mediterranean",
        resume_kind="landing",
        first_bidder_id=first.id,
    )
    game.flush_menus()

    auction_action_ids = {"bid_minimum", "place_bid", "pass_auction"}

    def auction_actions(player):
        action_set = game.get_action_set(player, "turn")
        assert action_set is not None
        return {
            resolved.action.id: resolved
            for resolved in action_set.get_visible_actions(game, player)
            if resolved.action.id in auction_action_ids
        }

    for player in (first, second, third):
        assert set(auction_actions(player)) == auction_action_ids
    assert all(item.enabled for item in auction_actions(first).values())
    assert not any(item.enabled for item in auction_actions(second).values())
    assert not any(item.enabled for item in auction_actions(third).values())

    game.handle_event(
        first,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "bid_minimum",
        },
    )

    assert game.auction_state is not None
    assert game.auction_state.highest_bid == 1
    assert game.decision_player_id == second.id
    assert not any(item.enabled for item in auction_actions(first).values())
    assert all(item.enabled for item in auction_actions(second).values())
    assert first_user.menus["turn_menu"]["selection_id"] == "bid_minimum"
    assert "$2" in auction_actions(first)["bid_minimum"].label

    third_user.clear_messages()
    game.handle_event(
        third,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "bid_minimum",
        },
    )
    assert game.auction_state.highest_bid == 1
    assert game.decision_player_id == second.id
    assert second.name in third_user.get_last_spoken()

    for bidder in (second, third):
        game.handle_event(
            bidder,
            {
                "type": "menu",
                "menu_id": "turn_menu",
                "selection_id": "bid_minimum",
            },
        )
    assert game.decision_player_id == first.id
    assert all(item.enabled for item in auction_actions(first).values())

    game.handle_event(
        first,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "manage_properties",
        },
    )
    assert game.phase == PHASE_MANAGE
    for player in (first, second, third):
        assert set(auction_actions(player)) == auction_action_ids
        assert not any(item.enabled for item in auction_actions(player).values())

    game.handle_event(
        first,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "finish_management",
        },
    )
    game.handle_event(
        first,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "pass_auction",
        },
    )
    assert game.auction_state is not None
    assert first.id not in game.auction_state.active_bidder_ids
    assert auction_actions(first) == {}
    assert set(auction_actions(second)) == auction_action_ids
    assert set(auction_actions(third)) == auction_action_ids


def test_auction_input_blocks_stale_underlying_turn_menu_events() -> None:
    game = make_game(start=True, touch=True)
    bidder = game.players[0]
    game._start_auction(
        "mediterranean",
        resume_kind="landing",
        first_bidder_id=bidder.id,
    )
    game.flush_menus()

    game.handle_event(
        bidder,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "place_bid",
        },
    )
    assert game._pending_actions[bidder.id] == "place_bid"
    user = game.get_user(bidder)
    assert user is not None
    user.clear_messages()

    game.handle_event(
        bidder,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "pass_auction",
        },
    )

    assert game.auction_state is not None
    assert bidder.id in game.auction_state.active_bidder_ids
    assert game.decision_player_id == bidder.id
    assert game._pending_actions[bidder.id] == "place_bid"
    assert any(
        message.type == "show_editbox"
        and message.data.get("input_id") == "action_input_editbox"
        for message in user.messages
    )


def test_obsolete_auction_input_is_dismissed_before_property_menu_repaint() -> None:
    game = make_game(start=True, touch=True)
    bidder = game.players[0]
    user = game.get_user(bidder)
    assert user is not None
    game._start_auction(
        "mediterranean",
        resume_kind="landing",
        first_bidder_id=bidder.id,
    )
    game.flush_menus()
    game.handle_event(
        bidder,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "place_bid",
        },
    )
    assert "action_input_editbox" in user.editboxes
    user.clear_messages()

    # Simulate a public transition superseding an input while its client packet
    # is still in flight. The next framework flush must not leave that player on
    # the old auction UI forever.
    game.auction_state = None
    game.pending_property_id = "baltic"
    game.phase = PHASE_PROPERTY
    game.decision_player_id = bidder.id
    game.refresh_menus()
    game.flush_menus()

    assert bidder.id not in game._pending_actions
    assert "action_input_editbox" not in user.editboxes
    item_ids = [item.id for item in user.get_current_menu_items("turn_menu") or []]
    assert "buy_property" in item_ids
    assert "decline_property" in item_ids
    assert "pass_auction" not in item_ids
    message_types = [message.type for message in user.messages]
    assert message_types.index("remove_editbox") < message_types.index("show_menu")


def test_stale_auction_button_resyncs_current_property_prompt() -> None:
    game = make_game(start=True, touch=True)
    buyer = game.players[0]
    user = game.get_user(buyer)
    assert user is not None
    game.auction_state = None
    game.pending_property_id = "baltic"
    game.phase = PHASE_PROPERTY
    game.decision_player_id = buyer.id
    game.refresh_menus(buyer)
    game.flush_menus()
    user.clear_messages()

    game.handle_event(
        buyer,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection": 2,
            "selection_id": "pass_auction",
        },
    )

    assert game.phase == PHASE_PROPERTY
    assert game.pending_property_id == "baltic"
    assert game.decision_player_id == buyer.id
    item_ids = [item.id for item in user.get_current_menu_items("turn_menu") or []]
    assert "buy_property" in item_ids
    assert "decline_property" in item_ids
    assert "pass_auction" not in item_ids
    assert any(
        message.type == "show_menu"
        and message.data.get("menu_id") == "turn_menu"
        for message in user.messages
    )


def test_auction_turn_is_announced_to_bidder_and_observer() -> None:
    game = make_game(start=True)
    bidder, observer = game.players[:2]
    bidder_user = game.get_user(bidder)
    observer_user = game.get_user(observer)
    assert bidder_user is not None and observer_user is not None
    bidder_user.clear_messages()
    observer_user.clear_messages()

    game._start_auction(
        "baltic",
        resume_kind="landing",
        first_bidder_id=bidder.id,
    )

    assert "Your auction turn for Baltic Avenue" in bidder_user.get_last_spoken()
    assert (
        f"{bidder.name} is next to bid on Baltic Avenue"
        in observer_user.get_last_spoken()
    )


def test_active_bidder_can_mortgage_before_bidding_but_cannot_trade() -> None:
    game = make_game(start=True)
    bidder = game.players[0]
    force_current(game)
    game.property_states["reading_railroad"].owner_id = bidder.id
    game._start_auction(
        "mediterranean", resume_kind="landing", first_bidder_id=bidder.id
    )

    assert game._is_manage_entry_enabled(bidder) is None
    assert (
        game._is_propose_trade_enabled(bidder)
        == "monopoly-error-no-trade-during-auction"
    )
    game._action_manage_properties(bidder, "manage_properties")
    game._action_choose_managed_property(
        bidder, "reading_railroad", "choose_managed_property"
    )
    game._action_mortgage(bidder, "mortgage")
    game._action_finish_management(bidder, "finish_management")

    assert game.phase == PHASE_AUCTION
    assert game.decision_player_id == bidder.id
    assert game.property_states["reading_railroad"].mortgaged is True
    assert bidder.cash == BOARD.starting_cash + 100


def test_turn_menu_keeps_a_stable_roll_anchor_for_every_active_player() -> None:
    game = make_game(start=True, touch=True)
    first, second = game.players[:2]
    game.phase = PHASE_RENT
    game.decision_player_id = second.id

    for player in (first, second):
        game.before_menu_build(player)
        action_set = game.get_action_set(player, "turn")
        assert action_set is not None
        visible = action_set.get_visible_actions(game, player)
        assert visible
        assert visible[0].action.id == "roll_dice"
        assert visible[0].enabled is False
    owner_turn = game.get_action_set(second, "turn")
    assert owner_turn is not None
    owner_visible = owner_turn.get_visible_actions(game, second)
    assert [item.action.id for item in owner_visible[1:3]] == [
        "claim_rent",
        "waive_rent",
    ]


def test_user_transition_focuses_first_phase_action_without_moving_others() -> None:
    game = make_game(start=True, touch=True)
    actor, observer = game.players[:2]
    actor_user = game.get_user(actor)
    observer_user = game.get_user(observer)
    assert actor_user is not None and observer_user is not None
    force_current(game)
    game._roll_pair = lambda: (1, 2)  # type: ignore[method-assign]
    actor_user.clear_messages()
    observer_user.clear_messages()

    game._action_roll_dice(actor, "roll_dice")
    drain_sequence(game, "monopoly_roll")
    game.flush_menus()

    actor_turn_packets = [
        message
        for message in actor_user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    observer_turn_packets = [
        message
        for message in observer_user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert game.phase == PHASE_PROPERTY
    assert actor_turn_packets[-1].data["selection_id"] == "buy_property"
    assert observer_turn_packets[-1].data["selection_id"] is None

    actor_user.clear_messages()
    game._action_decline_property(actor, "decline_property")
    game.flush_menus()
    actor_turn_packets = [
        message
        for message in actor_user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert actor_turn_packets[-1].data["selection_id"] == "bid_minimum"


def test_property_management_root_focuses_first_task_without_moving_observers() -> None:
    game = make_game(start=True, touch=True)
    player, observer = game.players[:2]
    user = game.get_user(player)
    observer_user = game.get_user(observer)
    assert user is not None and observer_user is not None
    force_current(game)
    game.property_states["new_york"].owner_id = player.id
    user.clear_messages()
    observer_user.clear_messages()

    game._action_manage_properties(player, "manage_properties")
    game.flush_menus()

    assert game.phase == PHASE_MANAGE
    assert game.management_property_id == ""
    turn_packets = [
        message
        for message in user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    observer_packets = [
        message
        for message in observer_user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert turn_packets[-1].data["selection_id"] == "choose_build_property"
    assert observer_packets[-1].data["selection_id"] is None


def test_property_inspection_focuses_build_even_when_build_is_disabled() -> None:
    game = make_game(start=True, touch=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    game.property_states["new_york"].owner_id = player.id
    game._action_manage_properties(player, "manage_properties")
    user.clear_messages()

    game._action_choose_managed_property(player, "new_york", "choose_managed_property")
    assert game._is_build_enabled(player) == "monopoly-error-need-color-set"
    game.flush_menus()

    turn_packets = [
        message
        for message in user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert turn_packets[-1].data["selection_id"] == "build"


def test_nonstreet_management_hides_building_actions_and_focuses_mortgage() -> None:
    game = make_game(start=True, touch=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    game.property_states["reading_railroad"].owner_id = player.id
    user.clear_messages()

    game._action_manage_properties(player, "manage_properties")
    game._action_choose_managed_property(
        player, "reading_railroad", "choose_managed_property"
    )
    game.flush_menus()

    turn_packets = [
        message
        for message in user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    packet = turn_packets[-1]
    assert packet.data["selection_id"] == "mortgage"
    item_ids = {item.id for item in packet.data["items"]}
    assert not {"build", "sell_building", "sell_group_buildings"} & item_ids


@pytest.mark.parametrize(
    ("phase", "expected"),
    (
        (PHASE_AWAIT_ROLL, "roll_dice"),
        (PHASE_PROPERTY, "buy_property"),
        (PHASE_RENT, "claim_rent"),
        (PHASE_AUCTION, "bid_minimum"),
        (PHASE_JAIL, "jail_roll"),
        (PHASE_DEBT, "pay_debt"),
        (PHASE_TRADE_BUILD, "trade_offer_property"),
        (PHASE_TRADE_RESPONSE, "trade_review"),
        (PHASE_MORTGAGE_TRANSFER, "keep_received_mortgaged"),
        (PHASE_TURN_ACTIONS, "roll_dice"),
    ),
)
def test_every_user_opened_phase_has_a_semantic_first_focus(
    phase: str, expected: str
) -> None:
    game = make_game(start=True, touch=True)
    player, other = game.players[:2]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    game.phase = phase
    game.decision_player_id = player.id
    if phase == PHASE_PROPERTY:
        game.pending_property_id = "mediterranean"
    elif phase == PHASE_RENT:
        game.rent_state = RentState(other.id, player.id, "mediterranean", 2)
    elif phase == PHASE_AUCTION:
        game.auction_state = AuctionState(
            "mediterranean",
            bidder_ids=[player.id, other.id],
            active_bidder_ids=[player.id, other.id],
        )
    elif phase == PHASE_JAIL:
        player.in_jail = True
    elif phase == PHASE_DEBT:
        player.cash = 0
        game.debt_state = DebtState(player.id, "", 100, "monopoly-debt-tax")
    elif phase == PHASE_TRADE_BUILD:
        game.trade_state = TradeState(player.id, other.id)
    elif phase == PHASE_TRADE_RESPONSE:
        game.trade_state = TradeState(other.id, player.id, submitted=True)
    elif phase == PHASE_MORTGAGE_TRANSFER:
        game.property_states["mediterranean"] = PropertyState(player.id, True, 0)
        game.mortgage_transfer_state = MortgageTransferState(
            property_ids=["mediterranean"]
        )
    user.clear_messages()

    game._focus_after_user_transition(player)
    game.flush_menus()

    turn_packets = [
        message
        for message in user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert turn_packets[-1].data["selection_id"] == expected


def test_automatic_required_action_change_never_forces_focus() -> None:
    game = make_game(start=True, touch=True)
    first = game.players[0]
    first_user = game.get_user(first)
    assert first_user is not None
    first_user.clear_messages()

    game._start_auction(
        "mediterranean", resume_kind="landing", first_bidder_id=first.id
    )
    game.flush_menus()

    turn_packets = [
        message
        for message in first_user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert turn_packets[-1].data["selection_id"] is None


def test_user_opened_selection_menus_explicitly_focus_the_first_item() -> None:
    lobby_game = make_game()
    host = lobby_game.players[0]
    host_user = lobby_game.get_user(host)
    assert host_user is not None

    lobby_game.execute_action(host, "set_board_id")

    assert host_user.menus["action_input_menu"]["selection_id"] == "standard"
    assert [
        item.id
        for item in host_user.menus["action_input_menu"]["items"]
        if item.id != "_cancel"
    ] == [
        "standard",
        "australia",
        "germany",
        "hanoi",
        "italy",
        "london",
        "madrid",
        "new_zealand",
        "paris",
        "tokyo",
    ]
    assert any(
        "United States" in item.text
        for item in host_user.menus["action_input_menu"]["items"]
    )
    assert any(
        "London" in item.text for item in host_user.menus["action_input_menu"]["items"]
    )
    assert any(
        "Paris" in item.text for item in host_user.menus["action_input_menu"]["items"]
    )
    assert any(
        "Germany" in item.text for item in host_user.menus["action_input_menu"]["items"]
    )
    assert any(
        "Italy" in item.text for item in host_user.menus["action_input_menu"]["items"]
    )
    assert any(
        "Madrid" in item.text for item in host_user.menus["action_input_menu"]["items"]
    )
    assert any(
        "Tokyo" in item.text for item in host_user.menus["action_input_menu"]["items"]
    )
    assert any(
        "Australia" in item.text
        for item in host_user.menus["action_input_menu"]["items"]
    )
    board_items = {
        item.id: item for item in host_user.menus["action_input_menu"]["items"]
    }
    assert board_items["standard"].description == (
        "Atlantic City properties, US dollars, and railroads."
    )
    assert board_items["madrid"].description == ("Madrid streets, euros, and stations.")
    assert board_items["tokyo"].description == (
        "Tokyo districts, Monopoly dollars, and stations."
    )
    assert board_items["australia"].description == (
        "Australian capital-city streets, Australian dollars, and stations."
    )
    assert board_items["new_zealand"].description == (
        "Streets across New Zealand, New Zealand dollars, and stations."
    )
    assert board_items["hanoi"].description == (
        "Hanoi streets and businesses, Vietnamese đồng, bus stations, and landmarks."
    )
    lobby_game.handle_event(
        host,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection_id": "london",
        },
    )
    assert lobby_game.options.board_id == "london"

    game = make_game(start=True)
    player, target = game.players[:2]
    force_current(game)
    user = game.get_user(player)
    assert user is not None

    game.execute_action(player, "propose_trade")

    assert user.menus["action_input_menu"]["selection_id"] == target.id


def test_board_menu_sorts_regional_boards_by_the_viewers_localized_names() -> None:
    game = make_game()
    host = game.players[0]
    user = game.get_user(host)
    assert user is not None
    user._locale = "vi"

    game.execute_action(host, "set_board_id")

    menu = user.menus["action_input_menu"]
    assert menu["selection_id"] == "standard"
    assert [item.id for item in menu["items"] if item.id != "_cancel"] == [
        "standard",
        "germany",
        "hanoi",
        "london",
        "madrid",
        "new_zealand",
        "paris",
        "tokyo",
        "australia",
        "italy",
    ]


def test_stale_trade_target_keeps_updated_target_prompt_open() -> None:
    game = make_game(player_count=3, start=True)
    proposer, stale_target, current_target = game.players
    force_current(game)
    user = game.get_user(proposer)
    assert user is not None

    game.execute_action(proposer, "propose_trade")
    assert game._pending_actions[proposer.id] == "propose_trade"

    stale_target.bankrupt = True
    user.clear_messages()
    game.handle_event(
        proposer,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection_id": stale_target.id,
        },
    )

    assert game.trade_state is None
    assert game._pending_actions[proposer.id] == "propose_trade"
    assert [
        item.id
        for item in user.get_current_menu_items("action_input_menu") or []
    ] == [current_target.id, "_cancel"]


def test_portfolio_player_prompt_refreshes_cash_without_reopening_or_refocusing() -> None:
    game = make_game(player_count=3, start=True)
    viewer, owner = game.players[:2]
    user = game.get_user(viewer)
    assert user is not None

    game.execute_action(viewer, "read_portfolios")
    assert game._pending_actions[viewer.id] == "read_portfolios"
    original = next(
        item.text
        for item in user.menus["action_input_menu"]["items"]
        if item.id == owner.id
    )
    owner.cash += 275
    user.clear_messages()

    game.refresh_menus(viewer)
    game.flush_menus()

    assert game._pending_actions[viewer.id] == "read_portfolios"
    refreshed = next(
        item.text
        for item in user.menus["action_input_menu"]["items"]
        if item.id == owner.id
    )
    assert refreshed != original
    assert "cash: $1,775" in refreshed
    prompt_packets = [
        message
        for message in user.messages
        if message.type == "show_menu"
        and message.data.get("menu_id") == "action_input_menu"
    ]
    assert prompt_packets[-1].data["selection_id"] is None


def test_property_management_selector_refreshes_live_cash_without_losing_state() -> None:
    game = make_game(start=True, touch=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    own_group(game, player.id, "brown")
    game._action_manage_properties(player, "manage_properties")

    game.execute_action(player, "choose_build_property")
    assert game._pending_actions[player.id] == "choose_build_property"
    player.cash -= 100
    user.clear_messages()

    game.refresh_menus(player)
    game.flush_menus()

    assert game.phase == PHASE_MANAGE
    assert game._pending_actions[player.id] == "choose_build_property"
    options = [
        item.text
        for item in user.menus["action_input_menu"]["items"]
        if item.id != "_cancel"
    ]
    assert options
    assert all("cash $1,400" in option for option in options)
    prompt_packets = [
        message
        for message in user.messages
        if message.type == "show_menu"
        and message.data.get("menu_id") == "action_input_menu"
    ]
    assert prompt_packets[-1].data["selection_id"] is None


def test_trade_target_prompt_locks_gameplay_until_explicit_cancel() -> None:
    game = make_game(player_count=3, start=True)
    current, proposer = game.players[:2]
    current_user = game.get_user(current)
    proposer_user = game.get_user(proposer)
    assert current_user is not None and proposer_user is not None
    force_current(game)

    game.execute_action(proposer, "propose_trade")

    assert game._pending_actions[proposer.id] == "propose_trade"
    assert game._is_roll_enabled(current) == (
        "monopoly-error-trade-partner-selection-player",
        {"player": proposer.name},
    )
    current_user.clear_messages()
    game.handle_event(
        current,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "roll_dice",
        },
    )

    assert not game.has_active_sequence(tag="monopoly_roll")
    assert game._pending_actions[proposer.id] == "propose_trade"
    assert "action_input_menu" in proposer_user.menus
    assert current_user.get_last_spoken() == (
        f"Waiting for {proposer.name} to choose a trade partner."
    )

    game.handle_event(
        proposer,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection_id": "_cancel",
        },
    )

    assert proposer.id not in game._pending_actions
    assert game._is_roll_enabled(current) is None


def test_legacy_save_migrates_trade_target_gameplay_lock() -> None:
    game = make_game(start=True)
    for player in game.get_active_players():
        action = game.find_action(player, "propose_trade")
        assert action is not None
        assert isinstance(action.input_request, MenuInput)
        action.input_request.locks_gameplay = False

    restored = MonopolyGame.from_json(game.to_json())
    restored.rebuild_runtime_state()

    for player in restored.get_active_players():
        action = restored.find_action(player, "propose_trade")
        assert action is not None
        assert isinstance(action.input_request, MenuInput)
        assert action.input_request.locks_gameplay is True


def test_trade_target_lock_is_released_when_prompt_owner_becomes_a_bot() -> None:
    game = make_game(player_count=3, start=True)
    current, proposer = game.players[:2]
    force_current(game)

    game.execute_action(proposer, "propose_trade")
    game._menu_dirty_all = False
    game._menu_dirty.clear()

    assert game._replace_with_bot(proposer)

    assert proposer.id not in game._pending_actions
    assert game._gameplay_input_lock_owner() is None
    assert game._is_roll_enabled(current) is None
    assert game._menu_dirty_all is True


def test_property_detail_can_return_to_full_list_without_leaving_management() -> None:
    game = make_game(start=True, touch=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    game.property_states["new_york"].owner_id = player.id
    game.property_states["reading_railroad"].owner_id = player.id
    game._action_manage_properties(player, "manage_properties")
    game._action_choose_managed_property(player, "new_york", "choose_managed_property")

    game.before_menu_build(player)
    action_set = game.get_action_set(player, "turn")
    assert action_set is not None
    detail_ids = [
        item.action.id for item in action_set.get_visible_actions(game, player)
    ]
    assert "back_to_property_list" in detail_ids
    assert "choose_managed_property" not in detail_ids
    assert not {
        "choose_build_property",
        "choose_sell_property",
        "choose_mortgage_property",
        "choose_unmortgage_property",
    } & set(detail_ids)

    game.execute_action(player, "back_to_property_list")

    assert user.menus["action_input_menu"]["selection_id"] == "reading_railroad"
    assert [
        item.id
        for item in user.menus["action_input_menu"]["items"]
        if item.id != "_cancel"
    ] == ["reading_railroad", "new_york"]
    user.clear_messages()
    game.handle_event(
        player,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection_id": "reading_railroad",
        },
    )

    assert game.phase == PHASE_MANAGE
    assert game.management_property_id == "reading_railroad"
    assert "Managing Reading Railroad" in user.get_last_spoken()
    turn_packets = [
        message
        for message in user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert turn_packets[-1].data["selection_id"] == "mortgage"


def test_single_property_detail_still_offers_back_to_property_list() -> None:
    game = make_game(start=True, touch=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    game.property_states["reading_railroad"].owner_id = player.id
    game._action_manage_properties(player, "manage_properties")
    game._action_choose_managed_property(
        player, "reading_railroad", "choose_managed_property"
    )

    game.execute_action(player, "back_to_property_list")

    menu = user.menus["action_input_menu"]
    assert menu["selection_id"] == "reading_railroad"
    assert [item.id for item in menu["items"]] == ["reading_railroad", "_cancel"]


def test_management_workspace_groups_tasks_and_filters_legal_properties() -> None:
    game = make_game(start=True, touch=True)
    player = game.players[0]
    force_current(game)
    own_group(game, player.id, "brown")
    game.property_states["reading_railroad"].owner_id = player.id
    game._action_manage_properties(player, "manage_properties")

    game.before_menu_build(player)
    action_set = game.get_action_set(player, "turn")
    assert action_set is not None
    visible = action_set.get_visible_actions(game, player)
    assert [item.action.id for item in visible[:7]] == [
        "roll_dice",
        "choose_build_property",
        "choose_sell_property",
        "choose_mortgage_property",
        "choose_unmortgage_property",
        "choose_managed_property",
        "finish_management",
    ]
    enabled = {item.action.id: item.enabled for item in visible}
    assert enabled["choose_build_property"] is True
    assert enabled["choose_sell_property"] is False
    assert enabled["choose_mortgage_property"] is True
    assert enabled["choose_unmortgage_property"] is False
    assert game._build_property_options(player) == ["mediterranean", "baltic"]
    assert game._mortgage_property_options(player) == [
        "mediterranean",
        "baltic",
        "reading_railroad",
    ]


def test_build_workspace_tracks_even_building_and_focuses_confirmation() -> None:
    game = make_game(start=True, touch=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    own_group(game, player.id, "brown")
    game._action_manage_properties(player, "manage_properties")

    game.execute_action(player, "choose_build_property")

    menu = user.menus["action_input_menu"]
    assert menu["selection_id"] == "mediterranean"
    assert [item.id for item in menu["items"][:-1]] == ["mediterranean", "baltic"]
    assert menu["items"][-1].id == "_cancel"
    assert "house for $50" in menu["items"][0].text
    user.clear_messages()
    game.handle_event(
        player,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection_id": "mediterranean",
        },
    )

    assert game.management_property_id == "mediterranean"
    turn_packets = [
        message
        for message in user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert turn_packets[-1].data["selection_id"] == "build"
    user.clear_messages()
    game._action_build(player, "build")
    game.flush_menus()

    assert game.property_states["mediterranean"].buildings == 1
    assert game._build_property_options(player) == ["baltic"]
    turn_packets = [
        message
        for message in user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert turn_packets[-1].data["selection_id"] == "choose_build_property"
    game.execute_action(player, "choose_build_property")
    assert user.menus["action_input_menu"]["selection_id"] == "baltic"


def test_management_sale_and_mortgage_tasks_track_changing_eligibility() -> None:
    game = make_game(start=True)
    player = game.players[0]
    force_current(game)
    own_group(game, player.id, "brown")
    game.property_states["reading_railroad"] = PropertyState(player.id, True, 0)
    game.property_states["mediterranean"].buildings = 2
    game.property_states["baltic"].buildings = 1
    game.bank_houses -= 3
    game._action_manage_properties(player, "manage_properties")

    assert game._sell_property_options(player) == ["mediterranean"]
    assert game._mortgage_property_options(player) == []
    assert game._unmortgage_property_options(player) == ["reading_railroad"]

    game._action_choose_management_property(
        player, "mediterranean", "choose_sell_property"
    )
    game._action_sell_building(player, "sell_building")

    assert game.property_states["mediterranean"].buildings == 1
    assert game._sell_property_options(player) == ["mediterranean", "baltic"]
    game._action_choose_management_property(
        player, "reading_railroad", "choose_unmortgage_property"
    )
    game._action_unmortgage(player, "unmortgage")
    assert game.property_states["reading_railroad"].mortgaged is False
    assert "reading_railroad" in game._mortgage_property_options(player)


def test_sell_workspace_exposes_safe_group_liquidation_during_hotel_shortage() -> None:
    game = make_game(start=True, touch=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    own_group(game, player.id, "brown")
    for property_id in ("mediterranean", "baltic"):
        game.property_states[property_id].buildings = 5
    game.bank_houses = 0
    game.bank_hotels = 10
    game._action_manage_properties(player, "manage_properties")

    assert game._sell_property_options(player) == ["group:brown"]
    game.execute_action(player, "choose_sell_property")
    menu = user.menus["action_input_menu"]
    assert menu["selection_id"] == "group:brown"
    assert "brown color group" in menu["items"][0].text
    user.clear_messages()
    game.handle_event(
        player,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection_id": "group:brown",
        },
    )

    assert game.property_states["mediterranean"].buildings == 5
    assert game.property_states["baltic"].buildings == 5
    turn_packets = [
        message
        for message in user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert turn_packets[-1].data["selection_id"] == "sell_group_buildings"
    game._action_sell_group_buildings(player, "sell_group_buildings")
    assert game.property_states["mediterranean"].buildings == 0
    assert game.property_states["baltic"].buildings == 0
    assert game.bank_hotels == 12


def test_management_selector_rejects_a_stale_or_forged_property() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    own_group(game, player.id, "brown")
    game._action_manage_properties(player, "manage_properties")
    user.clear_messages()

    game._action_choose_management_property(
        player, "boardwalk", "choose_build_property"
    )

    assert game.management_property_id == ""
    assert user.get_last_spoken() == (
        "That property is no longer eligible for the selected management action. "
        "Review the updated choices."
    )


def test_rent_math_for_sets_transit_utilities_and_mortgage() -> None:
    states = {
        space.id: PropertyState()
        for space in BOARD.spaces
        if space.kind in {"street", "transit", "utility"}
    }
    states["mediterranean"].owner_id = "p1"
    states["baltic"].owner_id = "p1"
    assert calculate_rent(BOARD, states, BOARD.space("mediterranean"), 7) == 4
    states["mediterranean"].buildings = 3
    assert calculate_rent(BOARD, states, BOARD.space("mediterranean"), 7) == 90
    states["mediterranean"].mortgaged = True
    assert calculate_rent(BOARD, states, BOARD.space("mediterranean"), 7) == 0

    for transit in BOARD.group_spaces("transit")[:3]:
        states[transit.id].owner_id = "p1"
    assert calculate_rent(BOARD, states, BOARD.space("reading_railroad"), 7) == 100
    for utility in BOARD.group_spaces("utility"):
        states[utility.id].owner_id = "p1"
    assert calculate_rent(BOARD, states, BOARD.space("electric_company"), 7) == 70
    assert (
        calculate_rent(
            BOARD,
            states,
            BOARD.space("electric_company"),
            8,
            rent_multiplier=10,
            utility_override=True,
        )
        == 80
    )

    custom_rules = replace(
        BOARD.rules,
        utility_single_multiplier=5,
        utility_complete_group_multiplier=12,
    )
    custom_board = replace(BOARD, rules=custom_rules)
    assert (
        calculate_rent(custom_board, states, custom_board.space("electric_company"), 7)
        == 84
    )

    hanoi_states = {
        space.id: PropertyState()
        for space in HANOI_BOARD.spaces
        if space.kind in {"street", "transit", "utility"}
    }
    hanoi_states["one_pillar_pagoda"].owner_id = "p1"
    assert (
        calculate_rent(
            HANOI_BOARD,
            hanoi_states,
            HANOI_BOARD.space("one_pillar_pagoda"),
            7,
        )
        == 28_000
    )
    hanoi_states["long_bien_bridge"].owner_id = "p1"
    assert (
        calculate_rent(
            HANOI_BOARD,
            hanoi_states,
            HANOI_BOARD.space("one_pillar_pagoda"),
            7,
        )
        == 70_000
    )
    assert (
        calculate_rent(
            HANOI_BOARD,
            hanoi_states,
            HANOI_BOARD.space("one_pillar_pagoda"),
            8,
            rent_multiplier=10,
            utility_override=True,
        )
        == 80_000
    )


@pytest.mark.parametrize("owner_is_bot", [False, True])
def test_hanoi_landmark_rent_roll_is_scaled_equally_for_human_and_bot_owners(
    owner_is_bot: bool,
) -> None:
    game = make_game()
    game.options.board_id = "hanoi"
    game.on_start()
    drain_sequence(game, "monopoly_intro")
    tenant, owner = game.players[:2]
    tenant_user = game.get_user(tenant)
    owner_user = game.get_user(owner)
    assert tenant_user is not None and owner_user is not None
    owner.is_bot = owner_is_bot
    force_current(game)
    own_group(game, owner.id, "utility")
    tenant.position = HANOI_BOARD.space_index("one_pillar_pagoda")
    game.last_die_1 = 6
    game.last_die_2 = 6
    game._roll_pair = lambda: (3, 4)  # type: ignore[method-assign]
    tenant_user.clear_messages()
    owner_user.clear_messages()

    game._resolve_landing(tenant)

    assert game.has_active_sequence(tag="monopoly_utility_rent")
    assert game.rent_state is None
    assert tenant_user.get_last_spoken() == (
        "Your new landmark rent roll is 3 and 4, totaling 7."
    )
    assert owner_user.get_last_spoken() == (
        f"{tenant.name}'s new landmark rent roll is 3 and 4, totaling 7."
    )
    assert (game.last_die_1, game.last_die_2) == (3, 4)

    drain_sequence(game, "monopoly_utility_rent")

    assert game.phase == PHASE_RENT
    assert game.decision_player_id == owner.id
    assert game.rent_state == RentState(
        tenant_id=tenant.id,
        owner_id=owner.id,
        property_id="one_pillar_pagoda",
        amount=70_000,
    )
    assert owner_user.get_last_spoken() == (
        f"{tenant.name} landed on your One Pillar Pagoda. "
        "You may claim 70,000 VND rent or waive it."
    )
    tenant_cash = tenant.cash
    owner_cash = owner.cash

    game._action_claim_rent(owner, "claim_rent")
    game._action_pay_debt(tenant, "pay_debt")

    assert tenant.cash == tenant_cash - 70_000
    assert owner.cash == owner_cash + 70_000


def test_nearest_hanoi_landmark_card_uses_scaled_complete_group_rate() -> None:
    game = make_game()
    game.options.board_id = "hanoi"
    game.on_start()
    drain_sequence(game, "monopoly_intro")
    tenant, owner = game.players[:2]
    force_current(game)
    game.property_states["one_pillar_pagoda"].owner_id = owner.id
    tenant.position = HANOI_BOARD.space_index("cau_go")
    game._roll_pair = lambda: (2, 3)  # type: ignore[method-assign]

    game._move_to(
        tenant,
        "one_pillar_pagoda",
        collect_go=True,
        rent_multiplier=10,
        utility_override=True,
    )
    drain_sequence(game, "monopoly_utility_rent")

    assert game.rent_state is not None
    assert game.rent_state.amount == 50_000


def test_utility_rent_roll_sequence_survives_save_and_restore() -> None:
    game = make_game()
    game.options.board_id = "hanoi"
    game.on_start()
    drain_sequence(game, "monopoly_intro")
    tenant, owner = game.players[:2]
    force_current(game)
    own_group(game, owner.id, "utility")
    tenant.position = HANOI_BOARD.space_index("long_bien_bridge")
    game._roll_pair = lambda: (5, 4)  # type: ignore[method-assign]

    game._resolve_landing(tenant)
    restored = MonopolyGame.from_json(game.to_json())

    assert restored.has_active_sequence(tag="monopoly_utility_rent")
    drain_sequence(restored, "monopoly_utility_rent")
    assert restored.rent_state is not None
    assert restored.rent_state.amount == 90_000
    assert restored.phase == PHASE_RENT


def test_rent_is_an_explicit_out_of_turn_owner_decision() -> None:
    game = make_game(start=True)
    tenant, owner = game.players[:2]
    force_current(game)
    game.property_states["mediterranean"].owner_id = owner.id
    tenant.position = BOARD.space_index("mediterranean")
    game._resolve_landing(tenant)

    assert game.phase == PHASE_RENT
    assert game.current_player == tenant
    assert game.decision_player_id == owner.id
    owner_cash = owner.cash
    tenant_cash = tenant.cash
    game._action_claim_rent(owner, "claim_rent")
    assert owner.cash == owner_cash + 2
    assert tenant.cash == tenant_cash - 2


def test_rent_prompt_is_private_and_payment_is_one_perspective_aware_message() -> None:
    game = make_game(3, start=True)
    tenant, owner, observer = game.players
    tenant_user = game.get_user(tenant)
    owner_user = game.get_user(owner)
    observer_user = game.get_user(observer)
    assert tenant_user is not None
    assert owner_user is not None
    assert observer_user is not None
    force_current(game)
    game.property_states["mediterranean"].owner_id = owner.id
    tenant.position = BOARD.space_index("mediterranean")
    for user in (tenant_user, owner_user, observer_user):
        user.clear_messages()

    game._resolve_landing(tenant)

    assert owner_user.get_spoken_messages() == [
        f"{tenant.name} landed on your Mediterranean Avenue. "
        "You may claim $2 rent or waive it."
    ]
    assert tenant_user.get_spoken_messages() == []
    assert observer_user.get_spoken_messages() == []

    for user in (tenant_user, owner_user, observer_user):
        user.clear_messages()
    game._action_claim_rent(owner, "claim_rent")

    assert owner_user.get_spoken_messages() == [
        f"You collect $2 rent from {tenant.name} for Mediterranean Avenue. "
        "You now have $1,502."
    ]
    assert tenant_user.get_spoken_messages() == [
        f"You pay $2 rent to {owner.name} for Mediterranean Avenue. "
        "You have $1,498 left."
    ]
    assert observer_user.get_spoken_messages() == [
        f"{tenant.name} pays {owner.name} $2 rent for Mediterranean Avenue."
    ]


def test_rent_debt_context_is_serialized_and_legacy_debts_remain_compatible() -> None:
    game = make_game(start=True)
    tenant, owner = game.players
    tenant.cash = 0
    game._start_debt(
        tenant,
        owner.id,
        2,
        "monopoly-debt-rent",
        continuation="finish_landing",
        property_id="mediterranean",
    )

    restored = MonopolyGame.from_json(game.to_json())
    assert restored.debt_state is not None
    assert restored.debt_state.property_id == "mediterranean"

    legacy = DebtState.from_dict(
        {
            "debtor_id": tenant.id,
            "creditor_id": owner.id,
            "amount": 2,
            "reason_key": "monopoly-debt-rent",
            "continuation": "finish_landing",
        }
    )
    assert legacy.property_id == ""


def test_owned_and_mortgaged_landings_explain_why_no_rent_is_due() -> None:
    game = make_game(start=True)
    tenant, owner = game.players[:2]
    tenant_user = game.get_user(tenant)
    owner_user = game.get_user(owner)
    assert tenant_user is not None and owner_user is not None
    force_current(game)

    game.property_states["mediterranean"].owner_id = tenant.id
    tenant.position = BOARD.space_index("mediterranean")
    tenant_user.clear_messages()
    owner_user.clear_messages()
    game._resolve_landing(tenant)

    assert "your own Mediterranean Avenue" in tenant_user.get_last_spoken()
    assert (
        f"{tenant.name} lands on their own Mediterranean Avenue"
        in owner_user.get_last_spoken()
    )
    assert game.rent_state is None

    game.property_states["baltic"] = PropertyState(owner.id, True, 0)
    tenant.position = BOARD.space_index("baltic")
    tenant_user.clear_messages()
    owner_user.clear_messages()
    game._resolve_landing(tenant)

    assert f"{owner.name}'s Baltic Avenue" in tenant_user.get_last_spoken()
    assert "mortgaged" in tenant_user.get_last_spoken()
    assert "No rent is due" in owner_user.get_last_spoken()
    assert game.rent_state is None


def test_even_building_hotel_exchange_and_shortage_rules() -> None:
    game = make_game(start=True)
    owner = game.players[0]
    own_group(game, owner.id, "brown")

    assert (
        can_build(BOARD, game.property_states, "mediterranean", owner.id, 32, 12)
        is None
    )
    game._apply_build(owner, "mediterranean", announce=False)
    assert (
        can_build(BOARD, game.property_states, "mediterranean", owner.id, 31, 12)
        == "monopoly-error-build-evenly"
    )
    game._apply_build(owner, "baltic", announce=False)
    for _ in range(3):
        game._apply_build(owner, "mediterranean", announce=False)
        game._apply_build(owner, "baltic", announce=False)
    assert game.property_states["mediterranean"].buildings == 4
    houses_before = game.bank_houses
    hotels_before = game.bank_hotels
    game._apply_build(owner, "mediterranean", announce=False)
    assert game.property_states["mediterranean"].buildings == 5
    assert game.bank_houses == houses_before + 4
    assert game.bank_hotels == hotels_before - 1
    game._apply_build(owner, "baltic", announce=False)
    assert game.property_states["baltic"].buildings == 5
    assert game.bank_houses == houses_before + 8
    assert game.bank_hotels == hotels_before - 2

    game.bank_houses = 3
    assert (
        can_sell_building(
            BOARD, game.property_states, "mediterranean", owner.id, game.bank_houses
        )
        == "monopoly-error-bank-needs-four-houses"
    )


def test_whole_group_sale_resolves_hotel_shortage_and_debt_deadlock() -> None:
    game = make_game(start=True)
    owner = game.players[0]
    force_current(game)
    own_group(game, owner.id, "brown")
    for property_id in ("mediterranean", "baltic"):
        game.property_states[property_id].buildings = 5
    game.bank_houses = 0
    game.bank_hotels = 10
    owner.cash = 0
    game._start_debt(owner, "", 300, "monopoly-debt-tax", continuation="finish_landing")

    game._action_raise_cash(owner, "raise_cash")

    assert game.property_states["mediterranean"].buildings == 0
    assert game.property_states["baltic"].buildings == 0
    assert game.bank_hotels == 12
    assert owner.cash >= 300
    assert game._is_pay_debt_enabled(owner) is None


def test_mortgage_interest_rounding() -> None:
    assert unmortgage_cost(75) == 83
    assert unmortgage_cost(100) == 110
    assert transfer_mortgage_interest(75) == 8
    assert transfer_mortgage_interest(100) == 10


def test_trade_blocks_built_group_and_charges_mortgage_transfer_interest() -> None:
    game = make_game(start=True)
    proposer, target = game.players[:2]
    force_current(game)
    own_group(game, proposer.id, "brown")
    game.property_states["mediterranean"].buildings = 1
    assert game._property_is_tradeable("baltic", proposer.id) is False

    game.property_states["mediterranean"].buildings = 0
    game.property_states["mediterranean"].mortgaged = True
    proposer_cash = proposer.cash
    target_cash = target.cash
    game._action_propose_trade(proposer, target.id, "propose_trade")
    assert game.phase == PHASE_TRADE_BUILD
    game.trade_state.offered_property_ids = ["mediterranean"]  # type: ignore[union-attr]
    game._action_trade_submit(proposer, "trade_submit")
    assert game.phase == PHASE_TRADE_RESPONSE
    game._action_trade_accept(target, "trade_accept")

    assert game.property_states["mediterranean"].owner_id == target.id
    assert proposer.cash == proposer_cash
    assert target.cash == target_cash
    assert game.phase == "mortgage_transfer"
    game._action_keep_received_mortgaged(target, "keep_received_mortgaged")
    assert target.cash == target_cash - 3
    assert game.property_states["mediterranean"].mortgaged is True


def test_received_mortgage_can_be_lifted_immediately_without_double_interest() -> None:
    game = make_game(start=True)
    proposer, target = game.players[:2]
    force_current(game)
    game.property_states["mediterranean"].owner_id = proposer.id
    game.property_states["mediterranean"].mortgaged = True
    target_cash = target.cash
    game._action_propose_trade(proposer, target.id, "propose_trade")
    game.trade_state.offered_property_ids = ["mediterranean"]  # type: ignore[union-attr]
    game._action_trade_submit(proposer, "trade_submit")
    game._action_trade_accept(target, "trade_accept")

    game._action_unmortgage_received_now(target, "unmortgage_received_now")

    assert game.property_states["mediterranean"].mortgaged is False
    assert target.cash == target_cash - 33
    assert game.phase == "await_roll"


def test_trade_recipient_can_review_full_deeds_before_deciding() -> None:
    game = make_game(start=True, touch=True)
    proposer, target = game.players[:2]
    target_user = game.get_user(target)
    assert target_user is not None
    force_current(game)
    game.property_states["mediterranean"] = PropertyState(proposer.id, True, 0)
    game.trade_state = TradeState(
        proposer.id,
        target.id,
        offered_property_ids=["mediterranean"],
        submitted=True,
    )
    game.phase = PHASE_TRADE_RESPONSE
    game.decision_player_id = target.id

    game.before_menu_build(target)
    turn = game.get_action_set(target, "turn")
    assert turn is not None
    visible_ids = [
        resolved.action.id for resolved in turn.get_visible_actions(game, target)
    ]
    assert visible_ids[:4] == [
        "roll_dice",
        "trade_review",
        "trade_accept",
        "trade_reject",
    ]

    game._action_trade_review(target, "trade_review")

    status = target_user.menus["status_box"]
    assert status["selection_id"] == "trade:summary"
    rows = [item.text for item in status["items"]]
    assert any("Mediterranean Avenue" in row for row in rows)
    assert any("brown color group" in row for row in rows)
    assert any("Minimum immediate transfer interest: $3" in row for row in rows)


def test_trade_notifications_address_proposer_target_and_observer() -> None:
    game = make_game(start=True)
    proposer, target = game.players[:2]
    watcher_user = MockUser("Watcher", uuid="watcher")
    game.add_spectator("Watcher", watcher_user)
    proposer_user = game.get_user(proposer)
    target_user = game.get_user(target)
    assert proposer_user is not None and target_user is not None
    force_current(game)
    game.property_states["mediterranean"].owner_id = proposer.id
    game.property_states["boardwalk"].owner_id = target.id
    game._action_propose_trade(proposer, target.id, "propose_trade")
    assert game.trade_state is not None
    game.trade_state.offered_property_ids = ["mediterranean"]
    game.trade_state.requested_property_ids = ["boardwalk"]
    proposer_user.clear_messages()
    target_user.clear_messages()
    watcher_user.clear_messages()

    game._action_trade_submit(proposer, "trade_submit")

    proposer_text = proposer_user.get_last_spoken()
    target_text = target_user.get_last_spoken()
    watcher_text = watcher_user.get_last_spoken()
    assert "You offer" in proposer_text
    assert "You give Mediterranean Avenue" in proposer_text
    assert f"{target.name} gives Boardwalk" in proposer_text
    assert f"{proposer.name} offers you" in target_text
    assert "you give Boardwalk" in target_text
    assert proposer.name in watcher_text and target.name in watcher_text

    proposer_user.clear_messages()
    target_user.clear_messages()
    watcher_user.clear_messages()
    game._action_trade_accept(target, "trade_accept")

    assert "You accept" in target_user.get_last_spoken()
    assert f"{target.name} accepts your trade" in proposer_user.get_last_spoken()
    assert f"{target.name} accepts {proposer.name}'s trade" in (
        watcher_user.get_last_spoken()
    )


def test_trade_cancel_restores_interrupted_property_decision() -> None:
    game = make_game(start=True)
    proposer, target = game.players[:2]
    force_current(game)
    game.pending_property_id = "mediterranean"
    game.phase = PHASE_PROPERTY
    game.decision_player_id = proposer.id

    game._action_propose_trade(proposer, target.id, "propose_trade")
    game._action_trade_cancel(proposer, "trade_cancel")

    assert game.trade_state is None
    assert game.phase == PHASE_PROPERTY
    assert game.decision_player_id == proposer.id
    assert game.pending_property_id == "mediterranean"


def test_trading_every_asset_does_not_bankrupt_a_player_without_debt() -> None:
    game = make_game(start=True)
    proposer, target = game.players[:2]
    force_current(game)
    property_ids = ["mediterranean", "baltic"]
    for property_id in property_ids:
        game.property_states[property_id].owner_id = proposer.id
    starting_cash = proposer.cash

    game._action_propose_trade(proposer, target.id, "propose_trade")
    assert game.trade_state is not None
    game.trade_state.offered_property_ids = property_ids
    game.trade_state.offered_cash = starting_cash
    game._action_trade_submit(proposer, "trade_submit")
    game._action_trade_accept(target, "trade_accept")

    assert proposer.cash == 0
    assert game._owned_property_ids(proposer.id) == []
    assert proposer.bankrupt is False
    assert proposer in game.alive_players
    assert game.debt_state is None

    game._start_debt(
        proposer,
        "",
        1,
        "monopoly-debt-tax",
        continuation="finish_landing",
    )

    assert game.phase == PHASE_DEBT
    assert game._is_bankruptcy_enabled(proposer) is None


def test_debt_liquidation_and_bankruptcy_to_player() -> None:
    game = make_game(start=True)
    debtor, creditor = game.players[:2]
    force_current(game)
    debtor.cash = 0
    game.property_states["mediterranean"].owner_id = debtor.id
    game._start_debt(
        debtor, creditor.id, 100, "monopoly-debt-rent", continuation="finish_landing"
    )
    assert game.phase == PHASE_DEBT
    assert game._is_bankruptcy_enabled(debtor) is None

    game._action_declare_bankruptcy(debtor, "declare_bankruptcy")

    assert debtor.bankrupt is True
    assert game.property_states["mediterranean"].owner_id == creditor.id
    assert game.winner_id == creditor.id
    assert game.status == "finished"


@pytest.mark.parametrize(
    ("deck_id", "card_id", "actor_cash", "other_cash", "verb"),
    [
        ("chance", "chance_chairperson", 1_150, 1_550, "pay"),
        ("community", "community_party", 1_570, 1_490, "collect"),
    ],
)
def test_multi_player_card_payments_use_one_summary_and_one_sound(
    deck_id: str,
    card_id: str,
    actor_cash: int,
    other_cash: int,
    verb: str,
) -> None:
    game = make_game(8, start=True)
    actor = game.players[0]
    force_current(game)
    users = [game.get_user(player) for player in game.players]
    assert all(user is not None for user in users)
    for user in users:
        assert user is not None
        user.clear_messages()

    game._resolve_card(actor, game.board.card(deck_id, card_id))

    assert actor.cash == actor_cash
    assert all(player.cash == other_cash for player in game.players[1:])
    assert game.payment_batch_state is None
    for user in users:
        assert user is not None
        spoken = user.get_spoken_messages()
        assert len(spoken) == 1
        assert verb in spoken[0]
        assert "7 players" in spoken[0]
        assert "a payment to another player" not in spoken[0]
        assert user.get_sounds_played() == [monopoly_audio.SOUND_RENT_PAID]


def test_multi_player_payment_summary_honors_brief_locale_per_listener() -> None:
    game = make_game(3, start=True, locale="vi")
    actor, observer = game.players[:2]
    force_current(game)
    actor_user = game.get_user(actor)
    observer_user = game.get_user(observer)
    assert actor_user is not None and observer_user is not None
    actor_user.preferences.set_game_override("brief_announcements", "monopoly", True)
    for player in game.players:
        user = game.get_user(player)
        assert user is not None
        user.clear_messages()

    game._resolve_card(actor, game.board.card("chance", "chance_chairperson"))

    assert actor_user.get_last_spoken() == (
        "Đã trả tổng cộng 100 đô la cho 2 người chơi."
    )
    assert observer_user.get_last_spoken() == (
        f"{actor.name} trả 50 đô la cho mỗi người trong số 2 người chơi, "
        "tổng cộng 100 đô la. Họ còn 1.400 đô la."
    )


def test_multi_player_payment_batch_survives_save_during_liquidation() -> None:
    game = make_game(4, start=True)
    actor = game.players[0]
    force_current(game)
    actor.cash = 60

    game._resolve_card(actor, game.board.card("chance", "chance_chairperson"))

    assert game.phase == PHASE_DEBT
    assert game.debt_state is not None
    assert game.payment_batch_state is not None
    assert game.payment_batch_state.completed_count == 1
    assert game.payment_batch_state.completed_total == 50
    assert len(game.payment_batch_state.payments) == 1

    restored = MonopolyGame.from_json(game.to_json())

    assert restored.payment_batch_state is not None
    assert restored.payment_batch_state.completed_count == 1
    assert restored.payment_batch_state.completed_total == 50
    assert len(restored.payment_batch_state.payments) == 1
    assert restored.debt_state is not None
    assert restored.debt_state.continuation == "payment_batch"


def test_bankruptcy_ends_multi_player_payment_without_repeating_prior_cues() -> None:
    game = make_game(3, start=True)
    actor = game.players[0]
    force_current(game)
    actor.cash = 60
    game._resolve_card(actor, game.board.card("chance", "chance_chairperson"))
    assert game.phase == PHASE_DEBT
    for player in game.players:
        user = game.get_user(player)
        assert user is not None
        user.clear_messages()

    game._action_declare_bankruptcy(actor, "declare_bankruptcy")

    assert actor.bankrupt is True
    assert game.payment_batch_state is None
    assert game.players[1].cash == 1_550
    # The creditor receives the actor's remaining cash under bankruptcy rules.
    assert game.players[2].cash == 1_510
    for player in game.players:
        user = game.get_user(player)
        assert user is not None
        sounds = user.get_sounds_played()
        assert sounds.count(monopoly_audio.SOUND_RENT_PAID) == 1
        assert sounds.count(monopoly_audio.SOUND_BANKRUPTCY_DECLARED) == 1


def test_collect_from_each_continues_after_one_payer_goes_bankrupt() -> None:
    game = make_game(3, start=True)
    collector, insolvent, payer = game.players
    force_current(game)
    insolvent.cash = 0

    game._resolve_card(
        collector,
        game.board.card("community", "community_party"),
    )
    assert game.phase == PHASE_DEBT
    assert game.debt_state is not None
    assert game.debt_state.debtor_id == insolvent.id
    for player in game.players:
        user = game.get_user(player)
        assert user is not None
        user.clear_messages()

    game._action_declare_bankruptcy(insolvent, "declare_bankruptcy")

    assert insolvent.bankrupt is True
    assert collector.cash == 1_510
    assert payer.cash == 1_490
    assert game.payment_batch_state is None
    collector_user = game.get_user(collector)
    assert collector_user is not None
    assert any(
        "collect $10 from each of 1 player" in message
        for message in collector_user.get_spoken_messages()
    )
    sounds = collector_user.get_sounds_played()
    assert sounds.count(monopoly_audio.SOUND_RENT_PAID) == 1
    assert sounds.count(monopoly_audio.SOUND_BANKRUPTCY_DECLARED) == 1


def test_bankruptcy_to_bank_returns_and_auctions_properties() -> None:
    game = make_game(3, start=True)
    debtor = game.players[0]
    force_current(game)
    debtor.cash = 0
    game.property_states["mediterranean"].owner_id = debtor.id
    game.debt_state = DebtState(debtor.id, "", 100, "monopoly-debt-tax")
    game.phase = PHASE_DEBT
    game.decision_player_id = debtor.id

    game._action_declare_bankruptcy(debtor, "declare_bankruptcy")

    assert debtor.bankrupt is True
    assert game.phase == PHASE_AUCTION
    assert game.auction_state is not None
    assert game.auction_state.property_id == "mediterranean"


def test_information_views_have_stable_rows_and_priority_order() -> None:
    game = make_game(start=True, touch=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    board = game._build_board_status(player, user)
    assert len(board.items) == 40
    assert board.items[0].id == "space:go"
    assert board.items[-1].id == "space:boardwalk"
    groups = game._build_property_groups_status(player, user)
    assert len(groups.items) == len(BOARD.property_groups)
    assert groups.items[0].id == "group:brown"
    assert "Mediterranean Avenue" in groups.items[0].text
    assert "Baltic Avenue" in groups.items[0].text
    player.position = BOARD.space_index("mediterranean")
    user.clear_messages()
    game._action_read_current_space(player, "read_current_space")
    current_space = user.get_last_spoken()
    assert "brown color group" in current_space
    assert "hotel $250" in current_space
    assert "status_box" not in user.menus

    standard = game.get_action_set(player, "standard")
    assert standard is not None
    assert standard._order[-len(game.touch_standard_action_order) :] == list(
        game.touch_standard_action_order
    )

    game._action_read_board(player, "read_board")
    assert user.menus["status_box"]["selection_id"] == "space:go"

    game._action_read_property_groups(player, "read_property_groups")
    assert user.menus["status_box"]["selection_id"] == "group:brown"

    game._action_read_cash(player, "read_cash")
    assert "You have $1,500" in user.get_last_spoken()


def test_touch_standard_actions_prioritize_frequent_controls() -> None:
    game = make_game(start=True, touch=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)

    standard = game.get_action_set(player, "standard")
    assert standard is not None
    expected = list(game.touch_standard_action_order)
    assert standard._order[-len(expected) :] == expected

    game.flush_menus()
    visible_ids = [
        item.id
        for item in user.menus["turn_menu"]["items"]
        if getattr(item, "id", None)
    ]
    assert visible_ids[: len(expected) + 1] == ["roll_dice", *expected]


def test_desktop_actions_menu_preserves_framework_and_native_game_order() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)

    standard = game.get_action_set(player, "standard")
    assert standard is not None
    assert standard._order == [
        "show_actions",
        "save_table",
        "whose_turn",
        "whos_at_table",
        "check_scores",
        "check_scores_detailed",
        "predict_outcomes",
        "game_info",
        "game_rules",
        "read_cash",
        "read_current_space",
        "read_board",
        "read_property_groups",
        "read_portfolios",
        "read_my_portfolio",
        "read_status",
        "manage_properties",
        "propose_trade",
    ]

    game._action_show_actions_menu(player, "show_actions")
    action_ids = [
        item.id
        for item in user.menus["actions_menu"]["items"]
        if getattr(item, "id", None)
    ]
    assert action_ids == [
        "host_management",
        "leave_game",
        "save_table",
        "whose_turn",
        "whos_at_table",
        "predict_outcomes",
        "game_info",
        "game_rules",
        "read_cash",
        "read_current_space",
        "read_board",
        "read_property_groups",
        "read_portfolios",
        "read_my_portfolio",
        "read_status",
        "manage_properties",
        "propose_trade",
        "go_back",
    ]


def test_standard_action_order_tracks_client_capability_changes() -> None:
    game = make_game(start=True, touch=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    standard = game.get_action_set(player, "standard")
    assert standard is not None
    touch_order = list(game.touch_standard_action_order)
    assert standard._order[-len(touch_order) :] == touch_order

    user.client_type = "python"
    game.before_menu_build(player)

    assert standard._order[:4] == [
        "show_actions",
        "save_table",
        "whose_turn",
        "whos_at_table",
    ]
    assert standard._order[-2:] == ["manage_properties", "propose_trade"]

    user.client_type = "mobile"
    game.before_menu_build(player)

    assert standard._order[-len(touch_order) :] == touch_order


def test_all_portfolios_uses_player_then_property_hierarchy() -> None:
    game = make_game(8, start=True, touch=True)
    first, second = game.players[:2]
    user = game.get_user(first)
    assert user is not None
    game.property_states["mediterranean"].owner_id = first.id
    game.property_states["boardwalk"].owner_id = second.id

    game.execute_action(first, "read_portfolios")

    menu = user.menus["action_input_menu"]
    assert menu["selection_id"] == first.id
    rows = [item for item in menu["items"] if item.id != "_cancel"]
    assert [item.id for item in rows] == [player.id for player in game.players]
    assert all("cash:" in item.text for item in rows)
    assert all("estimated net worth:" in item.text for item in rows)
    assert all("color group" not in item.text for item in rows)

    game.handle_event(
        first,
        {
            "type": "menu",
            "menu_id": "action_input_menu",
            "selection_id": second.id,
        },
    )

    detail = user.menus["status_box"]
    assert detail["selection_id"] == "selected:property:boardwalk"
    detail_rows = [item.text for item in detail["items"]]
    assert len(detail_rows) == 1
    assert "Boardwalk" in detail_rows[0]
    assert first.name not in detail_rows[0]


def test_spectator_sees_public_state_but_not_private_trade_draft() -> None:
    game = make_game(start=True, touch=True)
    proposer, target = game.players[:2]
    watcher_user = MockUser("Watcher", uuid="watcher")
    watcher_user.client_type = "mobile"
    watcher = game.add_spectator("Watcher", watcher_user)
    game.property_states["mediterranean"].owner_id = proposer.id
    game.property_states["boardwalk"].owner_id = target.id
    game.trade_state = TradeState(
        proposer.id,
        target.id,
        offered_cash=100,
        requested_property_ids=["boardwalk"],
    )
    game.phase = PHASE_TRADE_BUILD
    game.decision_player_id = proposer.id

    public_ids = [item.action.id for item in game.get_all_visible_actions(watcher)]
    assert public_ids == [
        "read_status",
        "read_property_groups",
        "read_portfolios",
        "read_board",
        "whose_turn",
        "whos_at_table",
    ]
    assert (
        not {
            "read_cash",
            "read_current_space",
            "read_my_portfolio",
            "manage_properties",
            "propose_trade",
        }
        & set(public_ids)
    )

    spectator_status = game._build_game_status(watcher, watcher_user)
    trade_row = next(item.text for item in spectator_status.items if item.id == "trade")
    assert "preparing a trade" in trade_row
    assert "Boardwalk" not in trade_row
    assert "$100" not in trade_row

    target_user = game.get_user(target)
    assert target_user is not None
    target_status = game._build_game_status(target, target_user)
    target_trade = next(item.text for item in target_status.items if item.id == "trade")
    assert "preparing a trade" in target_trade
    assert "Boardwalk" not in target_trade

    proposer_user = game.get_user(proposer)
    assert proposer_user is not None
    proposer_status = game._build_game_status(proposer, proposer_user)
    proposer_trade = next(
        item.text for item in proposer_status.items if item.id == "trade"
    )
    assert "Boardwalk" in proposer_trade
    assert "You give $100" in proposer_trade


def test_buy_action_returns_focus_to_stable_roll_anchor() -> None:
    game = make_game(start=True, touch=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    player.position = BOARD.space_index("mediterranean")
    game._resolve_landing(player)
    user.clear_messages()

    game._action_buy_property(player, "buy_property")
    game.flush_menus()

    packets = [
        message
        for message in user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert packets[-1].data["selection_id"] == "roll_dice"
    assert packets[-1].data["items"][0].id == "roll_dice"


def test_explicit_end_turn_focuses_only_the_acting_players_roll_anchor() -> None:
    game = make_game(3, start=True, touch=True)
    player, next_player, observer = game.players
    player_user = game.get_user(player)
    next_user = game.get_user(next_player)
    observer_user = game.get_user(observer)
    assert player_user is not None
    assert next_user is not None
    assert observer_user is not None
    force_current(game)
    game.phase = PHASE_TURN_ACTIONS
    game.refresh_menus()
    game.flush_menus()
    for user in (player_user, next_user, observer_user):
        user.clear_messages()

    game.handle_event(
        player,
        {
            "type": "menu",
            "menu_id": "turn_menu",
            "selection_id": "end_turn",
        },
    )

    assert game.current_player == next_player
    player_packets = [
        message
        for message in player_user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    next_packets = [
        message
        for message in next_user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    observer_packets = [
        message
        for message in observer_user.messages
        if message.type in {"show_menu", "update_menu"}
        and message.data.get("menu_id") == "turn_menu"
    ]
    assert player_packets[-1].data["selection_id"] == "roll_dice"
    assert next_packets[-1].data["selection_id"] is None
    assert observer_packets[-1].data["selection_id"] is None

    game._pending_menu_focus.clear()
    game.phase = PHASE_TURN_ACTIONS
    game.decision_player_id = next_player.id
    game._finish_turn()
    assert game._pending_menu_focus == {}


def test_group_context_and_completion_are_announced_to_actor_and_observer() -> None:
    game = make_game(start=True)
    buyer, observer = game.players[:2]
    buyer_user = game.get_user(buyer)
    observer_user = game.get_user(observer)
    assert buyer_user is not None and observer_user is not None
    force_current(game)
    game.property_states["mediterranean"].owner_id = buyer.id
    buyer.position = BOARD.space_index("baltic")
    game._resolve_landing(buyer)

    label = game._get_buy_label(buyer, "buy_property")
    description = game._get_buy_description(buyer, "buy_property")
    assert "brown color group" in label
    assert "Mediterranean Avenue" in description
    assert "Baltic Avenue" in description
    assert "mortgage: $30" in description
    assert "hotel $450" in description

    buyer_user.clear_messages()
    observer_user.clear_messages()
    game._action_buy_property(buyer, "buy_property")

    sounds = buyer_user.get_sounds_played()
    assert sounds == [
        monopoly_audio.SOUND_PROPERTY_PURCHASED,
        monopoly_audio.SOUND_COLOR_GROUP_COMPLETED,
    ]
    color_cue = next(
        message
        for message in buyer_user.messages
        if message.type == "play_sound"
        and message.data["name"] == monopoly_audio.SOUND_COLOR_GROUP_COMPLETED
    )
    assert color_cue.data["max_instances"] == 1
    assert not any(
        scheduled[1] == monopoly_audio.SOUND_COLOR_GROUP_COMPLETED
        for scheduled in game.scheduled_sounds
    )
    assert "You now own the complete brown color group" in buyer_user.get_last_spoken()
    assert (
        f"{buyer.name} now owns the complete brown color group"
        in observer_user.get_last_spoken()
    )


def test_trade_completing_two_players_groups_plays_one_cue_and_keeps_both_tts() -> None:
    game = make_game(start=True)
    proposer, target = game.players[:2]
    proposer_user = game.get_user(proposer)
    target_user = game.get_user(target)
    assert proposer_user is not None and target_user is not None
    force_current(game)
    for property_id in ("mediterranean", "oriental", "vermont"):
        game.property_states[property_id].owner_id = proposer.id
    for property_id in ("baltic", "connecticut"):
        game.property_states[property_id].owner_id = target.id
    game.trade_state = TradeState(
        proposer.id,
        target.id,
        offered_property_ids=["mediterranean"],
        requested_property_ids=["connecticut"],
        submitted=True,
    )
    game.phase = PHASE_TRADE_RESPONSE
    game.decision_player_id = target.id
    proposer_user.clear_messages()
    target_user.clear_messages()

    game._action_trade_accept(target, "trade_accept")

    for user in (proposer_user, target_user):
        assert user.get_sounds_played() == [
            monopoly_audio.SOUND_TRADE_ACCEPTED,
            monopoly_audio.SOUND_COLOR_GROUP_COMPLETED,
        ]
        group_messages = [
            text
            for text in user.get_spoken_messages()
            if "complete" in text and "color group" in text
        ]
        assert len(group_messages) == 2
        assert any("brown color group" in text for text in group_messages)
        assert any("light blue color group" in text for text in group_messages)


def test_declarative_actions_resolve_without_missing_callbacks_or_raw_keys() -> None:
    game = make_game(start=True)
    player = game.players[0]
    callback_fields = (
        "handler",
        "is_enabled",
        "is_hidden",
        "get_label",
        "get_description",
    )
    for action_set in game.get_action_sets(player):
        for action in action_set._actions.values():
            for field_name in callback_fields:
                callback_name = getattr(action, field_name)
                if callback_name:
                    assert callable(getattr(game, callback_name, None))
            request = action.input_request
            if request:
                for field_name in (
                    "options",
                    "option_label",
                    "option_description",
                    "bot_input",
                    "bot_select",
                    "initial_selection",
                ):
                    callback_name = getattr(request, field_name, None)
                    if callback_name:
                        is_framework_option_lookup = (
                            field_name == "options"
                            and callback_name.startswith("_options_for_")
                        )
                        assert is_framework_option_lookup or callable(
                            getattr(game, callback_name, None)
                        )
        for resolved in action_set.resolve_actions(game, player):
            assert resolved.label
            assert not resolved.label.startswith("monopoly-")
            if resolved.description:
                assert not resolved.description.startswith("monopoly-")


def test_whose_turn_reports_pending_out_of_turn_owner_action() -> None:
    game = make_game(start=True)
    tenant, owner = game.players[:2]
    force_current(game)
    game.rent_state = RentState(tenant.id, owner.id, "mediterranean", 2)
    game.phase = PHASE_RENT
    game.decision_player_id = owner.id
    user = game.get_user(tenant)
    assert user is not None
    user.clear_messages()

    game._action_whose_turn(tenant, "whose_turn")

    spoken = user.get_last_spoken()
    assert "your turn" in spoken
    assert tenant.name not in spoken
    assert owner.name in spoken
    assert "claim or waive rent" in spoken

    owner_user = game.get_user(owner)
    assert owner_user is not None
    owner_user.clear_messages()
    game._action_whose_turn(owner, "whose_turn")
    owner_spoken = owner_user.get_last_spoken()
    assert tenant.name in owner_spoken
    assert "but you must claim or waive rent" in owner_spoken
    assert owner.name not in owner_spoken


def test_whose_turn_uses_first_person_for_the_active_players_own_action() -> None:
    game = make_game(start=True)
    current, observer = game.players[:2]
    force_current(game)
    current_user = game.get_user(current)
    observer_user = game.get_user(observer)
    assert current_user is not None and observer_user is not None
    current_user.clear_messages()
    observer_user.clear_messages()

    game._action_whose_turn(current, "whose_turn")
    game._action_whose_turn(observer, "whose_turn")

    assert current_user.get_last_spoken() == "It is your turn; you must roll the dice."
    assert observer_user.get_last_spoken() == (
        f"It is {current.name}'s turn; they must roll the dice."
    )


def test_serialization_preserves_complex_pending_state() -> None:
    game = make_game(3, start=True)
    first, second = game.players[:2]
    force_current(game)
    game.phase = PHASE_AUCTION
    game.decision_player_id = second.id
    game.auction_state = AuctionState(
        property_id="boardwalk",
        bidder_ids=[player.id for player in game.players],
        active_bidder_ids=[first.id, second.id],
        highest_bidder_id=first.id,
        highest_bid=300,
    )
    game.options.free_parking_cash = True
    game.free_parking_pot = 175
    first.passed_go_once = True
    game.turn_number = 27
    first.bot_trade_turn = 26

    restored = MonopolyGame.from_json(game.to_json())
    restored.rebuild_runtime_state()

    assert restored.phase == PHASE_AUCTION
    assert restored.decision_player_id == second.id
    assert restored.auction_state is not None
    assert restored.auction_state.highest_bid == 300
    assert len(restored.property_states) == 28
    assert restored.options.free_parking_cash is True
    assert restored.free_parking_pot == 175
    assert restored.players[0].passed_go_once is True
    assert restored.turn_number == 27
    assert restored.players[0].bot_trade_turn == 26


def test_end_screen_uses_the_board_currency_snapshotted_in_the_result() -> None:
    game = make_game(start=True)
    winner = game.players[0]
    game.winner_id = winner.id
    result = game.build_game_result()

    assert result.custom_data["board_id"] == "standard"
    assert result.custom_data["currency_key"] == "monopoly-currency-usd"
    original_lines = game.format_end_screen(result, "en")
    assert "$1,500" in original_lines[1]

    # The waiting-lobby instance can change its next board while another
    # player still has this result screen open. The old result must not adopt
    # the next game's currency.
    game.options.board_id = "hanoi"
    changed_lines = game.format_end_screen(result, "en")
    assert changed_lines == original_lines
    assert "VND" not in changed_lines[1]


@pytest.mark.parametrize(
    ("board_id", "board", "property_id"),
    (
        ("london", LONDON_BOARD, "mayfair"),
        ("paris", PARIS_BOARD, "rue_paix"),
        ("germany", GERMANY_BOARD, "schlossallee"),
        ("italy", ITALY_BOARD, "parco_della_vittoria"),
        ("madrid", MADRID_BOARD, "paseo_prado"),
        ("tokyo", TOKYO_BOARD, "ginza"),
        ("australia", AUSTRALIA_BOARD, "kings_avenue"),
        ("new_zealand", NEW_ZEALAND_BOARD, "queen_street"),
        ("hanoi", HANOI_BOARD, "lo_duc"),
    ),
)
def test_regional_board_round_trip_preserves_state(
    board_id: str, board: BoardDefinition, property_id: str
) -> None:
    game = make_game()
    game.options.board_id = board_id
    game.on_start()
    owner = game.players[0]
    game.property_states[property_id] = PropertyState(owner.id, True, 0)
    game.chance_deck.remove("chance_jail_free")
    owner.jail_card_ids = ["chance_jail_free"]

    restored = MonopolyGame.from_json(game.to_json())
    restored.rebuild_runtime_state()

    assert restored.options.board_id == board_id
    assert restored.board is board
    assert restored.property_states[property_id] == PropertyState(owner.id, True, 0)
    assert restored.players[0].jail_card_ids == ["chance_jail_free"]
    assert len(restored.chance_deck) == len(board.chance_cards) - 1


def test_monopoly_audio_assets_match_every_first_party_sound_pack() -> None:
    expected = {
        "game_monopoly/auction_bid.ogg",
        "game_monopoly/auction_sold.ogg",
        "game_monopoly/auction_started.ogg",
        "game_monopoly/bankruptcy_declared.ogg",
        "game_monopoly/board_setup.ogg",
        "game_monopoly/cash_received1.ogg",
        "game_monopoly/cash_received2.ogg",
        "game_monopoly/color_group_completed.ogg",
        "game_monopoly/debt_warning.ogg",
        "game_monopoly/deck_shuffle.ogg",
        "game_monopoly/development_built.ogg",
        "game_monopoly/development_sold.ogg",
        "game_monopoly/dice_roll1.ogg",
        "game_monopoly/dice_roll2.ogg",
        "game_monopoly/game_won.ogg",
        "game_monopoly/large_cash_payout.ogg",
        "game_monopoly/leave_jail.ogg",
        "game_monopoly/music_loop.ogg",
        "game_monopoly/property_mortgaged.ogg",
        "game_monopoly/property_purchased.ogg",
        "game_monopoly/property_unmortgaged.ogg",
        "game_monopoly/rent_paid.ogg",
        "game_monopoly/repair_fee.ogg",
        "game_monopoly/roll_doubles.ogg",
        "game_monopoly/sent_to_jail.ogg",
        "game_monopoly/snake_eyes_bonus.ogg",
        "game_monopoly/tax_or_fine_paid.ogg",
        "game_monopoly/token_landed.ogg",
        "game_monopoly/trade_accepted.ogg",
        "game_monopoly/trade_proposed.ogg",
    }
    assert set(monopoly_audio.MONOPOLY_ASSET_PATHS) == expected
    assert all(monopoly_audio.AUDIO_DURATIONS_TICKS[path] > 0 for path in expected)

    reference_bytes: dict[str, bytes] = {}
    for pack_root in (
        ROOT / "client" / "sounds",
        ROOT / "web_client" / "sounds",
        ROOT / "mobile_client" / "sounds",
    ):
        monopoly_root = pack_root / "game_monopoly"
        actual = {
            f"game_monopoly/{path.name}"
            for path in monopoly_root.iterdir()
            if path.is_file()
        }
        assert actual == expected
        for sound in expected:
            data = (pack_root / sound).read_bytes()
            if sound in reference_bytes:
                assert data == reference_bytes[sound], sound
            else:
                reference_bytes[sound] = data

    for sound, expected_ticks in monopoly_audio.AUDIO_DURATIONS_TICKS.items():
        path = ROOT / "client" / "sounds" / sound
        assert path.is_file(), sound
        assert (
            measure_audio_duration_ticks(
                path,
                ticks_per_second=monopoly_audio.TICKS_PER_SECOND,
            )
            == expected_ticks
        )


def test_sound_pack_versions_are_synchronized_after_monopoly_audio() -> None:
    versions = {
        (ROOT / pack / "sounds" / "version.txt").read_text(encoding="utf-8").strip()
        for pack in ("client", "web_client", "mobile_client")
    }
    assert SOUNDS_VERSION == "4"
    assert versions == {"4"}


def test_regular_roll_audio_sequence_resolves_in_cinematic_order() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    player.position = game.board.space_index("community_1")
    game._roll_pair = lambda: (1, 1)  # type: ignore[method-assign]
    user.clear_messages()

    game._action_roll_dice(player, "roll_dice")
    assert player.position == game.board.space_index("community_1")
    assert game.has_active_sequence(tag="monopoly_roll")

    drain_sequence(game, "monopoly_roll")

    sounds = [
        message.data["name"]
        for message in user.messages
        if message.type == "play_sound"
    ]
    assert sounds[0] in monopoly_audio.SOUND_DICE_ROLLS
    assert sounds[1:] == [
        monopoly_audio.SOUND_ROLL_DOUBLES,
        monopoly_audio.SOUND_TOKEN_LANDED,
        monopoly_audio.SOUND_TAX_OR_FINE_PAID,
    ]
    assert player.position == game.board.space_index("income_tax")


def test_doubles_cue_does_not_add_its_audio_duration_to_roll_pacing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    game = make_game(start=True)
    player = game.players[0]
    original_sound_ticks = monopoly_audio.sound_ticks
    monkeypatch.setattr(
        monopoly_audio,
        "sound_ticks",
        lambda sound: (
            10_000
            if sound == monopoly_audio.SOUND_ROLL_DOUBLES
            else original_sound_ticks(sound)
        ),
    )

    doubles_beats = game._build_roll_cue_beats(player, 3, 3)

    assert sum(beat.delay_after_ticks for beat in doubles_beats) == (
        doubles_beats[0].delay_after_ticks
    )
    assert doubles_beats[-1].delay_after_ticks == 0
    assert doubles_beats[-1].ops[0].sound == monopoly_audio.SOUND_ROLL_DOUBLES


def test_roll_spam_cannot_replace_an_authoritative_outcome() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    player.position = game.board.space_index("go")
    outcomes = [(1, 2), (6, 6)]
    calls = 0

    def roll_pair() -> tuple[int, int]:
        nonlocal calls
        outcome = outcomes[calls]
        calls += 1
        return outcome

    game._roll_pair = roll_pair  # type: ignore[method-assign]
    game.execute_action(player, "roll_dice")
    game.execute_action(player, "roll_dice")

    assert calls == 1
    assert (game.last_die_1, game.last_die_2) == (1, 2)
    assert len(
        [sequence for sequence in game.active_sequences if sequence.tag == "monopoly_roll"]
    ) == 1
    assert user.get_last_spoken() == (
        "The current roll or space effect is still resolving. Please wait."
    )

    drain_sequence(game, "monopoly_roll")
    assert player.position == game.board.space_index("baltic")


def test_gameplay_sequence_blocks_mutating_overlays_but_keeps_status_available() -> None:
    game = make_game(start=True, touch=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    game.property_states["reading_railroad"].owner_id = player.id
    game._roll_pair = lambda: (1, 2)  # type: ignore[method-assign]
    game.execute_action(player, "roll_dice")
    assert game.is_sequence_gameplay_locked()
    assert game.phase == PHASE_AWAIT_ROLL

    user.clear_messages()
    game.execute_action(player, "manage_properties")
    game.execute_action(player, "propose_trade")

    resolving = Localization.get("en", "monopoly-error-roll-resolving")
    assert user.get_spoken_messages() == [resolving, resolving]
    assert game.phase == PHASE_AWAIT_ROLL
    assert game.management_resume_phase == ""
    assert player.id not in game._pending_actions

    user.clear_messages()
    game.execute_action(player, "whose_turn")
    assert user.get_last_spoken() == (
        "It is your turn; you must wait for the current roll or space effect "
        "to finish."
    )

    game.execute_action(player, "read_status")
    assert "status_box" in user.menus
    status_items = user.menus["status_box"]["items"]
    assert "wait for the current roll or space effect to finish" in (
        status_items[0].text
    )
    drain_sequence(game, "monopoly_roll")
    game.flush_menus()
    assert "status_box" in user.menus
    assert game.phase == PHASE_PROPERTY


def test_jail_roll_sequence_blocks_alternate_jail_actions() -> None:
    game = make_game(start=True, touch=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    player.in_jail = True
    player.position = game.board.space_index(game.board.jail_space_id)
    player.jail_card_ids.append("chance_jail_free")
    game.phase = PHASE_JAIL
    game._roll_pair = lambda: (1, 2)  # type: ignore[method-assign]
    cash_before = player.cash
    game.execute_action(player, "jail_roll")
    assert game.is_sequence_gameplay_locked()

    turn = game.get_action_set(player, "turn")
    assert turn is not None
    jail_actions = {
        resolved.action.id: resolved
        for resolved in turn.get_visible_actions(game, player)
        if resolved.action.id in {"jail_roll", "jail_pay", "jail_card"}
    }
    assert set(jail_actions) == {"jail_roll", "jail_pay", "jail_card"}
    assert not any(resolved.enabled for resolved in jail_actions.values())

    user.clear_messages()
    game.execute_action(player, "jail_pay")
    game.execute_action(player, "jail_card")

    resolving = Localization.get("en", "monopoly-error-roll-resolving")
    assert user.get_spoken_messages() == [resolving, resolving]
    assert player.cash == cash_before
    assert player.in_jail is True
    assert player.jail_card_ids == ["chance_jail_free"]


def test_jail_roll_spam_cannot_replace_an_authoritative_outcome() -> None:
    game = make_game(start=True)
    player = game.players[0]
    force_current(game)
    player.in_jail = True
    player.position = game.board.space_index(game.board.jail_space_id)
    game.phase = PHASE_JAIL
    game.decision_player_id = player.id
    outcomes = [(1, 2), (6, 6)]
    calls = 0

    def roll_pair() -> tuple[int, int]:
        nonlocal calls
        outcome = outcomes[calls]
        calls += 1
        return outcome

    game._roll_pair = roll_pair  # type: ignore[method-assign]
    game.execute_action(player, "jail_roll")
    game.execute_action(player, "jail_roll")

    assert calls == 1
    assert (game.last_die_1, game.last_die_2) == (1, 2)
    drain_sequence(game, "monopoly_roll")
    assert player.in_jail is True


def test_card_draw_audio_finishes_before_the_card_event_sound() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    game.chance_deck.remove("chance_dividend")
    game.chance_deck.insert(0, "chance_dividend")
    cash_before = player.cash
    user.clear_messages()

    game._draw_card(player, "chance")
    assert player.cash == cash_before
    drain_sequence(game, "monopoly_card")

    sounds = [
        message.data["name"]
        for message in user.messages
        if message.type == "play_sound"
    ]
    assert sounds[0] in monopoly_audio.SOUND_CARD_DRAWS
    assert sounds[1] in monopoly_audio.SOUND_CASH_RECEIVED
    assert player.cash == cash_before + 50


def test_jail_payment_starts_the_fine_and_unlock_together() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    player.in_jail = True
    player.position = game.board.space_index(game.board.jail_space_id)
    game.phase = PHASE_JAIL
    game.decision_player_id = player.id
    user.clear_messages()

    game._action_jail_pay(player, "jail_pay")
    assert not game.has_active_sequence(tag="monopoly_jail_release")
    sounds = [
        message.data["name"]
        for message in user.messages
        if message.type == "play_sound"
    ]
    assert sounds == [
        monopoly_audio.SOUND_TAX_OR_FINE_PAID,
        monopoly_audio.SOUND_LEAVE_JAIL,
    ]
    assert player.in_jail is False
    assert game.phase == PHASE_AWAIT_ROLL
    assert game._is_roll_enabled(player) is None


def test_jail_card_plays_the_unlock_before_normal_rolling_resumes() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    player.in_jail = True
    player.position = game.board.space_index(game.board.jail_space_id)
    player.jail_card_ids = ["chance_jail_free"]
    game.chance_deck.remove("chance_jail_free")
    game.phase = PHASE_JAIL
    game.decision_player_id = player.id
    user.clear_messages()

    game.execute_action(player, "jail_card")

    assert not game.has_active_sequence(tag="monopoly_jail_release")
    assert game._is_roll_enabled(player) is None
    sounds = [
        message.data["name"]
        for message in user.messages
        if message.type == "play_sound"
    ]
    assert sounds == [monopoly_audio.SOUND_LEAVE_JAIL]
    assert player.in_jail is False
    assert player.jail_card_ids == []
    assert game.chance_deck[-1] == "chance_jail_free"
    assert game.phase == PHASE_AWAIT_ROLL


def test_rolling_doubles_plays_the_shared_jail_release_sound() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    player.in_jail = True
    player.position = game.board.space_index(game.board.jail_space_id)
    game.phase = PHASE_JAIL
    game.decision_player_id = player.id
    user.clear_messages()

    game._start_jail_roll_sequence(player, 2, 2)
    drain_sequence(game, "monopoly_roll")

    sounds = [
        message.data["name"]
        for message in user.messages
        if message.type == "play_sound"
    ]
    assert sounds.count(monopoly_audio.SOUND_LEAVE_JAIL) == 1
    assert sounds.index(monopoly_audio.SOUND_LEAVE_JAIL) < sounds.index(
        monopoly_audio.SOUND_TOKEN_LANDED
    )
    assert player.in_jail is False


def test_forced_third_turn_jail_fine_releases_before_movement() -> None:
    game = make_game(start=True)
    player = game.players[0]
    user = game.get_user(player)
    assert user is not None
    force_current(game)
    player.in_jail = True
    player.jail_turns = 2
    player.position = game.board.space_index(game.board.jail_space_id)
    game.phase = PHASE_JAIL
    game.decision_player_id = player.id
    user.clear_messages()

    game._start_jail_roll_sequence(player, 1, 2)
    drain_sequence(game, "monopoly_roll")

    assert not game.has_active_sequence(tag="monopoly_jail_release")
    sounds = [
        message.data["name"]
        for message in user.messages
        if message.type == "play_sound"
    ]
    assert sounds[-3:] == [
        monopoly_audio.SOUND_TAX_OR_FINE_PAID,
        monopoly_audio.SOUND_LEAVE_JAIL,
        monopoly_audio.SOUND_TOKEN_LANDED,
    ]
    assert player.in_jail is False


def test_auction_audio_routes_start_bid_and_sale_events() -> None:
    game = make_game(start=True)
    first, second = game.players[:2]
    user = game.get_user(first)
    assert user is not None
    force_current(game)
    user.clear_messages()

    game._start_auction(
        "mediterranean", resume_kind="landing", first_bidder_id=first.id
    )
    assert game._place_bid(first, game._auction_minimum_bid()) is True
    game._action_pass_auction(second, "pass_auction")

    sounds = [
        message.data["name"]
        for message in user.messages
        if message.type == "play_sound"
    ]
    assert sounds == [
        monopoly_audio.SOUND_AUCTION_STARTED,
        monopoly_audio.SOUND_AUCTION_BID,
        monopoly_audio.SOUND_AUCTION_SOLD,
    ]


def test_roll_audio_sequence_survives_save_and_restore() -> None:
    game = make_game(start=True)
    player = game.players[0]
    force_current(game)
    game._roll_pair = lambda: (1, 2)  # type: ignore[method-assign]

    game._action_roll_dice(player, "roll_dice")
    for _ in range(3):
        game.on_tick()
    restored = MonopolyGame.from_json(game.to_json())

    assert restored.has_active_sequence(tag="monopoly_roll")
    drain_sequence(restored, "monopoly_roll")
    restored_player = restored.players[0]
    assert restored_player.position == restored.board.space_index("baltic")
    assert restored.phase == PHASE_PROPERTY


def test_winner_stops_music_before_the_victory_cue_and_announcement() -> None:
    game = make_game(start=True)
    winner, eliminated = game.players[:2]
    user = game.get_user(winner)
    assert user is not None
    eliminated.bankrupt = True
    user.clear_messages()

    assert game._check_for_winner() is True

    relevant = [
        (
            message.type,
            message.data.get("name", ""),
            message.data.get("text", ""),
        )
        for message in user.messages
        if message.type in {"stop_music", "play_sound", "speak"}
    ]
    stop_index = next(
        index for index, event in enumerate(relevant) if event[0] == "stop_music"
    )
    victory_index = next(
        index
        for index, event in enumerate(relevant)
        if event[:2] == ("play_sound", monopoly_audio.SOUND_GAME_WON)
    )
    speech_index = next(
        index
        for index, event in enumerate(relevant)
        if event[0] == "speak" and "win" in event[2].lower()
    )
    assert stop_index < victory_index < speech_index


def test_bot_actions_receive_a_fresh_humanized_delay() -> None:
    game = make_game(start=True, bots=True)
    player = game.players[0]
    force_current(game)
    player.bot_think_ticks = 0
    player.bot_pending_action = None
    game._bot_pacing_actor_id = ""

    game.on_tick()

    assert (
        monopoly_audio.BOT_ACTION_DELAY_MIN_TICKS
        <= player.bot_think_ticks
        <= monopoly_audio.BOT_ACTION_DELAY_MAX_TICKS
    )
    assert player.bot_pending_action is None


def test_english_vietnamese_monopoly_locale_parity() -> None:
    def keys(path: Path) -> set[str]:
        return {
            line.split("=", 1)[0].strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line and not line.startswith((" ", "#")) and "=" in line
        }

    english = keys(ROOT / "server" / "locales" / "en" / "monopoly.ftl")
    vietnamese = keys(ROOT / "server" / "locales" / "vi" / "monopoly.ftl")
    assert english == vietnamese


def test_vietnamese_board_names_and_movement_cards_use_localized_terms() -> None:
    game = MonopolyGame()
    assert Localization.get("vi", "monopoly-space-new-york") == "Đại lộ New York"
    assert Localization.get("vi", "monopoly-space-reading-railroad") == "Ga Reading"
    assert Localization.get("vi", "monopoly-space-boardwalk") == "Boardwalk"
    assert "Đại lộ Illinois" in game._card_text(
        "vi", BOARD.card("chance", "chance_red_property")
    )
    assert Localization.get("vi", "monopoly-space-go") == "Khởi hành"
    assert Localization.get("vi", "monopoly-space-free-parking") == (
        "Bãi đậu xe miễn phí"
    )
    assert Localization.get("vi", "monopoly-space-london-trafalgar-square") == (
        "Quảng trường Trafalgar"
    )
    assert Localization.get("vi", "monopoly-space-london-kings-cross-station") == (
        "Ga King's Cross"
    )
    assert Localization.get("vi", "monopoly-space-paris-avenue-champs-elysees") == (
        "Avenue des Champs-Élysées"
    )
    assert Localization.get("vi", "monopoly-space-paris-rue-paix") == ("Rue de la Paix")
    assert Localization.get("vi", "monopoly-space-germany-schlossallee") == (
        "Schlossallee"
    )
    assert Localization.get("vi", "monopoly-space-germany-suedbahnhof") == (
        "Ga phía Nam"
    )
    assert Localization.get("vi", "monopoly-space-italy-parco-della-vittoria") == (
        "Parco della Vittoria"
    )
    assert Localization.get("vi", "monopoly-space-italy-stazione-est") == (
        "Ga phía Đông"
    )
    assert Localization.get("vi", "monopoly-space-madrid-paseo-prado") == (
        "Paseo del Prado"
    )
    assert Localization.get("vi", "monopoly-space-madrid-estacion-delicias") == (
        "Ga Las Delicias"
    )
    assert Localization.get("vi", "monopoly-space-tokyo-ginza") == "Ginza"
    assert Localization.get("vi", "monopoly-space-tokyo-shibuya-station") == (
        "Ga Shibuya"
    )
    assert Localization.get("vi", "monopoly-space-australia-kings-avenue") == (
        "Đại lộ Kings"
    )
    assert Localization.get("vi", "monopoly-space-australia-perth-station") == (
        "Ga Perth"
    )
    assert Localization.get("vi", "monopoly-space-new-zealand-queen-street") == (
        "Phố Queen"
    )
    assert Localization.get("vi", "monopoly-space-new-zealand-balclutha-station") == (
        "Ga Balclutha"
    )
    assert Localization.get("vi", "monopoly-space-hanoi-hoan-kiem-lake") == (
        "Hồ Hoàn Kiếm"
    )
    assert Localization.get("vi", "monopoly-space-hanoi-my-dinh-bus-station") == (
        "Bến xe Mỹ Đình"
    )
    assert Localization.get("vi", "monopoly-space-hanoi-one-pillar-pagoda") == (
        "Chùa Một Cột"
    )


@pytest.mark.parametrize("board_id", get_board_ids())
def test_every_board_content_key_is_localized_in_english_and_vietnamese(
    board_id: str,
) -> None:
    board = get_board(board_id)
    keys = {
        board.name_key,
        board.description_key,
        board.currency_key,
        board.terminology.street_kind_key,
        board.terminology.transit_kind_key,
        board.terminology.utility_kind_key,
        board.terminology.chance_kind_key,
        board.terminology.community_kind_key,
        board.terminology.chance_deck_key,
        board.terminology.community_deck_key,
        board.terminology.utility_rent_schedule_key,
        board.development.collective_key,
        board.development.build_selector_key,
        board.development.sell_selector_key,
        board.development.rent_schedule_key,
        board.development.bank_supply_key,
        board.development.group_sale_description_key,
        board.development.empty_key,
        *board.development.level_keys,
        *(replacement for _, replacement in board.development.error_key_overrides),
        *(group.name_key for group in board.property_groups),
        *(space.name_key for space in board.spaces),
        *(card.text_key for card in board.chance_cards),
        *(card.text_key for card in board.community_cards),
    }
    keys.discard("")
    for locale in ("en", "vi"):
        assert all(Localization.has_message(locale, key) for key in keys)


def test_player_text_is_neutral_beginner_friendly_and_avoids_rulebook_commentary() -> None:
    paths = (
        ROOT / "server" / "locales" / "en" / "monopoly.ftl",
        ROOT / "server" / "locales" / "vi" / "monopoly.ftl",
        ROOT / "server" / "documentation" / "content" / "en" / "games" / "monopoly.md",
        ROOT / "server" / "documentation" / "content" / "vi" / "games" / "monopoly.md",
    )
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    for phrase in (
        "house rule",
        "official rules",
        "original rules",
        "luật nhà",
        "luật chính thức",
        "luật gốc",
    ):
        assert phrase not in combined.casefold()
    english_manual = paths[2].read_text(encoding="utf-8")
    vietnamese_manual = paths[3].read_text(encoding="utf-8")
    assert english_manual.count("\\*\\*Default:") == 6
    assert vietnamese_manual.count("\\*\\*Mặc định:") == 6
    assert "\\*\\*Example of one turn\\*\\*" in english_manual
    assert "\\*\\*Ví dụ về một lượt chơi\\*\\*" in vietnamese_manual
    assert "\\*\\*Dice and doubles\\*\\*" in english_manual
    assert "\\*\\*Xúc xắc và ra đôi\\*\\*" in vietnamese_manual
    assert "both dice show the same number" in english_manual
    assert "cả hai xúc xắc có cùng số" in vietnamese_manual
    for vendor_or_history in (
        "Hasbro",
        "Lizzie",
        "Charles Darrow",
        "Parker Brothers",
    ):
        assert vendor_or_history not in english_manual
        assert vendor_or_history not in vietnamese_manual


def test_every_actor_broadcast_has_localized_first_and_third_person_forms() -> None:
    tree = ast.parse(
        (ROOT / "server" / "games" / "monopoly" / "game.py").read_text(encoding="utf-8")
    )
    pairs: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "_broadcast_actor"
            and len(node.args) >= 3
            and isinstance(node.args[1], ast.Constant)
            and isinstance(node.args[2], ast.Constant)
        ):
            continue
        pairs.append((node.args[1].value, node.args[2].value))
        keyword_names = {keyword.arg for keyword in node.keywords}
        assert (
            "brief_personal_key" in keyword_names or "suppress_brief" in keyword_names
        )

    assert pairs
    for personal_key, public_key in pairs:
        assert "-you-" in personal_key or "-your-" in personal_key
        assert "-player-" in public_key
        for locale in ("en", "vi"):
            assert Localization.has_message(locale, personal_key)
            assert Localization.has_message(locale, public_key)

    target_triplets: list[tuple[str, str, str]] = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "_broadcast_actor_target"
            and len(node.args) >= 5
            and all(isinstance(argument, ast.Constant) for argument in node.args[2:5])
        ):
            continue
        target_triplets.append(tuple(argument.value for argument in node.args[2:5]))
        keyword_names = {keyword.arg for keyword in node.keywords}
        assert {
            "brief_personal_key",
            "brief_target_key",
            "brief_others_key",
        } <= keyword_names

    assert target_triplets
    for personal_key, target_key, public_key in target_triplets:
        assert "-you-" in personal_key
        assert "-you" in target_key
        assert "-player-" in public_key
        for locale in ("en", "vi"):
            assert Localization.has_message(locale, personal_key)
            assert Localization.has_message(locale, target_key)
            assert Localization.has_message(locale, public_key)

    global_pairs: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "_broadcast_global"
            and len(node.args) >= 2
            and all(isinstance(argument, ast.Constant) for argument in node.args[:2])
        ):
            continue
        global_pairs.append((node.args[0].value, node.args[1].value))
    assert global_pairs
    for full_key, brief_key in global_pairs:
        for locale in ("en", "vi"):
            assert Localization.has_message(locale, full_key)
            assert Localization.has_message(locale, brief_key)


def test_bot_auction_uses_meaningful_bid_steps() -> None:
    game = make_game(2, start=True, bots=True)
    bidder = game.players[0]
    force_current(game)
    game._start_auction(
        "boardwalk",
        resume_kind="landing",
        first_bidder_id=bidder.id,
    )

    assert game.bot_think(bidder) == "place_bid"
    bid = int(game._bot_bid_input(bidder))
    assert bid > game.board.rules.auction_opening_bid
    game.execute_action(bidder, "place_bid")

    assert game.auction_state is not None
    assert game.auction_state.highest_bid == bid


def test_bot_auction_budget_always_keeps_an_emergency_reserve() -> None:
    states = {space.id: PropertyState() for space in BOARD.spaces if space.price}
    states["mediterranean"].owner_id = "buyer"
    cash = 500

    maximum = maximum_auction_bid(
        BOARD,
        states,
        BOARD.space("baltic"),
        "buyer",
        cash,
    )

    assert maximum <= cash - cash_reserve(BOARD)
    assert maximum < cash


def test_bot_traffic_model_uses_board_layout_and_movement_cards() -> None:
    assert landing_weight(BOARD, "illinois") > landing_weight(BOARD, "boardwalk")
    assert landing_weight(BOARD, "new_york") > landing_weight(BOARD, "park_place")
    assert landing_weight(LONDON_BOARD, "trafalgar_square") > landing_weight(
        LONDON_BOARD, "mayfair"
    )
    assert landing_weight(LONDON_BOARD, "vine_street") > landing_weight(
        LONDON_BOARD, "park_lane"
    )
    assert landing_weight(PARIS_BOARD, "avenue_henri_martin") > landing_weight(
        PARIS_BOARD, "rue_paix"
    )
    assert landing_weight(PARIS_BOARD, "place_pigalle") > landing_weight(
        PARIS_BOARD, "avenue_champs_elysees"
    )
    assert landing_weight(GERMANY_BOARD, "opernplatz") > landing_weight(
        GERMANY_BOARD, "schlossallee"
    )
    assert landing_weight(GERMANY_BOARD, "berliner_strasse") > landing_weight(
        GERMANY_BOARD, "parkstrasse"
    )
    assert landing_weight(ITALY_BOARD, "largo_colombo") > landing_weight(
        ITALY_BOARD, "parco_della_vittoria"
    )
    assert landing_weight(ITALY_BOARD, "piazza_dante") > landing_weight(
        ITALY_BOARD, "viale_dei_giardini"
    )
    assert landing_weight(MADRID_BOARD, "calle_cea_bermudez") > landing_weight(
        MADRID_BOARD, "paseo_prado"
    )
    assert landing_weight(MADRID_BOARD, "calle_serrano") > landing_weight(
        MADRID_BOARD, "paseo_castellana"
    )


def test_bots_can_complete_a_full_game_on_every_bundled_board(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Exercise the complete rules engine without spending wall-clock time on
    # the separately tested human-facing audio and bot pacing delays.
    monkeypatch.setattr(monopoly_audio, "sound_ticks", lambda sound: 0)
    monkeypatch.setattr(monopoly_audio, "ROLL_TO_LANDING_PAUSE_TICKS", 0)
    monkeypatch.setattr(monopoly_audio, "LANDING_TO_EVENT_PAUSE_TICKS", 0)
    monkeypatch.setattr(monopoly_audio, "OPENING_ROLL_GAP_TICKS", 0)
    monkeypatch.setattr(monopoly_audio, "BOT_ACTION_DELAY_MIN_TICKS", 1)
    monkeypatch.setattr(monopoly_audio, "BOT_ACTION_DELAY_MAX_TICKS", 1)
    random_state = random.getstate()
    try:
        for board_index, board_id in enumerate(get_board_ids()):
            random.seed(8_400 + board_index)
            game = make_game(4, bots=True)
            game.options.board_id = board_id
            game.on_start()

            for _ in range(20_000):
                game.on_tick()
                if game.status != "playing":
                    break

            assert game.status == "finished", board_id
            assert game.winner is not None
            assert len(game.alive_players) == 1
    finally:
        random.setstate(random_state)


def test_bot_values_blocking_an_opponents_completed_group() -> None:
    states = {space.id: PropertyState() for space in BOARD.spaces if space.price}
    space = BOARD.space("baltic")
    ordinary_bid = maximum_auction_bid(
        BOARD, states, space, "buyer", BOARD.starting_cash
    )
    states["mediterranean"].owner_id = "opponent"

    blocking_bid = maximum_auction_bid(
        BOARD, states, space, "buyer", BOARD.starting_cash
    )

    assert blocking_bid > ordinary_bid


def test_bot_preserves_house_scarcity_before_upgrading_to_a_hotel() -> None:
    game = make_game(2, start=True, bots=True)
    builder, opponent = game.players
    own_group(game, builder.id, "dark_blue")
    own_group(game, opponent.id, "brown")
    for space in game.board.group_spaces("dark_blue"):
        game.property_states[space.id].buildings = 4
    builder.cash = 5_000
    game.bank_houses = 4

    assert game._bot_management_choice(builder, "boardwalk") is None

    game.bank_houses = 8
    choice = game._bot_management_choice(builder, "boardwalk")
    assert choice is not None and choice[0] == "build"


def test_bot_does_not_unmortgage_a_received_deed_into_rent_danger() -> None:
    game = make_game(2, start=True, bots=True)
    recipient, opponent = game.players[:2]
    own_group(game, opponent.id, "dark_blue")
    for space in game.board.group_spaces("dark_blue"):
        game.property_states[space.id].buildings = 5
    game.property_states["mediterranean"] = PropertyState(
        recipient.id,
        True,
        0,
    )
    game.mortgage_transfer_state = MortgageTransferState(
        property_ids=["mediterranean"]
    )
    game.phase = PHASE_MORTGAGE_TRANSFER
    game.decision_player_id = recipient.id

    recipient.cash = 600
    assert game.bot_think(recipient) == "keep_received_mortgaged"

    recipient.cash = 800
    assert game.bot_think(recipient) == "unmortgage_received_now"


def test_automatic_liquidation_protects_more_valuable_income() -> None:
    game = make_game(start=True)
    player = game.players[0]
    own_group(game, player.id, "brown")
    own_group(game, player.id, "dark_blue")
    game.property_states["reading_railroad"].owner_id = player.id
    for group_id in ("brown", "dark_blue"):
        for space in game.board.group_spaces(group_id):
            game.property_states[space.id].buildings = 1

    assert game._best_building_sale(player.id) == "mediterranean"

    for state in game.property_states.values():
        state.buildings = 0
    assert game._best_mortgage(player.id) == "reading_railroad"


def test_bot_does_not_spend_auction_liquidity_on_buildings() -> None:
    game = make_game(2, start=True, bots=True)
    bidder, leader = game.players[:2]
    force_current(game)
    own_group(game, bidder.id, "brown")
    bidder.cash = 300
    game.phase = PHASE_AUCTION
    game.decision_player_id = bidder.id
    game.auction_state = AuctionState(
        property_id="boardwalk",
        bidder_ids=[player.id for player in game.players],
        active_bidder_ids=[player.id for player in game.players],
        highest_bidder_id=leader.id,
        highest_bid=100,
        minimum_bid=101,
    )

    assert game._bot_management_choice(bidder, "mediterranean") is None
    assert game.bot_think(bidder) == "pass_auction"


def test_bot_develops_complete_groups_through_normal_actions() -> None:
    game = make_game(2, start=True, bots=True)
    builder = game.players[0]
    force_current(game)
    own_group(game, builder.id, "brown")
    game.phase = PHASE_TURN_ACTIONS
    game.decision_player_id = builder.id

    for _ in range(40):
        action = game.bot_think(builder)
        assert action is not None
        if action == "end_turn":
            break
        game.execute_action(builder, action)

    levels = [
        game.property_states[space.id].buildings
        for space in game.board.group_spaces("brown")
    ]
    assert min(levels) >= 3
    assert max(levels) - min(levels) <= 1


def test_bot_proposes_and_accepts_a_fair_group_completing_trade() -> None:
    game = make_game(2, start=True, bots=True)
    proposer, target = game.players[:2]
    force_current(game)
    game.property_states["mediterranean"].owner_id = proposer.id
    game.property_states["baltic"].owner_id = target.id
    game.phase = PHASE_TURN_ACTIONS
    game.decision_player_id = proposer.id

    assert game.bot_think(proposer) == "propose_trade"
    game.execute_action(proposer, "propose_trade")
    assert game.phase == PHASE_TRADE_BUILD
    assert game.trade_state is not None
    assert game.trade_state.target_id == target.id

    for _ in range(10):
        action = game.bot_think(proposer)
        assert action is not None
        game.execute_action(proposer, action)
        if game.phase == PHASE_TRADE_RESPONSE:
            break

    assert game.phase == PHASE_TRADE_RESPONSE
    assert game.trade_state is not None
    assert game.trade_state.requested_property_ids == ["baltic"]
    assert game.trade_state.offered_cash > 0
    assert game.bot_think(target) == "trade_accept"


def test_bot_remembers_a_rejected_trade_goal_before_trying_again() -> None:
    game = make_game(2, start=True, bots=True)
    proposer, target = game.players[:2]
    force_current(game)
    game.property_states["mediterranean"].owner_id = proposer.id
    game.property_states["baltic"].owner_id = target.id
    game.phase = PHASE_TURN_ACTIONS
    game.decision_player_id = proposer.id

    game.execute_action(proposer, "propose_trade")
    for _ in range(10):
        action = game.bot_think(proposer)
        assert action is not None
        game.execute_action(proposer, action)
        if game.phase == PHASE_TRADE_RESPONSE:
            break
    assert game.phase == PHASE_TRADE_RESPONSE

    game.execute_action(target, "trade_reject")

    memory_key = game._bot_trade_memory_key(target.id, "baltic")
    expires = proposer.bot_trade_cooldowns[memory_key]
    assert expires > game.turn_number
    assert game._bot_best_trade_plan(proposer) is None

    restored = MonopolyGame.from_json(game.to_json())
    restored_proposer = restored.get_player_by_id(proposer.id)
    assert restored_proposer is not None
    assert restored_proposer.bot_trade_cooldowns[memory_key] == expires

    game.turn_number = expires
    assert game._bot_best_trade_plan(proposer) is not None


def test_bot_trade_memory_is_bounded_and_cleared_when_game_is_discarded() -> None:
    game = make_game(2, start=True, bots=True)
    proposer, target = game.players[:2]
    valid_key = game._bot_trade_memory_key(target.id, "baltic")
    proposer.bot_trade_turn = game.turn_number
    proposer.bot_trade_cooldowns = {
        valid_key: game.turn_number + 10,
        "removed-player:missing-property": game.turn_number + 10_000,
    }

    game._prune_bot_trade_cooldowns(proposer)
    assert proposer.bot_trade_cooldowns == {valid_key: game.turn_number + 10}

    game.destroy()
    assert game._destroyed is True
    assert proposer.bot_trade_turn == -1
    assert proposer.bot_trade_cooldowns == {}
    assert game._bot_pacing_actor_id == ""


def test_bot_jail_strategy_changes_after_the_board_is_developed() -> None:
    game = make_game(2, start=True, bots=True)
    player = game.players[0]
    force_current(game)
    player.in_jail = True
    player.jail_card_ids = ["chance_jail_free"]
    game.phase = PHASE_JAIL
    game.decision_player_id = player.id

    assert game.bot_think(player) == "jail_card"

    own_group(game, player.id, "brown")
    game.property_states["mediterranean"].buildings = 2
    assert opponent_rent_pressure(game.board, game.property_states, player.id) == 0
    assert game.bot_think(player) == "jail_card"

    for space in game.board.group_spaces("brown"):
        game.property_states[space.id] = PropertyState()
    own_group(game, game.players[1].id, "brown")
    game.property_states["mediterranean"].buildings = 2
    assert opponent_rent_pressure(game.board, game.property_states, player.id) > 0
    assert game.bot_think(player) == "jail_roll"
    player.jail_turns = 2
    assert game.bot_think(player) == "jail_roll"


def test_bot_game_reaches_a_winner() -> None:
    game = make_game(2, start=True, bots=True)
    debtor, owner = game.players
    force_current(game)
    own_group(game, owner.id, "dark_blue")
    debtor.cash = 0
    debtor.position = BOARD.space_index("park_place")
    game._roll_pair = lambda: (1, 1)  # type: ignore[method-assign]

    for _ in range(1_000):
        if game.status == "finished":
            break
        game.on_tick()
        game.flush_menus()

    assert game.status == "finished"
    assert game.winner_id
