"""Tests for Coup game."""

import pytest
from server.games.coup.game import CoupGame
from server.games.coup.cards import Character, Card
from server.users.test_user import MockUser

@pytest.fixture
def game():
    """Create a new Coup game with 2 players."""
    g = CoupGame()
    g.players.append(g.create_player("player1", "Alice"))
    g.players.append(g.create_player("player2", "Bob"))

    # Attach mock users
    g.attach_user("player1", MockUser("Alice", "player1"))
    g.attach_user("player2", MockUser("Bob", "player2"))

    g.on_start()
    return g

@pytest.fixture
def game3():
    """Create a new Coup game with 3 players: Alice, Bob, Charlie."""
    g = CoupGame()
    g.players.append(g.create_player("player1", "Alice"))
    g.players.append(g.create_player("player2", "Bob"))
    g.players.append(g.create_player("player3", "Charlie"))

    g.attach_user("player1", MockUser("Alice", "player1"))
    g.attach_user("player2", MockUser("Bob", "player2"))
    g.attach_user("player3", MockUser("Charlie", "player3"))

    g.on_start()
    return g

def advance_ticks(game, ticks=100):
    for _ in range(ticks):
        game.on_tick()

def advance_until(game, condition_fn, max_ticks=500):
    """Advance one tick at a time until condition_fn() returns True.
    Returns True if condition was met, False if max_ticks exhausted."""
    for _ in range(max_ticks):
        game.on_tick()
        if condition_fn():
            return True
    return False

def test_income(game):
    """Test the income action."""
    alice = game.get_player_by_name("Alice")
    initial_coins = alice.coins
    game._action_income(alice, "income")
    # Action is snappy but the game needs a tick
    assert alice.coins == initial_coins + 1
    assert game.current_player.name == "Bob"

def test_coup_action(game):
    """Test the coup action."""
    alice = game.get_player_by_name("Alice")
    bob = game.get_player_by_name("Bob")

    alice.coins = 7
    game._action_coup(alice, "Bob", "coup")
    advance_ticks(game, 150)

    assert alice.coins == 0
    assert game.turn_phase == "losing_influence"
    assert game._losing_player_id == bob.id

    # Bob loses an influence
    game._action_lose_influence(bob, "lose_influence_0")
    advance_ticks(game, 100)
    assert len(bob.live_influences) == 1
    assert game.current_player.name == "Bob"

def test_foreign_aid_and_block(game):
    """Test foreign aid and block."""
    alice = game.get_player_by_name("Alice")
    bob = game.get_player_by_name("Bob")

    game._action_foreign_aid(alice, "foreign_aid")
    assert game.turn_phase == "action_declared"
    assert game.active_action == "foreign_aid"
    assert game.active_claimer_id == alice.id

    # Bob blocks
    game._action_block(bob, "block")
    assert game.turn_phase == "waiting_block"
    assert game.active_claimer_id == bob.id

def test_assassinate_and_challenge(game):
    """Test assassinate and challenge."""
    alice = game.get_player_by_name("Alice")
    bob = game.get_player_by_name("Bob")

    # Force Alice to not have Assassin to guarantee she loses the challenge
    alice.influences = [Card(Character.DUKE), Card(Character.CONTESSA)]
    alice.coins = 3

    game._action_assassinate(alice, "Bob", "assassinate")
    assert game.turn_phase == "action_declared"
    assert game.active_target_id == bob.id

    # Bob challenges Alice
    game._action_challenge(bob, "challenge")
    advance_ticks(game, 150)
    advance_ticks(game, 50)

    # Alice failed challenge (didn't have Assassin)
    # So Alice loses an influence immediately, and action fails.
    assert game.turn_phase == "losing_influence"
    assert game._losing_player_id == alice.id

    # Alice chooses to lose the first one
    game._action_lose_influence(alice, "lose_influence_0")
    advance_ticks(game, 100)

    assert len(alice.live_influences) == 1

    # Turn ends
    assert game.current_player.name == "Bob"

