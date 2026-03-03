# Coup

Welcome to Coup, an intense game of deduction, deception, and political maneuvering. Set in a dystopian future where the government is run for profit by a new "royal class" of multinational CEOs, you are the head of a family vying for power. Your goal is to be the last player standing by eliminating the influence of your rivals and forcing them into exile. In Coup, bluffing is not just an option—it is often a necessity.

## Components and Setup

- **The Deck**: There are 15 character cards in the deck, consisting of 3 copies of each of the 5 characters: Duke, Assassin, Captain, Ambassador, and Contessa.
- **Starting State**: Every player starts with 2 coins and 2 face-down character cards (your "influences"). You only lose when you lose both of your influences.

## Core Rules and Actions

On your turn, you may perform exactly **one** action. If the action requires a specific character, you must claim that you have that character. You don't have to actually have the card—you just have to claim it!

### Standard Actions (No character required)
- **Income**: Take 1 coin from the treasury. This action is perfectly safe and cannot be blocked.
- **Foreign Aid**: Take 2 coins from the treasury. (Can be blocked by anyone claiming the Duke).
- **Coup**: Pay 7 coins to launch a Coup against another player. That player immediately loses one influence. A Coup cannot be blocked or challenged. **If you start your turn with 10 or more coins, you must take the Coup action.**

### Character Actions
- **Duke (Tax)**: Take 3 coins from the treasury.
- **Assassin (Assassinate)**: Pay 3 coins and choose a target player. If successful, that player loses an influence. (Can be blocked by the Contessa).
- **Captain (Steal)**: Steal 2 coins from another player. If they only have 1 coin, steal 1. (Can be blocked by the Captain or the Ambassador).
- **Ambassador (Exchange)**: Draw 2 cards from the deck, look at them along with your current face-down cards, and return exactly 2 cards to the deck.

## Challenges and Blocks (The Interrupt Window)

Whenever a player claims a character—either to perform an action (like Tax) or to block an action (like the Duke blocking Foreign Aid)—a brief window of time opens (usually 5 to 7 seconds). During this time, any other player can react using their Keyboard Shortcuts.

### Challenging a Claim
If you think someone is bluffing, you can challenge them.
- If they **were telling the truth**, they reveal the claimed card, shuffle it back into the deck, and draw a new card. You, the challenger, lose an influence for being wrong!
- If they **were bluffing**, they fail to perform their action and must lose an influence.

### Blocking an Action
Some actions can be blocked by specific characters. For example, if Alice tries to steal from Bob, Bob can claim he has the Captain to block it. This block is a claim itself, meaning Alice (or anyone else) can now challenge Bob's claim of having the Captain!

## Step-by-Step Example

1. **Action**: Alice says, "I claim the Duke and take 3 coins for Tax."
2. **Interrupt Window**: A timer starts. Bob thinks Alice is lying. He presses `c` to Challenge.
3. **Resolution**:
   - If Alice *has* the Duke, she reveals it. Bob loses an influence. Alice gets her 3 coins.
   - If Alice *does not have* the Duke, her action fails (no coins) and she loses an influence.

## Keyboard Shortcuts

During the fast-paced interrupt window, using keyboard shortcuts is highly recommended, especially for screen reader users.

### Reaction Shortcuts (Interrupt Window)
- **c** : Challenge a claim or block.
- **v** : Block an action targeted at you (or block Foreign Aid).
- **p** : Pass (agreeing not to challenge or block). If everyone passes, the timer fast-forwards.

### Information Shortcuts (Anytime)
- **w** : Check Wealth (Lists all alive players and their coins).
- **h** : Check Hand (Reminds you of your current face-down cards).
- **l** : Check Table (Lists all the dead, revealed cards on the table).