import pytest
from server.games.pirates.game import PiratesGame, PiratesPlayer, PiratesOptions
from server.games.pirates.leveling import get_xp_for_level
from server.games.pirates.combat import do_attack
from server.users.test_user import MockUser

@pytest.fixture
def mock_users():
    return [MockUser("player1"), MockUser("player2")]

@pytest.fixture
def pirates_game(mock_users):
    game = PiratesGame()
    game.add_player("player1", mock_users[0])
    game.add_player("player2", mock_users[1])

    game.on_start()
    return game

def test_pirates_game_initialization(pirates_game):
    assert len(pirates_game.players) == 2
    assert pirates_game.status == "playing"
    assert pirates_game.round == 1

    player1 = pirates_game.get_player_by_name("player1")
    assert isinstance(player1, PiratesPlayer)
    assert player1.score == 0
    assert player1.level == 0
    assert player1.xp == 0

    # 18 gems on map
    assert sum(1 for g in pirates_game.gem_positions.values() if g != -1) == 18

def test_leveling_formula(pirates_game):
    assert get_xp_for_level(0) == 0
    assert get_xp_for_level(1) == 20
    assert get_xp_for_level(10) == 200
    assert get_xp_for_level(15) == 300
    assert get_xp_for_level(150) == 3000

    player1 = pirates_game.get_player_by_name("player1")

    # Gain 25 XP (should be level 1, 5/40 progress)
    player1.leveling.give_xp(pirates_game, "player1", 25)
    assert player1.level == 1
    assert player1.xp == 25

    # Gain 200 more XP (225 total XP)
    # Level 10 needs 200 XP, Level 11 needs 220 XP, Level 12 needs 240 XP.
    # Therefore, 225 XP brings the player to Level 11.
    player1.leveling.give_xp(pirates_game, "player1", 200)
    assert player1.level == 11
    assert player1.xp == 225

def test_golden_moon_multiplier(pirates_game):
    player1 = pirates_game.get_player_by_name("player1")

    # Round 1 (No Golden Moon)
    pirates_game.round = 1
    assert not pirates_game.golden_moon_active
    player1.leveling.give_xp(pirates_game, "player1", 10)
    assert player1.xp == 10

    # Round 3 (Golden Moon)
    pirates_game.round = 3
    # Actually golden_moon_active is set in _start_round, so let's set it manually for test
    pirates_game.golden_moon_active = True
    player1.leveling.give_xp(pirates_game, "player1", 10, golden_moon_multiplier=3.0)
    assert player1.xp == 40 # 10 + (10 * 3)

def test_movement_ranges(pirates_game):
    player1 = pirates_game.get_player_by_name("player1")

    # Level 0
    player1.leveling.level = 0
    assert pirates_game._is_move_enabled(player1) is None
    assert pirates_game._is_move_2_enabled(player1) == "pirates-requires-level-15"
    assert pirates_game._is_move_3_enabled(player1) == "pirates-requires-level-150"

    # Level 15
    player1.leveling.level = 15
    assert pirates_game._is_move_enabled(player1) is None
    assert pirates_game._is_move_2_enabled(player1) is None
    assert pirates_game._is_move_3_enabled(player1) == "pirates-requires-level-150"

    # Level 150
    player1.leveling.level = 150
    assert pirates_game._is_move_enabled(player1) is None
    assert pirates_game._is_move_2_enabled(player1) is None
    assert pirates_game._is_move_3_enabled(player1) is None

def test_skill_unlocks(pirates_game):
    player1 = pirates_game.get_player_by_name("player1")
    player1.leveling.level = 0

    from server.games.pirates.skills import (
        SAILORS_INSTINCT, PORTAL, GEM_SEEKER, SWORD_FIGHTER, PUSH,
        SKILLED_CAPTAIN, BATTLESHIP, DOUBLE_DEVASTATION
    )

    assert not SAILORS_INSTINCT.is_unlocked(player1)

    player1.leveling.level = 10
    assert SAILORS_INSTINCT.is_unlocked(player1)
    assert not PORTAL.is_unlocked(player1)

    player1.leveling.level = 25
    assert PORTAL.is_unlocked(player1)
    assert not GEM_SEEKER.is_unlocked(player1)

    player1.leveling.level = 40
    assert GEM_SEEKER.is_unlocked(player1)
    assert not SWORD_FIGHTER.is_unlocked(player1)

    player1.leveling.level = 60
    assert SWORD_FIGHTER.is_unlocked(player1)
    assert not PUSH.is_unlocked(player1)

    player1.leveling.level = 75
    assert PUSH.is_unlocked(player1)
    assert not SKILLED_CAPTAIN.is_unlocked(player1)

    player1.leveling.level = 90
    assert SKILLED_CAPTAIN.is_unlocked(player1)
    assert not BATTLESHIP.is_unlocked(player1)

    player1.leveling.level = 125
    assert BATTLESHIP.is_unlocked(player1)
    assert not DOUBLE_DEVASTATION.is_unlocked(player1)

    player1.leveling.level = 200
    assert DOUBLE_DEVASTATION.is_unlocked(player1)

