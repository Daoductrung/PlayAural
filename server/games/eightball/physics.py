"""Deterministic, server-authoritative physics for Eight-Ball Pool."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import random

from mashumaro.mixins.json import DataClassJSONMixin


# One simulation unit represents one inch. The selectable playing surfaces are
# real 7-foot bar, 8-foot tournament, and 9-foot professional proportions.
# Ball and pocket sizes do not scale with the table.
BALL_RADIUS = 1.125
CORNER_POCKET_MOUTH = 4.5625
SIDE_POCKET_MOUTH = 5.0625
# One concrete WPA-compliant pocket profile.  Mouths and shelves use the
# midpoints of the published ranges; horizontal cut angles are the specified
# values.  These values describe the playable slate/cushion geometry, not a
# decorative table cabinet.
CORNER_POCKET_SHELF = 1.625
SIDE_POCKET_SHELF = 0.1875
CORNER_POCKET_CUT_ANGLE = 142.0
SIDE_POCKET_CUT_ANGLE = 104.0
POCKET_BACK_DRAFT_ANGLE = 13.5


def _capture_radius(mouth: float) -> float:
    """Approximate the legal pocket mouth in the point-pocket table model.

    The ball centre must clear both cushion noses. The circular capture zone
    combines its rail-normal radius with half of the remaining mouth clearance.
    """
    half_clearance = (mouth - BALL_RADIUS * 2.0) / 2.0
    return math.hypot(BALL_RADIUS, half_clearance)


CORNER_POCKET_RADIUS = _capture_radius(CORNER_POCKET_MOUTH)
SIDE_POCKET_RADIUS = _capture_radius(SIDE_POCKET_MOUTH)


@dataclass(frozen=True)
class TableGeometry:
    size: str
    half_width: float
    half_height: float

    @property
    def pockets(self) -> tuple[tuple[float, float], ...]:
        return (
            (-self.half_width, self.half_height),
            (0.0, self.half_height),
            (self.half_width, self.half_height),
            (-self.half_width, -self.half_height),
            (0.0, -self.half_height),
            (self.half_width, -self.half_height),
        )

    @property
    def pocket_aim_points(self) -> tuple[tuple[float, float], ...]:
        """Physical drop-line targets, distinct from decorative pocket centres."""
        corner_inset = CORNER_JAW_OFFSET / 2.0
        corner_depth = CORNER_POCKET_SHELF / math.sqrt(2.0)
        corner_x = self.half_width - corner_inset + corner_depth
        corner_y = self.half_height - corner_inset + corner_depth
        side_y = self.half_height + SIDE_POCKET_SHELF
        return (
            (-corner_x, corner_y),
            (0.0, side_y),
            (corner_x, corner_y),
            (-corner_x, -corner_y),
            (0.0, -side_y),
            (corner_x, -corner_y),
        )

    @property
    def pocket_radii(self) -> tuple[float, ...]:
        return (
            CORNER_POCKET_RADIUS, SIDE_POCKET_RADIUS, CORNER_POCKET_RADIUS,
            CORNER_POCKET_RADIUS, SIDE_POCKET_RADIUS, CORNER_POCKET_RADIUS,
        )

    @property
    def pocket_capture_allowances(self) -> tuple[float, ...]:
        """Distance before the nominal pocket centre at which a ball drops.

        Corner-pocket distance is measured on the 45-degree centre line.  A
        side-pocket ball must pass the cushion nose by the shelf depth, hence
        its allowance is negative.
        """
        corner = CORNER_POCKET_MOUTH / 2.0 - CORNER_POCKET_SHELF
        side = -SIDE_POCKET_SHELF
        return (corner, side, corner, corner, side, corner)


TABLE_SIZES = ("7ft", "8ft", "9ft")
TABLE_GEOMETRIES: dict[str, TableGeometry] = {
    "7ft": TableGeometry("7ft", 39.0, 19.5),
    "8ft": TableGeometry("8ft", 46.0, 23.0),
    "9ft": TableGeometry("9ft", 50.0, 25.0),
}


def get_table_geometry(table_size: str = "9ft") -> TableGeometry:
    return TABLE_GEOMETRIES.get(table_size, TABLE_GEOMETRIES["9ft"])


# Backward-compatible aliases describe the default professional table.
_DEFAULT_GEOMETRY = get_table_geometry()
TABLE_HALF_WIDTH = _DEFAULT_GEOMETRY.half_width
TABLE_HALF_HEIGHT = _DEFAULT_GEOMETRY.half_height
POCKETS = _DEFAULT_GEOMETRY.pockets
POCKET_RADII = _DEFAULT_GEOMETRY.pocket_radii
# Retained for callers that need a conservative single pocket radius.
POCKET_RADIUS = max(POCKET_RADII)
CORNER_JAW_OFFSET = CORNER_POCKET_MOUTH / math.sqrt(2.0)
CORNER_POCKET_CUSHION_GAP = CORNER_JAW_OFFSET - BALL_RADIUS
SIDE_POCKET_CUSHION_GAP = SIDE_POCKET_MOUTH / 2.0 - BALL_RADIUS
STOP_SPEED = 0.32
SIMULATION_HZ = 60
MAX_SECONDS = 30.0
RAIL_RESTITUTION = 0.92
BALL_RESTITUTION = 0.97
# A firm centre-ball stroke must be capable of travelling roughly four table
# lengths on tournament cloth, as required by the WPA equipment specification.
FRICTION_PER_60HZ = 0.995
GRAVITY = 245.0
VERTICAL_RESTITUTION = 0.34
SPIN_DECAY_PER_60HZ = 0.982

@dataclass
class Ball(DataClassJSONMixin):
    number: int
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    z: float = 0.0
    vz: float = 0.0
    side_spin: float = 0.0
    roll_spin: float = 0.0
    potted: bool = False
    pocket_potted: int = -1


@dataclass
class PhysicsEvent(DataClassJSONMixin):
    tick: int
    kind: str
    x: float
    y: float
    z: float = 0.0
    ball: int = -1
    other_ball: int = -1
    pocket: int = -1
    strength: float = 0.0


@dataclass
class ShotResult(DataClassJSONMixin):
    balls: list[Ball] = field(default_factory=list)
    events: list[PhysicsEvent] = field(default_factory=list)
    first_contact: int = -1
    potted: list[int] = field(default_factory=list)
    cue_scratch: bool = False
    off_table: list[int] = field(default_factory=list)
    rail_after_contact: bool = False
    rail_balls: list[int] = field(default_factory=list)
    duration_ticks: int = 1


def build_rack(*, randomize: bool = False, table_size: str = "9ft") -> list[Ball]:
    """Return a regulation-style rack with the eight in the centre."""
    geometry = get_table_geometry(table_size)
    foot_spot = -geometry.half_width / 2.0
    balls = [Ball(number=0, x=-foot_spot, y=0.0)]
    if randomize:
        solids = list(range(1, 8))
        stripes = list(range(9, 16))
        corner_solid = random.choice(solids)
        corner_stripe = random.choice(stripes)
        remaining = [number for number in solids + stripes if number not in {corner_solid, corner_stripe}]
        random.shuffle(remaining)
        values = iter(remaining)
        rack = (
            (next(values),),
            (next(values), next(values)),
            (next(values), 8, next(values)),
            (next(values), next(values), next(values), next(values)),
            (corner_solid, next(values), next(values), next(values), corner_stripe),
        )
        if random.choice((False, True)):
            rack = rack[:-1] + ((corner_stripe, *rack[-1][1:-1], corner_solid),)
    else:
        rack = (
            (1,),
            (9, 2),
            (3, 8, 10),
            (11, 4, 12, 5),
            (6, 13, 7, 14, 15),
        )
    spacing_x = BALL_RADIUS * math.sqrt(3.0)
    spacing_y = BALL_RADIUS * 2.0
    for column, numbers in enumerate(rack):
        x = foot_spot - column * spacing_x
        y0 = -(len(numbers) - 1) * spacing_y / 2.0
        for row, number in enumerate(numbers):
            balls.append(Ball(number=number, x=x, y=y0 + row * spacing_y))
    return balls


def build_cutthroat_rack(*, table_size: str = "9ft") -> list[Ball]:
    """Return the published BCA Cut-Throat rack: 1 apex, 6/11 corners."""
    geometry = get_table_geometry(table_size)
    foot_spot = -geometry.half_width / 2.0
    remaining = [number for number in range(2, 16) if number not in {6, 11}]
    random.shuffle(remaining)
    values = iter(remaining)
    rack = (
        (1,),
        (next(values), next(values)),
        (next(values), next(values), next(values)),
        (next(values), next(values), next(values), next(values)),
        (6, next(values), next(values), next(values), 11),
    )
    balls = [Ball(number=0, x=-foot_spot, y=0.0)]
    spacing_x = BALL_RADIUS * math.sqrt(3.0)
    spacing_y = BALL_RADIUS * 2.0
    for column, numbers in enumerate(rack):
        x = foot_spot - column * spacing_x
        y0 = -(len(numbers) - 1) * spacing_y / 2.0
        for row, number in enumerate(numbers):
            balls.append(Ball(number=number, x=x, y=y0 + row * spacing_y))
    return balls


def shot_speed(power: float) -> float:
    """Map the human-friendly 10-100 power scale to cue-ball speed."""
    normalized = max(0.1, min(1.0, power / 100.0))
    return 4.0 + 146.0 * normalized**1.70


def simulate_shot(
    source_balls: list[Ball], angle_degrees: float, power: float, spin: int = 0,
    side_spin: int = 0, elevation_degrees: float = 0.0, *, table_size: str = "9ft",
) -> ShotResult:
    """Simulate a complete shot without mutating ``source_balls``.

    Fixed time steps, adaptive substeps, and stable ball-number iteration keep
    the authoritative result reproducible across server platforms.
    """
    geometry = get_table_geometry(table_size)
    balls = [Ball.from_dict(ball.to_dict()) for ball in source_balls]
    cue = next((ball for ball in balls if ball.number == 0 and not ball.potted), None)
    if cue is None:
        return ShotResult(balls=balls)

    speed = shot_speed(power)
    angle = math.radians(angle_degrees)
    elevation = math.radians(max(0.0, min(45.0, elevation_degrees)))
    horizontal_speed = speed * math.cos(elevation)
    cue.vx = math.cos(angle) * horizontal_speed
    cue.vy = math.sin(angle) * horizontal_speed
    # A level stroke stays on the cloth. Raising the butt of the cue gives the
    # cue ball genuine vertical velocity; the ball can then jump over another
    # ball instead of merely changing a two-dimensional trajectory.
    cue.vz = speed * math.sin(elevation) * 0.54
    cue.side_spin = max(-2, min(2, side_spin)) * speed * 0.018
    cue.roll_spin = max(-2, min(2, spin)) * speed * 0.042
    events: list[PhysicsEvent] = [
        PhysicsEvent(0, "cue", cue.x, cue.y, ball=0, strength=power / 100.0)
    ]
    first_contact = -1
    rail_after_contact = False
    rail_balls: set[int] = set()
    potted: list[int] = []
    off_table: list[int] = []
    spin_applied = False
    stopped_frames = 0
    elapsed_ticks = 1

    dt = 1.0 / SIMULATION_HZ
    max_steps = int(MAX_SECONDS * SIMULATION_HZ)
    for step in range(max_steps):
        moving = [ball for ball in balls if not ball.potted]
        fastest = max((math.hypot(ball.vx, ball.vy) for ball in moving), default=0.0)
        # Keep fast cut shots accurate. Large collision steps can detect an
        # overlap too late, changing the contact normal and therefore the
        # object-ball angle according to shot power.
        substeps = max(1, min(6, math.ceil(fastest * dt / (BALL_RADIUS * 0.45))))
        sub_dt = dt / substeps

        for _ in range(substeps):
            for ball in moving:
                ball.x += ball.vx * sub_dt
                ball.y += ball.vy * sub_dt
                if ball.z > 0.0 or ball.vz > 0.0:
                    ball.z += ball.vz * sub_dt
                    ball.vz -= GRAVITY * sub_dt
                    if ball.z <= 0.0:
                        impact = abs(ball.vz)
                        ball.z = 0.0
                        if impact > 8.0:
                            ball.vz = impact * VERTICAL_RESTITUTION
                            events.append(PhysicsEvent(
                                _audio_tick(step), "land", ball.x, ball.y, z=0.0,
                                ball=ball.number, strength=min(1.0, impact / 70.0),
                            ))
                        else:
                            ball.vz = 0.0

            for ball in moving:
                pocket_index = (
                    _pocket_index(ball, geometry) if ball.z < BALL_RADIUS * 0.7 else -1
                )
                if pocket_index >= 0:
                    ball.potted = True
                    ball.pocket_potted = pocket_index
                    ball.z = _pocket_drop_z(ball, geometry, pocket_index)
                    ball.vx = ball.vy = ball.vz = 0.0
                    potted.append(ball.number)
                    px, py = geometry.pockets[pocket_index]
                    events.append(
                        PhysicsEvent(
                            _audio_tick(step), "pocket", px, py, z=ball.z,
                            ball=ball.number, pocket=pocket_index, strength=0.9,
                        )
                    )

            for ball in moving:
                if ball.potted:
                    continue
                if (
                    abs(ball.x) > geometry.half_width + BALL_RADIUS
                    or abs(ball.y) > geometry.half_height + BALL_RADIUS
                ):
                    ball.potted = True
                    ball.pocket_potted = -2
                    ball.vx = ball.vy = ball.vz = 0.0
                    off_table.append(ball.number)
                    events.append(PhysicsEvent(
                        _audio_tick(step), "off_table", ball.x, ball.y, z=ball.z,
                        ball=ball.number, strength=0.9,
                    ))

            moving = [ball for ball in balls if not ball.potted]
            for ball in moving:
                jaw_hit = (
                    ball.z < BALL_RADIUS
                    and _resolve_pocket_facing_collision(ball, geometry)
                )
                rail_x = (
                    ball.z < BALL_RADIUS
                    and abs(ball.x) > geometry.half_width - BALL_RADIUS
                    and not _in_vertical_cushion_gap(ball.y, geometry)
                )
                rail_y = (
                    ball.z < BALL_RADIUS
                    and abs(ball.y) > geometry.half_height - BALL_RADIUS
                    and not _in_horizontal_cushion_gap(ball.x, geometry)
                )
                if rail_x:
                    ball.x = math.copysign(geometry.half_width - BALL_RADIUS, ball.x)
                    ball.vx = -ball.vx * RAIL_RESTITUTION
                    ball.vy += ball.side_spin * 0.85 * math.copysign(1.0, ball.x)
                    ball.side_spin *= 0.72
                if rail_y:
                    ball.y = math.copysign(geometry.half_height - BALL_RADIUS, ball.y)
                    ball.vy = -ball.vy * RAIL_RESTITUTION
                    ball.vx -= ball.side_spin * 0.85 * math.copysign(1.0, ball.y)
                    ball.side_spin *= 0.72
                if rail_x or rail_y or jaw_hit:
                    if first_contact >= 0:
                        rail_after_contact = True
                        rail_balls.add(ball.number)
                    strength = min(1.0, math.hypot(ball.vx, ball.vy) / 90.0)
                    events.append(
                        PhysicsEvent(
                            _audio_tick(step), "rail", ball.x, ball.y,
                            ball=ball.number, strength=strength,
                        )
                    )

            moving.sort(key=lambda ball: ball.number)
            for index, first in enumerate(moving):
                for second in moving[index + 1 :]:
                    dx = second.x - first.x
                    dy = second.y - first.y
                    dz = second.z - first.z
                    distance_sq = dx * dx + dy * dy + dz * dz
                    diameter = BALL_RADIUS * 2.0
                    contact_tau = _swept_contact_time(first, second, diameter, sub_dt)
                    if distance_sq >= diameter * diameter and contact_tau is None:
                        continue
                    if contact_tau is not None:
                        first_contact_x = first.x + first.vx * contact_tau
                        first_contact_y = first.y + first.vy * contact_tau
                        first_contact_z = first.z + first.vz * contact_tau
                        second_contact_x = second.x + second.vx * contact_tau
                        second_contact_y = second.y + second.vy * contact_tau
                        second_contact_z = second.z + second.vz * contact_tau
                        dx = second_contact_x - first_contact_x
                        dy = second_contact_y - first_contact_y
                        dz = second_contact_z - first_contact_z
                        distance = math.sqrt(max(dx * dx + dy * dy + dz * dz, 1e-9))
                        nx, ny, nz = dx / distance, dy / distance, dz / distance
                    else:
                        distance = math.sqrt(max(distance_sq, 1e-9))
                        nx, ny, nz = dx / distance, dy / distance, dz / distance
                    relative = (
                        (second.vx - first.vx) * nx
                        + (second.vy - first.vy) * ny
                        + (second.vz - first.vz) * nz
                    )
                    if relative >= 0.0:
                        continue
                    if contact_tau is not None:
                        first.x, first.y, first.z = (
                            first_contact_x, first_contact_y, max(0.0, first_contact_z)
                        )
                        second.x, second.y, second.z = (
                            second_contact_x, second_contact_y, max(0.0, second_contact_z)
                        )
                    else:
                        overlap = diameter - distance
                        first.x -= nx * overlap * 0.5
                        first.y -= ny * overlap * 0.5
                        first.z = max(0.0, first.z - nz * overlap * 0.5)
                        second.x += nx * overlap * 0.5
                        second.y += ny * overlap * 0.5
                        second.z = max(0.0, second.z + nz * overlap * 0.5)
                    impulse = -(1.0 + BALL_RESTITUTION) * relative * 0.5
                    first.vx -= impulse * nx
                    first.vy -= impulse * ny
                    first.vz -= impulse * nz
                    second.vx += impulse * nx
                    second.vy += impulse * ny
                    second.vz += impulse * nz
                    if first_contact < 0 and (first.number == 0 or second.number == 0):
                        object_ball = second if first.number == 0 else first
                        first_contact = object_ball.number
                    if not spin_applied and first_contact >= 0:
                        # Follow and draw act after impact through retained cue-ball
                        # rotation. Side spin adds a small collision throw.
                        cue.vx += math.cos(angle) * cue.roll_spin
                        cue.vy += math.sin(angle) * cue.roll_spin
                        tangent_x, tangent_y = -ny, nx
                        cue.vx += tangent_x * cue.side_spin * 0.35
                        cue.vy += tangent_y * cue.side_spin * 0.35
                        object_ball.vx -= tangent_x * cue.side_spin * 0.18
                        object_ball.vy -= tangent_y * cue.side_spin * 0.18
                        spin_applied = True
                    if contact_tau is not None:
                        remaining = -contact_tau
                        first.x += first.vx * remaining
                        first.y += first.vy * remaining
                        first.z = max(0.0, first.z + first.vz * remaining)
                        second.x += second.vx * remaining
                        second.y += second.vy * remaining
                        second.z = max(0.0, second.z + second.vz * remaining)
                    events.append(
                        PhysicsEvent(
                            _audio_tick(step), "collision",
                            (first.x + second.x) / 2.0,
                            (first.y + second.y) / 2.0,
                            ball=first.number, other_ball=second.number,
                            strength=min(1.0, abs(relative) / 75.0),
                        )
                    )

        friction = FRICTION_PER_60HZ ** (60.0 / SIMULATION_HZ)
        for ball in balls:
            if ball.potted:
                continue
            if ball.z == 0.0:
                # Cloth-side spin produces a progressively curving masse path.
                horizontal = math.hypot(ball.vx, ball.vy)
                if horizontal > STOP_SPEED and ball.side_spin:
                    curve = ball.side_spin * 0.0028
                    ball.vx, ball.vy = (
                        ball.vx - ball.vy * curve,
                        ball.vy + ball.vx * curve,
                    )
                ball.vx *= friction
                ball.vy *= friction
                ball.roll_spin *= SPIN_DECAY_PER_60HZ ** (60.0 / SIMULATION_HZ)
                ball.side_spin *= SPIN_DECAY_PER_60HZ ** (60.0 / SIMULATION_HZ)
            if math.hypot(ball.vx, ball.vy) < STOP_SPEED and ball.z == 0.0:
                ball.vx = ball.vy = 0.0

        elapsed_ticks = _audio_tick(step) + 1
        if all(ball.potted or (ball.vx == 0.0 and ball.vy == 0.0 and ball.vz == 0.0) for ball in balls):
            stopped_frames += 1
            if stopped_frames >= 3:
                break
        else:
            stopped_frames = 0

    for ball in balls:
        ball.vx = ball.vy = ball.vz = 0.0
    events = _thin_audio_events(events)
    return ShotResult(
        balls=balls,
        events=events,
        first_contact=first_contact,
        potted=potted,
        cue_scratch=0 in potted or 0 in off_table,
        off_table=off_table,
        rail_after_contact=rail_after_contact,
        rail_balls=sorted(rail_balls),
        duration_ticks=max(1, elapsed_ticks),
    )


def _pocket_index(ball: Ball, geometry: TableGeometry) -> int:
    # Side pockets: the centre must clear both noses, pass the cushion line,
    # and traverse the WPA shelf before it can fall.  The 104-degree facings
    # are resolved separately as real collision surfaces.
    side_clearance = SIDE_POCKET_MOUTH / 2.0 - BALL_RADIUS
    for index, side in ((1, 1.0), (4, -1.0)):
        depth = side * ball.y - geometry.half_height
        if depth >= SIDE_POCKET_SHELF and abs(ball.x) <= side_clearance:
            return index

    # Corner pockets use coordinates aligned with the 45-degree pocket axis.
    # The mouth lies at s=mouth/2 and the slate cut lies one shelf-depth behind
    # it.  Requiring ball-centre clearance on both sides prevents a ball that
    # clips a jaw from being declared pocketed.
    centre_clearance = (CORNER_POCKET_MOUTH - BALL_RADIUS * 2.0) / 2.0
    for index, sx, sy in (
        (0, -1.0, 1.0), (2, 1.0, 1.0),
        (3, -1.0, -1.0), (5, 1.0, -1.0),
    ):
        inward_x = geometry.half_width - sx * ball.x
        inward_y = geometry.half_height - sy * ball.y
        axial = (inward_x + inward_y) / math.sqrt(2.0)
        transverse = abs(inward_x - inward_y) / math.sqrt(2.0)
        depth = CORNER_POCKET_MOUTH / 2.0 - axial
        if depth >= CORNER_POCKET_SHELF and transverse <= centre_clearance:
            return index
    return -1


def _pocket_drop_z(ball: Ball, geometry: TableGeometry, pocket: int) -> float:
    """Place a captured ball below the slate using the WPA back-draft angle."""
    if pocket in {1, 4}:
        side = 1.0 if pocket == 1 else -1.0
        penetration = max(
            0.0, side * ball.y - geometry.half_height - SIDE_POCKET_SHELF,
        )
    else:
        sx = -1.0 if pocket in {0, 3} else 1.0
        sy = 1.0 if pocket in {0, 2} else -1.0
        inward_x = geometry.half_width - sx * ball.x
        inward_y = geometry.half_height - sy * ball.y
        axial = (inward_x + inward_y) / math.sqrt(2.0)
        penetration = max(
            0.0,
            CORNER_POCKET_MOUTH / 2.0 - axial - CORNER_POCKET_SHELF,
        )
    return -(
        BALL_RADIUS
        + penetration * math.tan(math.radians(POCKET_BACK_DRAFT_ANGLE))
    )


def _resolve_pocket_facing_collision(ball: Ball, geometry: TableGeometry) -> bool:
    """Collide a ball with the twelve regulation-angle pocket facings."""
    hit = False
    for ax, ay, bx, by in _pocket_facing_segments(geometry):
        segment_x, segment_y = bx - ax, by - ay
        length_squared = segment_x * segment_x + segment_y * segment_y
        progress = max(0.0, min(
            1.0,
            ((ball.x - ax) * segment_x + (ball.y - ay) * segment_y)
            / max(length_squared, 1e-9),
        ))
        closest_x = ax + progress * segment_x
        closest_y = ay + progress * segment_y
        dx, dy = ball.x - closest_x, ball.y - closest_y
        distance = math.hypot(dx, dy)
        if distance >= BALL_RADIUS:
            continue
        if distance <= 1e-9:
            # Choose the segment normal that points toward the table centre.
            nx, ny = -segment_y, segment_x
            normal_length = math.hypot(nx, ny)
            nx, ny = nx / normal_length, ny / normal_length
            if nx * (-closest_x) + ny * (-closest_y) < 0.0:
                nx, ny = -nx, -ny
        else:
            nx, ny = dx / distance, dy / distance
        overlap = BALL_RADIUS - distance
        ball.x += nx * overlap
        ball.y += ny * overlap
        normal_speed = ball.vx * nx + ball.vy * ny
        if normal_speed < 0.0:
            ball.vx -= (1.0 + RAIL_RESTITUTION) * normal_speed * nx
            ball.vy -= (1.0 + RAIL_RESTITUTION) * normal_speed * ny
            tangent_x, tangent_y = -ny, nx
            tangent_spin = ball.side_spin * 0.85
            ball.vx += tangent_x * tangent_spin
            ball.vy += tangent_y * tangent_spin
            ball.side_spin *= 0.72
        hit = True
    return hit


def _pocket_facing_segments(
    geometry: TableGeometry,
) -> tuple[tuple[float, float, float, float], ...]:
    """Return cushion-facing segments using WPA horizontal cut angles."""
    segments: list[tuple[float, float, float, float]] = []

    # Side pockets.  A 104-degree cut is 14 degrees away from the direction
    # normal to the long cushion.
    side_tilt = math.radians(SIDE_POCKET_CUT_ANGLE - 90.0)
    side_length = SIDE_POCKET_SHELF / max(math.cos(side_tilt), 1e-9)
    for sy in (-1.0, 1.0):
        for sx in (-1.0, 1.0):
            ax = sx * SIDE_POCKET_MOUTH / 2.0
            ay = sy * geometry.half_height
            bx = ax - sx * math.sin(side_tilt) * side_length
            by = ay + sy * math.cos(side_tilt) * side_length
            segments.append((ax, ay, bx, by))

    # Corner pockets.  The facing makes 142 degrees with the inward-running
    # cushion, or 38 degrees with its outward continuation.
    corner_angle = math.radians(180.0 - CORNER_POCKET_CUT_ANGLE)
    corner_length = CORNER_POCKET_SHELF / max(
        math.cos(math.radians(45.0) - corner_angle), 1e-9,
    )
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            top_x = sx * (geometry.half_width - CORNER_JAW_OFFSET)
            top_y = sy * geometry.half_height
            segments.append((
                top_x, top_y,
                top_x + sx * math.cos(corner_angle) * corner_length,
                top_y + sy * math.sin(corner_angle) * corner_length,
            ))
            side_x = sx * geometry.half_width
            side_y = sy * (geometry.half_height - CORNER_JAW_OFFSET)
            segments.append((
                side_x, side_y,
                side_x + sx * math.sin(corner_angle) * corner_length,
                side_y + sy * math.cos(corner_angle) * corner_length,
            ))
    return tuple(segments)


def _swept_contact_time(
    first: Ball, second: Ball, diameter: float, sub_dt: float,
) -> float | None:
    """Find the entering contact time, measured backwards from this substep."""
    rx = second.x - first.x
    ry = second.y - first.y
    rz = second.z - first.z
    vx = second.vx - first.vx
    vy = second.vy - first.vy
    vz = second.vz - first.vz
    if (
        abs(rx) > diameter + abs(vx) * sub_dt
        or abs(ry) > diameter + abs(vy) * sub_dt
        or abs(rz) > diameter + abs(vz) * sub_dt
    ):
        return None
    a = vx * vx + vy * vy + vz * vz
    if a <= 1e-12:
        return None
    b = 2.0 * (rx * vx + ry * vy + rz * vz)
    c = rx * rx + ry * ry + rz * rz - diameter * diameter
    discriminant = b * b - 4.0 * a * c
    if discriminant < 0.0:
        return None
    root = math.sqrt(discriminant)
    candidates = (
        (-b - root) / (2.0 * a),
        (-b + root) / (2.0 * a),
    )
    valid = [value for value in candidates if -sub_dt - 1e-9 <= value <= 1e-9]
    return min(valid) if valid else None


def _in_vertical_cushion_gap(y: float, geometry: TableGeometry) -> bool:
    """Whether a ball centre is inside either corner-pocket opening."""
    return geometry.half_height - abs(y) <= CORNER_POCKET_CUSHION_GAP


def _in_horizontal_cushion_gap(x: float, geometry: TableGeometry) -> bool:
    """Whether a ball centre is inside a corner or side-pocket opening."""
    corner_gap = geometry.half_width - abs(x) <= CORNER_POCKET_CUSHION_GAP
    side_gap = abs(x) <= SIDE_POCKET_CUSHION_GAP
    return corner_gap or side_gap


def _audio_tick(simulation_step: int) -> int:
    return int(simulation_step * 20 / SIMULATION_HZ)


def _thin_audio_events(events: list[PhysicsEvent]) -> list[PhysicsEvent]:
    """Keep the soundscape legible when a break creates many simultaneous hits."""
    kept: list[PhysicsEvent] = []
    last_by_kind: dict[str, int] = {}
    for event in sorted(events, key=lambda item: (item.tick, item.kind, item.ball)):
        minimum_gap = 0 if event.kind in {"cue", "pocket"} else 1
        if event.tick - last_by_kind.get(event.kind, -99) < minimum_gap:
            continue
        kept.append(event)
        last_by_kind[event.kind] = event.tick
        if len(kept) >= 72:
            break
    return kept
