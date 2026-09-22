"""Validated spatial tactical maps for Breach Point."""

from __future__ import annotations

import math
from dataclasses import dataclass

TERRAIN_LOW_COVER = "low_cover"
TERRAIN_FULL_COVER = "full_cover"
TERRAIN_DOORWAY = "doorway"
TERRAIN_KINDS = frozenset({TERRAIN_LOW_COVER, TERRAIN_FULL_COVER, TERRAIN_DOORWAY})


@dataclass(frozen=True, order=True)
class GridPoint:
    """One integer coordinate in a map's two-dimensional world space."""

    x: int
    y: int


@dataclass(frozen=True)
class GridRect:
    """Inclusive rectangular footprint in map coordinates."""

    min_x: int
    min_y: int
    max_x: int
    max_y: int

    @property
    def width(self) -> int:
        return self.max_x - self.min_x + 1

    @property
    def height(self) -> int:
        return self.max_y - self.min_y + 1

    def contains(self, point: GridPoint) -> bool:
        return (
            self.min_x <= point.x <= self.max_x and self.min_y <= point.y <= self.max_y
        )

    def contains_rect(self, other: GridRect) -> bool:
        return (
            self.min_x <= other.min_x <= other.max_x <= self.max_x
            and self.min_y <= other.min_y <= other.max_y <= self.max_y
        )

    def overlaps(self, other: GridRect) -> bool:
        return not (
            self.max_x < other.min_x
            or other.max_x < self.min_x
            or self.max_y < other.min_y
            or other.max_y < self.min_y
        )

    def points(self) -> tuple[GridPoint, ...]:
        return tuple(
            GridPoint(x, y)
            for y in range(self.min_y, self.max_y + 1)
            for x in range(self.min_x, self.max_x + 1)
        )


@dataclass(frozen=True)
class TerrainFeature:
    """One named obstacle or piece of cover within a tactical area."""

    id: str
    name_key: str
    bounds: GridRect
    kind: str
    blocks_placement: bool = True


@dataclass(frozen=True)
class MapAmbienceLayer:
    """One map-authored global or acoustic-zone ambience loop."""

    id: str
    asset: str
    volume: int


@dataclass(frozen=True)
class MapAmbientEmitter:
    """One non-looping environmental sound family placed in world space."""

    id: str
    assets: tuple[str, ...]
    family: str
    position: GridPoint
    minimum_interval_seconds: int
    maximum_interval_seconds: int
    volume: int
    source_height_meters: float = 1.0
    audible_node_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class TacticalNode:
    """One named tactical area occupying a physical map footprint."""

    id: str
    name_key: str
    description_key: str
    footprint: GridRect
    anchor: GridPoint
    adjacent: tuple[str, ...]
    terrain: tuple[TerrainFeature, ...] = ()
    bomb_site: bool = False
    acoustic_zone: str = ""
    footstep_surface: str = "sand"

    def is_walkable(self, point: GridPoint) -> bool:
        """Return whether a coordinate is inside the area and free of terrain."""

        return self.footprint.contains(point) and not any(
            feature.blocks_placement and feature.bounds.contains(point)
            for feature in self.terrain
        )

    def placement_points(self, minimum_spacing: int = 1) -> tuple[GridPoint, ...]:
        """Return a dense walkable lattice with guaranteed occupant spacing."""

        walkable = tuple(
            point for point in self.footprint.points() if self.is_walkable(point)
        )
        if minimum_spacing <= 1:
            return walkable
        lattices = tuple(
            tuple(
                point
                for point in walkable
                if point.x % minimum_spacing == offset_x
                and point.y % minimum_spacing == offset_y
            )
            for offset_y in range(minimum_spacing)
            for offset_x in range(minimum_spacing)
        )
        return max(lattices, key=len, default=())


@dataclass(frozen=True)
class TacticalSightline:
    """One unobstructed, bidirectional firing lane between named areas."""

    first_node_id: str
    second_node_id: str

    def connects(self, source_id: str, target_id: str) -> bool:
        return (
            source_id == self.first_node_id and target_id == self.second_node_id
        ) or (source_id == self.second_node_id and target_id == self.first_node_id)

    def other(self, node_id: str) -> str | None:
        if node_id == self.first_node_id:
            return self.second_node_id
        if node_id == self.second_node_id:
            return self.first_node_id
        return None


