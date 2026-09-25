from datetime import datetime, timedelta, timezone

import pytest

from ..moderation.chat_history import GlobalChatHistoryFilter
from ..moderation.reports import MAX_REPORTS_PER_WINDOW
from ..persistence.database import Database


def _connected_database(path) -> Database:
    database = Database(path)
    database.connect()
    return database


def test_report_persists_identity_time_reason_channel_and_message_anchor(
    tmp_path,
) -> None:
    path = tmp_path / "reports.sqlite"
    database = _connected_database(path)
    reporter = database.create_user("Reporter", "hash")
    target = database.create_user("Target", "hash")
    matching_message = database.add_global_chat_message(
        target.uuid,
        target.username,
        "en",
        "English context",
    )
    database.add_global_chat_message(
        target.uuid,
        target.username,
        "es",
        "Newer but different channel",
    )

    result = database.submit_moderation_report(
        reporter_uuid=reporter.uuid,
        reporter_username=reporter.username,
        reported_uuid=target.uuid,
        reported_username=target.username,
        reason_code="harassment",
        channel_code="en-US",
    )
    assert result.outcome == "created"
    assert result.report_id is not None
    database.close()

    reopened = _connected_database(path)
    try:
        report = reopened.get_moderation_report(result.report_id)
        assert report is not None
        assert report.reporter_uuid == reporter.uuid
        assert report.reporter_username == reporter.username
        assert report.reported_uuid == target.uuid
        assert report.reported_username == target.username
        assert report.reason_code == "harassment"
        assert report.channel_code == "en"
        assert report.context_anchor_message_id == matching_message.id
        assert report.status == "open"
        assert report.reviewed_by_uuid is None
        timestamp = datetime.fromisoformat(report.reported_at_utc)
        assert timestamp.utcoffset() == timedelta(0)
        assert reopened.count_moderation_reports(status="open") == 1
    finally:
        reopened.close()


def test_report_limits_are_persistent_and_do_not_change_target_state(tmp_path) -> None:
    database = _connected_database(tmp_path / "limits.sqlite")
    try:
        reporter = database.create_user("Reporter", "hash")
        targets = [
            database.create_user(f"Target {index}", "hash")
            for index in range(MAX_REPORTS_PER_WINDOW + 1)
        ]

        first = database.submit_moderation_report(
            reporter_uuid=reporter.uuid,
            reporter_username=reporter.username,
            reported_uuid=targets[0].uuid,
            reported_username=targets[0].username,
            reason_code="spam",
        )
        duplicate = database.submit_moderation_report(
            reporter_uuid=reporter.uuid,
            reporter_username=reporter.username,
            reported_uuid=targets[0].uuid,
            reported_username=targets[0].username,
            reason_code="spam",
        )
        assert first.outcome == "created"
        assert duplicate.outcome == "target_cooldown"
        assert duplicate.retry_after_seconds > 0

        for target in targets[1:MAX_REPORTS_PER_WINDOW]:
            result = database.submit_moderation_report(
                reporter_uuid=reporter.uuid,
                reporter_username=reporter.username,
                reported_uuid=target.uuid,
                reported_username=target.username,
                reason_code="other",
            )
            assert result.outcome == "created"

        limited = database.submit_moderation_report(
            reporter_uuid=reporter.uuid,
            reporter_username=reporter.username,
            reported_uuid=targets[-1].uuid,
            reported_username=targets[-1].username,
            reason_code="threats",
        )
        assert limited.outcome == "reporter_limit"
        assert limited.retry_after_seconds > 0
        assert database.count_moderation_reports() == MAX_REPORTS_PER_WINDOW
        assert database.get_user(targets[0].username) is not None
        assert database.get_active_mute(targets[0].username) is None
        indexes = {
            row["name"]
            for row in database._conn.execute(
                "PRAGMA index_list(moderation_reports)"
            ).fetchall()
        }
        assert "idx_moderation_reports_reporter_target_time" in indexes
    finally:
        database.close()


