"""Generic cinematic sequence runner for timed gameplay/audio flows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from mashumaro.mixins.json import DataClassJSONMixin

if TYPE_CHECKING:
    from ..games.base import Player


@dataclass
class SequenceOperation(DataClassJSONMixin):
    """A single operation within a sequence beat."""

    kind: str
    sound: str = ""
    sounds_by_locale: dict[str, str] = field(default_factory=dict)
    fallback_locale: str = "en"
    volume: int = 100
    pan: int = 0
    pitch: int = 100
    callback_id: str = ""
    payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def sound_op(
        cls,
        sound: str,
        *,
        volume: int = 100,
        pan: int = 0,
        pitch: int = 100,
    ) -> "SequenceOperation":
        return cls(
            kind="sound",
            sound=sound,
            volume=volume,
            pan=pan,
            pitch=pitch,
        )

    @classmethod
    def localized_sound_op(
        cls,
        sounds_by_locale: dict[str, str],
        *,
        fallback_locale: str = "en",
        volume: int = 100,
        pan: int = 0,
        pitch: int = 100,
    ) -> "SequenceOperation":
        return cls(
            kind="localized_sound",
            sounds_by_locale=dict(sounds_by_locale),
            fallback_locale=fallback_locale,
            volume=volume,
            pan=pan,
            pitch=pitch,
        )

    @classmethod
    def callback_op(
        cls,
        callback_id: str,
        payload: dict[str, Any] | None = None,
    ) -> "SequenceOperation":
        return cls(
            kind="callback",
            callback_id=callback_id,
            payload=payload or {},
        )


@dataclass
class SequenceBeat(DataClassJSONMixin):
    """A group of operations that execute together, then wait."""

    ops: list[SequenceOperation] = field(default_factory=list)
    delay_after_ticks: int = 0

    @classmethod
    def pause(cls, delay_after_ticks: int) -> "SequenceBeat":
        return cls(delay_after_ticks=delay_after_ticks)


@dataclass
class SequenceState(DataClassJSONMixin):
    """Serialized state for an active cinematic sequence."""

    sequence_id: str
    beats: list[SequenceBeat] = field(default_factory=list)
    current_index: int = 0
    next_tick: int = 0
    tag: str = ""
    lock_scope: str = "none"
    pause_bots: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class SequenceRunnerMixin:
    """Run serialized, tick-driven action sequences for games."""

    SEQUENCE_LOCK_NONE = "none"
    SEQUENCE_LOCK_GAMEPLAY = "gameplay"
    SEQUENCE_LOCK_ALL = "all"
    MAX_SEQUENCE_BEATS_PER_TICK = 100

    def start_sequence(
        self,
        sequence_id: str,
        beats: list[SequenceBeat],
        *,
        start_delay: int = 0,
        tag: str = "",
        lock_scope: str = SEQUENCE_LOCK_NONE,
        pause_bots: bool = False,
        metadata: dict[str, Any] | None = None,
        replace_existing: bool = True,
        start_immediately: bool = True,
    ) -> None:
        """Start or replace a serialized sequence."""
        if replace_existing:
            self.cancel_sequence(sequence_id)

        sequence = SequenceState(
            sequence_id=sequence_id,
            beats=list(beats),
            next_tick=self.sound_scheduler_tick + max(0, start_delay),
            tag=tag,
            lock_scope=lock_scope,
            pause_bots=pause_bots,
            metadata=metadata or {},
        )
        self.active_sequences.append(sequence)
        if start_immediately:
            self._process_sequence(sequence_id, current_tick=self.sound_scheduler_tick)

    def process_sequences(self) -> None:
        """Advance any active sequences whose next beat is ready."""
        if not self.active_sequences:
            return

        before_signature = self._sequence_state_signature()
        current_tick = self.sound_scheduler_tick
        for sequence_id in [sequence.sequence_id for sequence in self.active_sequences]:
            self._process_sequence(sequence_id, current_tick=current_tick)
        after_signature = self._sequence_state_signature()
        if after_signature != before_signature:
            self.rebuild_all_menus()

    def cancel_sequence(self, sequence_id: str) -> None:
        self.active_sequences = [
            sequence
            for sequence in self.active_sequences
            if sequence.sequence_id != sequence_id
        ]

    def cancel_sequences_by_tag(self, tag: str) -> None:
        if not tag:
            return
        self.active_sequences = [
            sequence
            for sequence in self.active_sequences
            if sequence.tag != tag
        ]

    def cancel_all_sequences(self) -> None:
        self.active_sequences.clear()

    def has_active_sequence(
        self,
        *,
        sequence_id: str | None = None,
        tag: str | None = None,
    ) -> bool:
        for sequence in self.active_sequences:
            if sequence_id is not None and sequence.sequence_id != sequence_id:
                continue
            if tag is not None and sequence.tag != tag:
                continue
            return True
        return False

    def is_sequence_gameplay_locked(self) -> bool:
        return any(
            sequence.lock_scope in {self.SEQUENCE_LOCK_GAMEPLAY, self.SEQUENCE_LOCK_ALL}
            for sequence in self.active_sequences
        )

    def is_sequence_input_fully_locked(self) -> bool:
        return any(
            sequence.lock_scope == self.SEQUENCE_LOCK_ALL
            for sequence in self.active_sequences
        )

    def is_sequence_bot_paused(self) -> bool:
        return any(sequence.pause_bots for sequence in self.active_sequences)

    def on_sequence_callback(
        self,
        sequence_id: str,
        callback_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Hook for subclasses to react to sequence callback operations."""

    def _get_sequence(self, sequence_id: str) -> SequenceState | None:
        for sequence in self.active_sequences:
            if sequence.sequence_id == sequence_id:
                return sequence
        return None

    def _sequence_state_signature(self) -> tuple:
        return (
            tuple(
                (
                    sequence.sequence_id,
                    sequence.current_index,
                    sequence.next_tick,
                    sequence.lock_scope,
                    sequence.pause_bots,
                )
                for sequence in self.active_sequences
            ),
            self.is_sequence_gameplay_locked(),
            self.is_sequence_input_fully_locked(),
            self.is_sequence_bot_paused(),
        )

    def _process_sequence(self, sequence_id: str, *, current_tick: int) -> None:
        sequence = self._get_sequence(sequence_id)
        if sequence is None:
            return

        beats_processed = 0
        while sequence.current_index < len(sequence.beats) and sequence.next_tick <= current_tick:
            beat = sequence.beats[sequence.current_index]

            for operation in beat.ops:
                self._execute_sequence_operation(sequence.sequence_id, operation)
                current_sequence = self._get_sequence(sequence_id)
                if current_sequence is None:
                    return
                if current_sequence is not sequence:
                    return

            sequence.current_index += 1
            if sequence.current_index >= len(sequence.beats):
                self.cancel_sequence(sequence_id)
                return

            sequence.next_tick = current_tick + max(0, beat.delay_after_ticks)
            beats_processed += 1
            if beat.delay_after_ticks > 0:
                return
            if beats_processed >= self.MAX_SEQUENCE_BEATS_PER_TICK:
                sequence.next_tick = current_tick + 1
                return

    def _execute_sequence_operation(
        self,
        sequence_id: str,
        operation: SequenceOperation,
    ) -> None:
        if operation.kind == "sound":
            if operation.sound:
                self.play_sound(
                    operation.sound,
                    volume=operation.volume,
                    pan=operation.pan,
                    pitch=operation.pitch,
                )
            return

        if operation.kind == "localized_sound":
            self._play_localized_sequence_sound(operation)
            return

        if operation.kind == "callback":
            self.on_sequence_callback(
                sequence_id,
                operation.callback_id,
                dict(operation.payload),
            )

    def _play_localized_sequence_sound(self, operation: SequenceOperation) -> None:
        if not operation.sounds_by_locale:
            return

        fallback_sound = operation.sounds_by_locale.get(operation.fallback_locale)
        if fallback_sound is None:
            fallback_sound = next(iter(operation.sounds_by_locale.values()), None)

        if fallback_sound is None:
            return

        for player in self.players:
            user = self.get_user(player)
            if not user:
                continue
            locale = getattr(user, "locale", operation.fallback_locale)
            sound = operation.sounds_by_locale.get(locale, fallback_sound)
            user.play_sound(
                sound,
                volume=operation.volume,
                pan=operation.pan,
                pitch=operation.pitch,
            )
