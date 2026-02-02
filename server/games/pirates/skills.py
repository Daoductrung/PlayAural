"""
Skill System for Pirates of the Lost Seas.

Skills are stateless - they read/write state from the player's skill dicts.
This avoids complex serialization issues with polymorphic types.

Player stores skill state in simple dicts:
- skill_cooldowns: dict[str, int] - remaining cooldown turns
- skill_active: dict[str, int] - remaining active turns for buffs
- skill_uses: dict[str, int] - remaining uses for limited-use skills
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import random

from ...messages.localization import Localization

if TYPE_CHECKING:
    from .game import PiratesGame
    from .player import PiratesPlayer


# =============================================================================
# Base Skill Classes
# =============================================================================


class Skill(ABC):
    """
    Base class for all skills. Skills are stateless singletons.

    State (cooldowns, active duration, uses) is stored on the player,
    not on the skill instance.
    """

    name: str = ""
    description: str = ""
    required_level: int = 0
    skill_id: str = ""  # Unique identifier for state lookups

    @abstractmethod
    def can_perform(self, game: "PiratesGame", player: "PiratesPlayer") -> tuple[bool, str | None]:
        """Check if this skill can be performed."""
        ...

    @abstractmethod
    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        """Execute the skill. Returns 'end_turn' or 'continue'."""
        ...

    def on_turn_start(self, game: "PiratesGame", player: "PiratesPlayer") -> None:
        """Called at the start of the player's turn."""
        pass

    def get_menu_label(self, player: "PiratesPlayer", locale: str = "en") -> str:
        """Get the label for the skill menu."""
        return Localization.get(locale, self.name)

    def is_unlocked(self, player: "PiratesPlayer") -> bool:
        """Check if the player's level is high enough."""
        return player.level >= self.required_level


class CooldownSkill(Skill):
    """Base class for skills with a cooldown."""

    max_cooldown: int = 0

    def get_cooldown(self, player: "PiratesPlayer") -> int:
        """Get remaining cooldown turns."""
        return player.skill_cooldowns.get(self.skill_id, 0)

    def set_cooldown(self, player: "PiratesPlayer", value: int) -> None:
        """Set cooldown turns."""
        player.skill_cooldowns[self.skill_id] = value

    def is_on_cooldown(self, player: "PiratesPlayer") -> bool:
        """Check if the skill is currently on cooldown."""
        return self.get_cooldown(player) > 0

    def start_cooldown(self, player: "PiratesPlayer") -> None:
        """Start the cooldown timer."""
        self.set_cooldown(player, self.max_cooldown)

    def tick_cooldown(self, player: "PiratesPlayer") -> None:
        """Reduce cooldown by 1."""
        cd = self.get_cooldown(player)
        if cd > 0:
            self.set_cooldown(player, cd - 1)

    def on_turn_start(self, game: "PiratesGame", player: "PiratesPlayer") -> None:
        """Tick the cooldown at turn start."""
        self.tick_cooldown(player)


