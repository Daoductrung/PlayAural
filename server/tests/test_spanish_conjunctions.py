"""Tests for the Spanish y/e and o/u conjunction rules."""

from pathlib import Path

import pytest

from ..messages.localization import Localization
from ..messages.spanish_grammar import (
    fix_list_conjunction,
    spanish_and,
    spanish_or,
    starts_with_i_sound,
    starts_with_o_sound,
)

_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


@pytest.mark.parametrize(
    "text",
    [
        "I 20",
        "I",
        "Isabel",
        "Iván",
        "Ignacio",
        "ídolo",
        "hilo",
        "Hilda",
        "híbrido",
        "IA",
        "¿Irene?",
        '"Inés"',
        "(Ismael)",
        "\u2068Isabel\u2069",
        "  Iván",
    ],
)
def test_words_starting_with_the_sound_i_take_e(text: str) -> None:
    assert starts_with_i_sound(text)
    assert spanish_and(text) == "e"


@pytest.mark.parametrize(
    "text",
    [
        "hielo",
        "hierro",
        "hiena",
        "hiato",
        "ion",
        "iodo",
        "Iago",
        "Ian",
        "Iuri",
        "B 5",
        "N 33",
        "O 70",
        "Ana",
        "Hugo",
        "yo",
        "uno",
        "8",
        "11",
        "",
        "   ",
        "...",
        "+I",
        "\u2068Ana\u2069",
    ],
)
def test_other_words_keep_y(text: str) -> None:
    assert not starts_with_i_sound(text)
    assert spanish_and(text) == "y"


@pytest.mark.parametrize(
    "text",
    [
        "O 70",
        "O",
        "Obispo",
        "ocho",
        "once",
        "Óscar",
        "hotel",
        "Hombre",
        "\u2068Obispo\u2069",
        "(ocho)",
        "$88",
        "$8",
        "\u20ac80",
        "\u00a3880",
        "$11",
        "hola",
        "homenaje",
        "8",
        "88",
        "880",
        "8,5",
        "8 de oros",
        "11",
        "11.000",
        "11,5",
    ],
)
def test_words_starting_with_the_sound_o_take_u(text: str) -> None:
    assert starts_with_o_sound(text)
    assert spanish_or(text) == "u"


@pytest.mark.parametrize(
    "text",
    [
        "I 20",
        "N 33",
        "Ana",
        "Ladrón",
        "uno",
        "7",
        "18",
        "110",
        "115",
        "-8",
        "+8",
        "#8",
        "$18",
        "$110",
        "A$88",
        "hockey",
        "Hold'em",
        "",
    ],
)
def test_other_words_keep_o(text: str) -> None:
    assert not starts_with_o_sound(text)
    assert spanish_or(text) == "o"


def test_fix_list_conjunction_only_touches_the_conjunction_before_the_last_item() -> None:
    assert fix_list_conjunction("B 5 y I 20", ["B 5", "I 20"], "y") == "B 5 e I 20"
    assert (
        fix_list_conjunction("I 5, B 6 y I 20", ["I 5", "B 6", "I 20"], "y")
        == "I 5, B 6 e I 20"
    )
    # Only the item after the conjunction decides.
    assert fix_list_conjunction("I 20 y B 5", ["I 20", "B 5"], "y") == "I 20 y B 5"
    # Nothing to fix for one item, an empty list, or text Babel did not shape.
    assert fix_list_conjunction("I 20", ["I 20"], "y") == "I 20"
    assert fix_list_conjunction("", [], "y") == ""
    assert fix_list_conjunction("I 20; B 5", ["B 5", "I 20"], "y") == "I 20; B 5"


@pytest.mark.parametrize(
    ("items", "expected"),
    [
        (["B 5", "I 20"], "B 5 e I 20"),
        (["B 5", "N 33", "I 20"], "B 5, N 33 e I 20"),
        (["I 20", "B 5"], "I 20 y B 5"),
        (["B 5", "O 70"], "B 5 y O 70"),
        (["Ana", "Isabel"], "Ana e Isabel"),
        (["Ana", "Hilda"], "Ana e Hilda"),
        (["Ana", "Hielo"], "Ana y Hielo"),
        (["Ana"], "Ana"),
        ([], ""),
    ],
)
def test_spanish_and_lists(items: list[str], expected: str) -> None:
    assert Localization.format_list_and("es", items) == expected
    assert Localization.format_list("es", items) == expected


