"""Pytest configuration and fixtures."""

import pytest
import shutil
import sys
import tempfile
import uuid
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Initialize localization for tests
from ..messages.localization import Localization

_locales_dir = Path(__file__).parent.parent / "locales"
Localization.init(_locales_dir)


@pytest.fixture(autouse=True)
def _isolate_localization():
    """Give every test an isolated localization environment.

    ``Localization`` keeps its loaded bundles and active locales dir in
    class-level state. Some tests deliberately repoint or wipe that state
    (e.g. the MOTD fixture nulls ``_locales_dir``/``_bundles`` to force raw
    keys). Without isolation that leaks to whichever test runs next in the same
    process — invisible serially because of ordering luck, but a source of
    intermittent, order-dependent failures under ``pytest-xdist``. Snapshotting
    and restoring the class state around each test makes the suite parallel-safe
    and keeps the leak contained no matter what a test does internally.
    """
    saved_dir = Localization._locales_dir
    saved_bundles = Localization._bundles
    saved_cache = Localization._bundle_cache_by_dir
    saved_locale_codes = Localization._available_locale_codes_cache
    # Re-pin the canonical locales dir in case a prior test left it nulled.
    Localization.init(_locales_dir)
    try:
        yield
    finally:
        Localization._locales_dir = saved_dir
        Localization._bundles = saved_bundles
        Localization._bundle_cache_by_dir = saved_cache
        Localization._available_locale_codes_cache = saved_locale_codes
        Localization._resolve_locale_from_catalog.cache_clear()


@pytest.fixture
def tmp_path() -> Path:
    """Use a dedicated temp root that is writable for pytest and SQLite."""
    base = Path(tempfile.gettempdir()) / "playaural-tests"
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"tmp_{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def mock_user():
    """Create a mock user."""
    from ..users.test_user import MockUser

    return MockUser("TestPlayer")


@pytest.fixture
def bot():
    """Create a bot user."""
    from ..users.bot import Bot

    return Bot("TestBot")


@pytest.fixture
def pig_game():
    """Create a fresh Pig game."""
    from ..games.pig.game import PigGame

    return PigGame()


@pytest.fixture
def pig_game_with_players():
    """Create a Pig game with two players."""
    from ..games.pig.game import PigGame
    from ..users.test_user import MockUser

    game = PigGame()
    user1 = MockUser("Alice")
    user2 = MockUser("Bob")
    game.add_player("Alice", user1)
    game.add_player("Bob", user2)
    return game, user1, user2

