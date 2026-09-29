"""Coverage for canonical account gender and localized grammatical forms."""

from pathlib import Path

import pytest

from server.gender import (
    GENDER_OPTIONS,
    Gender,
    gender_localization_kwargs,
    normalize_gender,
    require_gender,
)
from server.games.coup.game import CoupGame
from server.games.metalpipe.game import MetalPipeGame
from server.games.pig.game import PigGame
from server.games.tradeoff.game import TradeoffGame
from server.messages.localization import Localization
from server.persistence.database import Database
from server.tables.table import Table
from server.users.bot import Bot
from server.users.test_user import MockUser


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Gender.MALE, Gender.MALE),
        ("Male", Gender.MALE),
        ("male", Gender.MALE),
        (" FEMALE ", Gender.FEMALE),
        ("non-binary", Gender.NON_BINARY),
        ("unspecified", Gender.UNSPECIFIED),
        ("Not set", Gender.UNSPECIFIED),
        (None, Gender.UNSPECIFIED),
        ("forged", Gender.UNSPECIFIED),
    ],
)
def test_gender_normalization_is_canonical_and_neutral_by_default(
    value: object,
    expected: Gender,
) -> None:
    assert normalize_gender(value) is expected


def test_gender_mutations_reject_unknown_values_and_kwargs_are_bounded() -> None:
    assert require_gender("female") is Gender.FEMALE
    assert gender_localization_kwargs(Gender.FEMALE, "target_player") == {
        "target_player_gender": "female"
    }
    with pytest.raises(ValueError):
        require_gender("female); DROP TABLE users")
    with pytest.raises(ValueError):
        MockUser("Alex").set_gender("forged")
    for invalid_variable in ("", "1player", "player-name", "player name", "người"):
        with pytest.raises(ValueError):
            gender_localization_kwargs(Gender.MALE, invalid_variable)


def test_gender_options_have_unique_stable_protocol_and_locale_values() -> None:
    assert len({gender.value for gender in GENDER_OPTIONS}) == len(GENDER_OPTIONS)
    assert len({gender.selector for gender in GENDER_OPTIONS}) == len(GENDER_OPTIONS)
    assert len({gender.menu_item_id for gender in GENDER_OPTIONS}) == len(GENDER_OPTIONS)
    for gender in GENDER_OPTIONS:
        assert Localization.get("en", gender.localization_key) != gender.localization_key
        assert Localization.get("vi", gender.localization_key) != gender.localization_key


@pytest.mark.parametrize(
    ("gender", "subject", "possessive"),
    [
        (Gender.MALE, "he", "his"),
        (Gender.FEMALE, "she", "her"),
        (Gender.NON_BINARY, "they", "their"),
        (Gender.UNSPECIFIED, "they", "their"),
    ],
)
def test_english_gender_terms_select_expected_forms(
    gender: Gender,
    subject: str,
    possessive: str,
) -> None:
    assert Localization._format_gender_term("en", gender, "subject") == subject
    assert (
        Localization._format_gender_term("en", gender, "possessive-determiner")
        == possessive
    )


def test_vietnamese_gender_terms_use_selected_or_neutral_forms() -> None:
    assert Localization._format_gender_term("vi", Gender.MALE, "subject") == "anh ấy"
    assert Localization._format_gender_term("vi", Gender.FEMALE, "subject") == "cô ấy"
    for neutral_gender in (Gender.NON_BINARY, Gender.UNSPECIFIED):
        for form in (
            "subject",
            "subject-capitalized",
            "object",
            "possessive-determiner",
            "possessive-pronoun",
            "reflexive",
        ):
            rendered = Localization._format_gender_term(
                "vi",
                neutral_gender,
                form,
            )
            assert "họ" in rendered.casefold()
            assert "chúng" not in rendered.casefold()


def test_neutral_english_sentences_preserve_plural_pronoun_agreement() -> None:
    substitution = Localization.get(
        "en",
        "player-substitution-self-incoming-consent-sent",
        player="Alex",
        player_gender=Gender.UNSPECIFIED.selector,
    )
    piracy = Localization.get(
        "en",
        "pirates-steal-no-gems-you",
        target="Alex",
        target_gender=Gender.UNSPECIFIED.selector,
    )

    assert "accepted by them" in substitution
    assert "their ship carries no gems" in piracy
    assert "they agrees" not in substitution
    assert "they carries" not in piracy


def test_contextual_gender_terms_are_data_driven_and_reject_payloads(
    tmp_path: Path,
) -> None:
    locales_dir = tmp_path / "locales"
    en_dir = locales_dir / "en"
    vi_dir = locales_dir / "vi"
    en_dir.mkdir(parents=True)
    vi_dir.mkdir()
    (en_dir / "main.ftl").write_text(
        """
gender-term-subject =
    { $gender ->
        [male] he
        [female] she
       *[other] they
    }
arena-gender-term-subject =
    { $gender ->
        [male] champion
        [female] champion
       *[other] champion
    }
""".strip(),
        encoding="utf-8",
    )
    (vi_dir / "main.ftl").write_text(
        """
gender-term-subject =
    { $gender ->
       *[other] họ
    }
""".strip(),
        encoding="utf-8",
    )
    Localization.init(locales_dir)

    assert (
        Localization._format_gender_term("en", Gender.FEMALE, "subject", "arena")
        == "champion"
    )
    assert (
        Localization._format_gender_term(
            "en",
            Gender.FEMALE,
            "not-a-supported-form",
            "../../arena); malicious",
        )
        == "she"
    )
    assert (
        Localization._format_gender_term("vi", Gender.FEMALE, "subject", "arena")
        == "họ"
    )