def test_steal_block_and_failed_challenge(game):
    """Test steal, Ambassador block, and the blocker successfully defending a challenge."""
    alice = game.get_player_by_name("Alice")
    bob = game.get_player_by_name("Bob")

    alice.coins = 2
    bob.coins = 2
    # Bob has an Ambassador
    bob.influences = [Card(Character.AMBASSADOR), Card(Character.CONTESSA)]

    game._action_steal(alice, "Bob", "steal")
    assert game.turn_phase == "action_declared"

    # Bob blocks with Ambassador
    game._action_block(bob, "block")
    assert game.turn_phase == "waiting_block"
    assert game.active_claimer_id == bob.id
    assert game.original_claimer_id == alice.id

    # Alice challenges Bob's block
    game._action_challenge(alice, "challenge")
    advance_ticks(game, 150)
    advance_ticks(game, 50)

    # Bob DOES have the Ambassador, so the challenge fails (Alice is wrong)
    # Alice loses influence; active_target_id must remain Bob (the original steal target)
    assert game.turn_phase == "losing_influence"
    assert game.active_target_id == bob.id

    # Bob successfully blocked, meaning Alice's steal fails and turn should end after she loses influence
    assert game._next_action_after_lose == "end_turn"
    assert game._losing_player_id == alice.id

    # Alice chooses to lose the first one
    game._action_lose_influence(alice, "lose_influence_0")
    advance_ticks(game, 100)
    assert len(alice.live_influences) == 1

    # Turn ends
    assert game.current_player.name == "Bob"
    # Coins didn't change because steal failed
    assert alice.coins == 2
    assert bob.coins == 2


def test_assassination_third_party_challenger_target_not_swapped(game3):
    """Regression: when a third party challenges an assassination and loses the challenge,
    active_target_id must NOT be overwritten.  The assassination must resolve against the
    original target (Charlie), not the challenger (Bob)."""
    alice = game3.get_player_by_name("Alice")
    bob = game3.get_player_by_name("Bob")
    charlie = game3.get_player_by_name("Charlie")

    # Give Alice an Assassin so she wins any challenge
    alice.influences = [Card(Character.ASSASSIN), Card(Character.DUKE)]
    alice.coins = 3
    # Bob has 2 cards and no Assassin (so he'll lose his challenge)
    bob.influences = [Card(Character.DUKE), Card(Character.CONTESSA)]
    charlie.influences = [Card(Character.CAPTAIN), Card(Character.AMBASSADOR)]

    # Alice assassinates Charlie
    game3._action_assassinate(alice, "Charlie", "assassinate")
    assert game3.active_target_id == charlie.id
    assert game3.active_action == "assassinate"

    # Bob (third party) challenges Alice's Assassin claim
    game3._action_challenge(bob, "challenge")
    advance_ticks(game3, 200)

    # Alice has the Assassin — challenge FAILS for Bob.
    # Bob must lose an influence.  active_target_id must still be Charlie.
    assert game3.active_target_id == charlie.id
    assert game3._losing_player_id == bob.id
    assert game3.turn_phase == "losing_influence"

    # Bob chooses which card to lose
    game3._action_lose_influence(bob, "lose_influence_0")
    advance_ticks(game3, 200)

    # Assassination now resolves: Charlie (not Bob) must lose an influence
    assert game3._losing_player_id == charlie.id
    assert game3.turn_phase == "losing_influence"

    # Bob still has 1 card (lost 1 from the failed challenge)
    assert len(bob.live_influences) == 1
    assert not bob.is_dead

    # Charlie has not yet lost a card (resolve is pending her choice)
    assert len(charlie.live_influences) == 2


# ── Bot Lose-Influence Regression Tests ──────────────────────────────────────

def test_bot_loses_influence_when_couped():
    """A bot that is the direct target of a Coup must auto-discard an influence."""
    g = CoupGame()
    alice = g.create_player("p1", "Alice")
    bot = g.create_player("b1", "BotBob", is_bot=True)
    g.players = [alice, bot]
    g.attach_user("p1", MockUser("Alice", "p1"))
    # setup_player_actions must be called so execute_action can find lose_influence_* actions
    g.setup_player_actions(alice)
    g.setup_player_actions(bot)
    g.on_start()

    # Ensure bot has 2 live cards so the choice is non-trivial
    from server.games.coup.cards import Card, Character
    bot.influences = [Card(Character.DUKE), Card(Character.CONTESSA)]

    alice.coins = 7
    g._action_coup(alice, "BotBob", "coup")

    # Wait until game enters losing_influence for the bot
    reached = advance_until(g, lambda: g.turn_phase == "losing_influence" and g._losing_player_id == bot.id)
    assert reached, "Game never entered losing_influence for bot"
    assert g._losing_player_id == bot.id

    # Wait until bot auto-discards and the game exits losing_influence
    reached = advance_until(g, lambda: len(bot.live_influences) == 1 and g.turn_phase != "losing_influence")
    assert reached, "Bot never discarded an influence or game never exited losing_influence"
    assert len(bot.live_influences) == 1


