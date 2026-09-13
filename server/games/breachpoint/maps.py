"""Validated tactical map definitions for Breach Point."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TacticalNode:
    """One named area in a tactical map graph."""

    id: str
    name_key: str
    adjacent: tuple[str, ...]
    sightlines: tuple[str, ...]
    bomb_site: bool = False


@dataclass(frozen=True)
class TacticalMap:
    """Immutable topology and deployment metadata for one map."""

    id: str
    name_key: str
    terrorist_spawn: str
    counter_terrorist_spawn: str
    nodes: tuple[TacticalNode, ...]

    def node_map(self) -> dict[str, TacticalNode]:
        return {node.id: node for node in self.nodes}

    def get_node(self, node_id: str) -> TacticalNode | None:
        return self.node_map().get(node_id)

    def bomb_site_ids(self) -> tuple[str, ...]:
        return tuple(node.id for node in self.nodes if node.bomb_site)


def _validate_map(tactical_map: TacticalMap) -> None:
    """Reject incomplete or asymmetric topology at import time."""

    if not tactical_map.id or not tactical_map.name_key:
        raise ValueError("Tactical maps require stable ids and localized names")
    nodes = tactical_map.node_map()
    if len(nodes) != len(tactical_map.nodes):
        raise ValueError(f"Duplicate node id in tactical map {tactical_map.id}")
    if tactical_map.terrorist_spawn not in nodes:
        raise ValueError(f"Missing Terrorist spawn in tactical map {tactical_map.id}")
    if tactical_map.counter_terrorist_spawn not in nodes:
        raise ValueError(
            f"Missing Counter-Terrorist spawn in tactical map {tactical_map.id}"
        )
    if not tactical_map.bomb_site_ids():
        raise ValueError(f"Tactical map {tactical_map.id} has no bomb sites")

    for node in tactical_map.nodes:
        if not node.id or not node.name_key:
            raise ValueError(f"Tactical map {tactical_map.id} has an unnamed node")
        if len(set(node.adjacent)) != len(node.adjacent):
            raise ValueError(f"Node {node.id} has duplicate movement edges")
        if len(set(node.sightlines)) != len(node.sightlines):
            raise ValueError(f"Node {node.id} has duplicate sightlines")
        if node.id in node.adjacent or node.id in node.sightlines:
            raise ValueError(f"Node {node.id} links to itself")
        for neighbor_id in node.adjacent:
            neighbor = nodes.get(neighbor_id)
            if neighbor is None:
                raise ValueError(f"Node {node.id} has unknown neighbor {neighbor_id}")
            if node.id not in neighbor.adjacent:
                raise ValueError(
                    f"Movement edge {node.id} -> {neighbor_id} is not reciprocal"
                )
            if neighbor_id not in node.sightlines:
                raise ValueError(
                    f"Movement edge {node.id} -> {neighbor_id} must grant line of sight"
                )
        for visible_id in node.sightlines:
            visible = nodes.get(visible_id)
            if visible is None:
                raise ValueError(f"Node {node.id} sees unknown node {visible_id}")
            if node.id not in visible.sightlines:
                raise ValueError(
                    f"Sightline {node.id} -> {visible_id} is not reciprocal"
                )

    reachable = {tactical_map.terrorist_spawn}
    frontier = [tactical_map.terrorist_spawn]
    while frontier:
        node_id = frontier.pop()
        for neighbor_id in nodes[node_id].adjacent:
            if neighbor_id not in reachable:
                reachable.add(neighbor_id)
                frontier.append(neighbor_id)
    if reachable != set(nodes):
        missing = ", ".join(sorted(set(nodes) - reachable))
        raise ValueError(
            f"Tactical map {tactical_map.id} has unreachable nodes: {missing}"
        )


DEPOT_MAP = TacticalMap(
    id="depot",
    name_key="breachpoint-map-depot",
    terrorist_spawn="t_spawn",
    counter_terrorist_spawn="ct_spawn",
    nodes=(
        TacticalNode(
            id="t_spawn",
            name_key="breachpoint-node-t-spawn",
            adjacent=("west_yard", "mid", "east_yard"),
            sightlines=("west_yard", "mid", "east_yard"),
        ),
        TacticalNode(
            id="west_yard",
            name_key="breachpoint-node-west-yard",
            adjacent=("t_spawn", "a_long"),
            sightlines=("t_spawn", "a_long"),
        ),
        TacticalNode(
            id="a_long",
            name_key="breachpoint-node-a-long",
            adjacent=("west_yard", "a_site"),
            sightlines=("west_yard", "a_site"),
        ),
        TacticalNode(
            id="a_site",
            name_key="breachpoint-node-a-site",
            adjacent=("a_long", "a_link", "connector"),
            sightlines=("a_long", "a_link", "connector", "mid_doors"),
            bomb_site=True,
        ),
        TacticalNode(
            id="a_link",
            name_key="breachpoint-node-a-link",
            adjacent=("a_site", "ct_spawn"),
            sightlines=("a_site", "ct_spawn"),
        ),
        TacticalNode(
            id="mid",
            name_key="breachpoint-node-mid",
            adjacent=("t_spawn", "mid_doors"),
            sightlines=("t_spawn", "mid_doors"),
        ),
        TacticalNode(
            id="mid_doors",
            name_key="breachpoint-node-mid-doors",
            adjacent=("mid", "connector"),
            sightlines=("mid", "connector", "a_site", "b_site"),
        ),
        TacticalNode(
            id="connector",
            name_key="breachpoint-node-connector",
            adjacent=("mid_doors", "a_site", "b_site", "ct_spawn"),
            sightlines=("mid_doors", "a_site", "b_site", "ct_spawn"),
        ),
        TacticalNode(
            id="east_yard",
            name_key="breachpoint-node-east-yard",
            adjacent=("t_spawn", "b_tunnels"),
            sightlines=("t_spawn", "b_tunnels"),
        ),
        TacticalNode(
            id="b_tunnels",
            name_key="breachpoint-node-b-tunnels",
            adjacent=("east_yard", "b_site"),
            sightlines=("east_yard", "b_site"),
        ),
        TacticalNode(
            id="b_site",
            name_key="breachpoint-node-b-site",
            adjacent=("b_tunnels", "b_link", "connector"),
            sightlines=("b_tunnels", "b_link", "connector", "mid_doors"),
            bomb_site=True,
        ),
        TacticalNode(
            id="b_link",
            name_key="breachpoint-node-b-link",
            adjacent=("b_site", "ct_spawn"),
            sightlines=("b_site", "ct_spawn"),
        ),
        TacticalNode(
            id="ct_spawn",
            name_key="breachpoint-node-ct-spawn",
            adjacent=("a_link", "connector", "b_link"),
            sightlines=("a_link", "connector", "b_link"),
        ),
    ),
)


TACTICAL_MAPS = {DEPOT_MAP.id: DEPOT_MAP}
DEFAULT_MAP_ID = DEPOT_MAP.id

for _map in TACTICAL_MAPS.values():
    _validate_map(_map)


def get_tactical_map(map_id: str) -> TacticalMap | None:
    """Return a registered map by stable id."""

    return TACTICAL_MAPS.get(map_id)