@dataclass(frozen=True)
class TacticalMap:
    """Immutable movement, visibility, terrain, and world-space metadata."""

    id: str
    name_key: str
    bounds: GridRect
    grid_unit_meters: float
    range_band_grid_units: float
    minimum_player_spacing: int
    maximum_area_occupants: int
    terrorist_spawn: str
    counter_terrorist_spawn: str
    terrorist_spawn_heading: int
    counter_terrorist_spawn_heading: int
    spectator_anchor: GridPoint
    nodes: tuple[TacticalNode, ...]
    sightlines: tuple[TacticalSightline, ...]
    spectator_heading: int = 0
    global_ambience: MapAmbienceLayer | None = None
    zone_ambience: tuple[MapAmbienceLayer, ...] = ()
    ambient_emitters: tuple[MapAmbientEmitter, ...] = ()

    def node_map(self) -> dict[str, TacticalNode]:
        return {node.id: node for node in self.nodes}

    def get_node(self, node_id: str) -> TacticalNode | None:
        return next((node for node in self.nodes if node.id == node_id), None)

    def bomb_site_ids(self) -> tuple[str, ...]:
        return tuple(node.id for node in self.nodes if node.bomb_site)

    def visible_node_ids(self, node_id: str) -> tuple[str, ...]:
        """Return visible areas in stable map-definition order."""

        visible = {
            other
            for sightline in self.sightlines
            if (other := sightline.other(node_id)) is not None
        }
        return tuple(node.id for node in self.nodes if node.id in visible)

    def has_sightline(self, source_id: str, target_id: str) -> bool:
        if source_id == target_id:
            return self.get_node(source_id) is not None
        return any(
            sightline.connects(source_id, target_id) for sightline in self.sightlines
        )

    def combat_distance(self, source_id: str, target_id: str) -> int | None:
        """Return a weapon range band for one clear firing lane."""

        source = self.get_node(source_id)
        target = self.get_node(target_id)
        if not source or not target or not self.has_sightline(source_id, target_id):
            return None
        if source_id == target_id:
            return 0
        grid_distance = math.hypot(
            target.anchor.x - source.anchor.x,
            target.anchor.y - source.anchor.y,
        )
        return max(1, math.ceil(grid_distance / self.range_band_grid_units))