class BuffSkill(CooldownSkill):
    """Base class for skills that provide a temporary buff."""

    duration: int = 0

    def get_active(self, player: "PiratesPlayer") -> int:
        """Get remaining active turns."""
        return player.skill_active.get(self.skill_id, 0)

    def set_active(self, player: "PiratesPlayer", value: int) -> None:
        """Set active turns."""
        player.skill_active[self.skill_id] = value

    def is_active(self, player: "PiratesPlayer") -> bool:
        """Check if the buff is currently active."""
        return self.get_active(player) > 0

    def activate(self, player: "PiratesPlayer") -> None:
        """Activate the buff and start cooldown."""
        self.set_active(player, self.duration)
        self.start_cooldown(player)

    def tick_active(self, game: "PiratesGame", player: "PiratesPlayer") -> bool:
        """Reduce active duration by 1. Returns True if buff just expired."""
        active = self.get_active(player)
        if active > 0:
            self.set_active(player, active - 1)
            if active - 1 == 0:
                # game.broadcast_l("pirates-buff-expired", player=player.name, skill=self.name)
                # Manual broadcast for localized skill name
                for p in game.get_active_players():
                    u = game.get_user(p)
                    if u:
                        s_name = Localization.get(u.locale, self.name)
                        u.speak_l("pirates-buff-expired", buffer="game", player=player.name, skill=s_name)
                return True
        return False

    def on_turn_start(self, game: "PiratesGame", player: "PiratesPlayer") -> None:
        """Tick both active duration and cooldown at turn start."""
        self.tick_active(game, player)
        self.tick_cooldown(player)

    def can_perform(self, game: "PiratesGame", player: "PiratesPlayer") -> tuple[bool, str | None]:
        """Check if the buff skill can be activated."""
        user = game.get_user(player)
        locale = user.locale if user else "en"

        if not self.is_unlocked(player):
            return False, Localization.get(locale, "pirates-req-level", level=self.required_level)
            
        if self.is_active(player):
            name_local = Localization.get(locale, self.name)
            return False, Localization.get(locale, "pirates-skill-active", name=name_local, turns=self.get_active(player))
            
        if self.is_on_cooldown(player):
            name_local = Localization.get(locale, self.name)
            return False, Localization.get(locale, "pirates-skill-cooldown", name=name_local, turns=self.get_cooldown(player))
            
        return True, None

    def get_menu_label(self, player: "PiratesPlayer", locale: str = "en") -> str:
        """Get dynamic menu label showing status."""
        name_local = Localization.get(locale, self.name)
        if self.is_active(player):
             return Localization.get(locale, "pirates-menu-active", name=name_local, turns=self.get_active(player))
        if self.is_on_cooldown(player):
             return Localization.get(locale, "pirates-menu-active", name=name_local, turns=self.get_cooldown(player))
        return Localization.get(locale, "pirates-menu-activate", name=name_local)


# =============================================================================
# Concrete Skill Implementations
# =============================================================================


class CannonballSkill(Skill):
    """Cannonball Shot - Attack a player within range."""

    name = "pirates-skill-cannon-name"
    description = "pirates-skill-cannon-desc"
    required_level = 0
    skill_id = "cannonball"

    def can_perform(self, game: "PiratesGame", player: "PiratesPlayer") -> tuple[bool, str | None]:
        if game.current_player != player:
            # Need locale to localize this error
            # But can_perform returns string. 
            # I will fetch locale from game.
            user = game.get_user(player)
            locale = user.locale if user else "en"
            return False, Localization.get(locale, "pirates-skill-not-turn")
        return True, None

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        return game.handle_cannonball_attack(player)


class SailorsInstinctSkill(Skill):
    """Sailor's Instinct - Show map sector information."""

    name = "pirates-skill-instinct-name"
    description = "pirates-skill-instinct-desc"
    required_level = 10
    skill_id = "instinct"

    def can_perform(self, game: "PiratesGame", player: "PiratesPlayer") -> tuple[bool, str | None]:
        if not self.is_unlocked(player):
            user = game.get_user(player)
            locale = user.locale if user else "en"
            return False, Localization.get(locale, "pirates-req-level", level=self.required_level)
        return True, None

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        sound_num = random.randint(1, 2)
        game.play_sound(f"game_pirates/instinct{sound_num}.ogg", volume=60)

        user = game.get_user(player)
        locale = user.locale if user else "en"

        ocean_index = (player.position - 1) // 10
        ocean_key = game.selected_oceans[ocean_index] if ocean_index < len(game.selected_oceans) else "pirates-ocean-unknown"
        
        ocean_name = Localization.get(locale, ocean_key)

        lines = [
            Localization.get(locale, "pirates-your-position", position=player.position, ocean=ocean_name),
            "",
            Localization.get(locale, "pirates-instinct-header")
        ]

        for sector in range(1, 9):
            sector_start = (sector - 1) * 5 + 1
            sector_end = sector * 5
            charted_count = sum(
                1 for i in range(sector_start, sector_end + 1)
                if game.charted_tiles.get(i, False)
            )

            if charted_count == 5:
                status = Localization.get(locale, "pirates-instinct-fully")
            elif charted_count > 0:
                status = Localization.get(locale, "pirates-instinct-partially", count=charted_count)
            else:
                status = Localization.get(locale, "pirates-instinct-uncharted")

            lines.append(Localization.get(locale, "pirates-instinct-sector", sector=sector, start=sector_start, end=sector_end, status=status))

        game.status_box(player, lines)
        return "continue"




