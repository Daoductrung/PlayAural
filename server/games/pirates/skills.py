"""Serializable skill rules for Pirates of the Lost Seas."""

from __future__ import annotations

from abc import ABC, abstractmethod
import random
from typing import TYPE_CHECKING

from ...messages.localization import Localization
from . import gems

if TYPE_CHECKING:
    from .game import PiratesGame
    from .player import PiratesPlayer


class Skill(ABC):
    """Stateless skill definition; all mutable state belongs to the player."""

    name: str = ""
    description: str = ""
    required_level: int = 0
    skill_id: str = ""

    @abstractmethod
    def can_perform(
        self, game: "PiratesGame", player: "PiratesPlayer"
    ) -> tuple[bool, str | None]:
        """Return whether this skill can be used and a localized reason if not."""

    @abstractmethod
    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        """Execute the skill and return ``end_turn`` or ``continue``."""

    def on_turn_start(self, game: "PiratesGame", player: "PiratesPlayer") -> None:
        """Update per-turn state."""

    def get_menu_label(self, player: "PiratesPlayer", locale: str = "en") -> str:
        return Localization.get(locale, self.name)

    def is_unlocked(self, player: "PiratesPlayer") -> bool:
        return player.level >= self.required_level

    def _level_error(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        user = game.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(
            locale,
            "pirates-req-level",
            skill=Localization.get(locale, self.name),
            current=player.level,
            required=self.required_level,
        )


class CooldownSkill(Skill):
    max_cooldown: int = 0

    def get_cooldown(self, player: "PiratesPlayer") -> int:
        return player.skill_cooldowns.get(self.skill_id, 0)

    def set_cooldown(self, player: "PiratesPlayer", value: int) -> None:
        player.skill_cooldowns[self.skill_id] = max(0, value)

    def is_on_cooldown(self, player: "PiratesPlayer") -> bool:
        return self.get_cooldown(player) > 0

    def start_cooldown(self, player: "PiratesPlayer") -> None:
        self.set_cooldown(player, self.max_cooldown)

    def on_turn_start(self, game: "PiratesGame", player: "PiratesPlayer") -> None:
        self.set_cooldown(player, self.get_cooldown(player) - 1)

    def _cooldown_error(
        self, game: "PiratesGame", player: "PiratesPlayer"
    ) -> str:
        user = game.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(
            locale,
            "pirates-skill-cooldown",
            name=Localization.get(locale, self.name),
            turns=self.get_cooldown(player),
        )

    def get_menu_label(self, player: "PiratesPlayer", locale: str = "en") -> str:
        name = Localization.get(locale, self.name)
        if self.is_on_cooldown(player):
            return Localization.get(
                locale,
                "pirates-menu-cooldown",
                name=name,
                turns=self.get_cooldown(player),
            )
        return Localization.get(locale, "pirates-menu-activate", name=name)


class BuffSkill(CooldownSkill):
    duration: int = 0
    incompatible_skill_ids: tuple[str, ...] = ()

    def get_active(self, player: "PiratesPlayer") -> int:
        return player.skill_active.get(self.skill_id, 0)

    def set_active(self, player: "PiratesPlayer", value: int) -> None:
        player.skill_active[self.skill_id] = max(0, value)

    def is_active(self, player: "PiratesPlayer") -> bool:
        return self.get_active(player) > 0

    def activate(self, player: "PiratesPlayer") -> None:
        self.set_active(player, self.duration)
        self.start_cooldown(player)
        player.skill_activated_this_turn = True

    def on_turn_start(self, game: "PiratesGame", player: "PiratesPlayer") -> None:
        active = self.get_active(player)
        if active > 0:
            self.set_active(player, active - 1)
            if active == 1:
                for listener in game.players:
                    user = game.get_user(listener)
                    if not user:
                        continue
                    key = (
                        "pirates-buff-expired-you"
                        if listener.id == player.id
                        else "pirates-buff-expired"
                    )
                    if game._wants_brief(user):
                        key += "-brief"
                    payload = game._resolve_broadcast_kwargs(
                        user.locale,
                        {
                            "player": player,
                            "skill": Localization.get(user.locale, self.name),
                        },
                    )
                    user.speak_l(key, buffer="game", **payload)
        super().on_turn_start(game, player)

    def can_perform(
        self, game: "PiratesGame", player: "PiratesPlayer"
    ) -> tuple[bool, str | None]:
        user = game.get_user(player)
        locale = user.locale if user else "en"
        name = Localization.get(locale, self.name)
        if not self.is_unlocked(player):
            return False, self._level_error(game, player)
        if self.is_active(player):
            return False, Localization.get(
                locale,
                "pirates-skill-active",
                name=name,
                turns=self.get_active(player),
            )
        if self.is_on_cooldown(player):
            return False, self._cooldown_error(game, player)
        if player.skill_activated_this_turn:
            return False, Localization.get(
                locale, "pirates-skill-already-activated-this-turn"
            )
        for skill_id in self.incompatible_skill_ids:
            active_skill = SKILLS_BY_ID.get(skill_id)
            if isinstance(active_skill, BuffSkill) and active_skill.is_active(player):
                return False, Localization.get(
                    locale,
                    "pirates-skill-incompatible",
                    skill=name,
                    active=Localization.get(locale, active_skill.name),
                )
        return True, None

    def get_menu_label(self, player: "PiratesPlayer", locale: str = "en") -> str:
        name = Localization.get(locale, self.name)
        if self.is_active(player):
            return Localization.get(
                locale,
                "pirates-menu-active",
                name=name,
                turns=self.get_active(player),
            )
        return super().get_menu_label(player, locale)


def _speak_personal_activation(
    game: "PiratesGame",
    player: "PiratesPlayer",
    full_key: str,
    brief_key: str,
    **kwargs,
) -> None:
    user = game.get_user(player)
    if user:
        key = brief_key if game._wants_brief(user) else full_key
        user.speak_l(key, buffer="game", **kwargs)


def _broadcast_skill_activation(
    game: "PiratesGame", player: "PiratesPlayer", skill: Skill
) -> None:
    for listener in game.players:
        if listener.id == player.id:
            continue
        user = game.get_user(listener)
        if not user:
            continue
        key = (
            "pirates-skill-activated-brief"
            if game._wants_brief(user)
            else "pirates-skill-activated"
        )
        user.speak_l(
            key,
            buffer="game",
            player=player.name,
            skill=Localization.get(user.locale, skill.name),
            effect=Localization.get(user.locale, skill.description),
        )


class SailorsInstinctSkill(Skill):
    name = "pirates-skill-instinct-name"
    description = "pirates-skill-instinct-desc"
    required_level = 10
    skill_id = "instinct"

    def can_perform(
        self, game: "PiratesGame", player: "PiratesPlayer"
    ) -> tuple[bool, str | None]:
        if not self.is_unlocked(player):
            return False, self._level_error(game, player)
        return True, None

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        game.play_sound(f"game_pirates/instinct{random.randint(1, 2)}.ogg", volume=60)
        user = game.get_user(player)
        if not user:
            return "continue"
        locale = user.locale
        ocean_index = (player.position - 1) // 10
        ocean_key = (
            game.selected_oceans[ocean_index]
            if ocean_index < len(game.selected_oceans)
            else "pirates-ocean-unknown"
        )
        lines = [
            Localization.get(locale, "pirates-instinct-header"),
            Localization.get(
                locale,
                "pirates-your-position",
                position=player.position,
                ocean=Localization.get(locale, ocean_key),
                sector=((player.position - 1) // 5) + 1,
            ),
        ]
        for sector in range(1, 9):
            start = (sector - 1) * 5 + 1
            end = sector * 5
            gem_count = sum(
                gem_type != -1
                for position, gem_type in game.gem_positions.items()
                if start <= position <= end
            )
            player_count = sum(
                other.id != player.id and start <= other.position <= end
                for other in game.get_active_players()
            )
            lines.append(
                Localization.get(
                    locale,
                    "pirates-instinct-sector",
                    sector=sector,
                    start=start,
                    end=end,
                    gems=gem_count,
                    players=player_count,
                )
            )
        game.status_box(player, lines)
        return "continue"


class PortalSkill(CooldownSkill):
    name = "pirates-skill-portal-name"
    description = "pirates-skill-portal-desc"
    required_level = 25
    skill_id = "portal"
    max_cooldown = 3

    def can_perform(
        self, game: "PiratesGame", player: "PiratesPlayer"
    ) -> tuple[bool, str | None]:
        if not self.is_unlocked(player):
            return False, self._level_error(game, player)
        if self.is_on_cooldown(player):
            return False, self._cooldown_error(game, player)
        return True, None

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        return game.handle_portal(player)


class GemSeekerSkill(Skill):
    name = "pirates-skill-seeker-name"
    description = "pirates-skill-seeker-desc"
    required_level = 40
    skill_id = "gem_seeker"
    max_uses = 3

    def get_uses(self, player: "PiratesPlayer") -> int:
        return player.skill_uses.get(self.skill_id, self.max_uses)

    def set_uses(self, player: "PiratesPlayer", value: int) -> None:
        player.skill_uses[self.skill_id] = max(0, value)

    def can_perform(
        self, game: "PiratesGame", player: "PiratesPlayer"
    ) -> tuple[bool, str | None]:
        user = game.get_user(player)
        locale = user.locale if user else "en"
        if not self.is_unlocked(player):
            return False, self._level_error(game, player)
        if self.get_uses(player) <= 0:
            return False, Localization.get(locale, "pirates-skill-no-uses")
        if not any(gem_type != -1 for gem_type in game.gem_positions.values()):
            return False, Localization.get(locale, "pirates-skill-no-gems")
        return True, None

    def get_menu_label(self, player: "PiratesPlayer", locale: str = "en") -> str:
        return Localization.get(
            locale,
            "pirates-menu-gem-seeker",
            name=Localization.get(locale, self.name),
            uses=self.get_uses(player),
        )

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        self.set_uses(player, self.get_uses(player) - 1)
        game.play_sound(f"game_pirates/gemseeker{random.randint(1, 2)}.ogg", volume=60)
        for position, gem_type in game.gem_positions.items():
            if gem_type == -1:
                continue
            user = game.get_user(player)
            if user:
                user.speak_l(
                    "pirates-gem-seeker-reveal",
                    buffer="game",
                    gem=Localization.get(user.locale, gems.get_gem_name(gem_type)),
                    position=position,
                    uses=self.get_uses(player),
                )
            break
        return "continue"


class SwordFighterSkill(BuffSkill):
    name = "pirates-skill-sword-name"
    description = "pirates-skill-sword-desc"
    required_level = 60
    skill_id = "sword_fighter"
    max_cooldown = 6
    duration = 3
    attack_bonus = 2
    incompatible_skill_ids = ("skilled_captain",)

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        self.activate(player)
        game.play_sound("game_pirates/swordfighter.ogg", volume=60)
        _speak_personal_activation(
            game,
            player,
            "pirates-sword-fighter-activated",
            "pirates-sword-fighter-activated-brief",
            bonus=self.attack_bonus,
            turns=self.duration,
            cooldown=self.max_cooldown,
        )
        _broadcast_skill_activation(game, player, self)
        return "continue"


class PushSkill(BuffSkill):
    name = "pirates-skill-push-name"
    description = "pirates-skill-push-desc"
    required_level = 75
    skill_id = "push"
    max_cooldown = 6
    duration = 3
    push_bonus = 2

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        self.activate(player)
        game.play_sound(f"game_pirates/push{random.randint(1, 2)}.ogg", volume=60)
        _speak_personal_activation(
            game,
            player,
            "pirates-push-activated",
            "pirates-push-activated-brief",
            bonus=self.push_bonus,
            turns=self.duration,
            cooldown=self.max_cooldown,
        )
        _broadcast_skill_activation(game, player, self)
        return "continue"


class SkilledCaptainSkill(BuffSkill):
    name = "pirates-skill-captain-name"
    description = "pirates-skill-captain-desc"
    required_level = 90
    skill_id = "skilled_captain"
    max_cooldown = 7
    duration = 4
    attack_bonus = 1
    defense_bonus = 1
    incompatible_skill_ids = ("sword_fighter",)

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        self.activate(player)
        game.play_sound("game_pirates/skilledcaptain.ogg", volume=60)
        _speak_personal_activation(
            game,
            player,
            "pirates-skilled-captain-activated",
            "pirates-skilled-captain-activated-brief",
            attack=self.attack_bonus,
            defense=self.defense_bonus,
            turns=self.duration,
            cooldown=self.max_cooldown,
        )
        _broadcast_skill_activation(game, player, self)
        return "continue"


class BattleshipSkill(CooldownSkill):
    name = "pirates-skill-battleship-name"
    description = "pirates-skill-battleship-desc"
    required_level = 125
    skill_id = "battleship"
    max_cooldown = 4

    def can_perform(
        self, game: "PiratesGame", player: "PiratesPlayer"
    ) -> tuple[bool, str | None]:
        user = game.get_user(player)
        locale = user.locale if user else "en"
        if not self.is_unlocked(player):
            return False, self._level_error(game, player)
        if self.is_on_cooldown(player):
            return False, self._cooldown_error(game, player)
        if player.skill_activated_this_turn:
            return False, Localization.get(locale, "pirates-battleship-after-buff")
        if DOUBLE_DEVASTATION.is_active(player):
            return False, Localization.get(
                locale,
                "pirates-skill-incompatible",
                skill=Localization.get(locale, self.name),
                active=Localization.get(locale, DOUBLE_DEVASTATION.name),
            )
        if not game.get_targets_in_range(player):
            return False, Localization.get(
                locale,
                "pirates-skill-no-targets",
                range=get_attack_range(player),
            )
        return True, None

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        self.start_cooldown(player)
        return game.handle_battleship(player)


class DoubleDevastationSkill(BuffSkill):
    name = "pirates-skill-devastation-name"
    description = "pirates-skill-devastation-desc"
    required_level = 200
    skill_id = "double_devastation"
    max_cooldown = 10
    duration = 3
    range_bonus = 5

    def do_action(self, game: "PiratesGame", player: "PiratesPlayer") -> str:
        self.activate(player)
        game.play_sound("game_pirates/doubledevastation.ogg", volume=60)
        attack_range = 5 + self.range_bonus
        _speak_personal_activation(
            game,
            player,
            "pirates-double-devastation-activated",
            "pirates-double-devastation-activated-brief",
            range=attack_range,
            turns=self.duration,
            cooldown=self.max_cooldown,
        )
        _broadcast_skill_activation(game, player, self)
        return "continue"


SAILORS_INSTINCT = SailorsInstinctSkill()
PORTAL = PortalSkill()
GEM_SEEKER = GemSeekerSkill()
SWORD_FIGHTER = SwordFighterSkill()
PUSH = PushSkill()
SKILLED_CAPTAIN = SkilledCaptainSkill()
BATTLESHIP = BattleshipSkill()
DOUBLE_DEVASTATION = DoubleDevastationSkill()

ALL_SKILLS: list[Skill] = [
    SAILORS_INSTINCT,
    PORTAL,
    GEM_SEEKER,
    SWORD_FIGHTER,
    PUSH,
    SKILLED_CAPTAIN,
    BATTLESHIP,
    DOUBLE_DEVASTATION,
]
SKILLS_BY_ID: dict[str, Skill] = {skill.skill_id: skill for skill in ALL_SKILLS}


def get_available_skills(player: "PiratesPlayer") -> list[Skill]:
    return [skill for skill in ALL_SKILLS if skill.is_unlocked(player)]


def on_turn_start(game: "PiratesGame", player: "PiratesPlayer") -> None:
    for skill in ALL_SKILLS:
        skill.on_turn_start(game, player)


def get_attack_bonus(player: "PiratesPlayer") -> int:
    bonus = SWORD_FIGHTER.attack_bonus if SWORD_FIGHTER.is_active(player) else 0
    if SKILLED_CAPTAIN.is_active(player):
        bonus += SKILLED_CAPTAIN.attack_bonus
    return bonus


def get_defense_bonus(player: "PiratesPlayer") -> int:
    if SKILLED_CAPTAIN.is_active(player):
        return SKILLED_CAPTAIN.defense_bonus
    return 0


def get_push_bonus(player: "PiratesPlayer") -> int:
    return PUSH.push_bonus if PUSH.is_active(player) else 0


def get_attack_range(player: "PiratesPlayer") -> int:
    return 10 if DOUBLE_DEVASTATION.is_active(player) else 5


def format_active_skills(player: "PiratesPlayer", locale: str) -> str:
    active = [
        Localization.get(
            locale,
            "pirates-active-skill-status",
            skill=Localization.get(locale, skill.name),
            turns=skill.get_active(player),
        )
        for skill in (SWORD_FIGHTER, PUSH, SKILLED_CAPTAIN, DOUBLE_DEVASTATION)
        if skill.is_active(player)
    ]
    if not active:
        return Localization.get(locale, "pirates-no-active-skills")
    return Localization.format_list_and(locale, active)
