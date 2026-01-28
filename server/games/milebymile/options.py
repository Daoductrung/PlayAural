"""Game options for Mile by Mile."""

from dataclasses import dataclass

from ..base import GameOptions
from ...game_utils.options import (
    IntOption,
    MenuOption,
    BoolOption,
    TeamModeOption,
    option_field,
)
from ...game_utils.teams import TeamManager


@dataclass
class MileByMileOptions(GameOptions):
    """Options for Mile by Mile game."""

    round_distance: int = option_field(
        IntOption(
            default=1000,
            min_val=300,
            max_val=3000,
            value_key="miles",
            label="milebymile-set-distance",
            prompt="milebymile-enter-distance",
            change_msg="milebymile-option-changed-distance",
        )
    )
    winning_score: int = option_field(
        IntOption(
            default=5000,
            min_val=1000,
            max_val=10000,
            value_key="score",
            label="milebymile-set-winning-score",
            prompt="milebymile-enter-winning-score",
            change_msg="milebymile-option-changed-winning",
        )
    )
    team_mode: str = option_field(
        TeamModeOption(
            default="individual",
            value_key="mode",
            choices=lambda g, p: TeamManager.get_all_team_modes(2, 9),
            label="game-set-team-mode",
            prompt="game-select-team-mode",
            change_msg="game-option-changed-team",
        )
    )
    only_allow_perfect_crossing: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="milebymile-toggle-perfect-crossing",
            change_msg="milebymile-option-changed-crossing",
        )
    )
    allow_stacking_attacks: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="milebymile-toggle-stacking",
            change_msg="milebymile-option-changed-stacking",
        )
    )
    reshuffle_discard_pile: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="milebymile-toggle-reshuffle",
            change_msg="milebymile-option-changed-reshuffle",
        )
    )
    karma_rule: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="milebymile-toggle-karma",
            change_msg="milebymile-option-changed-karma",
        )
    )
    rig_game: str = option_field(
        MenuOption(
            default="none",
            value_key="rig",
            choices=["none", "no_duplicates", "2x_attacks", "2x_defenses"],
            choice_labels={
                "none": "milebymile-rig-none",
                "no_duplicates": "milebymile-rig-no-duplicates",
                "2x_attacks": "milebymile-rig-2x-attacks",
                "2x_defenses": "milebymile-rig-2x-defenses",
            },
            label="milebymile-set-rig",
            prompt="milebymile-select-rig",
            change_msg="milebymile-option-changed-rig",
        )
    )