class PortalSkill(CooldownSkill):
    """Portal - Teleport to an ocean occupied by another player."""

    name = "pirates-skill-portal-name"
    description = "pirates-skill-portal-desc"
    required_level = 25
    skill_id = "portal"
    max_cooldown = 3

    def can_perform(self, game: "PiratesGame", player: "PiratesPlayer") -> tuple[bool, str | None]:
        user = game.get_user(player)
        locale = user.locale if user else "en"
        
        if not self.is_unlocked(player):
            return False, Localization.get(locale, "pirates-req-level", level=self.required_level)
            
        if self.is_on_cooldown(player):
            name_local = Localization.get(locale, self.name)
            return False, Localization.get(locale, "pirates-skill-cooldown", name=name_local, turns=self.get_cooldown(player))
            
        return True, None

    def get_menu_label(self, player: "PiratesPlayer", locale: str = "en") -> str:
        name_local = Localization.get(locale, self.name)
        if self.is_on_cooldown(player):
             return Localization.get(locale, "pirates-menu-cooldown", name=name_local, turns=self.get_cooldown(player))
        return name_local # Using default or specialized label?
        # Original: "Portal (teleport to occupied ocean)" vs "Portal (cooldown...)"
        # I'll stick to name_local for simplicity, or use specific key?
        # "pirates-skill-portal-desc" is description.
        # I'll just return name_local. The description is shown elsewhere if needed.
        # Or I can use "pirates-menu-activate"?
        return Localization.get(locale, "pirates-menu-activate", name=name_local)

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        return game.handle_portal(player, self)




class GemSeekerSkill(Skill):
    """Gem Seeker - Reveal the location of one uncollected gem."""

    name = "pirates-skill-seeker-name"
    description = "pirates-skill-seeker-desc"
    required_level = 40
    skill_id = "gem_seeker"
    max_uses = 3

    def get_uses(self, player: "PiratesPlayer") -> int:
        """Get remaining uses. Defaults to max_uses if not set."""
        return player.skill_uses.get(self.skill_id, self.max_uses)

    def set_uses(self, player: "PiratesPlayer", value: int) -> None:
        """Set remaining uses."""
        player.skill_uses[self.skill_id] = value

    def can_perform(self, game: "PiratesGame", player: "PiratesPlayer") -> tuple[bool, str | None]:
        user = game.get_user(player)
        locale = user.locale if user else "en"
        
        if not self.is_unlocked(player):
            return False, Localization.get(locale, "pirates-req-level", level=self.required_level)
        if self.get_uses(player) <= 0:
            return False, Localization.get(locale, "pirates-skill-no-uses")
        return True, None

    def get_menu_label(self, player: "PiratesPlayer", locale: str = "en") -> str:
        name_local = Localization.get(locale, self.name)
        uses = self.get_uses(player)
        return Localization.get(locale, "pirates-menu-gem-seeker", name=name_local, uses=uses)

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        self.set_uses(player, self.get_uses(player) - 1)

        sound_num = random.randint(1, 2)
        game.play_sound(f"game_pirates/gemseeker{sound_num}.ogg", volume=60)

        from .gems import GEM_NAMES
        for pos, gem_type in game.gem_positions.items():
            if gem_type != -1:
                gem_key = GEM_NAMES.get(gem_type, "pirates-gem-unknown")
                user = game.get_user(player)
                if user:
                    gem_name = Localization.get(user.locale, gem_key)
                    user.speak_l(
                        "pirates-gem-seeker-reveal",
                        gem=gem_name,
                        position=pos,
                        uses=self.get_uses(player)
                    )
                break

        return "continue"