def _validate_map(tactical_map: TacticalMap) -> None:
    """Reject incomplete, ambiguous, or spatially invalid map definitions."""

    if not tactical_map.id or not tactical_map.name_key:
        raise ValueError("Tactical maps require stable ids and localized names")
    if tactical_map.bounds.width <= 0 or tactical_map.bounds.height <= 0:
        raise ValueError(f"Tactical map {tactical_map.id} has invalid bounds")
    if tactical_map.grid_unit_meters <= 0 or tactical_map.range_band_grid_units <= 0:
        raise ValueError(f"Tactical map {tactical_map.id} has invalid spatial scale")
    if tactical_map.minimum_player_spacing <= 0:
        raise ValueError(f"Tactical map {tactical_map.id} has invalid player spacing")
    if tactical_map.maximum_area_occupants <= 0:
        raise ValueError(f"Tactical map {tactical_map.id} has invalid area capacity")
    if not tactical_map.bounds.contains(tactical_map.spectator_anchor):
        raise ValueError(
            f"Tactical map {tactical_map.id} has an invalid spectator anchor"
        )
    for heading in (
        tactical_map.terrorist_spawn_heading,
        tactical_map.counter_terrorist_spawn_heading,
        tactical_map.spectator_heading,
    ):
        if not 0 <= heading < 360:
            raise ValueError(f"Tactical map {tactical_map.id} has an invalid heading")

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
    if not any(
        node.is_walkable(tactical_map.spectator_anchor) for node in tactical_map.nodes
    ):
        raise ValueError(
            f"Tactical map {tactical_map.id} has a non-walkable spectator anchor"
        )

    ambience_layers = (
        () if tactical_map.global_ambience is None else (tactical_map.global_ambience,)
    ) + tactical_map.zone_ambience
    ambience_ids = [layer.id for layer in ambience_layers]
    if len(set(ambience_ids)) != len(ambience_ids):
        raise ValueError(f"Tactical map {tactical_map.id} has duplicate ambience ids")
    for layer in ambience_layers:
        if not layer.id or not layer.asset or not 0 <= layer.volume <= 100:
            raise ValueError(
                f"Tactical map {tactical_map.id} has invalid ambience metadata"
            )
    zone_ids = {layer.id for layer in tactical_map.zone_ambience}

    emitter_ids = [emitter.id for emitter in tactical_map.ambient_emitters]
    if len(set(emitter_ids)) != len(emitter_ids):
        raise ValueError(f"Tactical map {tactical_map.id} has duplicate emitters")
    for emitter in tactical_map.ambient_emitters:
        if (
            not emitter.id
            or not emitter.assets
            or any(not asset for asset in emitter.assets)
            or (len(emitter.assets) > 1 and not emitter.family)
            or not tactical_map.bounds.contains(emitter.position)
            or emitter.minimum_interval_seconds <= 0
            or emitter.maximum_interval_seconds < emitter.minimum_interval_seconds
            or not 0 <= emitter.volume <= 100
            or emitter.source_height_meters < 0
            or len(set(emitter.audible_node_ids)) != len(emitter.audible_node_ids)
            or any(node_id not in nodes for node_id in emitter.audible_node_ids)
        ):
            raise ValueError(
                f"Tactical map {tactical_map.id} has invalid ambient emitter metadata"
            )

    terrain_ids: set[str] = set()
    for index, node in enumerate(tactical_map.nodes):
        if not node.id or not node.name_key or not node.description_key:
            raise ValueError(f"Tactical map {tactical_map.id} has an unnamed node")
        if not tactical_map.bounds.contains_rect(node.footprint):
            raise ValueError(f"Node {node.id} extends beyond the tactical map")
        if not node.footprint.contains(node.anchor):
            raise ValueError(f"Node {node.id} has an anchor outside its footprint")
        if len(set(node.adjacent)) != len(node.adjacent):
            raise ValueError(f"Node {node.id} has duplicate movement edges")
        if node.id in node.adjacent:
            raise ValueError(f"Node {node.id} links to itself")
        if node.acoustic_zone and node.acoustic_zone not in zone_ids:
            raise ValueError(
                f"Node {node.id} uses unknown acoustic zone {node.acoustic_zone}"
            )
        if not node.footstep_surface:
            raise ValueError(f"Node {node.id} has no footstep surface")
        for other in tactical_map.nodes[index + 1 :]:
            if node.footprint.overlaps(other.footprint):
                raise ValueError(f"Node footprints {node.id} and {other.id} overlap")
        for neighbor_id in node.adjacent:
            neighbor = nodes.get(neighbor_id)
            if neighbor is None:
                raise ValueError(f"Node {node.id} has unknown neighbor {neighbor_id}")
            if node.id not in neighbor.adjacent:
                raise ValueError(
                    f"Movement edge {node.id} -> {neighbor_id} is not reciprocal"
                )
        for feature in node.terrain:
            if not feature.id or not feature.name_key:
                raise ValueError(f"Node {node.id} has unnamed terrain")
            if feature.id in terrain_ids:
                raise ValueError(f"Duplicate terrain id {feature.id}")
            terrain_ids.add(feature.id)
            if feature.kind not in TERRAIN_KINDS:
                raise ValueError(f"Terrain {feature.id} has an unknown kind")
            if not node.footprint.contains_rect(feature.bounds):
                raise ValueError(f"Terrain {feature.id} extends beyond node {node.id}")
            if feature.blocks_placement and feature.bounds.contains(node.anchor):
                raise ValueError(f"Terrain {feature.id} blocks node {node.id}'s anchor")
        if (
            len(node.placement_points(tactical_map.minimum_player_spacing))
            < tactical_map.maximum_area_occupants
        ):
            raise ValueError(f"Node {node.id} cannot hold the maximum roster")

    sightline_pairs: set[frozenset[str]] = set()
    for sightline in tactical_map.sightlines:
        pair = frozenset({sightline.first_node_id, sightline.second_node_id})
        if len(pair) != 2:
            raise ValueError("Tactical sightlines must connect two different nodes")
        if not pair.issubset(nodes):
            raise ValueError(f"Tactical map {tactical_map.id} has an unknown sightline")
        if pair in sightline_pairs:
            raise ValueError(
                f"Tactical map {tactical_map.id} has a duplicate sightline"
            )
        sightline_pairs.add(pair)
        distance = tactical_map.combat_distance(
            sightline.first_node_id,
            sightline.second_node_id,
        )
        if distance is None or distance <= 0:
            raise ValueError(f"Tactical map {tactical_map.id} has an invalid sightline")

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


