"""Table management for games."""

import json
import logging
import math
import time
import types
from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING, Any, Literal, Union, get_args, get_origin

from mashumaro.mixins.json import DataClassJSONMixin

from ..game_utils.bot_names import bot_name_key, normalize_bot_name
from ..games.registry import get_game_class
from ..users.bot import Bot

if TYPE_CHECKING:
    from ..games.base import Game
    from ..users.base import User


ABANDONED_ACTIVE_TABLE_TIMEOUT_SECONDS = 15 * 60
WAITING_MEMBER_DISCONNECT_TIMEOUT_SECONDS = 15
TABLE_STATE_SCHEMA_VERSION = 1
SAVED_TABLE_PROPERTY = "saved_table_property"


def _encode_saved_table_value(value: Any) -> Any:
    """Convert one declared table property to deterministic JSON-safe data."""
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("saved table properties cannot contain non-finite numbers")
        return value
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise TypeError("saved table property mappings must use string keys")
        return {
            key: _encode_saved_table_value(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_encode_saved_table_value(item) for item in value]
    if isinstance(value, (set, frozenset)):
        encoded = [_encode_saved_table_value(item) for item in value]
        return sorted(
            encoded,
            key=lambda item: json.dumps(
                item,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
    raise TypeError(
        f"unsupported saved table property type: {type(value).__name__}"
    )


def _decode_saved_table_value(value: Any, annotation: Any, path: str) -> Any:
    """Strictly validate and rebuild one declared table property."""
    origin = get_origin(annotation)
    arguments = get_args(annotation)

    if annotation is Any:
        return _encode_saved_table_value(value)
    if annotation is type(None):
        if value is not None:
            raise ValueError(f"{path} must be null")
        return None
    if origin in (Union, types.UnionType):
        for member_type in arguments:
            try:
                return _decode_saved_table_value(value, member_type, path)
            except (TypeError, ValueError):
                continue
        raise ValueError(f"{path} has an invalid value")
    if origin is Literal:
        if value not in arguments or type(value) not in {type(item) for item in arguments}:
            raise ValueError(f"{path} has an unsupported value")
        return value
    if annotation is bool:
        if type(value) is not bool:
            raise ValueError(f"{path} must be a boolean")
        return value
    if annotation is int:
        if type(value) is not int:
            raise ValueError(f"{path} must be an integer")
        return value
    if annotation is float:
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"{path} must be a finite number")
        return float(value)
    if annotation is str:
        if not isinstance(value, str):
            raise ValueError(f"{path} must be a string")
        return value
    collection_type = origin or annotation
    if collection_type in (list, set, frozenset):
        if not isinstance(value, list):
            raise ValueError(f"{path} must be a list")
        item_type = arguments[0] if arguments else Any
        decoded = [
            _decode_saved_table_value(item, item_type, f"{path}[{index}]")
            for index, item in enumerate(value)
        ]
        if collection_type in (set, frozenset):
            unique = collection_type(decoded)
            if len(unique) != len(decoded):
                raise ValueError(f"{path} cannot contain duplicate values")
            return unique
        return decoded
    if collection_type is tuple:
        if not isinstance(value, list):
            raise ValueError(f"{path} must be a list")
        if len(arguments) == 2 and arguments[1] is Ellipsis:
            return tuple(
                _decode_saved_table_value(item, arguments[0], f"{path}[{index}]")
                for index, item in enumerate(value)
            )
        if arguments and len(value) != len(arguments):
            raise ValueError(f"{path} has the wrong number of values")
        return tuple(
            _decode_saved_table_value(
                item,
                arguments[index] if arguments else Any,
                f"{path}[{index}]",
            )
            for index, item in enumerate(value)
        )
    if collection_type is dict:
        if not isinstance(value, dict):
            raise ValueError(f"{path} must be an object")
        key_type, item_type = arguments if arguments else (str, Any)
        if key_type is not str or not all(isinstance(key, str) for key in value):
            raise ValueError(f"{path} must use string keys")
        return {
            key: _decode_saved_table_value(item, item_type, f"{path}.{key}")
            for key, item in value.items()
        }
    raise TypeError(f"{path} uses an unsupported persisted type: {annotation!r}")


@dataclass
class TableMember:
    """A member of a table (player or spectator)."""

    username: str
    is_spectator: bool = False


@dataclass(frozen=True)
class _GameTransitionSeat:
    """One participant reconstructed in a fresh game activity."""

    player_id: str
    name: str
    user: "User"
    is_bot: bool
    is_spectator: bool
    bot_name_base: str = ""


@dataclass
class Table(DataClassJSONMixin):
    """
    A game table that holds members and a game instance.

    Tables track who is present and forward actions to the game.
    Role management is handled by games, not tables.
    """

    table_id: str
    game_type: str
    host: str
    members: list[TableMember] = field(default_factory=list)
    game_json: str | None = None  # Serialized game state
    status: str = "waiting"  # waiting, playing, finished
    is_private: bool = field(
        default=False,
        metadata={SAVED_TABLE_PROPERTY: "is_private"},
    )  # Private tables are hidden from active tables lists

    # These properties follow this table through manual saves and transient
    # server checkpoints. They are not account-global: final table/save
    # deletion still ends their lifecycle.
    _banned_uuids: set[str] = field(
        default_factory=set,
        init=False,
        repr=False,
        metadata={SAVED_TABLE_PROPERTY: "banned_uuids"},
    )

    # Not serialized
    _game: "Game | None" = field(default=None, repr=False)
    _users: dict[str, "User"] = field(default_factory=dict, repr=False)
    _manager: Any = field(default=None, repr=False)  # Reference to TableManager
    _server: Any = field(default=None, repr=False)  # Reference to Server (for saves)
    _db: Any = field(default=None, repr=False)  # Reference to Database (for ratings)
    _last_menu_state_hash: str | None = field(default=None, repr=False)
    _member_offline_since: dict = field(default_factory=dict, repr=False)
    _offline_since: float | None = field(default=None, repr=False)
    _destroyed: bool = field(default=False, repr=False)

    def __post_init__(self):
        self._game = None
        self._users = {}
        self._manager = None
        self._server = None
        self._db = None
        self._last_menu_state_hash = None
        self._member_offline_since = {}
        self._offline_since = None
        self._destroyed = False
        self._power_restore_started_at: float | None = None
        self._power_restore_grace_seconds: int = 0
        self._power_restore_processed: bool = False

    @classmethod
    def _saved_property_fields(cls) -> dict[str, Any]:
        """Return the single declarative registry of persisted table fields."""
        registered: dict[str, Any] = {}
        for declared_field in fields(cls):
            property_name = declared_field.metadata.get(SAVED_TABLE_PROPERTY)
            if property_name is None:
                continue
            if not isinstance(property_name, str) or not property_name:
                raise TypeError(
                    f"{declared_field.name} has an invalid saved-table property name"
                )
            if property_name in registered:
                raise TypeError(
                    f"duplicate saved-table property name: {property_name}"
                )
            registered[property_name] = declared_field
        return registered

    def serialize_saved_state(self) -> str:
        """Serialize every declaratively persisted table property."""
        properties: dict[str, Any] = {}
        for property_name, declared_field in self._saved_property_fields().items():
            encoded_value = _encode_saved_table_value(
                getattr(self, declared_field.name)
            )
            _decode_saved_table_value(
                encoded_value,
                declared_field.type,
                f"properties.{property_name}",
            )
            properties[property_name] = encoded_value
        return json.dumps(
            {
                "version": TABLE_STATE_SCHEMA_VERSION,
                "properties": properties,
            },
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    @classmethod
    def deserialize_saved_state(cls, state_json: str | None) -> dict[str, Any]:
        """Validate persisted state without mutating or exposing a table.

        Empty objects are legacy records created before table properties were
        stored. Unknown fields fail closed so an older server cannot silently
        discard a newer privacy, admission, or lifecycle rule.
        """
        if state_json in (None, ""):
            return {}
        try:
            payload = json.loads(state_json)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("saved table state is not valid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("saved table state must be an object")
        if not payload:
            return {}
        if set(payload) != {"version", "properties"}:
            raise ValueError("saved table state has unsupported fields")
        version = payload["version"]
        if type(version) is not int or version != TABLE_STATE_SCHEMA_VERSION:
            raise ValueError("saved table state has an unsupported version")
        properties = payload["properties"]
        if not isinstance(properties, dict):
            raise ValueError("saved table properties must be an object")

        registered = cls._saved_property_fields()
        unknown = set(properties) - set(registered)
        if unknown:
            raise ValueError(
                "saved table state contains unsupported properties: "
                + ", ".join(sorted(str(name) for name in unknown))
            )

        return {
            declared_field.name: _decode_saved_table_value(
                properties[property_name],
                declared_field.type,
                f"properties.{property_name}",
            )
            for property_name, declared_field in registered.items()
            if property_name in properties
        }

    def restore_saved_state(self, state: dict[str, Any]) -> None:
        """Apply state returned by :meth:`deserialize_saved_state`."""
        allowed_fields = {
            declared_field.name
            for declared_field in self._saved_property_fields().values()
        }
        if not isinstance(state, dict) or not set(state) <= allowed_fields:
            raise ValueError("saved table state was not validated")
        for field_name, value in state.items():
            setattr(self, field_name, value)

    @property
    def game(self) -> "Game | None":
        return self._game

    @game.setter
    def game(self, value: "Game | None") -> None:
        self._game = value
        if value:
            self.game_json = value.to_json()
            self._sync_status_from_game()
        if self._server and hasattr(self._server, "on_tables_changed"):
            self._server.on_tables_changed()

    def effective_status(self) -> str:
        """Return the game lifecycle status that should drive table cleanup."""
        return getattr(self._game, "status", self.status) if self._game else self.status

    def _sync_status_from_game(self) -> None:
        """Keep the persisted/listing status aligned with the attached game."""
        if not self._game:
            return
        game_status = getattr(self._game, "status", self.status)
        if self.status == game_status:
            return
        old_status = self.status
        self.status = game_status
        if old_status == "waiting" and self.status != "waiting":
            self._member_offline_since.clear()
        if self._server and hasattr(self._server, "on_tables_changed"):
            self._server.on_tables_changed()

    def add_member(
        self, username: str, user: "User", as_spectator: bool = False
    ) -> bool:
        """Add a member to the table."""
        user_uuid = getattr(user, "uuid", None)

        # Canonical account names are exact runtime identities. Folded names
        # are used only by has_name_conflict() to keep bot/display labels
        # distinguishable; they must never merge two legacy user accounts.
        for member in self.members:
            if member.username != username:
                continue

            existing_user = self._users.get(member.username)
            if user_uuid and (
                not existing_user
                or getattr(existing_user, "uuid", None) == user_uuid
            ):
                member.is_spectator = as_spectator
                self._users[member.username] = user
                if not as_spectator:
                    self._offline_since = None
                if self._manager and hasattr(self._manager, "_username_to_table"):
                    self._manager._username_to_table[member.username] = self.table_id
                if self._server and hasattr(self._server, "on_tables_changed"):
                    self._server.on_tables_changed()
                return True
            return False

        if self.has_name_conflict(username, allowed_user_uuid=user_uuid):
            return False

        self.members.append(TableMember(username=username, is_spectator=as_spectator))
        self._users[username] = user
        if not as_spectator:
            self._offline_since = None
        if self._manager and hasattr(self._manager, "_username_to_table"):
            self._manager._username_to_table[username] = self.table_id
        if self._server and hasattr(self._server, "on_tables_changed"):
            self._server.on_tables_changed()
        return True

    def reserved_names(self, *, exclude_player_id: str | None = None) -> list[str]:
        """Return every display/account name reserved by this table."""
        names = [member.username for member in self.members]
        if self._game:
            for player in self._game.players:
                if getattr(player, "id", None) == exclude_player_id:
                    continue
                names.append(player.name)
                replaced_name = getattr(player, "replaced_human_name", "")
                if replaced_name:
                    names.append(replaced_name)
        return [name for name in names if normalize_bot_name(name)]

    def has_name_conflict(
        self,
        username: str,
        *,
        allowed_user_uuid: str | None = None,
    ) -> bool:
        """Return whether a name is already reserved by another table slot."""
        username_key = bot_name_key(username)
        if not username_key:
            return False

        for member in self.members:
            if bot_name_key(member.username) != username_key:
                continue
            member_user = self._users.get(member.username)
            member_uuid = getattr(member_user, "uuid", None)
            if not member_uuid and self._db:
                member_record = self._db.get_user(member.username)
                member_uuid = getattr(member_record, "uuid", None)
            if (
                allowed_user_uuid
                and member_uuid == allowed_user_uuid
            ):
                continue
            return True

        if self._game:
            for player in self._game.players:
                if allowed_user_uuid and getattr(player, "id", None) == allowed_user_uuid:
                    continue
                replaced_name = getattr(player, "replaced_human_name", "")
                if replaced_name and bot_name_key(replaced_name) == username_key:
                    return True
                if bot_name_key(player.name) != username_key:
                    continue
                if getattr(player, "is_bot", False):
                    base_name = normalize_bot_name(
                        getattr(player, "bot_name_base", "") or player.name
                    )
                    if bot_name_key(base_name) == username_key:
                        # The game will conditionally mark this bot before the
                        # human is appended. Bot identity is never name-based.
                        continue
                return True

        return False

    def remove_member(
        self,
        username: str,
        *,
        voice_reason: str = "voice-status-left-table",
    ) -> bool:
        """Remove one current member, returning whether anything changed."""
        if not any(member.username == username for member in self.members):
            return False

        if self._game and hasattr(self._game, "_discard_end_screen_player_id"):
            for player in list(self._game.players):
                replaced_name = getattr(player, "replaced_human_name", "")
                if player.name == username or replaced_name == username:
                    self._game._discard_end_screen_player_id(player.id)
                    break

        self.members = [m for m in self.members if m.username != username]
        self._users.pop(username, None)
        if self._manager and hasattr(self._manager, "_username_to_table"):
            self._manager._username_to_table.pop(username, None)
        if self._server and hasattr(self._server, "on_table_member_removed"):
            self._server.on_table_member_removed(
                self,
                username,
                voice_reason=voice_reason,
            )

        if username == self.host:
            promoted = self._promote_table_host(message_key="new-host")
            if not promoted:
                # Ownership must never point at an account that has left. A
                # live spectator host can deliberately supervise an active
                # bot-only table, but once that host leaves and no seated human
                # can inherit ownership, the table has no valid controller.
                self.destroy()
                return True

        # Auto-destroy if no members left (e.g. all humans left)
        if not self.members:
            self.destroy()
            return True

        if self._server and hasattr(self._server, "on_tables_changed"):
            self._server.on_tables_changed()
        return True

    def apply_player_substitution(
        self,
        incoming_username: str,
        *,
        outgoing_username: str = "",
        outgoing_becomes_spectator: bool = False,
    ) -> bool:
        """Apply table-member roles after a game-level seat substitution.

        A live outgoing human remains at the table as a spectator, including
        when that account owns the table. An offline reservation relinquished
        from a replacement bot is removed. Voice membership is unchanged for
        role swaps because both live accounts remain in the same context.
        """
        incoming_member = next(
            (
                member
                for member in self.members
                if member.username == incoming_username
            ),
            None,
        )
        if incoming_member is None or not incoming_member.is_spectator:
            return False

        outgoing_member = None
        if outgoing_username and outgoing_username != incoming_username:
            outgoing_member = next(
                (
                    member
                    for member in self.members
                    if member.username == outgoing_username
                ),
                None,
            )
            if outgoing_becomes_spectator and outgoing_member is None:
                return False

        incoming_member.is_spectator = False
        self._offline_since = None

        if outgoing_username and outgoing_username != incoming_username:
            if outgoing_becomes_spectator:
                assert outgoing_member is not None
                outgoing_member.is_spectator = True
                self._member_offline_since.pop(outgoing_username, None)
            else:
                had_outgoing_member = outgoing_member is not None
                self.members = [
                    member
                    for member in self.members
                    if member.username != outgoing_username
                ]
                self._users.pop(outgoing_username, None)
                self._member_offline_since.pop(outgoing_username, None)
                if self._manager and hasattr(self._manager, "_username_to_table"):
                    self._manager._username_to_table.pop(outgoing_username, None)
                if (
                    had_outgoing_member
                    and self._server
                    and hasattr(self._server, "on_table_member_removed")
                ):
                    self._server.on_table_member_removed(
                        self,
                        outgoing_username,
                        voice_reason="voice-status-left-table",
                    )

                if self.host == outgoing_username:
                    self.host = incoming_username
                    if self._game:
                        self._game.host = incoming_username

        if self._manager and hasattr(self._manager, "_username_to_table"):
            self._manager._username_to_table[incoming_username] = self.table_id
            if outgoing_becomes_spectator and outgoing_username:
                self._manager._username_to_table[outgoing_username] = self.table_id
        if self._server and hasattr(self._server, "on_tables_changed"):
            self._server.on_tables_changed()
        return True

    def is_banned(self, user_uuid: str) -> bool:
        """Check if a UUID is banned from this table lifecycle."""
        return user_uuid in self._banned_uuids

    def ban_user(self, user_uuid: str) -> None:
        """Add a UUID to the table-scoped ban list."""
        self._banned_uuids.add(user_uuid)

    def get_user(self, username: str) -> "User | None":
        """Get a user by username."""
        return self._users.get(username)

    def attach_user(self, username: str, user: "User") -> None:
        """Attach a user to a member (e.g., after deserialization)."""
        self._users[username] = user
        member = next(
            (member for member in self.members if member.username == username),
            None,
        )
        if member and not member.is_spectator:
            self._offline_since = None
        if self._manager and hasattr(self._manager, "_username_to_table"):
            self._manager._username_to_table[username] = self.table_id

    def get_players(self) -> list[TableMember]:
        """Get all non-spectator members."""
        return [m for m in self.members if not m.is_spectator]

    def get_spectators(self) -> list[TableMember]:
        """Get all spectator members."""
        return [m for m in self.members if m.is_spectator]

    def has_online_spectator_host(self) -> bool:
        """Return whether the table owner is present as a live spectator.

        Table ownership is independent from gameplay-seat ownership.  The
        member registry is authoritative for the host's current role, while
        the server session registry proves that the attached user is still the
        live account session rather than a stale post-disconnect object.
        """
        host_member = next(
            (member for member in self.members if member.username == self.host),
            None,
        )
        if host_member is None or not host_member.is_spectator:
            return False

        table_user = self._users.get(self.host)
        if table_user is None or getattr(table_user, "is_bot", False):
            return False
        if self._server is None:
            return True
        return self._server._users.get(self.host) is table_user

    @property
    def player_count(self) -> int:
        """Get the number of players (non-spectators)."""
        return len(self.get_players())

    def broadcast(self, text: str, buffer: str = "game") -> None:
        """Send a message to all members."""
        for username, user in self._users.items():
            user.speak(text, buffer)

    def broadcast_sound(self, name: str, volume: int = 100) -> None:
        """Play a sound for all members."""
        for user in self._users.values():
            user.play_sound(name, volume)

    def mark_power_restored(self, grace_seconds: int) -> None:
        """Hold restored gameplay briefly while clients auto-reconnect."""
        self._power_restore_started_at = time.time()
        self._power_restore_grace_seconds = max(0, int(grace_seconds))
        self._power_restore_processed = False
        self._member_offline_since.clear()

    def clear_power_restore_grace(self) -> None:
        self._power_restore_started_at = None
        self._power_restore_grace_seconds = 0
        self._power_restore_processed = True

    def is_power_restore_grace_active(self) -> bool:
        return (
            self._power_restore_started_at is not None
            and not self._power_restore_processed
        )

    def power_restore_remaining_seconds(self) -> int:
        if self._power_restore_started_at is None:
            return 0
        elapsed = time.time() - self._power_restore_started_at
        remaining = self._power_restore_grace_seconds - elapsed
        return max(0, math.ceil(remaining))

    def power_restore_missing_player_names(self) -> list[str]:
        """Return active human seats still missing during reboot restore grace."""
        return [
            player.replaced_human_name or player.name
            for player in self._offline_active_humans()
        ]

    def _online_active_humans(self) -> list[Any]:
        if not self._game or not self._server:
            return []
        result = []
        for player in self._game.players:
            if player.is_bot or player.is_spectator:
                continue
            user = self._game.get_user(player)
            if user and user.username in self._server._users:
                result.append(player)
        return result

    def _offline_active_humans(self) -> list[Any]:
        if not self._game or not self._server:
            return []
        result = []
        for player in self._game.players:
            if player.is_bot or player.is_spectator:
                continue
            user = self._game.get_user(player)
            if not user or user.username not in self._server._users:
                result.append(player)
        return result

    def _all_active_humans_are_online(self) -> bool:
        if not self._game:
            return True
        return not self._offline_active_humans()

    def _reserved_active_human_seat_count(self) -> int:
        """Return the number of active seats still owned by human accounts.

        ``members`` is the table's authoritative human-seat registry. A
        disconnected player remains here while a game player or replacement
        bot continues holding the gameplay slot, so ordinary network absence
        does not turn that account-owned seat into a dedicated bot seat.
        """
        return sum(not member.is_spectator for member in self.members)

    def _active_human_player_count(self) -> int:
        """Return active gameplay seats currently represented by humans."""
        if not self._game:
            return 0
        return self._game.get_active_human_player_count()

    def _handle_abandoned_playing_table(self, current_time: float) -> bool:
        """Pause and eventually retire an unattended active table.

        A normal active table receives this bounded cleanup once at most one
        gameplay seat is still represented by a human; account-owned seats
        already held by replacement bots remain reclaimable during the grace.
        During planned-reboot restoration, the same timeout also bounds tables
        where none of several humans has returned. Elapsed grace time is
        checkpointed so rebooting cannot reset the countdown, while server
        downtime itself does not consume it.
        """
        if not self._server:
            self._offline_since = None
            return False
        if self.effective_status() != "playing":
            self._offline_since = None
            return False

        spectator_host_online = self.has_online_spectator_host()
        if (
            self._reserved_active_human_seat_count() == 0
            and not spectator_host_online
        ):
            self.destroy()
            return True

        # A present owner may supervise an active table without occupying a
        # gameplay seat.  Bot-controlled seats continue normally; a malformed
        # or transitional game with no seats is retained but frozen so the
        # owner can restart or close it safely.  Inspect structural seats here,
        # not get_active_players(): games may temporarily exclude eliminated
        # seats while a result sequence still needs to tick to completion.
        if spectator_host_online and self._active_human_player_count() == 0:
            self._offline_since = None
            has_gameplay_seat = bool(
                self._game
                and any(not player.is_spectator for player in self._game.players)
            )
            return not has_gameplay_seat

        # Reboot recovery has its own grace-period state machine.  Once the
        # spectator owner is back, let that handler replace missing seats at
        # expiry instead of trapping the table in abandonment pause first.
        if spectator_host_online and self.is_power_restore_grace_active():
            self._offline_since = None
            return False

        should_pause = not self._online_active_humans() and (
            self._active_human_player_count() <= 1
            or self.is_power_restore_grace_active()
        )
        if not should_pause:
            self._offline_since = None
            return False

        if self._offline_since is None:
            self._offline_since = current_time
        elif (
            current_time - self._offline_since
            >= ABANDONED_ACTIVE_TABLE_TIMEOUT_SECONDS
        ):
            if self._game:
                self._game.broadcast_l(
                    "table-closed-disconnect-timeout",
                    buffer="system",
                    minutes=math.ceil(
                        ABANDONED_ACTIVE_TABLE_TIMEOUT_SECONDS / 60
                    ),
                )
            self.destroy()
        return True

    def _handle_power_restore_grace(self, current_time: float) -> bool:
        """Return True when normal table ticking should remain paused."""
        if not self.is_power_restore_grace_active():
            return False

        if self._all_active_humans_are_online():
            if self.effective_status() == "playing" and self._game:
                self._game.broadcast_l(
                    "server-power-restore-complete",
                    buffer="system",
                )
            self.clear_power_restore_grace()
            return False

        assert self._power_restore_started_at is not None
        elapsed = current_time - self._power_restore_started_at
        if elapsed < self._power_restore_grace_seconds:
            return True

        if self.effective_status() == "playing":
            online_humans = self._online_active_humans()
            if not self._game:
                self.clear_power_restore_grace()
                return False
            if not online_humans and not self.has_online_spectator_host():
                # Nobody is present to supervise the restored game yet. Keep
                # gameplay frozen. _handle_abandoned_playing_table() owns the
                # shared normal/reboot timeout and its persisted timestamp.
                return True
            offline_players = self._offline_active_humans()
            missing_usernames = {
                player.replaced_human_name or player.name
                for player in offline_players
            }
            replaced_any = False
            for player in offline_players:
                if self._game._replace_with_bot(player):
                    replaced_any = True
            self._promote_power_restore_host_if_missing(missing_usernames)
            if replaced_any and hasattr(self._game, "refresh_menus"):
                self._game.broadcast_l(
                    "server-power-restore-complete-with-bots",
                    buffer="system",
                )
                self._game.refresh_menus()
            self.clear_power_restore_grace()
            return False

        if self.effective_status() == "waiting":
            self._prune_waiting_power_restore_absentees()
            self.clear_power_restore_grace()
        return False

    def _prune_waiting_power_restore_absentees(self) -> None:
        """Remove offline humans from a restored waiting lobby after grace."""
        if not self._server:
            return

        online_members = [
            member
            for member in self.members
            if member.username in self._server._users
        ]
        if not online_members:
            self.destroy()
            return

        offline_usernames = {
            member.username
            for member in self.members
            if member.username not in self._server._users
        }
        if not offline_usernames:
            return

        self.members = [
            member
            for member in self.members
            if member.username not in offline_usernames
        ]
        for username in offline_usernames:
            self._users.pop(username, None)
            if self._manager and hasattr(self._manager, "_username_to_table"):
                self._manager._username_to_table.pop(username, None)

        if self._game:
            removed_player_ids = [
                player.id
                for player in self._game.players
                if not (
                    player.is_bot
                    or player.name not in offline_usernames
                    or getattr(player, "replaced_human_name", "")
                )
            ]
            self._game.players = [
                player
                for player in self._game.players
                if player.is_bot
                or player.name not in offline_usernames
                or getattr(player, "replaced_human_name", "")
            ]
            for player_id in removed_player_ids:
                self._game.prune_audio_recipient(player_id)
            for player_id in list(self._game.player_action_sets):
                if not self._game.get_player_by_id(player_id):
                    self._game.player_action_sets.pop(player_id, None)
            for player_id in list(self._game._users):
                if not self._game.get_player_by_id(player_id):
                    self._game._users.pop(player_id, None)

        if self.host in offline_usernames:
            candidates = [member for member in self.members if not member.is_spectator]
            if candidates:
                self.host = candidates[0].username
                if self._game:
                    self._game.host = self.host
            else:
                self.destroy()
                return

        if self._server and hasattr(self._server, "on_tables_changed"):
            self._server.on_tables_changed()

    def _promote_power_restore_host_if_missing(
        self, missing_usernames: set[str]
    ) -> None:
        """Promote an online human if the restored table host never returned."""
        if self.host not in missing_usernames:
            return
        self._promote_table_host(
            message_key="table-new-host-promoted",
            online_only=True,
        )

    def _promote_table_host(
        self,
        *,
        message_key: str,
        online_only: bool = False,
    ) -> bool:
        """Promote the next eligible human table member to host."""
        candidates = []
        for member in self.members:
            if member.is_spectator:
                continue
            member_user = self._users.get(member.username)
            if member_user and getattr(member_user, "is_bot", False):
                continue
            if online_only and (
                not self._server or member.username not in self._server._users
            ):
                continue
            candidates.append(member)

        if not candidates:
            return False

        if self._server:
            candidates.sort(
                key=lambda member: member.username in self._server._users,
                reverse=True,
            )

        new_host = candidates[0].username
        if new_host == self.host:
            return True

        self.host = new_host
        if self._game:
            self._game.host = new_host
            self._game.broadcast_l(message_key, buffer="system", player=new_host)
            if hasattr(self._game, "refresh_menus"):
                self._game.refresh_menus()
        if self._server and hasattr(self._server, "on_tables_changed"):
            self._server.on_tables_changed()
        return True

    def on_tick(self) -> None:
        """Called every tick. Forwards to game."""
        current_time = time.time()
        self._sync_status_from_game()
        if self._handle_abandoned_playing_table(current_time):
            return
        if self._handle_power_restore_grace(current_time):
            return

        if self._game:
            self._game.on_tick()
            self._sync_status_from_game()

            # Check if state changed for menu auto-refresh
            table_status = self.effective_status()
            current_state_hash = f"{table_status}|{len(self.members)}|{self.host}"
            if self._last_menu_state_hash is None:
                self._last_menu_state_hash = current_state_hash
            elif self._last_menu_state_hash != current_state_hash:
                self._last_menu_state_hash = current_state_hash
                if self._server and hasattr(self._server, "on_tables_changed"):
                    self._server.on_tables_changed()

        # Waiting lobbies retain their established short per-member cleanup.
        # Active-game abandonment is handled before gameplay ticks above.
        if self._server and self.effective_status() == "waiting":
            host_online = self.host in self._server._users
            if self._game:
                any_human_present = bool(self._online_active_humans())
            else:
                any_human_present = any(
                    not member.is_spectator
                    and member.username in self._server._users
                    for member in self.members
                )

            should_destroy = not host_online and not any_human_present
            if not should_destroy:
                for member in list(self.members):
                    if member.username in self._server._users:
                        self._member_offline_since.pop(member.username, None)
                        continue

                    user = self._users.get(member.username)
                    if user and getattr(user, "is_bot", False):
                        continue

                    offline_since = self._member_offline_since.get(member.username)
                    if offline_since is None:
                        self._member_offline_since[member.username] = current_time
                        continue
                    if (
                        current_time - offline_since
                        <= WAITING_MEMBER_DISCONNECT_TIMEOUT_SECONDS
                    ):
                        continue

                    if self._game:
                        self._game.broadcast_l(
                            "player-kicked-offline",
                            buffer="system",
                            player=member.username,
                        )
                        user_record = self._users.get(member.username)
                        if user_record:
                            player = self._game.get_player_by_id(user_record.uuid)
                            if member.is_spectator:
                                self._game.remove_spectator(user_record.uuid)
                            else:
                                self._game.remove_player(user_record.uuid)
                            if player:
                                self._game.play_table_kick_sound(
                                    player,
                                    is_spectator=member.is_spectator,
                                )

                    self.remove_member(
                        member.username,
                        voice_reason="voice-status-connection-lost",
                    )
                    self._member_offline_since.pop(member.username, None)

            if should_destroy:
                self.destroy()

    def save_game_state(self) -> None:
        """Save the current game state to game_json."""
        if self._game:
            self.game_json = self._game.to_json()

    def destroy(self) -> None:
        """Destroy this table. Called by Game.destroy()."""
        if self._destroyed:
            return
        self._destroyed = True

        # Ensure Game is also destroyed (e.g. if table is destroyed by timeout)
        # We need to avoid infinite recursion since Game.destroy calls Table.destroy
        if self._game and hasattr(self._game, "destroy") and not getattr(self._game, "_destroyed", False):
             self._game.destroy()

        if self._manager:
            self._manager.on_table_destroy(self)

    def _live_members_for_game_transition(
        self,
    ) -> tuple[list[TableMember], dict[str, "User"]]:
        """Return current human members backed by the authoritative session.

        A game change is a live table operation, not saved-table restoration.
        Disconnected reservations therefore end with the old match. Replacement
        bots are retained separately as ordinary bots, matching normal reset
        behavior without carrying another account's reclaim rights into a new
        game.
        """
        live_members: list[TableMember] = []
        live_users: dict[str, User] = {}
        server_users = getattr(self._server, "_users", None)

        for member in self.members:
            attached_user = self._users.get(member.username)
            expected_uuid = str(getattr(attached_user, "uuid", ""))
            if not expected_uuid and self._db:
                account = self._db.get_user(member.username)
                expected_uuid = str(getattr(account, "uuid", ""))
            if server_users is None:
                current_user = attached_user
            else:
                current_user = server_users.get(member.username)
            if current_user is None or getattr(current_user, "is_bot", False):
                continue
            if (
                not expected_uuid
                or str(getattr(current_user, "uuid", "")) != expected_uuid
            ):
                continue
            live_members.append(member)
            live_users[member.username] = current_user

        return live_members, live_users

    def _game_transition_seats(
        self,
    ) -> tuple[list[TableMember], dict[str, "User"], list[_GameTransitionSeat]]:
        """Snapshot the ordered roster that can enter a fresh game lobby."""
        if not self._game:
            return [], {}, []

        live_members, live_users = self._live_members_for_game_transition()
        member_by_uuid: dict[str, TableMember] = {}
        for member in live_members:
            user = live_users[member.username]
            user_uuid = str(getattr(user, "uuid", ""))
            if not user_uuid or user_uuid in member_by_uuid:
                raise ValueError("Table members must have unique account identifiers")
            member_by_uuid[user_uuid] = member

        seats: list[_GameTransitionSeat] = []
        seat_ids: set[str] = set()
        included_humans: set[str] = set()

        def add_seat(seat: _GameTransitionSeat) -> None:
            if not seat.player_id or seat.player_id in seat_ids:
                raise ValueError("Game transition seats must have unique identifiers")
            seat_ids.add(seat.player_id)
            seats.append(seat)

        for old_player in self._game.players:
            player_id = str(getattr(old_player, "id", ""))
            live_member = member_by_uuid.get(player_id)

            # A replacement seat belongs to its returning live account if the
            # authoritative session has already reappeared. This prevents a
            # narrow reconnect/switch race from duplicating that account and
            # its temporary bot in the new lobby.
            if old_player.is_bot and old_player.replaced_human and live_member:
                user = live_users[live_member.username]
                add_seat(
                    _GameTransitionSeat(
                        player_id=str(user.uuid),
                        name=live_member.username,
                        user=user,
                        is_bot=False,
                        is_spectator=live_member.is_spectator,
                    )
                )
                included_humans.add(live_member.username)
                continue

            if old_player.is_bot:
                base_name = normalize_bot_name(
                    old_player.bot_name_base or old_player.name
                )
                old_bot_user = self._game._users.get(player_id)
                if old_player.replaced_human:
                    bot_user = Bot(old_player.name)
                elif isinstance(old_bot_user, Bot):
                    # Clone the runtime facade so target-name reconciliation
                    # cannot mutate the current game before the atomic commit.
                    bot_user = Bot(
                        old_player.name,
                        locale=old_bot_user.locale,
                        uuid=player_id,
                        gender=old_bot_user.gender,
                    )
                else:
                    bot_user = Bot(old_player.name, uuid=player_id)
                add_seat(
                    _GameTransitionSeat(
                        player_id=str(bot_user.uuid),
                        name=old_player.name,
                        user=bot_user,
                        is_bot=True,
                        is_spectator=old_player.is_spectator,
                        bot_name_base=base_name,
                    )
                )
                continue

            if live_member and live_member.username not in included_humans:
                user = live_users[live_member.username]
                add_seat(
                    _GameTransitionSeat(
                        player_id=str(user.uuid),
                        name=live_member.username,
                        user=user,
                        is_bot=False,
                        is_spectator=live_member.is_spectator,
                    )
                )
                included_humans.add(live_member.username)

        missing_members = [
            member.username
            for member in live_members
            if member.username not in included_humans
        ]
        if missing_members:
            raise ValueError(
                "Every live table member must have a matching game participant"
            )

        return live_members, live_users, seats

    def game_transition_active_seat_count(self) -> int:
        """Return the seats a target game's maximum must accommodate."""
        _members, _users, seats = self._game_transition_seats()
        return sum(1 for seat in seats if not seat.is_spectator)

    @staticmethod
    def _retire_game_runtime(
        game: "Game",
        *,
        stop_audio: bool = False,
        audio_audience: Any = None,
    ) -> None:
        """Detach every runtime-only path from a replaced game instance."""
        game._destroyed = True
        logger = logging.getLogger("playaural")
        game_type = type(game).__name__
        try:
            game_type = game.get_type()
        except Exception:
            logger.exception("Could not identify a game while retiring it")
        if stop_audio:
            # A hard activity change suppresses callbacks queued earlier in
            # this event-loop turn. Letting one dispatch during on_discard()
            # would briefly resurrect an old one-shot immediately before the
            # stop command intended to fence off that activity.
            table_audio_batcher = getattr(
                game,
                "_table_presence_audio_batcher",
                None,
            )
            if table_audio_batcher is not None:
                try:
                    table_audio_batcher.cancel()
                except Exception:
                    logger.exception(
                        "Pending audio cleanup failed while replacing %s",
                        game_type,
                    )
        try:
            game.on_discard()
        except Exception:
            logger.exception(
                "Game cleanup failed while replacing %s",
                game_type,
            )
        if stop_audio:
            try:
                # Stop every source, including already-started one-shots, so
                # nothing owned by the retired activity reaches the new lobby.
                game.stop_all_audio(fade_ms=0, audience=audio_audience)
            except Exception:
                logger.exception(
                    "Audio cleanup failed while replacing %s",
                    game_type,
                )
        # Keep retirement fail-closed even when delivery to one broken client
        # raises: no reconnectable audio ownership from this activity may
        # survive in server memory.
        game.active_audio.clear()
        game.current_music = ""
        game.current_ambience = ""
        game.current_ambience_outro = ""
        try:
            game.clear_scheduled_sounds()
        except Exception:
            logger.exception(
                "Scheduled audio cleanup failed while replacing %s",
                game_type,
            )
        try:
            game.cancel_all_sequences()
        except Exception:
            logger.exception(
                "Sequence cleanup failed while replacing %s",
                game_type,
            )
        for container_name in (
            "_keybinds",
            "_pending_actions",
            "_action_context",
            "_actions_menu_open",
            "_actions_menu_return_focus",
            "_pending_action_return_focus",
            "_status_box_open",
            "_live_status_boxes",
            "_status_box_return_focus",
            "_menu_dirty",
            "_pending_menu_focus",
            "_options_path",
            "_end_screen_open_player_ids",
            "_transcripts",
            "player_action_sets",
        ):
            container = getattr(game, container_name, None)
            if container is not None:
                container.clear()
        game._menu_dirty_all = False
        game._last_game_result = None
        game._users.clear()
        game._table = None

    def transition_to_game(self, game_type: str) -> bool:
        """Atomically replace the current match with a fresh game lobby.

        The table is the durable social/voice session. Its identity, owner,
        privacy, bans, and live human roles remain intact while match-owned
        state is replaced. Nothing is mutated until the complete target roster
        and its serialized state have been validated.
        """
        old_game = self._game
        if not old_game or not isinstance(game_type, str):
            return False
        target_class = get_game_class(game_type)
        if not target_class or game_type == self.game_type:
            return False

        new_game = None
        try:
            live_members, live_users, seats = self._game_transition_seats()
            if not any(member.username == self.host for member in live_members):
                return False
            active_seats = sum(1 for seat in seats if not seat.is_spectator)
            if active_seats > target_class.get_max_players():
                return False

            new_game = target_class()
            new_game.host = self.host
            new_game.status = "waiting"
            new_game.game_active = False
            new_game._table = self
            new_game.setup_keybinds()

            for seat in seats:
                player = new_game.create_player(
                    seat.player_id,
                    seat.name,
                    is_bot=seat.is_bot,
                )
                player.is_spectator = seat.is_spectator
                if seat.is_bot:
                    player.bot_name_base = seat.bot_name_base
                new_game.players.append(player)
                new_game.attach_user(player.id, seat.user)
                new_game.setup_player_actions(player)

            host_user = live_users[self.host]
            new_game.ensure_bot_display_names(host_user.locale)
            serialized_game = new_game.to_json()
        except Exception:
            logging.getLogger("playaural").exception(
                "Failed to prepare table %s transition from %s to %s",
                self.table_id,
                self.game_type,
                game_type,
            )
            if new_game is not None:
                self._retire_game_runtime(new_game)
            return False

        old_member_names = {member.username for member in self.members}
        live_member_names = {member.username for member in live_members}
        removed_member_names = old_member_names - live_member_names

        self.members = live_members
        self._users = live_users
        for username in removed_member_names:
            if (
                self._manager
                and hasattr(self._manager, "_username_to_table")
                and self._manager._username_to_table.get(username) == self.table_id
            ):
                self._manager._username_to_table.pop(username, None)
            if self._server:
                self._server.discard_voice_context_state(
                    username,
                    scope="table",
                    context_id=self.table_id,
                )
        if self._manager and hasattr(self._manager, "_username_to_table"):
            for member in live_members:
                self._manager._username_to_table[member.username] = self.table_id

        self.game_type = game_type
        self._game = new_game
        self.game_json = serialized_game
        self.status = "waiting"
        self._last_menu_state_hash = None
        self._member_offline_since.clear()
        self._offline_since = None
        self.clear_power_restore_grace()

        # A game change is a hard activity boundary. Retirement flushes any
        # final batched table cue, then stops every source (including one-shots)
        # so nothing from the old activity overlaps the fresh waiting lobby.
        # Table voice remains a separate, unchanged LiveKit context.
        # Put authoritative sessions first: audio recipient deduplication by
        # account UUID must favor a replacement device over its stale facade.
        retirement_audio_audience = (
            *live_users.values(),
            *old_game._users.values(),
        )
        self._retire_game_runtime(
            old_game,
            stop_audio=True,
            audio_audience=retirement_audio_audience,
        )
        if self._server and hasattr(self._server, "on_table_game_transition"):
            try:
                self._server.on_table_game_transition(self)
            except Exception:
                logging.getLogger("playaural").exception(
                    "Post-transition consent cleanup failed for table %s",
                    self.table_id,
                )
        if self._server and hasattr(self._server, "on_tables_changed"):
            try:
                self._server.on_tables_changed()
            except Exception:
                logging.getLogger("playaural").exception(
                    "Post-transition table notification failed for table %s",
                    self.table_id,
                )
        return True

    def reset_game(self, *, preserve_scheduled_sounds: bool = True) -> bool:
        """Reset the table to the lobby state with a completely fresh Game instance."""
        if not self._game:
            return False
        game_class = get_game_class(self.game_type)
        if not game_class:
            return False

        if self._server and hasattr(self._server, "on_table_game_reset"):
            self._server.on_table_game_reset(self)

        # 1. Store old game state we need
        old_game = self._game
        # A waiting lobby never owns background audio. This is normally a
        # no-op because finish_game() already retired replayable sources, but
        # it also makes direct/framework resets safe and leak-free.
        old_game.stop_replayable_audio(
            fade_ms=0,
            play_ambience_outros=False,
        )
        old_options = None
        if hasattr(old_game, "options"):
            old_options = old_game.options
        end_screen_state = None
        if hasattr(old_game, "_export_end_screen_state"):
            end_screen_state = old_game._export_end_screen_state()

        # 2. Clean up stale members
        # If a player disconnected during the end-game sequence, they might still be in self.members
        # but not in self._users. We must remove them now to prevent ghost players.
        # We also check the server's master user list to ensure they are actually online.
        valid_members = []
        invalid_usernames: list[str] = []
        for member in self.members:
            user = self._users.get(member.username)
            if user:
                # Bots are always "online" for the game's purposes, though they aren't in server._users
                is_bot = getattr(user, "is_bot", False)
                # Humans must be actively connected to the server
                if is_bot or (self._server and member.username in self._server._users):
                    valid_members.append(member)
                    continue
            invalid_usernames.append(member.username)

        for username in invalid_usernames:
            self._users.pop(username, None)
            if self._manager and hasattr(self._manager, "_username_to_table"):
                self._manager._username_to_table.pop(username, None)
            if self._server:
                self._server.discard_voice_context_state(
                    username,
                    scope="table",
                    context_id=self.table_id,
                )
        self.members = valid_members

        # 3. Track humans, bots, and spectators
        active_players = []
        active_spectators = []
        active_bots = []

        # Table.members is the SINGLE SOURCE OF TRUTH for humans and their roles
        for member in self.members:
            user = self._users.get(member.username)
            if not user:
                continue # Safety check, though we just cleaned up

            if member.is_spectator:
                active_spectators.append((user.uuid, member.username, user))
            else:
                active_players.append((user.uuid, member.username, user))

        # old_game.players is the ONLY source for bots
        for player in old_game.players:
            if player.is_bot:
                user = old_game._users.get(player.id)
                if user:
                    if getattr(player, "replaced_human", False):
                        user = Bot(player.name)
                    active_bots.append(
                        (
                            user.uuid,
                            player.name,
                            player.bot_name_base,
                            user,
                        )
                    )

        # 4. Re-evaluate host
        # If the old host left, they won't be in active_players or active_spectators
        old_host = self.host
        host_present = any(name == self.host for _, name, _ in active_players) or \
                       any(name == self.host for _, name, _ in active_spectators)

        if not host_present:
            # Promote a new host. Prioritize players over spectators.
            candidates = [p for p in active_players]
            if not candidates:
                candidates = [s for s in active_spectators]

            if candidates:
                # Prioritize online humans (though valid_members cleanup should ensure this)
                if self._server:
                    candidates.sort(key=lambda p: p[1] in self._server._users, reverse=True)
                self.host = candidates[0][1]
            else:
                # No humans left at all
                self.destroy()
                return False

        # 5. Instantiate fresh game
        new_game = game_class()

        # 6. Safe Option Cloning
        if old_options and hasattr(new_game, "options"):
            # Serialize old options to dict and rebuild to avoid deepcopy issues with dataclasses
            options_dict = old_options.to_dict()
            new_game.options = type(new_game.options).from_dict(options_dict)

        # 7. Link table
        new_game._table = self
        self._game = new_game

        # 8. Initialize lobby state
        new_game.host = self.host
        new_game.status = "waiting"
        new_game.setup_keybinds()

        def _restore_member(uuid_str: str, name: str, user: "User", *, is_spectator: bool) -> None:
            """Reattach an existing table member without replaying join side effects."""
            restored_player = new_game.create_player(uuid_str, name, is_bot=False)
            restored_player.is_spectator = is_spectator
            new_game.players.append(restored_player)
            new_game.attach_user(restored_player.id, user)
            new_game.setup_player_actions(restored_player)

        # 9. Add players back
        for uuid_str, name, user in active_players:
             _restore_member(uuid_str, name, user, is_spectator=False)

        for uuid_str, name, user in active_spectators:
             _restore_member(uuid_str, name, user, is_spectator=True)

        for uuid_str, name, base_name, user in active_bots:
             # Use the raw create_player/append logic for bots to perfectly match LobbyActionsMixin
             bot_player = new_game.create_player(uuid_str, name, is_bot=True)
             bot_player.bot_name_base = base_name
             new_game.players.append(bot_player)
             new_game.attach_user(bot_player.id, user)
             new_game.setup_player_actions(bot_player)

        new_game.ensure_bot_display_names()

        # 10. Announce new host if changed
        if old_host != self.host:
             new_game.broadcast_l("table-new-host-promoted", buffer="system", player=self.host)

        # 11. Transfer scheduled sounds only for the normal game-over flow.
        # Manual host restarts must discard every delayed gameplay artifact.
        if preserve_scheduled_sounds:
            new_game.scheduled_sounds = list(old_game.scheduled_sounds)
            new_game.sound_scheduler_tick = old_game.sound_scheduler_tick

        # 12. Preserve per-player post-game overlays across the fresh lobby game.
        if hasattr(new_game, "_import_end_screen_state"):
            new_game._import_end_screen_state(end_screen_state)

        # 13. Mark and detach old runtime state so ticks or stale callbacks cannot affect the table.
        self._retire_game_runtime(old_game)

        # 14. Sync status
        self.status = "waiting"
        self.game_json = new_game.to_json()
        self._last_menu_state_hash = None
        self._member_offline_since.clear()
        self._offline_since = None
        if self._server and hasattr(self._server, "on_tables_changed"):
            self._server.on_tables_changed()
        return True

    def save_and_close(self, username: str) -> None:
        """Save game state and close table. Called by game save action."""
        if self._server:
            self._server.on_table_save(self, username)

    def save_game_result(self, result: Any) -> None:
        """Save a game result to the database. Called by game when it finishes."""
        if self._server:
            self._server.on_game_result(result)