def test_bot_challenger_loses_influence_while_active_target_differs():
    """Regression: bot challenges and loses; active_target_id differs from
    _losing_player_id.  The bot must still auto-discard without freezing."""
    g = CoupGame()
    alice = g.create_player("p1", "Alice")
    bot = g.create_player("b1", "BotBob", is_bot=True)
    charlie = g.create_player("p3", "Charlie")
    g.players = [alice, bot, charlie]
    g.attach_user("p1", MockUser("Alice", "p1"))
    g.attach_user("p3", MockUser("Charlie", "p3"))
    # setup_player_actions must be called so execute_action can find lose_influence_* actions
    g.setup_player_actions(alice)
    g.setup_player_actions(bot)
    g.setup_player_actions(charlie)
    g.on_start()

    from server.games.coup.cards import Card, Character
    # Alice has Assassin so she wins any challenge
    alice.influences = [Card(Character.ASSASSIN), Card(Character.DUKE)]
    alice.coins = 3
    # Bot has two cards but no Assassin — it will lose the challenge
    bot.influences = [Card(Character.DUKE), Card(Character.CONTESSA)]
    charlie.influences = [Card(Character.CAPTAIN), Card(Character.AMBASSADOR)]

    # Alice assassinates Charlie
    g._action_assassinate(alice, "Charlie", "assassinate")
    assert g.active_target_id == charlie.id

    # Bot challenges Alice's claim — and loses (Alice has Assassin)
    g._action_challenge(bot, "challenge")

    # Wait until game enters losing_influence for the bot (active_target_id must still be Charlie)
    reached = advance_until(g, lambda: g.turn_phase == "losing_influence" and g._losing_player_id == bot.id)
    assert reached, "Game never entered losing_influence for bot"
    assert g.active_target_id == charlie.id
    assert g._losing_player_id == bot.id

    # Wait until bot auto-discards (live_influences drops to 1)
    reached = advance_until(g, lambda: len(bot.live_influences) == 1)
    assert reached, "Bot never discarded an influence"
    assert len(bot.live_influences) == 1

    # Assassination must now resolve: Charlie must be the one losing an influence
    reached = advance_until(g, lambda: g.turn_phase == "losing_influence" and g._losing_player_id == charlie.id)
    assert reached, "Assassination never resolved against Charlie"
    assert g.active_target_id == charlie.id
    assert g._losing_player_id == charlie.id


# ── Immortal-Player Regression Tests ────────────────────────────────────────


def test_zero_cards_player_is_marked_dead_on_lose_influence():
    """Regression: A player with 0 live cards but is_dead=False must be
    eliminated when _prompt_lose_influence is called (safety net)."""
    g = CoupGame()
    alice = g.create_player("p1", "Alice")
    bob = g.create_player("p2", "Bob")
    g.players = [alice, bob]
    g.attach_user("p1", MockUser("Alice", "p1"))
    g.attach_user("p2", MockUser("Bob", "p2"))
    g.on_start()

    # Manually corrupt Bob into the "immortal" state: 0 cards, not dead
    bob.influences = []
    bob.is_dead = False

    # Now trigger _prompt_lose_influence for Bob (e.g. from a coup)
    g._next_action_after_lose = "end_turn"
    g._prompt_lose_influence(bob.id, "coup")

    # Bob must now be dead
    assert bob.is_dead is True
    assert len(bob.live_influences) == 0


def test_bluffed_block_on_assassination_kills_blocker_then_target(game3):
    """Full flow: Alice assassinates Charlie, Charlie bluff-blocks (no Contessa),
    Alice challenges the block successfully.  Charlie loses a card from the
    failed bluff, then the assassination resolves and takes the second card."""
    alice = game3.get_player_by_name("Alice")
    bob = game3.get_player_by_name("Bob")
    charlie = game3.get_player_by_name("Charlie")

    from server.games.coup.cards import Card, Character

    alice.influences = [Card(Character.ASSASSIN), Card(Character.DUKE)]
    alice.coins = 3
    bob.influences = [Card(Character.CAPTAIN), Card(Character.AMBASSADOR)]
    # Charlie has 2 cards, no Contessa — bluff block will fail
    charlie.influences = [Card(Character.DUKE), Card(Character.CAPTAIN)]

    # Alice assassinates Charlie
    game3._action_assassinate(alice, "Charlie", "assassinate")
    assert game3.active_target_id == charlie.id

    # Charlie blocks (claims Contessa — bluffing)
    game3._action_block(charlie, "block")
    assert game3.turn_phase == "waiting_block"
    assert game3.active_claimer_id == charlie.id

    # Alice challenges the block — Charlie doesn't have Contessa
    game3._action_challenge(alice, "challenge")
    advance_ticks(game3, 200)

    # Charlie must lose a card from the failed bluff
    assert game3.turn_phase == "losing_influence"
    assert game3._losing_player_id == charlie.id
    assert game3._next_action_after_lose == "resolve_action"

    # Charlie picks which card to lose
    game3._action_lose_influence(charlie, "lose_influence_0")
    assert len(charlie.live_influences) == 1

    # Wait for the full chain: post_lose_influence → resolve_action (assassinate)
    # → prompt_lose_influence (auto-lose 2nd card) → post_lose_influence → end_turn
    reached = advance_until(game3, lambda: charlie.is_dead)
    assert reached, "Charlie was never eliminated after bluffed block + assassination"
    assert len(charlie.live_influences) == 0
    assert charlie.is_dead is True


