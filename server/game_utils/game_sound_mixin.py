"""Mixin providing sound scheduling and playback for games."""

import math
from collections.abc import Callable, Iterable
from dataclasses import replace
from typing import TYPE_CHECKING, Any

from ..audio import (
    DEFAULT_AMBIENCE_FADE_MS,
    DEFAULT_MUSIC_FADE_MS,
    AudioCommand,
    AudioGainAutomation,
    AudioMotion,
    AudioPlaybackState,
    AudioSequenceSegment,
    DistanceAttenuation,
    SameTurnAudioBatcher,
    new_audio_handle,
    normalize_audio_gain,
    normalize_audio_position,
    pan_from_position,
    seat_position,
)

if TYPE_CHECKING:
    from ..users.base import User
    from .player import Player


TABLE_PRESENCE_SOUND_SPECS = {
    "join": {
        "direction": "join",
        "player": "table_join.ogg",
        "spectator": "join_spectator.ogg",
    },
    "leave": {
        "direction": "leave",
        "player": "table_leave.ogg",
        "spectator": "leave_spectator.ogg",
    },
    "kick": {
        "direction": "leave",
        "player": "table_kick.ogg",
        "spectator": "table_kick.ogg",
    },
    "disconnect": {
        "direction": "leave",
        "player": "disconnect.ogg",
        "spectator": "disconnect.ogg",
    },
    "reconnect": {
        "direction": "join",
        "player": "reconnect.ogg",
        "spectator": "reconnect.ogg",
    },
}