def test_database_validates_mutations_and_neutralizes_legacy_corruption(
    tmp_path: Path,
) -> None:
    database = Database(tmp_path / "gender.db")
    database.connect()
    try:
        record = database.create_user("Ada", "hash")
        assert record is not None
        database.update_user_gender(record.username, Gender.FEMALE.value)
        assert database.get_user_gender_by_uuid(record.uuid) is Gender.FEMALE

        with pytest.raises(ValueError):
            database.update_user_gender(record.username, "unknown")

        database._conn.execute(
            "UPDATE users SET gender = ? WHERE uuid = ?",
            ("legacy-corrupt-value", record.uuid),
        )
        database._conn.commit()
        assert database.get_user_gender_by_uuid(record.uuid) is Gender.UNSPECIFIED
        assert database.get_user(record.username).gender == Gender.UNSPECIFIED.value
        assert database.get_user_gender_by_uuid("deleted-account") is Gender.UNSPECIFIED
    finally:
        database.close()


def test_game_gender_lookup_uses_live_user_then_account_uuid(
    tmp_path: Path,
) -> None:
    database = Database(tmp_path / "seats.db")
    database.connect()
    try:
        record = database.create_user("Alice", "hash")
        assert record is not None
        database.update_user_gender(record.username, Gender.FEMALE.value)

        game = PigGame()
        table = Table("table", game.get_type(), record.username)
        table._db = database
        game._table = table
        user = MockUser(record.username, uuid=record.uuid, gender=Gender.MALE)
        player = game.add_player(record.username, user)

        assert game.get_player_gender(player) is Gender.MALE

        game._users.pop(player.id)
        assert game.get_player_gender(player) is Gender.FEMALE

        player.is_bot = True
        player.replaced_human = True
        game.attach_user(player.id, Bot("Replacement", uuid=player.id))
        assert game.get_player_gender(player) is Gender.FEMALE

        native_bot = game.add_player("Native bot", Bot("Native bot"))
        original_lookup = database.get_user_gender_by_uuid
        queried_ids: list[str] = []

        def tracked_lookup(player_id: str) -> Gender:
            queried_ids.append(player_id)
            return original_lookup(player_id)

        database.get_user_gender_by_uuid = tracked_lookup
        assert game.get_player_gender(native_bot) is Gender.UNSPECIFIED
        assert queried_ids == []
        gendered_bot = game.add_player(
            "Gendered bot",
            Bot("Gendered bot", gender=Gender.FEMALE),
        )
        assert game.get_player_gender(gendered_bot) is Gender.FEMALE
    finally:
        database.close()


def test_broadcast_resolver_adds_gender_without_overriding_explicit_data() -> None:
    game = PigGame()
    actor_user = MockUser("Alice", gender=Gender.FEMALE)
    observer_user = MockUser("Bob", gender=Gender.MALE)
    actor = game.add_player(actor_user.username, actor_user)
    game.add_player(observer_user.username, observer_user)
    actor_user.clear_messages()
    observer_user.clear_messages()

    game._broadcast_actor_l(
        actor,
        "pig-you-roll-result",
        "pig-player-roll-result",
        roll=4,
        total=4,
    )

    assert "Her turn total" in observer_user.get_last_spoken()
    resolved = game._resolve_broadcast_kwargs(
        "en",
        {"player": actor, "player_gender": Gender.MALE.selector},
    )
    assert resolved == {"player": actor.name, "player_gender": "male"}


def test_broadcast_resolver_neutralizes_ambiguous_duplicate_names() -> None:
    game = PigGame()
    game.add_player("Shared", MockUser("Shared", gender=Gender.MALE))
    game.add_player("Shared", MockUser("Shared", gender=Gender.FEMALE))

    assert game._resolve_broadcast_kwargs("en", {"player": "Shared"}) == {
        "player": "Shared",
        "player_gender": Gender.UNSPECIFIED.selector,
    }


def test_custom_per_listener_broadcasters_resolve_gender() -> None:
    coup = CoupGame()
    coup_actor_user = MockUser("Ada", gender=Gender.FEMALE)
    coup_observer_user = MockUser("Ben")
    coup_actor = coup.add_player(coup_actor_user.username, coup_actor_user)
    coup.add_player(coup_observer_user.username, coup_observer_user)
    coup_actor_user.clear_messages()
    coup_observer_user.clear_messages()

    coup._broadcast_influence_loss_l(coup_actor, "duke")
    assert "loses her Duke" in coup_observer_user.get_last_spoken()

    tradeoff = TradeoffGame()
    tradeoff_actor_user = MockUser("Ada", gender=Gender.FEMALE)
    tradeoff_observer_user = MockUser("Ben")
    tradeoff_actor = tradeoff.add_player(
        tradeoff_actor_user.username,
        tradeoff_actor_user,
    )
    tradeoff.add_player(tradeoff_observer_user.username, tradeoff_observer_user)
    tradeoff_actor_user.clear_messages()
    tradeoff_observer_user.clear_messages()

    tradeoff._broadcast_scoring_result(tradeoff_actor, [], 0)
    assert "her 15 dice" in tradeoff_observer_user.get_last_spoken()

    metalpipe = MetalPipeGame()
    metalpipe_actor_user = MockUser("Ada", gender=Gender.FEMALE)
    metalpipe_observer_user = MockUser("Ben")
    metalpipe_actor = metalpipe.add_player(
        metalpipe_actor_user.username,
        metalpipe_actor_user,
    )
    metalpipe.add_player(metalpipe_observer_user.username, metalpipe_observer_user)
    metalpipe_actor_user.clear_messages()
    metalpipe_observer_user.clear_messages()

    metalpipe._broadcast_bonk(metalpipe_actor, metalpipe_actor, is_self=True)
    assert "hits herself" in metalpipe_observer_user.get_last_spoken()