def test_exchange_return_count_matches_draw_count():
    """Exchange that draws fewer than 2 cards (near-empty deck)
    must only require returning that many cards."""
    g = CoupGame()
    alice = g.create_player("p1", "Alice")
    bob = g.create_player("p2", "Bob")
    g.players = [alice, bob]
    g.attach_user("p1", MockUser("Alice", "p1"))
    g.attach_user("p2", MockUser("Bob", "p2"))
    g.on_start()

    from server.games.coup.cards import Card, Character

    # Leave only 1 card in the deck
    g.deck.cards = [Card(Character.CONTESSA)]
    alice.influences = [Card(Character.AMBASSADOR), Card(Character.DUKE)]
    alice.coins = 2

    # Simulate exchange resolving (skip the interrupt window)
    g.original_claimer_id = alice.id
    g.active_action = "exchange"
    g._resolve_action()

    # Only 1 card was drawn → _exchange_draw_count must be 1
    assert g._exchange_draw_count == 1
    assert g.turn_phase == "exchanging"
    assert len(alice.live_influences) == 3  # 2 original + 1 drawn

    # Return 1 card — exchange should complete (not wait for a second return)
    g._action_return_card(alice, "return_card_0")
    assert len(alice.live_influences) == 2
    # Turn should have ended (exchange complete after 1 return)
    assert g.turn_phase != "exchanging"


def test_exchange_empty_deck_skips_exchange_phase():
    """Exchange with a completely empty deck should complete immediately
    without entering the exchange phase."""
    g = CoupGame()
    alice = g.create_player("p1", "Alice")
    bob = g.create_player("p2", "Bob")
    g.players = [alice, bob]
    g.attach_user("p1", MockUser("Alice", "p1"))
    g.attach_user("p2", MockUser("Bob", "p2"))
    g.on_start()

    from server.games.coup.cards import Card, Character

    g.deck.cards = []  # Empty deck
    alice.influences = [Card(Character.AMBASSADOR), Card(Character.DUKE)]

    g.original_claimer_id = alice.id
    g.active_action = "exchange"
    g._resolve_action()

    # No cards drawn, exchange phase should be skipped entirely
    assert g.turn_phase != "exchanging"
    assert len(alice.live_influences) == 2  # Unchanged


def test_bot_never_passes_when_assassination_is_lethal():
    """A bot with 1 card and no Contessa must ALWAYS challenge or block
    when being assassinated — passing is guaranteed death."""
    from server.games.coup.bot import CoupBot

    g = CoupGame()
    alice = g.create_player("p1", "Alice")
    bot = g.create_player("b1", "BotBob", is_bot=True)
    g.players = [alice, bot]
    g.attach_user("p1", MockUser("Alice", "p1"))
    g.setup_player_actions(alice)
    g.setup_player_actions(bot)
    g.on_start()

    # Run 50 independent trials to verify the bot never passes.
    # Each trial sets up the exact scenario: bot has 1 card (Duke, not Contessa),
    # Alice declares assassination.
    pass_count = 0
    for _ in range(50):
        bot.influences = [Card(Character.DUKE)]
        bot.is_dead = False
        alice.influences = [Card(Character.ASSASSIN), Card(Character.CAPTAIN)]
        alice.coins = 3

        g.active_action = "assassinate"
        g.active_claimer_id = alice.id
        g.original_claimer_id = alice.id
        g.active_target_id = bot.id
        g.turn_phase = "action_declared"
        g.interrupt_timer_ticks = 100
        g.is_resolving = False
        g.passed_players = set()

        decision = CoupBot.bot_think(g, bot)
        if decision == "pass":
            pass_count += 1

    assert pass_count == 0, (
        f"Bot passed {pass_count}/50 times when assassination was lethal — "
        f"it should always challenge or bluff-block"
    )