class SwordFighterSkill(BuffSkill):
    """Sword Fighter - +4 attack bonus for 3 turns."""

    name = "pirates-skill-sword-name"
    description = "pirates-skill-sword-desc"
    required_level = 60
    skill_id = "sword_fighter"
    max_cooldown = 8
    duration = 3
    attack_bonus = 4

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        self.activate(player)
        game.play_sound("game_pirates/swordfighter.ogg", volume=60)

        user = game.get_user(player)
        if user:
            user.speak_l("pirates-sword-fighter-activated", buffer="game", turns=self.get_active(player))
        
        # Manual broadcast
        for p in game.get_active_players():
            if p.id == player.id: continue
            u = game.get_user(p)
            if u:
                s_name = Localization.get(u.locale, self.name)
                u.speak_l("pirates-skill-activated", buffer="game", player=player.name, skill=s_name)

        return "end_turn"




class PushSkill(BuffSkill):
    """Push - +3 defense bonus for 4 turns."""

    name = "pirates-skill-push-name"
    description = "pirates-skill-push-desc"
    required_level = 75
    skill_id = "push"
    max_cooldown = 8
    duration = 4
    defense_bonus = 3

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        self.activate(player)
        sound_num = random.randint(1, 2)
        game.play_sound(f"game_pirates/push{sound_num}.ogg", volume=60)

        user = game.get_user(player)
        if user:
            user.speak_l("pirates-push-activated", buffer="game", turns=self.get_active(player))

        # Manual broadcast
        for p in game.get_active_players():
            if p.id == player.id: continue
            u = game.get_user(p)
            if u:
                s_name = Localization.get(u.locale, self.name)
                u.speak_l("pirates-skill-activated", buffer="game", player=player.name, skill=s_name)

        return "end_turn"




class SkilledCaptainSkill(BuffSkill):
    """Skilled Captain - +2 attack and +2 defense for 4 turns."""

    name = "pirates-skill-captain-name"
    description = "pirates-skill-captain-desc"
    required_level = 90
    skill_id = "skilled_captain"
    max_cooldown = 8
    duration = 4
    attack_bonus = 2
    defense_bonus = 2

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        self.activate(player)
        game.play_sound("game_pirates/skilledcaptain.ogg", volume=60)

        user = game.get_user(player)
        if user:
            user.speak_l("pirates-skilled-captain-activated", buffer="game", turns=self.get_active(player))
            
        # Manual broadcast
        for p in game.get_active_players():
            if p.id == player.id: continue
            u = game.get_user(p)
            if u:
                s_name = Localization.get(u.locale, self.name)
                u.speak_l("pirates-skill-activated", buffer="game", player=player.name, skill=s_name)

        return "end_turn"




class BattleshipSkill(CooldownSkill):
    """Battleship - Fire two cannonballs in one turn."""

    name = "pirates-skill-battleship-name"
    description = "pirates-skill-battleship-desc"
    required_level = 125
    skill_id = "battleship"
    max_cooldown = 2

    def can_perform(self, game: "PiratesGame", player: "PiratesPlayer") -> tuple[bool, str | None]:
        user = game.get_user(player)
        locale = user.locale if user else "en"

        if not self.is_unlocked(player):
            return False, Localization.get(locale, "pirates-req-level", level=self.required_level)
        if self.is_on_cooldown(player):
            name_local = Localization.get(locale, self.name)
            return False, Localization.get(locale, "pirates-skill-cooldown", name=name_local, turns=self.get_cooldown(player))

        # Check if double devastation is active (incompatible)
        if DOUBLE_DEVASTATION.is_active(player):
             # "Cannot use { $skill } while { $active } is active."
             dd_name = Localization.get(locale, DOUBLE_DEVASTATION.name)
             my_name = Localization.get(locale, self.name)
             return False, Localization.get(locale, "pirates-skill-incompatible", skill=my_name, active=dd_name)

        # Check if there are targets in range
        targets = game.get_targets_in_range(player)
        if not targets:
            return False, Localization.get(locale, "pirates-skill-no-targets")

        return True, None

    def get_menu_label(self, player: "PiratesPlayer", locale: str = "en") -> str:
        name_local = Localization.get(locale, self.name)
        if self.is_on_cooldown(player):
            return Localization.get(locale, "pirates-menu-cooldown", name=name_local, turns=self.get_cooldown(player))
        return Localization.get(locale, "pirates-menu-activate", name=name_local)

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        self.start_cooldown(player)
        return game.handle_battleship(player)