class GameSoundMixin:
    """Mixin providing sound scheduling and playback functionality.

    Expects on the Game class:
        - self.scheduled_sounds: list
        - self.sound_scheduler_tick: int
        - self.active_audio: dict[str, AudioPlaybackState]
        - self.players: list[Player]
        - self.get_user(player) -> User | None
    """

    # ==========================================================================
    # Sound Scheduling
    # ==========================================================================

    TICKS_PER_SECOND = 20  # 50ms per tick

    def schedule_sound(
        self,
        sound: str,
        delay_ticks: int = 0,
        volume: int = 100,
        pan: int = 0,
        pitch: int = 100,
    ) -> None:
        """Schedule a sound to play after a delay.

        Args:
            sound: Sound file name to play.
            delay_ticks: Number of ticks to wait before playing (0 = next tick).
            volume: Volume (0-100).
            pan: Pan (-100 to 100, 0 = center).
            pitch: Pitch (100 = normal).
        """
        target_tick = self.sound_scheduler_tick + delay_ticks
        self.scheduled_sounds.append([target_tick, sound, volume, pan, pitch])

    def schedule_sound_sequence(
        self,
        sounds: list[tuple[str, int]],
        start_delay: int = 0,
    ) -> None:
        """Schedule a sequence of sounds with delays between them.

        Args:
            sounds: List of (sound_name, delay_after) tuples.
            start_delay: Initial delay before first sound.
        """
        current_tick = start_delay
        for sound, delay_after in sounds:
            self.schedule_sound(sound, delay_ticks=current_tick)
            current_tick += delay_after

    def clear_scheduled_sounds(self) -> None:
        """Clear all scheduled sounds."""
        self.scheduled_sounds.clear()

    def process_scheduled_sounds(self) -> None:
        """Process scheduled sounds. Called automatically in on_tick()."""
        current_tick = self.sound_scheduler_tick

        # Find and play sounds scheduled for this tick
        remaining = []
        for scheduled in self.scheduled_sounds:
            tick, sound, volume, pan, pitch = scheduled
            if tick <= current_tick:
                self.play_sound(sound, volume, pan, pitch)
            else:
                remaining.append(scheduled)

        self.scheduled_sounds = remaining
        self.sound_scheduler_tick += 1

    def process_audio_automations(self) -> None:
        """Advance persisted source parameters on the authoritative game tick."""
        tick_ms = 1000 // self.TICKS_PER_SECOND
        for state in self.active_audio.values():
            if state.motion is not None:
                motion = state.motion.advance(tick_ms)
                state.position = motion.position_at()
                state.pan = pan_from_position(state.position)
                state.motion = None if motion.complete else motion
            if state.gain_automation is not None:
                automation = state.gain_automation.advance(tick_ms)
                state.gain = automation.gain_at()
                state.gain_automation = (
                    None if automation.complete else automation
                )

    # ==========================================================================
    # Sound Playback
    # ==========================================================================

    def _audio_recipients(
        self, audience: Any = None
    ) -> tuple[list["User"], list[str]]:
        """Resolve users once so every command has a deterministic audience."""
        if audience is None:
            candidates: Iterable[Any] = self.players
        elif isinstance(audience, Iterable) and not isinstance(
            audience, (str, bytes)
        ):
            candidates = audience
        else:
            candidates = (audience,)

        public_audience = audience is None
        users: list["User"] = []
        player_ids: list[str] = []
        seen_users: set[str] = set()
        seen_players: set[str] = set()
        for candidate in candidates:
            player_id = getattr(candidate, "id", "")
            if not player_id and hasattr(candidate, "send_audio_command"):
                candidate_id = str(getattr(candidate, "uuid", ""))
                if any(player.id == candidate_id for player in self.players):
                    player_id = candidate_id
            if (
                not public_audience
                and player_id
                and str(player_id) not in seen_players
            ):
                normalized_player_id = str(player_id)
                seen_players.add(normalized_player_id)
                player_ids.append(normalized_player_id)

            user = (
                candidate
                if hasattr(candidate, "send_audio_command")
                else self.get_user(candidate)
            )
            if not user:
                continue
            user_id = str(getattr(user, "uuid", id(user)))
            if user_id in seen_users:
                continue
            seen_users.add(user_id)
            users.append(user)
        return users, [] if public_audience else player_ids

    @staticmethod
    def _audio_state_key(
        command: AudioCommand, recipient_ids: list[str]
    ) -> str:
        if command.kind == "sfx":
            recipients = ",".join(sorted(recipient_ids))
            return (
                f"sfx:{command.handle}:{recipients}"
                if recipients
                else f"sfx:{command.handle}"
            )
        recipients = ",".join(sorted(recipient_ids)) or "*"
        return (
            f"{command.kind}:{command.scope}:{command.context}:"
            f"{command.layer}:{recipients}"
        )

    def _dispatch_audio(
        self,
        command: AudioCommand,
        *,
        audience: Any = None,
        persist: bool = False,
    ) -> str:
        users, recipient_ids = self._audio_recipients(audience)
        if persist and command.segments:
            raise ValueError("Finite audio sequences cannot be persisted")
        if (
            command.command == "play"
            and command.handle
            and not persist
            and any(
                state.handle == command.handle
                for state in self.active_audio.values()
            )
        ):
            raise ValueError(
                "Runtime audio cannot replace a replayable stable handle"
            )
        if persist:
            if audience is not None and not recipient_ids:
                raise ValueError("Private replayable audio requires table recipients")
            self._store_audio_state(command, recipient_ids)
        for user in users:
            user.send_audio_command(command)
        return command.handle

    @staticmethod
    def _audio_states_conflict(
        command: AudioCommand, state: AudioPlaybackState
    ) -> bool:
        """Return whether two managed sources cannot coexist on one client."""
        if command.handle == state.handle:
            return True
        return command.kind in {"music", "ambience"} and (
            command.kind == state.kind
            and command.scope == state.scope
            and command.context == state.context
            and command.layer == state.layer
        )

    def _store_audio_state(
        self, command: AudioCommand, recipient_ids: list[str]
    ) -> None:
        """Mirror per-client handle and layer replacement in replayable state."""
        recipients = set(recipient_ids)
        conflicting = [
            state
            for state in self.active_audio.values()
            if self._audio_states_conflict(command, state)
        ]
        if recipients and any(not state.recipient_ids for state in conflicting):
            raise ValueError(
                "Private audio cannot replace a public handle or layer for only "
                "part of the table"
            )

        rebuilt: dict[str, AudioPlaybackState] = {}
        for state in self.active_audio.values():
            if not self._audio_states_conflict(command, state):
                rebuilt[
                    self._audio_state_key(state.to_command(), state.recipient_ids)
                ] = state
                continue
            if not recipients:
                continue
            remaining = [
                recipient
                for recipient in state.recipient_ids
                if recipient not in recipients
            ]
            if remaining:
                retained = replace(state, recipient_ids=remaining)
                rebuilt[
                    self._audio_state_key(retained.to_command(), remaining)
                ] = retained

        new_state = AudioPlaybackState.from_command(command, recipient_ids)
        rebuilt[self._audio_state_key(command, recipient_ids)] = new_state
        self.active_audio = rebuilt

    def migrate_legacy_audio_state(self) -> None:
        """Migrate pre-protocol current-track fields into canonical state once."""
        if not self.active_audio:
            legacy_commands = []
            if self.current_music:
                legacy_commands.append(
                    AudioCommand(
                        command="play",
                        kind="music",
                        asset=self.current_music,
                        handle="music",
                        bus="music",
                        loop=True,
                    )
                )
            if self.current_ambience:
                legacy_commands.append(
                    AudioCommand(
                        command="play",
                        kind="ambience",
                        asset=self.current_ambience,
                        handle="ambience:global:default:environment",
                        bus="ambience",
                        layer="environment",
                        loop=True,
                        outro=self.current_ambience_outro,
                        play_intro=False,
                    )
                )
            for command in legacy_commands:
                self.active_audio[self._audio_state_key(command, [])] = (
                    AudioPlaybackState.from_command(command, [])
                )

        # Retain the dataclass fields only so old save JSON can deserialize.
        # Current releases never write a second representation of audio state.
        self.current_music = ""
        self.current_ambience = ""
        self.current_ambience_outro = ""

    def prune_audio_recipient(self, player_id: str) -> None:
        """Remove a departed player from private replayable audio state."""
        rebuilt: dict[str, AudioPlaybackState] = {}
        for state in self.active_audio.values():
            if player_id not in state.recipient_ids:
                rebuilt[self._audio_state_key(
                    state.to_command(), state.recipient_ids
                )] = state
                continue
            state.recipient_ids = [
                recipient
                for recipient in state.recipient_ids
                if recipient != player_id
            ]
            if state.recipient_ids:
                rebuilt[self._audio_state_key(
                    state.to_command(), state.recipient_ids
                )] = state
        self.active_audio = rebuilt

    def _remove_audio_states(
        self,
        predicate: Callable[[AudioPlaybackState], bool],
        recipient_ids: list[str] | None,
    ) -> None:
        """Remove matching public state or only the selected private recipients."""
        recipients = None if recipient_ids is None else set(recipient_ids)
        rebuilt: dict[str, AudioPlaybackState] = {}
        for state in self.active_audio.values():
            if not predicate(state):
                rebuilt[self._audio_state_key(
                    state.to_command(), state.recipient_ids
                )] = state
                continue
            if recipients is None:
                continue
            # An explicit audience never mutates public replay state. Public
            # layers have no exclusion list and must be stopped publicly.
            if not state.recipient_ids:
                rebuilt[self._audio_state_key(
                    state.to_command(), state.recipient_ids
                )] = state
                continue
            remaining = [
                recipient
                for recipient in state.recipient_ids
                if recipient not in recipients
            ]
            if remaining:
                retained = replace(state, recipient_ids=remaining)
                rebuilt[self._audio_state_key(
                    retained.to_command(), retained.recipient_ids
                )] = retained
        self.active_audio = rebuilt

    def _set_audio_pause_state(
        self,
        predicate: Callable[[AudioPlaybackState], bool],
        paused: bool,
        recipient_ids: list[str] | None,
    ) -> None:
        """Update pause state, splitting a multi-recipient private layer safely."""
        recipients = None if recipient_ids is None else set(recipient_ids)
        rebuilt: dict[str, AudioPlaybackState] = {}
        for state in self.active_audio.values():
            if not predicate(state):
                rebuilt[self._audio_state_key(
                    state.to_command(), state.recipient_ids
                )] = state
                continue
            if recipients is None:
                updated = replace(state, paused=paused)
                rebuilt[self._audio_state_key(
                    updated.to_command(), updated.recipient_ids
                )] = updated
                continue
            if not state.recipient_ids:
                rebuilt[self._audio_state_key(
                    state.to_command(), state.recipient_ids
                )] = state
                continue
            affected = [
                recipient
                for recipient in state.recipient_ids
                if recipient in recipients
            ]
            remaining = [
                recipient
                for recipient in state.recipient_ids
                if recipient not in recipients
            ]
            if affected:
                updated = replace(state, recipient_ids=affected, paused=paused)
                rebuilt[self._audio_state_key(
                    updated.to_command(), updated.recipient_ids
                )] = updated
            if remaining:
                retained = replace(state, recipient_ids=remaining)
                rebuilt[self._audio_state_key(
                    retained.to_command(), retained.recipient_ids
                )] = retained
        self.active_audio = rebuilt

    def broadcast_sound(
        self,
        name: str,
        volume: int = 100,
        pan: int | None = None,
        pitch: int = 100,
        *,
        loop: bool = False,
        handle: str = "",
        bus: str = "sfx",
        fade_in_ms: int = 0,
        fade_out_ms: int = 0,
        priority: int = 0,
        max_instances: int = 0,
        ducking: dict[str, int] | None = None,
        audience: Any = None,
        scope: str = "global",
        context: str = "",
        layer: str = "main",
        persist: bool = False,
        position: tuple[float, float, float] | None = None,
        attenuation: DistanceAttenuation | dict[str, Any] | None = None,
        gain: float = 1.0,
        seat_of: "Player | None" = None,
    ) -> str:
        """Play an effect for an audience and optionally retain a loop.

        ``position`` places the sound at one point in every listener's frame.
        ``seat_of`` instead places it at that player's seat, computed for each
        listener from where they sit; the seated player hears it unpositioned.
        """
        if seat_of is not None and position is not None:
            raise ValueError("seat_of and position are mutually exclusive")
        if seat_of is not None and pan is not None:
            raise ValueError("seat_of derives pan for each listener")
        resolved_handle = handle or (new_audio_handle("sfx") if loop else "")
        command_fields = {
            "command": "play",
            "kind": "sfx",
            "asset": name,
            "handle": resolved_handle,
            "bus": bus,
            "scope": scope,
            "context": context,
            "layer": layer,
            "loop": loop,
            "volume": volume,
            "pan": pan,
            "pitch": pitch,
            "fade_in_ms": fade_in_ms,
            "fade_out_ms": fade_out_ms,
            "priority": priority,
            "max_instances": max_instances,
            "ducking": ducking or {},
            "attenuation": attenuation,
            "gain": gain,
        }
        if seat_of is not None:
            return self._dispatch_seated_audio(
                command_fields,
                seat_of,
                audience=audience,
                persist=persist and loop,
            )
        command = AudioCommand(**command_fields, position=position)
        return self._dispatch_audio(
            command, audience=audience, persist=persist and loop
        )

    def _seat_index_of(self, user: "User | Player | None") -> int | None:
        """Position in the seating order (``self.players``) of a user or player."""
        if user is None:
            return None
        target_id = str(getattr(user, "id", "") or getattr(user, "uuid", ""))
        for index, player in enumerate(self.players):
            if str(player.id) == target_id:
                return index
        return None

    def _dispatch_seated_audio(
        self,
        command_fields: dict[str, Any],
        seat_of: "Player",
        *,
        audience: Any = None,
        persist: bool = False,
    ) -> str:
        """Send one command per listener, positioned at ``seat_of``'s seat."""
        users, selected_player_ids = self._audio_recipients(audience)
        users_by_id = {
            str(user.uuid): user
            for user in users
            if getattr(user, "uuid", "")
        }
        player_ids = (
            [str(player.id) for player in self.players]
            if audience is None
            else selected_player_ids
        )
        seat_index = self._seat_index_of(seat_of)
        seat_count = len(self.players)
        deliveries: list[tuple["User | None", AudioCommand, list[str]]] = []
        table_recipient_ids: set[str] = set()
        for player_id in player_ids:
            player = self.get_player_by_id(player_id)
            if player is None:
                continue
            table_recipient_ids.add(player_id)
            listener_index = self._seat_index_of(player)
            position = (
                None
                if seat_index is None
                else seat_position(seat_index, listener_index, seat_count)
            )
            # The seated player is co-located and therefore hears this cue as
            # ordinary non-spatial audio with no distance falloff.
            personal_fields = dict(command_fields)
            personal_fields["pan"] = None
            personal_fields["attenuation"] = (
                command_fields["attenuation"] if position is not None else None
            )
            personal = AudioCommand(
                **personal_fields,
                position=position,
            )
            deliveries.append((users_by_id.get(player_id), personal, [player_id]))

        # Preserve the existing one-shot behavior for an explicitly supplied
        # connected user who is not a table participant. Such a recipient can
        # hear the seat-relative cue as a spectator, but cannot own persisted
        # table audio state.
        for user in users:
            user_id = str(getattr(user, "uuid", ""))
            if user_id in table_recipient_ids:
                continue
            position = (
                None
                if seat_index is None
                else seat_position(seat_index, None, seat_count)
            )
            personal_fields = dict(command_fields)
            personal_fields["pan"] = None
            personal_fields["attenuation"] = (
                command_fields["attenuation"] if position is not None else None
            )
            deliveries.append(
                (user, AudioCommand(**personal_fields, position=position), [])
            )
        if persist:
            if any(not recipient_ids for _, _, recipient_ids in deliveries):
                raise ValueError("Seated replayable audio requires table recipients")
            if any(
                not state.recipient_ids
                and any(
                    self._audio_states_conflict(command, state)
                    for _, command, _ in deliveries
                )
                for state in self.active_audio.values()
            ):
                raise ValueError(
                    "Private audio cannot replace a public handle or layer for "
                    "only part of the table"
                )
            for _, command, recipient_ids in deliveries:
                self._store_audio_state(command, recipient_ids)
        for user, command, _ in deliveries:
            if user is not None:
                user.send_audio_command(command)
        return str(command_fields["handle"])

    def play_sound(
        self,
        name: str,
        volume: int = 100,
        pan: int | None = None,
        pitch: int = 100,
        **kwargs: Any,
    ) -> str:
        """Alias for :meth:`broadcast_sound`."""
        return self.broadcast_sound(name, volume, pan, pitch, **kwargs)

    def play_sound_chain(
        self,
        segments: list[AudioSequenceSegment | dict[str, Any]],
        *,
        handle: str = "",
        bus: str = "sfx",
        buffer: str = "",
        volume: int = 100,
        pan: int | None = None,
        pitch: int = 100,
        fade_in_ms: int = 0,
        fade_out_ms: int = 0,
        priority: int = 0,
        max_instances: int = 0,
        ducking: dict[str, int] | None = None,
        audience: Any = None,
    ) -> str:
        """Play a finite, preloaded SFX chain on each client's audio clock."""
        resolved_handle = handle or new_audio_handle("sfx-sequence")
        command = AudioCommand(
            command="play",
            kind="sfx",
            handle=resolved_handle,
            bus=bus,
            buffer=buffer,
            volume=volume,
            pan=pan,
            pitch=pitch,
            fade_in_ms=fade_in_ms,
            fade_out_ms=fade_out_ms,
            priority=priority,
            max_instances=max_instances,
            ducking=ducking or {},
            segments=segments,
        )
        return self._dispatch_audio(command, audience=audience)

    def broadcast_sound_family(
        self,
        family: str,
        volume: int = 100,
        pan: int | None = None,
        pitch: int = 100,
        *,
        bus: str = "sfx",
        priority: int = 0,
        max_instances: int = 0,
        audience: Any = None,
        position: tuple[float, float, float] | None = None,
        attenuation: DistanceAttenuation | dict[str, Any] | None = None,
        gain: float = 1.0,
    ) -> str:
        """Play one dynamically discovered numbered member of an SFX family."""
        command = AudioCommand(
            command="play",
            kind="sfx",
            family=family,
            bus=bus,
            volume=volume,
            pan=pan,
            pitch=pitch,
            priority=priority,
            max_instances=max_instances,
            position=position,
            attenuation=attenuation,
            gain=gain,
        )
        return self._dispatch_audio(command, audience=audience)

    def play_sound_family(
        self,
        family: str,
        volume: int = 100,
        pan: int | None = None,
        pitch: int = 100,
        **kwargs: Any,
    ) -> str:
        """Alias for :meth:`broadcast_sound_family`."""
        return self.broadcast_sound_family(family, volume, pan, pitch, **kwargs)

    def stop_sound(
        self, handle: str, *, fade_ms: int = 0, audience: Any = None
    ) -> None:
        """Stop one managed loop by handle."""
        command = AudioCommand(
            command="stop",
            kind="sfx",
            handle=handle,
            fade_out_ms=fade_ms,
        )
        _, recipient_ids = self._audio_recipients(audience)
        self._dispatch_audio(command, audience=audience)
        self._remove_audio_states(
            lambda state: state.kind == "sfx" and state.handle == handle,
            None if audience is None else recipient_ids,
        )

    def _table_presence_flags(
        self,
        player: "Player | None" = None,
        *,
        is_bot: bool | None = None,
        is_spectator: bool | None = None,
    ) -> tuple[bool, bool]:
        """Resolve bot/spectator flags for table presence sounds."""
        resolved_bot = bool(getattr(player, "is_bot", False)) if is_bot is None else is_bot
        resolved_spectator = (
            bool(getattr(player, "is_spectator", False))
            if is_spectator is None
            else is_spectator
        )
        return resolved_bot, resolved_spectator

    def play_table_join_sound(
        self,
        player: "Player | None" = None,
        *,
        is_bot: bool | None = None,
        is_spectator: bool | None = None,
    ) -> None:
        """Play the appropriate table-entry sound for this game."""
        self._play_table_presence_sound(
            "join",
            player,
            is_bot=is_bot,
            is_spectator=is_spectator,
        )

    def play_table_leave_sound(
        self,
        player: "Player | None" = None,
        *,
        is_bot: bool | None = None,
        is_spectator: bool | None = None,
    ) -> None:
        """Play the appropriate table-exit sound for this game."""
        self._play_table_presence_sound(
            "leave",
            player,
            is_bot=is_bot,
            is_spectator=is_spectator,
        )

    def play_table_kick_sound(
        self,
        player: "Player | None" = None,
        *,
        is_bot: bool | None = None,
        is_spectator: bool | None = None,
    ) -> None:
        """Play the appropriate cue for an explicit or timeout table kick."""
        self._play_table_presence_sound(
            "kick",
            player,
            is_bot=is_bot,
            is_spectator=is_spectator,
        )

    def play_table_disconnect_sound(
        self,
        player: "Player | None" = None,
        *,
        is_bot: bool | None = None,
        is_spectator: bool | None = None,
    ) -> None:
        """Play the shared cue for an unexpected connection loss."""
        self._play_table_presence_sound(
            "disconnect",
            player,
            is_bot=is_bot,
            is_spectator=is_spectator,
        )

    def play_table_reconnect_sound(
        self,
        player: "Player | None" = None,
        *,
        is_bot: bool | None = None,
        is_spectator: bool | None = None,
    ) -> None:
        """Play the shared cue when a reserved table seat reconnects."""
        self._play_table_presence_sound(
            "reconnect",
            player,
            is_bot=is_bot,
            is_spectator=is_spectator,
        )

    def _play_table_presence_sound(
        self,
        event: str,
        player: "Player | None" = None,
        *,
        is_bot: bool | None = None,
        is_spectator: bool | None = None,
    ) -> None:
        """Resolve actor flags and enqueue one table-presence transition."""
        bot, spectator = self._table_presence_flags(
            player,
            is_bot=is_bot,
            is_spectator=is_spectator,
        )
        self._queue_table_presence_sound(
            event,
            is_bot=bot,
            is_spectator=spectator,
        )

    def _get_table_presence_sound(
        self,
        event: str,
        *,
        is_bot: bool,
        is_spectator: bool,
    ) -> str:
        """Return the game-specific cue for one table presence transition."""
        del is_bot
        spec = TABLE_PRESENCE_SOUND_SPECS.get(event)
        if spec is None:
            raise ValueError(f"Unknown table presence event: {event!r}")
        role = "spectator" if is_spectator else "player"
        return spec[role]

    def _queue_table_presence_sound(
        self,
        event: str,
        *,
        is_bot: bool,
        is_spectator: bool,
    ) -> None:
        """Play an identical table cue once per event-loop turn."""
        sound = self._get_table_presence_sound(
            event,
            is_bot=is_bot,
            is_spectator=is_spectator,
        )
        if not sound:
            return
        spec = TABLE_PRESENCE_SOUND_SPECS.get(event)
        if spec is None:
            raise ValueError(f"Unknown table presence event: {event!r}")
        direction = spec["direction"]
        table = getattr(self, "_table", None)
        server = getattr(table, "_server", None) if table else None
        if server and hasattr(server, "queue_presence_audio"):
            users, _ = self._audio_recipients()
            server.queue_presence_audio(
                users,
                event=direction,
                sound_name=sound,
                source="table",
            )
            return
        batcher = getattr(self, "_table_presence_audio_batcher", None)
        if batcher is None:
            batcher = SameTurnAudioBatcher()
            self._table_presence_audio_batcher = batcher
        batcher.queue(
            direction,
            lambda sound=sound: self.broadcast_sound(sound),
        )

    def play_music(
        self,
        name: str,
        looping: bool = True,
        *,
        handle: str = "music",
        bus: str = "music",
        fade_in_ms: int = DEFAULT_MUSIC_FADE_MS,
        fade_out_ms: int = DEFAULT_MUSIC_FADE_MS,
        priority: int = 0,
        ducking: dict[str, int] | None = None,
        audience: Any = None,
        scope: str = "global",
        context: str = "",
        layer: str = "main",
        pitch: int = 100,
        position: tuple[float, float, float] | None = None,
        attenuation: DistanceAttenuation | dict[str, Any] | None = None,
        gain: float = 1.0,
    ) -> str:
        """Play or crossfade an independently addressable music layer.

        Looping tracks are replayable state and resume after reconnect. Finite
        music cues are deliberately runtime-only; replacing a replayable track
        with one removes the old server-side ownership while the shared handle
        lets clients perform the authored crossfade.
        """
        command = AudioCommand(
            command="play",
            kind="music",
            asset=name,
            handle=handle,
            bus=bus,
            scope=scope,
            context=context,
            layer=layer,
            loop=looping,
            pitch=pitch,
            fade_in_ms=fade_in_ms,
            fade_out_ms=fade_out_ms,
            priority=priority,
            ducking=ducking or {},
            position=position,
            attenuation=attenuation,
            gain=gain,
        )
        persist = looping
        if not persist:
            _, recipient_ids = self._audio_recipients(audience)
            self._remove_audio_states(
                lambda state: self._audio_states_conflict(command, state),
                None if audience is None else recipient_ids,
            )
        return self._dispatch_audio(
            command,
            audience=audience,
            persist=persist,
        )

    def update_audio_source(
        self,
        kind: str,
        handle: str,
        duration_ms: int,
        *,
        destination: tuple[float, float, float] | None = None,
        gain: float | None = None,
        easing: str = "linear",
        audience: Any = None,
    ) -> str:
        """Automate independent parameters of one replayable managed source.

        A public source must move for its full audience. Private sources may be
        split by recipient so an individualized transition remains correct on
        reconnect and save restoration.
        """
        if destination is None and gain is None:
            raise ValueError("Audio update requires a destination or gain")
        destination_position = normalize_audio_position(destination)
        destination_gain = None if gain is None else normalize_audio_gain(gain)
        # Validate duration and easing before inspecting or mutating state. The
        # actual origins are captured below from the authoritative live state.
        if destination_position is not None:
            AudioMotion(
                origin_position=destination_position,
                destination_position=destination_position,
                duration_ms=duration_ms,
                easing=easing,
            )
        if destination_gain is not None:
            AudioGainAutomation(
                origin_gain=destination_gain,
                destination_gain=destination_gain,
                duration_ms=duration_ms,
                easing=easing,
            )
        _, recipient_ids = self._audio_recipients(audience)
        requested = None if audience is None else set(recipient_ids)
        if requested is not None and not requested:
            raise ValueError("Private audio updates require table recipients")

        matching = [
            state
            for state in self.active_audio.values()
            if state.kind == kind and state.handle == handle
        ]
        if not matching:
            raise ValueError(f"Unknown replayable audio source: {kind}:{handle}")
        if requested is not None and any(not state.recipient_ids for state in matching):
            raise ValueError(
                "Public audio sources cannot be updated for only part of the table"
            )
        if requested is not None:
            available = {
                recipient
                for state in matching
                for recipient in state.recipient_ids
            }
            if not requested <= available:
                raise ValueError("Audio source is not active for every requested recipient")
        selected = (
            matching
            if requested is None
            else [
                state
                for state in matching
                if requested.intersection(state.recipient_ids)
            ]
        )
        if destination_position is not None and any(
            state.position is None for state in selected
        ):
            raise ValueError("Audio motion requires an already-positioned source")

        rebuilt: dict[str, AudioPlaybackState] = {}
        deliveries: list[tuple[AudioCommand, list[str]]] = []
        for state in self.active_audio.values():
            if state.kind != kind or state.handle != handle:
                rebuilt[self._audio_state_key(state.to_command(), state.recipient_ids)] = state
                continue
            affected = (
                list(state.recipient_ids)
                if requested is None
                else [item for item in state.recipient_ids if item in requested]
            )
            if requested is not None and not affected:
                rebuilt[self._audio_state_key(state.to_command(), state.recipient_ids)] = state
                continue
            remaining = (
                []
                if requested is None
                else [item for item in state.recipient_ids if item not in requested]
            )
            motion = (
                AudioMotion(
                    origin_position=state.position,
                    destination_position=destination_position,
                    duration_ms=duration_ms,
                    easing=easing,
                )
                if destination_position is not None
                else state.motion
            )
            gain_automation = (
                AudioGainAutomation(
                    origin_gain=state.gain,
                    destination_gain=destination_gain,
                    duration_ms=duration_ms,
                    easing=easing,
                )
                if destination_gain is not None
                else state.gain_automation
            )
            updated = replace(
                state,
                recipient_ids=affected,
                motion=motion,
                gain_automation=gain_automation,
            )
            rebuilt[self._audio_state_key(updated.to_command(), affected)] = updated
            deliveries.append(
                (
                    AudioCommand(
                        command="update",
                        kind=kind,
                        handle=handle,
                        motion=(
                            motion if destination_position is not None else None
                        ),
                        gain_automation=(
                            gain_automation if destination_gain is not None else None
                        ),
                    ),
                    affected,
                )
            )
            if remaining:
                retained = replace(state, recipient_ids=remaining)
                rebuilt[self._audio_state_key(retained.to_command(), remaining)] = retained

        self.active_audio = rebuilt
        for command, recipients in deliveries:
            delivery_audience = None
            if recipients:
                recipient_set = set(recipients)
                delivery_audience = [
                    player for player in self.players if player.id in recipient_set
                ]
            self._dispatch_audio(command, audience=delivery_audience)
        return handle

    def move_audio_source(
        self,
        kind: str,
        handle: str,
        destination: tuple[float, float, float],
        duration_ms: int,
        **kwargs: Any,
    ) -> str:
        """Move a managed source along a resumable 3D trajectory."""
        return self.update_audio_source(
            kind,
            handle,
            duration_ms,
            destination=destination,
            **kwargs,
        )

    def set_audio_source_gain(
        self,
        kind: str,
        handle: str,
        gain: float,
        duration_ms: int,
        **kwargs: Any,
    ) -> str:
        """Automate an independent per-source mix gain without restarting it."""
        return self.update_audio_source(
            kind,
            handle,
            duration_ms,
            gain=gain,
            **kwargs,
        )

    def move_sound(
        self,
        handle: str,
        destination: tuple[float, float, float],
        duration_ms: int,
        **kwargs: Any,
    ) -> str:
        return self.move_audio_source("sfx", handle, destination, duration_ms, **kwargs)

    def move_music(
        self,
        handle: str,
        destination: tuple[float, float, float],
        duration_ms: int,
        **kwargs: Any,
    ) -> str:
        return self.move_audio_source("music", handle, destination, duration_ms, **kwargs)

    def move_ambience(
        self,
        handle: str,
        destination: tuple[float, float, float],
        duration_ms: int,
        **kwargs: Any,
    ) -> str:
        return self.move_audio_source("ambience", handle, destination, duration_ms, **kwargs)

    def set_sound_gain(
        self, handle: str, gain: float, duration_ms: int, **kwargs: Any
    ) -> str:
        return self.set_audio_source_gain("sfx", handle, gain, duration_ms, **kwargs)

    def set_music_gain(
        self, handle: str, gain: float, duration_ms: int, **kwargs: Any
    ) -> str:
        return self.set_audio_source_gain("music", handle, gain, duration_ms, **kwargs)

    def set_ambience_gain(
        self, handle: str, gain: float, duration_ms: int, **kwargs: Any
    ) -> str:
        return self.set_audio_source_gain(
            "ambience", handle, gain, duration_ms, **kwargs
        )

    @staticmethod
    def ambience_mix_gains(
        weights: dict[str, float], *, curve: str = "equal-power"
    ) -> dict[str, float]:
        """Convert non-negative zone weights into normalized layer gains."""
        if curve not in {"linear", "equal-power"}:
            raise ValueError(f"Unknown ambience mix curve: {curve!r}")
        if not weights:
            raise ValueError("Ambience mix requires at least one layer")
        normalized: dict[str, float] = {}
        for handle, weight in weights.items():
            if not isinstance(handle, str) or not handle:
                raise ValueError("Ambience mix handles must be non-empty strings")
            if (
                isinstance(weight, bool)
                or not isinstance(weight, (int, float))
                or not math.isfinite(float(weight))
                or float(weight) < 0.0
            ):
                raise ValueError(f"Invalid ambience weight for {handle!r}: {weight!r}")
            normalized[handle] = float(weight)
        total = sum(normalized.values())
        if not math.isfinite(total) or total <= 0.0:
            raise ValueError("Ambience mix requires a positive total weight")
        return {
            handle: (
                value / total
                if curve == "linear"
                else math.sqrt(value / total)
            )
            for handle, value in normalized.items()
        }

    def blend_ambience_layers(
        self,
        weights: dict[str, float],
        duration_ms: int,
        *,
        curve: str = "equal-power",
        easing: str = "linear",
        audience: Any = None,
    ) -> dict[str, float]:
        """Blend active ambience handles without restarting authored stems."""
        gains = self.ambience_mix_gains(weights, curve=curve)
        # Validate the complete operation before dispatching any packet.
        _, recipient_ids = self._audio_recipients(audience)
        requested = None if audience is None else set(recipient_ids)
        for handle, gain in gains.items():
            matching = [
                state
                for state in self.active_audio.values()
                if state.kind == "ambience" and state.handle == handle
            ]
            if not matching:
                raise ValueError(f"Unknown replayable audio source: ambience:{handle}")
            if requested is not None and (
                not requested
                or any(not state.recipient_ids for state in matching)
                or not requested
                <= {
                    recipient
                    for state in matching
                    for recipient in state.recipient_ids
                }
            ):
                raise ValueError(
                    "Ambience layer is not private to every requested recipient"
                )
            AudioGainAutomation(gain, gain, duration_ms, easing=easing)
        for handle, gain in gains.items():
            self.set_ambience_gain(
                handle,
                gain,
                duration_ms,
                easing=easing,
                audience=audience,
            )
        return gains

    def pause_music(
        self,
        *,
        handle: str = "music",
        fade_ms: int = DEFAULT_MUSIC_FADE_MS,
        audience: Any = None,
    ) -> None:
        """Fade and pause a music handle."""
        command = AudioCommand(
            command="pause",
            kind="music",
            handle=handle,
            fade_out_ms=fade_ms,
        )
        _, recipient_ids = self._audio_recipients(audience)
        self._dispatch_audio(command, audience=audience)
        self._set_audio_pause_state(
            lambda state: state.kind == "music" and state.handle == handle,
            True,
            None if audience is None else recipient_ids,
        )

    def resume_music(
        self,
        *,
        handle: str = "music",
        fade_ms: int = DEFAULT_MUSIC_FADE_MS,
        audience: Any = None,
    ) -> None:
        """Resume a paused music handle with a fade."""
        command = AudioCommand(
            command="resume",
            kind="music",
            handle=handle,
            fade_in_ms=fade_ms,
        )
        _, recipient_ids = self._audio_recipients(audience)
        self._dispatch_audio(command, audience=audience)
        self._set_audio_pause_state(
            lambda state: state.kind == "music" and state.handle == handle,
            False,
            None if audience is None else recipient_ids,
        )

    def stop_music(
        self,
        *,
        handle: str = "music",
        fade_ms: int = DEFAULT_MUSIC_FADE_MS,
        audience: Any = None,
    ) -> None:
        """Fade and stop a music handle."""
        command = AudioCommand(
            command="stop",
            kind="music",
            handle=handle,
            fade_out_ms=fade_ms,
        )
        _, recipient_ids = self._audio_recipients(audience)
        self._dispatch_audio(command, audience=audience)
        self._remove_audio_states(
            lambda state: state.kind == "music" and state.handle == handle,
            None if audience is None else recipient_ids,
        )

    def play_ambience(
        self,
        loop: str,
        intro: str = "",
        outro: str = "",
        *,
        handle: str = "",
        bus: str = "ambience",
        fade_in_ms: int = DEFAULT_AMBIENCE_FADE_MS,
        fade_out_ms: int = DEFAULT_AMBIENCE_FADE_MS,
        volume: int = 100,
        priority: int = 0,
        ducking: dict[str, int] | None = None,
        play_intro: bool = True,
        seamless: bool = True,
        audience: Any = None,
        scope: str = "global",
        context: str = "",
        layer: str = "environment",
        pitch: int = 100,
        position: tuple[float, float, float] | None = None,
        attenuation: DistanceAttenuation | dict[str, Any] | None = None,
        gain: float = 1.0,
    ) -> str:
        """Play or crossfade a global, private, or contextual ambience layer."""
        resolved_handle = handle or f"ambience:{scope}:{context or 'default'}:{layer}"
        command = AudioCommand(
            command="play",
            kind="ambience",
            asset=loop,
            handle=resolved_handle,
            bus=bus,
            scope=scope,
            context=context,
            layer=layer,
            loop=True,
            intro=intro,
            outro=outro,
            play_intro=play_intro,
            seamless=seamless,
            volume=volume,
            pitch=pitch,
            fade_in_ms=fade_in_ms,
            fade_out_ms=fade_out_ms,
            priority=priority,
            ducking=ducking or {},
            position=position,
            attenuation=attenuation,
            gain=gain,
        )
        return self._dispatch_audio(command, audience=audience, persist=True)

    def play_private_ambience(
        self, player: "Player", loop: str, **kwargs: Any
    ) -> str:
        """Convenience API for a player-specific ambience layer."""
        return self.play_ambience(
            loop,
            audience=player,
            scope="player",
            context=player.id,
            **kwargs,
        )

    def stop_ambience(
        self,
        *,
        handle: str = "",
        fade_ms: int = DEFAULT_AMBIENCE_FADE_MS,
        play_outro: bool = True,
        outro_mode: str = "immediate",
        audience: Any = None,
        scope: str = "global",
        context: str = "",
        layer: str = "environment",
    ) -> None:
        """Fade and stop an ambience handle or scoped layer."""
        command = AudioCommand(
            command="stop",
            kind="ambience",
            handle=handle,
            scope=scope,
            context=context,
            layer=layer,
            fade_out_ms=fade_ms,
            play_outro=play_outro,
            outro_mode=outro_mode,
        )
        _, recipient_ids = self._audio_recipients(audience)
        self._dispatch_audio(command, audience=audience)
        self._remove_audio_states(
            lambda state: (
                state.kind == "ambience"
                and (
                    (handle and state.handle == handle)
                    or (
                        not handle
                        and state.scope == scope
                        and state.context == context
                        and state.layer == layer
                    )
                )
            ),
            None if audience is None else recipient_ids,
        )

    def stop_all_ambience(
        self,
        *,
        fade_ms: int = DEFAULT_AMBIENCE_FADE_MS,
        play_outro: bool = True,
        outro_mode: str = "immediate",
        audience: Any = None,
    ) -> None:
        """Stop every ambience layer, preserving configured outros."""
        command = AudioCommand(
            command="stop",
            kind="ambience",
            all_layers=True,
            fade_out_ms=fade_ms,
            play_outro=play_outro,
            outro_mode=outro_mode,
        )
        _, recipient_ids = self._audio_recipients(audience)
        self._dispatch_audio(command, audience=audience)
        self._remove_audio_states(
            lambda state: state.kind == "ambience",
            None if audience is None else recipient_ids,
        )

    def set_audio_bus(
        self, bus: str, gain: int, *, fade_ms: int = 0, audience: Any = None
    ) -> None:
        """Set a named mix bus for an audience."""
        self._dispatch_audio(
            AudioCommand(
                command="set_bus",
                bus=bus,
                volume=gain,
                fade_in_ms=fade_ms,
            ),
            audience=audience,
        )

    def stop_all_audio(
        self,
        *,
        fade_ms: int = 0,
        play_outros: bool = False,
        outro_mode: str = "immediate",
        audience: Any = None,
    ) -> None:
        """Stop every server-controlled source and clear reconnect state."""
        _, recipient_ids = self._audio_recipients(audience)
        self._dispatch_audio(
            AudioCommand(
                command="stop_all",
                fade_out_ms=fade_ms,
                play_outros=play_outros,
                outro_mode=outro_mode,
            ),
            audience=audience,
        )
        if audience is None:
            self.active_audio.clear()
        else:
            self._remove_audio_states(
                lambda state: True,
                recipient_ids,
            )

    def stop_replayable_audio(
        self,
        *,
        fade_ms: int = 0,
        play_ambience_outros: bool = True,
        outro_mode: str = "immediate",
    ) -> None:
        """Stop every tracked layer without interrupting untracked one-shots.

        Game and lobby lifecycle boundaries use this instead of ``stop_all`` so
        victory cues that are already playing may finish while music, ambience,
        and managed looping effects are retired deterministically.
        """
        states = list(self.active_audio.values())
        for state in states:
            audience = None
            if state.recipient_ids:
                recipient_ids = set(state.recipient_ids)
                audience = [
                    player
                    for player in self.players
                    if player.id in recipient_ids
                ]
            self._dispatch_audio(
                AudioCommand(
                    command="stop",
                    kind=state.kind,
                    handle=state.handle,
                    scope=state.scope,
                    context=state.context,
                    layer=state.layer,
                    fade_out_ms=fade_ms,
                    play_outro=(
                        play_ambience_outros
                        if state.kind == "ambience"
                        else True
                    ),
                    outro_mode=outro_mode,
                ),
                audience=audience,
            )
        self.active_audio.clear()