def test_account_deletion_retains_report_snapshots_for_manual_review(tmp_path) -> None:
    database = _connected_database(tmp_path / "deleted_accounts.sqlite")
    try:
        reporter = database.create_user("Reporter", "hash")
        target = database.create_user("Target", "hash")
        result = database.submit_moderation_report(
            reporter_uuid=reporter.uuid,
            reporter_username=reporter.username,
            reported_uuid=target.uuid,
            reported_username=target.username,
            reason_code="sexual_content",
            channel_code="es",
        )
        assert result.report_id is not None

        assert database.delete_user(reporter.username)
        assert database.delete_user(target.username)

        report = database.get_moderation_report(result.report_id)
        assert report is not None
        assert report.reporter_uuid == reporter.uuid
        assert report.reporter_username == reporter.username
        assert report.reported_uuid == target.uuid
        assert report.reported_username == target.username
    finally:
        database.close()


@pytest.mark.parametrize(
    "changes",
    [
        {"reported_uuid": "reporter-id"},
        {"reason_code": "invented"},
        {"channel_code": "invented"},
        {"details": 123},
    ],
)
def test_report_submission_rejects_invalid_records(tmp_path, changes) -> None:
    database = _connected_database(tmp_path / "invalid.sqlite")
    try:
        values = {
            "reporter_uuid": "reporter-id",
            "reporter_username": "Reporter",
            "reported_uuid": "target-id",
            "reported_username": "Target",
            "reason_code": "spam",
            "channel_code": "en",
        }
        values.update(changes)
        with pytest.raises(ValueError):
            database.submit_moderation_report(**values)
        assert database.count_moderation_reports() == 0
    finally:
        database.close()


def test_report_submission_rejects_mismatched_current_identity(tmp_path) -> None:
    database = _connected_database(tmp_path / "identity.sqlite")
    try:
        reporter = database.create_user("Reporter", "hash")
        target = database.create_user("Target", "hash")

        with pytest.raises(ValueError, match="current accounts"):
            database.submit_moderation_report(
                reporter_uuid=reporter.uuid,
                reporter_username=reporter.username,
                reported_uuid=target.uuid,
                reported_username="Reused Name",
                reason_code="spam",
            )

        assert database.count_moderation_reports() == 0
    finally:
        database.close()


def test_history_filter_keeps_reused_username_identities_separate(tmp_path) -> None:
    database = _connected_database(tmp_path / "sender_filter.sqlite")
    try:
        original = database.create_user("Repeated Name", "hash")
        database.add_global_chat_message(
            original.uuid, original.username, "en", "old identity"
        )
        assert database.delete_user(original.username)
        replacement = database.create_user("Repeated Name", "hash")
        database.add_global_chat_message(
            replacement.uuid, replacement.username, "en", "new identity one"
        )
        database.add_global_chat_message(
            replacement.uuid, replacement.username, "vi", "new identity two"
        )

        summaries = database.find_global_chat_sender_summaries("repeated name")
        assert {summary.sender_uuid for summary in summaries} == {
            original.uuid,
            replacement.uuid,
        }
        counts = {
            summary.sender_uuid: summary.message_count for summary in summaries
        }
        assert counts == {original.uuid: 1, replacement.uuid: 2}
        assert [
            record.message
            for record in database.list_global_chat_messages(
                sender_uuid=replacement.uuid,
                limit=1,
            )
        ] == ["new identity two"]
        assert [
            record.message
            for record in database.list_global_chat_messages(
                sender_uuid=replacement.uuid,
                limit=1,
                offset=1,
            )
        ] == ["new identity one"]
    finally:
        database.close()


