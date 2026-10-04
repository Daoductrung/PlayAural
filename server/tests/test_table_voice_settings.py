import json

import pytest

from ..tables.table import Table
from ..users.test_user import MockUser


def _table_with_members() -> tuple[Table, MockUser, MockUser]:
    alice = MockUser("Alice", uuid="uuid-alice")
    bob = MockUser("Bob", uuid="uuid-bob")
    table = Table(table_id="table-one", game_type="pig", host="Alice")
    assert table.add_member("Alice", alice)
    assert table.add_member("Bob", bob)
    return table, alice, bob


def test_target_departure_preserves_others_settings_but_clears_listener_state() -> None:
    table, _alice, bob = _table_with_members()
    assert table.set_voice_host_muted(bob.uuid, True)
    assert table.set_personal_voice_volume("uuid-alice", bob.uuid, 40)
    assert table.set_personal_voice_muted("uuid-alice", bob.uuid, True)
    assert table.set_personal_voice_volume(bob.uuid, "uuid-alice", 70)

    assert table.remove_member("Bob")

    assert table.is_voice_host_muted(bob.uuid)
    assert table.get_personal_voice_settings("uuid-alice", bob.uuid) == (40, True)
    assert table.get_personal_voice_settings(bob.uuid, "uuid-alice") == (100, False)
    assert table.add_member("Bob", bob)
    assert table.get_personal_voice_settings("uuid-alice", bob.uuid) == (40, True)


def test_voice_settings_only_enter_durable_live_table_checkpoints() -> None:
    table, _alice, bob = _table_with_members()
    assert table.set_voice_host_muted(bob.uuid, True)
    assert table.set_personal_voice_volume("uuid-alice", bob.uuid, 30)

    manual_payload = json.loads(table.serialize_saved_state())
    checkpoint_json = table.serialize_saved_state(include_checkpoint_state=True)
    checkpoint_payload = json.loads(checkpoint_json)

    assert set(manual_payload["properties"]) == {"banned_uuids", "is_private"}
    assert "voice_host_muted_account_ids" in checkpoint_payload["properties"]
    restored = Table(table_id="table-one", game_type="pig", host="Alice")
    restored.restore_saved_state(
        Table.deserialize_saved_state(
            checkpoint_json,
            include_checkpoint_state=True,
        )
    )
    assert restored.is_voice_host_muted(bob.uuid)
    assert restored.get_personal_voice_settings("uuid-alice", bob.uuid) == (30, False)


@pytest.mark.parametrize(
    ("property_name", "invalid_value"),
    [
        ("voice_host_muted_account_ids", [" uuid-bob"]),
        ("voice_personal_volumes", {"uuid-alice": {"uuid-bob": 41}}),
    ],
)
def test_malformed_voice_checkpoint_state_is_rejected(
    property_name: str,
    invalid_value: object,
) -> None:
    table, _alice, _bob = _table_with_members()
    payload = json.loads(table.serialize_saved_state(include_checkpoint_state=True))
    payload["properties"][property_name] = invalid_value

    with pytest.raises(ValueError, match="voice_"):
        Table.deserialize_saved_state(
            json.dumps(payload),
            include_checkpoint_state=True,
        )


def test_deleted_account_is_pruned_as_listener_target_and_moderation_subject() -> None:
    table, _alice, bob = _table_with_members()
    assert table.set_voice_host_muted(bob.uuid, True)
    assert table.set_personal_voice_muted("uuid-alice", bob.uuid, True)
    assert table.set_personal_voice_volume(bob.uuid, "uuid-alice", 50)

    table.discard_voice_account_settings(bob.uuid)

    assert not table.is_voice_host_muted(bob.uuid)
    assert table.get_personal_voice_settings("uuid-alice", bob.uuid) == (100, False)
    assert table.get_personal_voice_settings(bob.uuid, "uuid-alice") == (100, False)


def test_destroy_clears_all_table_voice_settings() -> None:
    table, _alice, bob = _table_with_members()
    assert table.set_voice_host_muted(bob.uuid, True)
    assert table.set_personal_voice_muted("uuid-alice", bob.uuid, True)

    table.destroy()

    assert not table.is_voice_host_muted(bob.uuid)
    assert table.personal_voice_settings_snapshot("uuid-alice") == []
