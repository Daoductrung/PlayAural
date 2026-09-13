"""Stable state identifiers shared by Breach Point rules and bot strategy."""

PHASE_BUY = "buy"
PHASE_COMBAT = "combat"
PHASES = frozenset({PHASE_BUY, PHASE_COMBAT})

BOMB_CARRIED = "carried"
BOMB_DROPPED = "dropped"
BOMB_PLANTING = "planting"
BOMB_PLANTED = "planted"
BOMB_STATES = frozenset({BOMB_CARRIED, BOMB_DROPPED, BOMB_PLANTING, BOMB_PLANTED})

WIN_ELIMINATION = "elimination"
WIN_DEFUSED = "defused"
WIN_DETONATED = "detonated"
WIN_TIME = "time"
WIN_REASONS = frozenset({WIN_ELIMINATION, WIN_DEFUSED, WIN_DETONATED, WIN_TIME})

MATCH_REGULATION = "regulation"
MATCH_OVERTIME = "overtime"
MATCH_DRAW = "draw"
MATCH_RESULTS = frozenset({MATCH_REGULATION, MATCH_OVERTIME, MATCH_DRAW})