def test_global_message_filters_compose_with_stable_ordering(tmp_path) -> None:
    database = _connected_database(tmp_path / "message_filters.sqlite")
    try:
        sender = database.create_user("Sender", "hash")
        records = [
            database.add_global_chat_message(
                sender.uuid,
                sender.username,
                channel,
                message,
            )
            for channel, message in (
                ("en", "August English"),
                ("vi", "September Vietnamese"),
                ("en", "September English one"),
                ("en", "September English two"),
            )
        ]
        timestamps = (
            "2026-08-31T23:59:59.000000+00:00",
            "2026-09-01T00:00:00.000000+00:00",
            "2026-09-02T12:00:00.000000+00:00",
            "2026-09-02T12:00:00.000000+00:00",
        )
        for record, timestamp in zip(records, timestamps, strict=True):
            database._conn.execute(
                "UPDATE global_chat_messages SET sent_at_utc = ? WHERE id = ?",
                (timestamp, record.id),
            )

        query = {
            "channel_code": "en",
            "started_at_utc": "2026-09-01T00:00:00+00:00",
            "ended_before_utc": "2026-10-01T00:00:00+00:00",
        }
        assert database.count_global_chat_messages(**query) == 2
        assert [
            item.message
            for item in database.list_global_chat_messages(
                **query,
                sort_order="oldest",
            )
        ] == ["September English one", "September English two"]
        assert [
            item.message
            for item in database.list_global_chat_messages(
                **query,
                sort_order="newest",
                limit=1,
                offset=1,
            )
        ] == ["September English one"]

        with pytest.raises(ValueError, match="sort order"):
            database.list_global_chat_messages(sort_order="random")
        with pytest.raises(ValueError, match="timezone"):
            database.count_global_chat_messages(
                started_at_utc="2026-09-01T00:00:00"
            )
        with pytest.raises(ValueError, match="empty or reversed"):
            database.count_global_chat_messages(
                started_at_utc="2026-10-01T00:00:00+00:00",
                ended_before_utc="2026-09-01T00:00:00+00:00",
            )
    finally:
        database.close()