@pytest.mark.parametrize(
    ("items", "expected"),
    [
        (["N 33", "O 70"], "N 33 u O 70"),
        (["siete", "8"], "siete u 8"),
        (["Ana", "Hotel"], "Ana u Hotel"),
        (["Ana", "Hockey"], "Ana o Hockey"),
        (["B 5", "N 33", "O 70"], "B 5, N 33 u O 70"),
        (["O 70", "B 5"], "O 70 o B 5"),
        (["N 33", "I 20"], "N 33 o I 20"),
    ],
)
def test_spanish_or_lists(items: list[str], expected: str) -> None:
    assert Localization.format_list_or("es", items) == expected


def test_other_languages_keep_their_own_list_rules() -> None:
    assert Localization.format_list_and("en", ["B 5", "I 20"]) == "B 5 and I 20"
    assert Localization.format_list_or("en", ["N 33", "O 70"]) == "N 33 or O 70"
    # Portuguese already writes "e" for "and" in every position.
    assert Localization.format_list_and("pt", ["B 5", "I 20"]) == "B 5 e I 20"
    assert Localization.format_list_or("pt", ["N 33", "O 70"]) == "N 33 ou O 70"


def test_spanish_messages_pick_the_conjunction_from_the_next_name() -> None:
    def spanish(message_id: str, **kwargs: object) -> str:
        return Localization.get("es", message_id, **kwargs)

    assert (
        spanish("ageofheroes-road-built", tribe1="Ana", tribe2="Isabel")
        == "Ana e Isabel ahora están conectados por camino."
    )
    assert (
        spanish("ageofheroes-road-built", tribe1="Ana", tribe2="Pedro")
        == "Ana y Pedro ahora están conectados por camino."
    )
    assert (
        spanish("ageofheroes-road-built-you", tribe2="Ignacio")
        == "Tú e Ignacio ahora están conectados por camino."
    )
    assert (
        spanish("friend-error-blocked", username="Irene")
        == "Las solicitudes de amistad no están disponibles entre tú e Irene."
    )
    assert (
        spanish("team-arrangement-swapped-you", first="Ana", second="Iván")
        == "Intercambiaste de equipo a Ana e Iván."
    )


def test_spanish_citadels_lists_use_u_before_a_word_starting_with_o() -> None:
    def spanish(message_id: str, **kwargs: object) -> str:
        return Localization.get("es", message_id, **kwargs)

    assert spanish("citadels-list-pair", first="Mago", last="Obispo") == "Mago u Obispo"
    assert spanish("citadels-list-pair", first="Mago", last="Rey") == "Mago o Rey"
    assert (
        spanish("citadels-list-series", head="Mago, Rey", last="Obispo")
        == "Mago, Rey, u Obispo"
    )
    assert (
        spanish("citadels-list-series", head="Mago, Rey", last="Ladrón")
        == "Mago, Rey, o Ladrón"
    )


def test_spanish_monopoly_amounts_use_u_before_eighty_something() -> None:
    def spanish(**kwargs: object) -> str:
        return Localization.get(
            "es", "monopoly-you-receive-mortgaged-brief", property="Avenida", **kwargs
        )

    assert spanish(interest="$33", unmortgage="$88").endswith(
        "de interés u $88 para levantar la hipoteca."
    )
    assert spanish(interest="$33", unmortgage="$99").endswith(
        "de interés o $99 para levantar la hipoteca."
    )


def test_english_citadels_list_is_unchanged() -> None:
    """Only the Spanish catalog uses ES_AND/ES_OR; other locales are untouched."""
    english = Localization.get("en", "citadels-list-pair", first="Mage", last="Bishop")
    assert english == "Mage or Bishop"
