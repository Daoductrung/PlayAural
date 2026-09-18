"""Run reproducible full-match diagnostics for Breach Point bot strategy."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field

from server.games.breachpoint.game import (
    MATCH_DRAW,
    PHASE_BUY,
    TEAM_COUNTER_TERRORISTS,
    TEAM_TERRORISTS,
    BreachPointGame,
    BreachPointOptions,
)
from server.games.breachpoint.player import BreachPointPlayer
from server.games.breachpoint.rules import MATCH_FORMATS
from server.users.bot import Bot


SIDE_NAMES = {
    TEAM_TERRORISTS: "T",
    TEAM_COUNTER_TERRORISTS: "CT",
}
TEAM_SIZES = range(
    BreachPointGame.get_min_players() // 2,
    BreachPointGame.get_max_players() // 2 + 1,
)
DEFAULT_DIAGNOSTIC_MATCH_FORMAT = min(
    MATCH_FORMATS,
    key=lambda match_format_id: MATCH_FORMATS[match_format_id].regulation_rounds,
)


@dataclass(frozen=True)
class RoundDiagnostic:
    """One completed combat round observed at the action boundary."""

    round_number: int
    winning_side: int
    reason: str
    actions: int
    regulation_pistol_round: bool
    attack_strategy: str
    attack_site: str


@dataclass
class MatchDiagnostic:
    """Aggregate facts from one complete seeded match."""

    team_size: int
    seed: int
    actions: Counter[str] = field(default_factory=Counter)
    actions_by_side: dict[int, Counter[str]] = field(
        default_factory=lambda: {
            TEAM_TERRORISTS: Counter(),
            TEAM_COUNTER_TERRORISTS: Counter(),
        }
    )
    purchases: Counter[str] = field(default_factory=Counter)
    attacks_by_weapon: Counter[str] = field(default_factory=Counter)
    rounds: list[RoundDiagnostic] = field(default_factory=list)
    stalled_state: str = ""
    final_score: tuple[int, int] = (0, 0)
    winner_squad: int = -1
    result: str = ""


def _make_game(team_size: int, match_format: str, seed: int) -> BreachPointGame:
    game = BreachPointGame(
        options=BreachPointOptions(
            match_format=match_format,
            overtime_mode=MATCH_DRAW,
        )
    )
    game._bot_coordinator.seed_strategy(seed)
    game.setup_keybinds()
    for index in range(team_size * 2):
        name = f"Bot {index + 1}"
        game.add_player(name, Bot(name, uuid=f"diagnostic-{team_size}-{index}"))
    game.host = "Bot 1"
    game.on_start()
    return game


def _action_family(action_id: str) -> str:
    for prefix, family in (
        ("buy_", "buy"),
        ("move_", "move"),
        ("shoot_", "shoot"),
        ("throw_", "utility"),
        ("hold_angle_", "hold"),
        ("equip_", "equip"),
        ("reaction_", "reaction"),
    ):
        if action_id.startswith(prefix):
            return family
    return action_id


def _score(game: BreachPointGame) -> tuple[int, int]:
    return tuple(game._squad_score(index) for index in (0, 1))


def _state_fingerprint(game: BreachPointGame) -> tuple[object, ...]:
    current = game.current_player
    return (
        game.status,
        game.round,
        game.tactical_round,
        game.phase,
        current.id if current else "",
        game.bomb_state,
        game.bomb_carrier_id,
        game.bomb_location_id,
        game.bomb_fuse_remaining,
        tuple(game.round_acted_player_ids),
        tuple(game.buy_ready_player_ids),
        tuple(
            (
                player.id,
                player.position_id,
                player.health,
                player.action_points,
                player.eliminated,
                player.cash,
                player.equipped_weapon_id,
                player.sidearm_weapon_id,
                player.primary_weapon_id,
                player.armor,
                tuple(sorted(player.utility_counts.items())),
                tuple(sorted(player.equipment_counts.items())),
                tuple(sorted(player.weapon_shots_fired_this_activation.items())),
                player.held_angle_node_id,
            )
            for player in game.get_active_players()
            if isinstance(player, BreachPointPlayer)
        ),
    )


def run_match(
    team_size: int,
    *,
    match_format: str = DEFAULT_DIAGNOSTIC_MATCH_FORMAT,
    maximum_actions: int = 20_000,
    trace: bool = False,
    seed: int = 0,
) -> MatchDiagnostic:
    """Play one full all-bot match and return action-level diagnostics."""

    if team_size not in TEAM_SIZES:
        raise ValueError(
            "Breach Point diagnostics support team sizes from "
            f"{TEAM_SIZES.start} to {TEAM_SIZES.stop - 1}"
        )
    if match_format not in MATCH_FORMATS:
        raise ValueError(f"Unknown Breach Point match format: {match_format}")
    if maximum_actions <= 0:
        raise ValueError("Maximum actions must be positive")
    game = _make_game(team_size, match_format, seed)
    diagnostic = MatchDiagnostic(team_size=team_size, seed=seed)
    round_action_count = 0

    for action_number in range(1, maximum_actions + 1):
        if game.status == "finished":
            break
        current = game.current_player
        if not isinstance(current, BreachPointPlayer) or not current.is_bot:
            diagnostic.stalled_state = "No active bot owns the current turn"
            break
        action_id = game.bot_think(current)
        if not action_id:
            diagnostic.stalled_state = f"{current.name} produced no action"
            break

        family = _action_family(action_id)
        acting_side = current.team_index
        if action_id.startswith("buy_"):
            diagnostic.purchases[action_id] += 1
        if action_id.startswith("shoot_") or action_id == "reaction_shoot":
            weapon = game._equipped_weapon(current)
            if weapon:
                diagnostic.attacks_by_weapon[weapon.id] += 1
        previous_score = _score(game)
        previous_round = game.round
        previous_overtime_period = game.overtime_period
        previous_sides = tuple(game.side_squad_indexes)
        previous_state = _state_fingerprint(game)
        attack_plan = game._bot_coordinator.team_plans.get(TEAM_TERRORISTS)
        previous_attack_strategy = (
            attack_plan.attack_strategy_id if attack_plan else ""
        )
        previous_attack_site = attack_plan.attack_site_id if attack_plan else ""
        assignment = game._bot_coordinator.assignment_for(current.id)
        targets = game._bot_coordinator.target_nodes(game, current)
        previous_node = current.position_id
        previous_action_points = current.action_points

        game.execute_action(current, action_id)
        game.flush_menus()

        diagnostic.actions[family] += 1
        diagnostic.actions_by_side[acting_side][family] += 1
        round_action_count += 1
        if trace:
            print(
                f"{action_number:04d} R{previous_round} "
                f"{SIDE_NAMES.get(acting_side, acting_side)} {current.name}: "
                f"{action_id}; role={assignment.role if assignment else '-'}"
                f"/{assignment.anchor_node_id if assignment else '-'}; "
                f"targets={targets}; node={previous_node}->{current.position_id}; "
                f"AP={previous_action_points}->{current.action_points}"
            )

        current_score = _score(game)
        if current_score != previous_score:
            winning_squad = next(
                index
                for index, (before, after) in enumerate(
                    zip(previous_score, current_score, strict=True)
                )
                if after > before
            )
            winning_side = previous_sides.index(winning_squad)
            diagnostic.rounds.append(
                RoundDiagnostic(
                    round_number=previous_round,
                    winning_side=winning_side,
                    reason=game.last_round_win_reason,
                    actions=round_action_count,
                    regulation_pistol_round=bool(
                        previous_overtime_period == 0
                        and previous_round
                        in {1, game.match_format.rounds_per_half + 1}
                    ),
                    attack_strategy=previous_attack_strategy,
                    attack_site=previous_attack_site,
                )
            )
            round_action_count = 0
        elif _state_fingerprint(game) == previous_state:
            diagnostic.stalled_state = (
                f"Action {action_id} by {current.name} made no authoritative progress"
            )
            break
    else:
        if game.status != "finished":
            diagnostic.stalled_state = f"Exceeded {maximum_actions} actions"

    diagnostic.final_score = _score(game)
    diagnostic.winner_squad = game.winning_team_index
    diagnostic.result = game.win_reason
    game.on_discard()
    return diagnostic


def _print_diagnostic(diagnostic: MatchDiagnostic) -> None:
    winner = (
        "draw"
        if diagnostic.winner_squad < 0
        else f"squad {diagnostic.winner_squad + 1}"
    )
    print(
        f"{diagnostic.team_size}v{diagnostic.team_size} seed {diagnostic.seed}: "
        f"{diagnostic.final_score[0]}-{diagnostic.final_score[1]}, "
        f"{winner}, {diagnostic.result or 'unfinished'}"
    )
    print(
        "  rounds: "
        + ", ".join(
            f"R{item.round_number} {SIDE_NAMES[item.winning_side]} "
            f"{item.reason} ({item.actions} actions, "
            f"{item.attack_strategy}->{item.attack_site})"
            f"{' [pistol]' if item.regulation_pistol_round else ''}"
            for item in diagnostic.rounds
        )
    )
    print(
        "  actions: "
        + ", ".join(
            f"{name}={count}" for name, count in diagnostic.actions.most_common()
        )
    )
    print(
        "  purchases: "
        + ", ".join(
            f"{name}={count}" for name, count in diagnostic.purchases.most_common()
        )
    )
    print(
        "  attacks by weapon: "
        + ", ".join(
            f"{name}={count}"
            for name, count in diagnostic.attacks_by_weapon.most_common()
        )
    )
    if diagnostic.stalled_state:
        print(f"  STALLED: {diagnostic.stalled_state}")


def _print_summary(diagnostics: list[MatchDiagnostic]) -> None:
    team_size = diagnostics[0].team_size
    squad_wins = Counter(diagnostic.winner_squad for diagnostic in diagnostics)
    round_wins = Counter(
        round_diagnostic.winning_side
        for diagnostic in diagnostics
        for round_diagnostic in diagnostic.rounds
    )
    reasons = Counter(
        round_diagnostic.reason
        for diagnostic in diagnostics
        for round_diagnostic in diagnostic.rounds
    )
    actions = sum((diagnostic.actions for diagnostic in diagnostics), Counter())
    purchases = sum(
        (diagnostic.purchases for diagnostic in diagnostics),
        Counter(),
    )
    attacks_by_weapon = sum(
        (diagnostic.attacks_by_weapon for diagnostic in diagnostics),
        Counter(),
    )
    pistol_round_wins = Counter(
        round_diagnostic.winning_side
        for diagnostic in diagnostics
        for round_diagnostic in diagnostic.rounds
        if round_diagnostic.regulation_pistol_round
    )
    pistol_round_plans = Counter(
        (
            round_diagnostic.attack_strategy,
            round_diagnostic.attack_site,
            round_diagnostic.winning_side,
        )
        for diagnostic in diagnostics
        for round_diagnostic in diagnostic.rounds
        if round_diagnostic.regulation_pistol_round
    )
    attack_strategies = Counter(
        round_diagnostic.attack_strategy
        for diagnostic in diagnostics
        for round_diagnostic in diagnostic.rounds
    )
    terrorist_wins_by_strategy = Counter(
        round_diagnostic.attack_strategy
        for diagnostic in diagnostics
        for round_diagnostic in diagnostic.rounds
        if round_diagnostic.winning_side == TEAM_TERRORISTS
    )
    stalled = [
        diagnostic
        for diagnostic in diagnostics
        if diagnostic.stalled_state
    ]
    print(
        f"{team_size}v{team_size}, {len(diagnostics)} seeded matches: "
        f"squad 1 wins={squad_wins[0]}, squad 2 wins={squad_wins[1]}, "
        f"draws={squad_wins[-1]}"
    )
    total_side_rounds = sum(round_wins.values())
    side_round_summary = (
        ", ".join(
            f"{SIDE_NAMES[side]}={round_wins[side]} "
            f"({round_wins[side] * 100 / total_side_rounds:.1f}%)"
            for side in (TEAM_TERRORISTS, TEAM_COUNTER_TERRORISTS)
        )
        if total_side_rounds
        else "none completed"
    )
    print(f"  side rounds: {side_round_summary}")
    print(
        "  outcomes: "
        + ", ".join(f"{name}={count}" for name, count in reasons.most_common())
    )
    print(
        "  regulation pistol rounds: "
        + ", ".join(
            f"{SIDE_NAMES[side]}={pistol_round_wins[side]}"
            for side in (TEAM_TERRORISTS, TEAM_COUNTER_TERRORISTS)
        )
    )
    print(
        "  pistol plans: "
        + ", ".join(
            f"{strategy}->{site} {SIDE_NAMES[side]}={count}"
            for (strategy, site, side), count in sorted(pistol_round_plans.items())
        )
    )
    print(
        "  attack strategies: "
        + ", ".join(
            f"{name}={count} (T wins {terrorist_wins_by_strategy[name]})"
            for name, count in attack_strategies.most_common()
        )
    )
    print(
        "  actions: "
        + ", ".join(f"{name}={count}" for name, count in actions.most_common())
    )
    print(
        "  purchases: "
        + ", ".join(f"{name}={count}" for name, count in purchases.most_common())
    )
    print(
        "  attacks by weapon: "
        + ", ".join(
            f"{name}={count}" for name, count in attacks_by_weapon.most_common()
        )
    )
    if stalled:
        print(
            "  STALLED: "
            + ", ".join(
                f"seed {diagnostic.seed}: {diagnostic.stalled_state}"
                for diagnostic in stalled
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--team-size",
        type=int,
        action="append",
        choices=TEAM_SIZES,
        help=(
            "Team size to simulate; repeat for multiple sizes "
            f"(default: {TEAM_SIZES.start}-{TEAM_SIZES.stop - 1})"
        ),
    )
    parser.add_argument(
        "--match-format",
        choices=tuple(MATCH_FORMATS),
        default=DEFAULT_DIAGNOSTIC_MATCH_FORMAT,
    )
    parser.add_argument("--maximum-actions", type=int, default=20_000)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--trace", action="store_true")
    args = parser.parse_args()
    if args.maximum_actions <= 0:
        parser.error("--maximum-actions must be positive")
    if args.runs <= 0:
        parser.error("--runs must be positive")

    for team_size in args.team_size or TEAM_SIZES:
        diagnostics = [
            run_match(
                team_size,
                match_format=args.match_format,
                maximum_actions=args.maximum_actions,
                trace=args.trace,
                seed=args.seed + run_index,
            )
            for run_index in range(args.runs)
        ]
        if len(diagnostics) == 1:
            _print_diagnostic(diagnostics[0])
        else:
            _print_summary(diagnostics)


if __name__ == "__main__":
    main()