def test_sailors_instinct_radar(pirates_game):
    player1 = pirates_game.get_player_by_name("player1")
    player2 = pirates_game.get_player_by_name("player2")

    # Give the skill
    player1.leveling.level = 10

    from server.games.pirates.skills import SAILORS_INSTINCT

    # Setup controlled positions
    player1.position = 1
    player2.position = 3 # In same sector

    # Clear all gems, place exactly 2 gems in sector 1 (tiles 1-5)
    for i in range(1, 41):
        pirates_game.gem_positions[i] = -1

    pirates_game.gem_positions[2] = 0 # Type 0 (Common)
    pirates_game.gem_positions[4] = 1 # Type 1 (Rare)

    # Intercept status_box call to verify output
    status_lines = []
    original_status_box = pirates_game.status_box
    def mock_status_box(player, lines):
        status_lines.extend(lines)
    pirates_game.status_box = mock_status_box

    result = SAILORS_INSTINCT.do_action(pirates_game, player1)
    assert result == "continue"

    # Restore original function
    pirates_game.status_box = original_status_box

    # We expect Sector 1 (1-5) to have 2 gems and 1 player (player2)
    # The output string format is localized, so we search for numbers

    # Check lines
    sector_1_line = status_lines[3] # 0 is pos, 1 is empty, 2 is header, 3 is Sector 1

    assert "1" in sector_1_line and "5" in sector_1_line # Tiles 1-5

    # Check pluralization numbers
    assert "2 " in sector_1_line # 2 gems
    assert "1 " in sector_1_line # 1 player

    # Sector 2 should have 0 gems and 0 players
    sector_2_line = status_lines[4]
    assert "6" in sector_2_line and "10" in sector_2_line
    assert "0 " in sector_2_line

def test_combat_mechanics(pirates_game, monkeypatch):
    player1 = pirates_game.get_player_by_name("player1")
    player2 = pirates_game.get_player_by_name("player2")

    # Give them some initial XP and a gem for stealing
    player1.leveling.xp = 0
    player2.leveling.xp = 0
    player2.add_gem(0, 1) # Type 0, Value 1

    # 1. Test Attack Miss (Defender gets XP)
    # Monkeypatch random to force attacker to roll 1 and defender to roll 6
    original_randint = __import__('random').randint
    def mock_randint(a, b):
        if a == 1 and b == 6:
            # We are called for attack_roll then defense_roll
            mock_randint.call_count = getattr(mock_randint, 'call_count', 0) + 1
            if mock_randint.call_count == 1:
                return 1 # attacker
            elif mock_randint.call_count == 2:
                mock_randint.call_count = 0 # reset
                return 6 # defender
        return original_randint(a, b)

    monkeypatch.setattr('random.randint', mock_randint)

    result = do_attack(pirates_game, player1, player2)
    assert not result.hit
    assert player1.xp == 0
    # Defender should get between 10-30 XP (so xp > 0)
    assert player2.xp > 0

    # 2. Test Attack Hit (Attacker gets XP)
    player2.leveling.xp = 0 # reset

    def mock_randint_hit(a, b):
        if a == 1 and b == 6:
            mock_randint_hit.call_count = getattr(mock_randint_hit, 'call_count', 0) + 1
            if mock_randint_hit.call_count == 1:
                return 6 # attacker
            elif mock_randint_hit.call_count == 2:
                mock_randint_hit.call_count = 0 # reset
                return 1 # defender
        if a == 50 and b == 150:
            return 100 # Fixed XP
        return original_randint(a, b)

    monkeypatch.setattr('random.randint', mock_randint_hit)

    # We also need to mock _handle_boarding because it might try to use user.show_menu
    # which fails for MockUsers
    def mock_handle_boarding(*args, **kwargs):
        pass
    monkeypatch.setattr('server.games.pirates.combat._handle_boarding', mock_handle_boarding)

    result = do_attack(pirates_game, player1, player2)
    assert result.hit
    assert player1.xp == 100
    assert player2.xp == 0
