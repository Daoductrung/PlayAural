"""Mixin providing sound scheduling and playback for games."""

from collections.abc import Callable, Iterable
from dataclasses import replace
from typing import TYPE_CHECKING, Any

from ..audio import (
    AudioCommand,
    AudioPlaybackState,
    DEFAULT_AMBIENCE_FADE_MS,
    DEFAULT_MUSIC_FADE_MS,
    SameTurnAudioBatcher,
    new_audio_handle,
)

if TYPE_CHECKING:
    from .player import Player
    from ..users.base import User


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
        for user in users:
            user.send_audio_command(command)
        if persist:
            self.active_audio[self._audio_state_key(command, recipient_ids)] = (
                AudioPlaybackState.from_command(command, recipient_ids)
            )
        return command.handle

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
        pan: int = 0,
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
    ) -> str:
        """Play an effect for an audience and optionally retain a loop."""
        resolved_handle = handle or (new_audio_handle("sfx") if loop else "")
        command = AudioCommand(
            command="play",
            kind="sfx",
            asset=name,
            handle=resolved_handle,
            bus=bus,
            scope=scope,
            context=context,
            layer=layer,
            loop=loop,
            volume=volume,
            pan=pan,
            pitch=pitch,
            fade_in_ms=fade_in_ms,
            fade_out_ms=fade_out_ms,
            priority=priority,
            max_instances=max_instances,
            ducking=ducking or {},
        )
        return self._dispatch_audio(
            command, audience=audience, persist=persist and loop
        )

    def play_sound(
        self,
        name: str,
        volume: int = 100,
        pan: int = 0,
        pitch: int = 100,
        **kwargs: Any,
    ) -> str:
        """Alias for :meth:`broadcast_sound`."""
        return self.broadcast_sound(name, volume, pan, pitch, **kwargs)

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
    ) -> str:
        """Play or crossfade an independently addressable music layer."""
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
            fade_in_ms=fade_in_ms,
            fade_out_ms=fade_out_ms,
            priority=priority,
            ducking=ducking or {},
        )
        return self._dispatch_audio(command, audience=audience, persist=True)

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
            fade_in_ms=fade_in_ms,
            fade_out_ms=fade_out_ms,
            priority=priority,
            ducking=ducking or {},
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