def test_global_message_period_filters_use_precise_utc_boundaries() -> None:
    now = datetime(2026, 1, 1, 12, 30, 45, tzinfo=timezone.utc)

    assert GlobalChatHistoryFilter(period="all").utc_bounds(now=now) == (
        None,
        None,
    )
    assert GlobalChatHistoryFilter(period="today").utc_bounds(now=now) == (
        datetime(2026, 1, 1, tzinfo=timezone.utc),
        datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    assert GlobalChatHistoryFilter(period="previous_month").utc_bounds(
        now=now
    ) == (
        datetime(2025, 12, 1, tzinfo=timezone.utc),
        datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert GlobalChatHistoryFilter(period="last_7_days").utc_bounds(
        now=now
    ) == (now - timedelta(days=7), now)
    assert GlobalChatHistoryFilter.from_values(
        channel_code="unknown",
        period="unknown",
        sort_order="unknown",
    ) == GlobalChatHistoryFilter()
    with pytest.raises(ValueError, match="timezone"):
        GlobalChatHistoryFilter(period="today").utc_bounds(
            now=datetime(2026, 1, 1)
        )


def test_report_context_is_chronological_and_channel_scoped(tmp_path) -> None:
    database = _connected_database(tmp_path / "context.sqlite")
    try:
        reporter = database.create_user("Reporter", "hash")
        target = database.create_user("Target", "hash")
        other = database.create_user("Other", "hash")
        first = database.add_global_chat_message(
            other.uuid, other.username, "en", "before"
        )
        database.add_global_chat_message(
            other.uuid, other.username, "vi", "different channel"
        )
        target_message = database.add_global_chat_message(
            target.uuid, target.username, "en", "reported context"
        )
        result = database.submit_moderation_report(
            reporter_uuid=reporter.uuid,
            reporter_username=reporter.username,
            reported_uuid=target.uuid,
            reported_username=target.username,
            reason_code="harassment",
            channel_code="en",
        )
        report = database.get_moderation_report(result.report_id)
        after = database.add_global_chat_message(
            other.uuid, other.username, "en", "after"
        )

        context = database.get_global_chat_context(
            report.reported_at_utc,
            channel_code=report.channel_code,
            before_count=2,
            after_count=1,
        )
        assert [record.id for record in context] == [
            first.id,
            target_message.id,
            after.id,
        ]
    finally:
        database.close()


def test_manual_clear_lifecycle_preserves_open_reports(tmp_path) -> None:
    database = _connected_database(tmp_path / "clear.sqlite")
    try:
        reporter = database.create_user("Reporter", "hash")
        target = database.create_user("Target", "hash")
        reviewer = database.create_user("Developer", "hash", trust_level=3)
        database.add_global_chat_message(
            target.uuid, target.username, "en", "retained evidence"
        )
        first = database.submit_moderation_report(
            reporter_uuid=reporter.uuid,
            reporter_username=reporter.username,
            reported_uuid=target.uuid,
            reported_username=target.username,
            reason_code="spam",
            channel_code="en",
        )
        database._conn.execute(
            "UPDATE moderation_reports SET reported_at_utc = ? WHERE id = ?",
            (
                (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                first.report_id,
            ),
        )
        second = database.submit_moderation_report(
            reporter_uuid=reporter.uuid,
            reporter_username=reporter.username,
            reported_uuid=target.uuid,
            reported_username=target.username,
            reason_code="spam",
            channel_code="en",
        )
        assert second.outcome == "created"
        assert database.set_moderation_report_status(
            first.report_id,
            "dismissed",
            reviewer_uuid=reviewer.uuid,
            reviewer_username=reviewer.username,
        )
        assert not database.set_moderation_report_status(
            first.report_id,
            "actioned",
            reviewer_uuid=reviewer.uuid,
            reviewer_username=reviewer.username,
        )
        closed = database.get_moderation_report(first.report_id)
        assert closed.status == "dismissed"
        assert closed.reviewed_by_uuid == reviewer.uuid
        assert database.delete_user(reviewer.username)
        closed = database.get_moderation_report(first.report_id)
        assert closed.reviewed_by_username == reviewer.username

        assert database.clear_global_chat_messages() == 1
        assert database.count_global_chat_messages() == 0
        assert database.get_moderation_report(first.report_id).context_anchor_message_id is None
        assert database.get_moderation_report(second.report_id).context_anchor_message_id is None

        replacement_message = database.add_global_chat_message(
            target.uuid,
            target.username,
            "en",
            "numbering restarts after a complete clear",
        )
        assert replacement_message.id == 1

        assert database.clear_closed_moderation_reports() == 1
        assert database.get_moderation_report(first.report_id) is None
        assert database.get_moderation_report(second.report_id) is not None
        assert database.count_moderation_reports(status="open") == 1
        assert database.count_moderation_reports(
            statuses=("reviewed", "dismissed", "actioned")
        ) == 0
        extra_target = database.create_user("Another Target", "hash")
        third = database.submit_moderation_report(
            reporter_uuid=reporter.uuid,
            reporter_username=reporter.username,
            reported_uuid=extra_target.uuid,
            reported_username=extra_target.username,
            reason_code="spam",
        )
        assert third.report_id == 3
    finally:
        database.close()


def test_report_numbering_restarts_only_after_every_report_is_cleared(
    tmp_path,
) -> None:
    database = _connected_database(tmp_path / "report_sequence.sqlite")
    try:
        reporter = database.create_user("Reporter", "hash")
        target = database.create_user("Target", "hash")
        reviewer = database.create_user("Developer", "hash", trust_level=3)
        first = database.submit_moderation_report(
            reporter_uuid=reporter.uuid,
            reporter_username=reporter.username,
            reported_uuid=target.uuid,
            reported_username=target.username,
            reason_code="spam",
        )
        assert first.report_id == 1
        assert database.set_moderation_report_status(
            first.report_id,
            "dismissed",
            reviewer_uuid=reviewer.uuid,
            reviewer_username=reviewer.username,
        )
        assert database.clear_closed_moderation_reports() == 1
        assert database.count_moderation_reports() == 0

        replacement = database.submit_moderation_report(
            reporter_uuid=reporter.uuid,
            reporter_username=reporter.username,
            reported_uuid=target.uuid,
            reported_username=target.username,
            reason_code="spam",
        )
        assert replacement.report_id == 1
    finally:
        database.close()