def _terrain(
    feature_id: str,
    name_key: str,
    bounds: tuple[int, int, int, int],
    kind: str,
    *,
    blocks_placement: bool = True,
) -> TerrainFeature:
    return TerrainFeature(
        id=feature_id,
        name_key=name_key,
        bounds=GridRect(*bounds),
        kind=kind,
        blocks_placement=blocks_placement,
    )


DUST_OPEN_SKY_NODE_IDS = (
    "t_spawn",
    "outside_long",
    "pit",
    "a_long",
    "a_ramp",
    "a_site",
    "mid",
    "catwalk",
    "a_short",
    "ct_mid",
    "ct_spawn",
    "outside_tunnels",
    "b_doors",
    "b_site",
)
DUST_TUNNEL_NODE_IDS = ("upper_tunnels", "lower_tunnels", "b_tunnels")
DUST_LONG_NODE_IDS = ("long_doors", "pit", "a_long")


DUST_MAP = TacticalMap(
    id="dust",
    name_key="breachpoint-map-dust",
    bounds=GridRect(0, 0, 66, 55),
    grid_unit_meters=1.15,
    range_band_grid_units=12.0,
    minimum_player_spacing=2,
    maximum_area_occupants=10,
    terrorist_spawn="t_spawn",
    counter_terrorist_spawn="ct_spawn",
    terrorist_spawn_heading=0,
    counter_terrorist_spawn_heading=180,
    spectator_anchor=GridPoint(30, 15),
    spectator_heading=0,
    nodes=(
        TacticalNode(
            "t_spawn",
            "breachpoint-node-t-spawn",
            "breachpoint-area-t-spawn-description",
            GridRect(25, 0, 35, 7),
            GridPoint(30, 4),
            ("outside_long", "mid", "outside_tunnels"),
            (
                _terrain(
                    "t_spawn_crates",
                    "breachpoint-terrain-supply-crates",
                    (25, 0, 27, 2),
                    TERRAIN_FULL_COVER,
                ),
            ),
            acoustic_zone="sand_wind",
        ),
        TacticalNode(
            "outside_long",
            "breachpoint-node-outside-long",
            "breachpoint-area-outside-long-description",
            GridRect(43, 5, 51, 13),
            GridPoint(47, 9),
            ("t_spawn", "long_doors"),
            (
                _terrain(
                    "outside_long_crates",
                    "breachpoint-terrain-supply-crates",
                    (43, 11, 45, 13),
                    TERRAIN_FULL_COVER,
                ),
            ),
        ),
        TacticalNode(
            "long_doors",
            "breachpoint-node-long-doors",
            "breachpoint-area-long-doors-description",
            GridRect(52, 15, 58, 21),
            GridPoint(55, 18),
            ("outside_long", "pit", "a_long"),
            (
                _terrain(
                    "long_double_doors",
                    "breachpoint-terrain-double-doors",
                    (52, 15, 53, 18),
                    TERRAIN_DOORWAY,
                    blocks_placement=False,
                ),
            ),
            acoustic_zone="long_wind",
            footstep_surface="concrete",
        ),
        TacticalNode(
            "pit",
            "breachpoint-node-pit",
            "breachpoint-area-pit-description",
            GridRect(59, 23, 66, 31),
            GridPoint(62, 27),
            ("long_doors", "a_long"),
            (
                _terrain(
                    "pit_wall",
                    "breachpoint-terrain-stone-pit-wall",
                    (64, 23, 66, 25),
                    TERRAIN_LOW_COVER,
                ),
            ),
            acoustic_zone="long_wind",
            footstep_surface="gravel",
        ),
        TacticalNode(
            "a_long",
            "breachpoint-node-a-long",
            "breachpoint-area-a-long-description",
            GridRect(52, 29, 58, 38),
            GridPoint(55, 34),
            ("long_doors", "pit", "a_ramp"),
            (
                _terrain(
                    "a_long_car",
                    "breachpoint-terrain-disabled-car",
                    (56, 29, 58, 31),
                    TERRAIN_FULL_COVER,
                ),
            ),
            acoustic_zone="long_wind",
            footstep_surface="gravel",
        ),
        TacticalNode(
            "a_ramp",
            "breachpoint-node-a-ramp",
            "breachpoint-area-a-ramp-description",
            GridRect(49, 39, 56, 45),
            GridPoint(52, 42),
            ("a_long", "a_site"),
            (
                _terrain(
                    "a_ramp_boxes",
                    "breachpoint-terrain-ramp-boxes",
                    (49, 43, 51, 45),
                    TERRAIN_LOW_COVER,
                ),
            ),
            acoustic_zone="elevated_wind",
            footstep_surface="concrete",
        ),
        TacticalNode(
            "a_site",
            "breachpoint-node-a-site",
            "breachpoint-area-a-site-description",
            GridRect(50, 46, 63, 55),
            GridPoint(56, 51),
            ("a_ramp", "a_short", "ct_spawn"),
            (
                _terrain(
                    "a_site_crates",
                    "breachpoint-terrain-bomb-crates",
                    (50, 46, 53, 49),
                    TERRAIN_FULL_COVER,
                ),
                _terrain(
                    "a_site_goose",
                    "breachpoint-terrain-goose-wall",
                    (61, 52, 63, 55),
                    TERRAIN_FULL_COVER,
                ),
            ),
            bomb_site=True,
            acoustic_zone="elevated_wind",
            footstep_surface="concrete",
        ),
        TacticalNode(
            "mid",
            "breachpoint-node-mid",
            "breachpoint-area-mid-description",
            GridRect(26, 10, 35, 19),
            GridPoint(30, 15),
            ("t_spawn", "mid_doors", "catwalk", "lower_tunnels"),
            (
                _terrain(
                    "mid_xbox",
                    "breachpoint-terrain-xbox",
                    (33, 17, 35, 19),
                    TERRAIN_FULL_COVER,
                ),
            ),
        ),
        TacticalNode(
            "catwalk",
            "breachpoint-node-catwalk",
            "breachpoint-area-catwalk-description",
            GridRect(37, 21, 44, 29),
            GridPoint(40, 25),
            ("mid", "a_short"),
            (
                _terrain(
                    "catwalk_wall",
                    "breachpoint-terrain-catwalk-wall",
                    (37, 27, 39, 29),
                    TERRAIN_LOW_COVER,
                ),
            ),
            footstep_surface="concrete",
        ),
        TacticalNode(
            "a_short",
            "breachpoint-node-a-short",
            "breachpoint-area-a-short-description",
            GridRect(42, 31, 49, 38),
            GridPoint(48, 37),
            ("catwalk", "a_site", "ct_spawn"),
            (
                _terrain(
                    "a_short_boxes",
                    "breachpoint-terrain-short-boxes",
                    (42, 31, 44, 33),
                    TERRAIN_FULL_COVER,
                ),
            ),
            footstep_surface="concrete",
        ),
        TacticalNode(
            "mid_doors",
            "breachpoint-node-mid-doors",
            "breachpoint-area-mid-doors-description",
            GridRect(27, 22, 35, 29),
            GridPoint(31, 26),
            ("mid", "ct_mid"),
            (
                _terrain(
                    "mid_double_doors",
                    "breachpoint-terrain-double-doors",
                    (27, 25, 28, 28),
                    TERRAIN_DOORWAY,
                    blocks_placement=False,
                ),
            ),
            footstep_surface="concrete",
        ),
        TacticalNode(
            "ct_mid",
            "breachpoint-node-ct-mid",
            "breachpoint-area-ct-mid-description",
            GridRect(28, 32, 36, 40),
            GridPoint(32, 36),
            ("mid_doors", "ct_spawn", "b_doors"),
            (
                _terrain(
                    "ct_mid_boxes",
                    "breachpoint-terrain-ct-boxes",
                    (34, 38, 36, 40),
                    TERRAIN_FULL_COVER,
                ),
            ),
            footstep_surface="concrete",
        ),
        TacticalNode(
            "ct_spawn",
            "breachpoint-node-ct-spawn",
            "breachpoint-area-ct-spawn-description",
            GridRect(37, 41, 47, 49),
            GridPoint(42, 45),
            ("ct_mid", "a_short", "a_site", "b_doors"),
            (
                _terrain(
                    "ct_spawn_crates",
                    "breachpoint-terrain-supply-crates",
                    (37, 47, 39, 49),
                    TERRAIN_FULL_COVER,
                ),
            ),
            footstep_surface="concrete",
        ),
        TacticalNode(
            "outside_tunnels",
            "breachpoint-node-outside-tunnels",
            "breachpoint-area-outside-tunnels-description",
            GridRect(9, 6, 19, 14),
            GridPoint(14, 10),
            ("t_spawn", "upper_tunnels"),
            (
                _terrain(
                    "outside_tunnels_crates",
                    "breachpoint-terrain-supply-crates",
                    (9, 6, 11, 8),
                    TERRAIN_FULL_COVER,
                ),
            ),
            acoustic_zone="sand_wind",
        ),
        TacticalNode(
            "upper_tunnels",
            "breachpoint-node-upper-tunnels",
            "breachpoint-area-upper-tunnels-description",
            GridRect(7, 16, 18, 25),
            GridPoint(12, 21),
            ("outside_tunnels", "lower_tunnels", "b_tunnels"),
            (
                _terrain(
                    "upper_tunnel_pillars",
                    "breachpoint-terrain-tunnel-pillars",
                    (7, 16, 9, 19),
                    TERRAIN_FULL_COVER,
                ),
            ),
            acoustic_zone="tunnels",
            footstep_surface="concrete",
        ),
        TacticalNode(
            "lower_tunnels",
            "breachpoint-node-lower-tunnels",
            "breachpoint-area-lower-tunnels-description",
            GridRect(19, 20, 25, 27),
            GridPoint(22, 24),
            ("upper_tunnels", "mid"),
            (
                _terrain(
                    "lower_tunnel_corner",
                    "breachpoint-terrain-tunnel-corner",
                    (23, 25, 25, 27),
                    TERRAIN_FULL_COVER,
                ),
            ),
            acoustic_zone="tunnels",
            footstep_surface="concrete",
        ),
        TacticalNode(
            "b_tunnels",
            "breachpoint-node-b-tunnels",
            "breachpoint-area-b-tunnels-description",
            GridRect(6, 28, 15, 37),
            GridPoint(11, 33),
            ("upper_tunnels", "b_site"),
            (
                _terrain(
                    "b_tunnel_crates",
                    "breachpoint-terrain-tunnel-crates",
                    (6, 35, 8, 37),
                    TERRAIN_FULL_COVER,
                ),
            ),
            acoustic_zone="tunnels",
            footstep_surface="concrete",
        ),
        TacticalNode(
            "b_doors",
            "breachpoint-node-b-doors",
            "breachpoint-area-b-doors-description",
            GridRect(19, 35, 26, 43),
            GridPoint(23, 39),
            ("ct_mid", "ct_spawn", "b_site"),
            (
                _terrain(
                    "b_double_doors",
                    "breachpoint-terrain-double-doors",
                    (24, 35, 26, 37),
                    TERRAIN_DOORWAY,
                    blocks_placement=False,
                ),
            ),
            footstep_surface="concrete",
        ),
        TacticalNode(
            "b_site",
            "breachpoint-node-b-site",
            "breachpoint-area-b-site-description",
            GridRect(5, 44, 18, 55),
            GridPoint(12, 50),
            ("b_tunnels", "b_doors"),
            (
                _terrain(
                    "b_site_platform",
                    "breachpoint-terrain-b-platform",
                    (5, 44, 8, 47),
                    TERRAIN_LOW_COVER,
                ),
                _terrain(
                    "b_site_boxes",
                    "breachpoint-terrain-bomb-crates",
                    (15, 52, 18, 55),
                    TERRAIN_FULL_COVER,
                ),
            ),
            bomb_site=True,
            acoustic_zone="b_courtyard_wind",
            footstep_surface="concrete",
        ),
    ),
    sightlines=(
        TacticalSightline("t_spawn", "outside_long"),
        TacticalSightline("t_spawn", "mid"),
        TacticalSightline("t_spawn", "mid_doors"),
        TacticalSightline("t_spawn", "ct_mid"),
        TacticalSightline("t_spawn", "outside_tunnels"),
        TacticalSightline("outside_long", "long_doors"),
        TacticalSightline("long_doors", "pit"),
        TacticalSightline("long_doors", "a_long"),
        TacticalSightline("pit", "a_long"),
        TacticalSightline("pit", "a_site"),
        TacticalSightline("a_long", "a_ramp"),
        TacticalSightline("a_long", "a_site"),
        TacticalSightline("a_ramp", "a_site"),
        TacticalSightline("a_short", "a_site"),
        TacticalSightline("mid", "mid_doors"),
        TacticalSightline("mid", "catwalk"),
        TacticalSightline("mid", "ct_mid"),
        TacticalSightline("mid", "ct_spawn"),
        TacticalSightline("catwalk", "a_short"),
        TacticalSightline("a_short", "ct_spawn"),
        TacticalSightline("mid_doors", "ct_mid"),
        TacticalSightline("mid_doors", "ct_spawn"),
        TacticalSightline("ct_mid", "ct_spawn"),
        TacticalSightline("ct_mid", "b_doors"),
        TacticalSightline("ct_spawn", "a_site"),
        TacticalSightline("ct_spawn", "b_doors"),
        TacticalSightline("ct_spawn", "b_tunnels"),
        TacticalSightline("outside_tunnels", "upper_tunnels"),
        TacticalSightline("upper_tunnels", "lower_tunnels"),
        TacticalSightline("upper_tunnels", "b_tunnels"),
        TacticalSightline("b_tunnels", "b_doors"),
        TacticalSightline("b_tunnels", "b_site"),
        TacticalSightline("b_doors", "b_site"),
    ),
    global_ambience=MapAmbienceLayer(
        id="desert_wind",
        asset="game_breachpoint/ambience/bg_dust.ogg",
        volume=22,
    ),
    zone_ambience=(
        MapAmbienceLayer(
            id="tunnels",
            asset="game_breachpoint/ambience/dust/interior_tunnel.ogg",
            volume=30,
        ),
        MapAmbienceLayer(
            id="long_wind",
            asset="game_breachpoint/ambience/dust/wind_alley.ogg",
            volume=25,
        ),
        MapAmbienceLayer(
            id="elevated_wind",
            asset="game_breachpoint/ambience/dust/wind_strong.ogg",
            volume=24,
        ),
        MapAmbienceLayer(
            id="sand_wind",
            asset="game_breachpoint/ambience/dust/wind_sand.ogg",
            volume=23,
        ),
        MapAmbienceLayer(
            id="b_courtyard_wind",
            asset="game_breachpoint/ambience/dust/wind_thin.ogg",
            volume=22,
        ),
    ),
    ambient_emitters=(
        MapAmbientEmitter(
            id="aircraft",
            assets=tuple(
                f"game_breachpoint/ambience/dust/airplane{index}.ogg"
                for index in range(1, 4)
            ),
            family="game_breachpoint/ambience/dust/airplane",
            position=GridPoint(30, 28),
            minimum_interval_seconds=120,
            maximum_interval_seconds=180,
            volume=38,
            source_height_meters=18.0,
            audible_node_ids=DUST_OPEN_SKY_NODE_IDS,
        ),
        MapAmbientEmitter(
            id="cables",
            assets=tuple(
                f"game_breachpoint/ambience/dust/cable_stress{index}.ogg"
                for index in range(1, 7)
            ),
            family="game_breachpoint/ambience/dust/cable_stress",
            position=GridPoint(55, 18),
            minimum_interval_seconds=28,
            maximum_interval_seconds=62,
            volume=30,
            source_height_meters=4.0,
            audible_node_ids=DUST_LONG_NODE_IDS,
        ),
        MapAmbientEmitter(
            id="city",
            assets=tuple(
                f"game_breachpoint/ambience/dust/distant_city{index}.ogg"
                for index in range(1, 3)
            ),
            family="game_breachpoint/ambience/dust/distant_city",
            position=GridPoint(66, 48),
            minimum_interval_seconds=90,
            maximum_interval_seconds=180,
            volume=24,
            source_height_meters=5.0,
            audible_node_ids=DUST_OPEN_SKY_NODE_IDS,
        ),
        MapAmbientEmitter(
            id="tunnel_rockfall",
            assets=tuple(
                f"game_breachpoint/ambience/dust/rockfall{index}.ogg"
                for index in range(1, 9)
            ),
            family="game_breachpoint/ambience/dust/rockfall",
            position=GridPoint(12, 25),
            minimum_interval_seconds=24,
            maximum_interval_seconds=55,
            volume=32,
            source_height_meters=1.8,
            audible_node_ids=DUST_TUNNEL_NODE_IDS,
        ),
        MapAmbientEmitter(
            id="sand_gust",
            assets=tuple(
                f"game_breachpoint/ambience/dust/sand_gust{index}.ogg"
                for index in range(1, 13)
            ),
            family="game_breachpoint/ambience/dust/sand_gust",
            position=GridPoint(31, 26),
            minimum_interval_seconds=18,
            maximum_interval_seconds=48,
            volume=25,
            source_height_meters=0.8,
            audible_node_ids=DUST_OPEN_SKY_NODE_IDS,
        ),
        MapAmbientEmitter(
            id="market_basket",
            assets=tuple(
                f"game_breachpoint/ambience/dust/sand_basket{index}.ogg"
                for index in range(1, 5)
            ),
            family="game_breachpoint/ambience/dust/sand_basket",
            position=GridPoint(14, 10),
            minimum_interval_seconds=35,
            maximum_interval_seconds=78,
            volume=28,
            source_height_meters=1.0,
            audible_node_ids=("outside_tunnels", "t_spawn"),
        ),
        MapAmbientEmitter(
            id="desert_auto",
            assets=tuple(
                f"game_breachpoint/ambience/dust/sand_auto{index}.ogg"
                for index in range(1, 6)
            ),
            family="game_breachpoint/ambience/dust/sand_auto",
            position=GridPoint(47, 9),
            minimum_interval_seconds=42,
            maximum_interval_seconds=96,
            volume=24,
            source_height_meters=1.0,
            audible_node_ids=("outside_long", "long_doors", "t_spawn"),
        ),
        MapAmbientEmitter(
            id="tunnel_interior",
            assets=tuple(
                f"game_breachpoint/ambience/dust/interior{index}.ogg"
                for index in range(1, 3)
            ),
            family="game_breachpoint/ambience/dust/interior",
            position=GridPoint(12, 21),
            minimum_interval_seconds=80,
            maximum_interval_seconds=165,
            volume=24,
            source_height_meters=2.0,
            audible_node_ids=DUST_TUNNEL_NODE_IDS,
        ),
        MapAmbientEmitter(
            id="tunnel_light",
            assets=("game_breachpoint/ambience/dust/light1.ogg",),
            family="",
            position=GridPoint(22, 24),
            minimum_interval_seconds=35,
            maximum_interval_seconds=85,
            volume=25,
            source_height_meters=2.5,
            audible_node_ids=DUST_TUNNEL_NODE_IDS,
        ),
        MapAmbientEmitter(
            id="courtyard_birds",
            assets=("game_breachpoint/ambience/dust/trees_birds1.ogg",),
            family="",
            position=GridPoint(56, 51),
            minimum_interval_seconds=105,
            maximum_interval_seconds=210,
            volume=21,
            source_height_meters=5.0,
            audible_node_ids=("a_site", "a_ramp", "a_short", "ct_spawn"),
        ),
    ),
)


TACTICAL_MAPS = {DUST_MAP.id: DUST_MAP}
DEFAULT_MAP_ID = DUST_MAP.id

for _map in TACTICAL_MAPS.values():
    _validate_map(_map)


def get_tactical_map(map_id: str) -> TacticalMap | None:
    """Return a registered map by stable id."""

    return TACTICAL_MAPS.get(map_id)