class DoubleDevastationSkill(BuffSkill):
    """Double Devastation - Increases cannon range to 10 tiles for 3 turns."""

    name = "pirates-skill-devastation-name"
    description = "pirates-skill-devastation-desc"
    required_level = 200
    skill_id = "double_devastation"
    max_cooldown = 10
    duration = 3
    range_bonus = 5  # Adds 5 to base range of 5

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        self.activate(player)
        game.play_sound("game_pirates/doubledevastation.ogg", volume=60)

        user = game.get_user(player)
        if user:
            user.speak_l("pirates-double-devastation-activated", buffer="game", turns=self.get_active(player))
            
        # Manual broadcast
        for p in game.get_active_players():
            if p.id == player.id: continue
            u = game.get_user(p)
            if u:
                s_name = Localization.get(u.locale, self.name)
                u.speak_l("pirates-skill-activated", buffer="game", player=player.name, skill=s_name)

        return "end_turn"


# =============================================================================
# Skill Instances (Singletons)
# =============================================================================

CANNONBALL = CannonballSkill()
SAILORS_INSTINCT = SailorsInstinctSkill()
PORTAL = PortalSkill()
GEM_SEEKER = GemSeekerSkill()
SWORD_FIGHTER = SwordFighterSkill()
PUSH = PushSkill()
SKILLED_CAPTAIN = SkilledCaptainSkill()
BATTLESHIP = BattleshipSkill()
DOUBLE_DEVASTATION = DoubleDevastationSkill()

# All skills in order of unlock level
ALL_SKILLS: list[Skill] = [
    CANNONBALL,
    SAILORS_INSTINCT,
    PORTAL,
    GEM_SEEKER,
    SWORD_FIGHTER,
    PUSH,
    SKILLED_CAPTAIN,
    BATTLESHIP,
    DOUBLE_DEVASTATION,
]

# Skill lookup by ID
SKILLS_BY_ID: dict[str, Skill] = {skill.skill_id: skill for skill in ALL_SKILLS}


# =============================================================================
# Helper Functions
# =============================================================================


def get_available_skills(player: "PiratesPlayer") -> list[Skill]:
    """Get list of skills unlocked for this player."""
    return [skill for skill in ALL_SKILLS if skill.is_unlocked(player)]


def on_turn_start(game: "PiratesGame", player: "PiratesPlayer") -> None:
    """Called at the start of a player's turn to update all skill timers."""
    for skill in ALL_SKILLS:
        skill.on_turn_start(game, player)


def get_attack_bonus(player: "PiratesPlayer") -> int:
    """Calculate total attack bonus from active buffs."""
    bonus = 0
    if SWORD_FIGHTER.is_active(player):
        bonus += SWORD_FIGHTER.attack_bonus
    if SKILLED_CAPTAIN.is_active(player):
        bonus += SKILLED_CAPTAIN.attack_bonus
    return bonus


def get_defense_bonus(player: "PiratesPlayer") -> int:
    """Calculate total defense bonus from active buffs."""
    bonus = 0
    if PUSH.is_active(player):
        bonus += PUSH.defense_bonus
    if SKILLED_CAPTAIN.is_active(player):
        bonus += SKILLED_CAPTAIN.defense_bonus
    return bonus


def get_attack_range(player: "PiratesPlayer") -> int:
    """Get the current attack range (base 5, or 10 with Double Devastation)."""
    base_range = 5
    if DOUBLE_DEVASTATION.is_active(player):
        return base_range + DOUBLE_DEVASTATION.range_bonus
    return base_range
