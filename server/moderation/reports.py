"""Persistent manual-report policy shared by server and database layers."""

from dataclasses import dataclass
from typing import Literal


MAX_REPORT_DETAILS_LENGTH = 500
REPORT_LIMIT_WINDOW_SECONDS = 60 * 60
MAX_REPORTS_PER_WINDOW = 5
SAME_TARGET_REPORT_COOLDOWN_SECONDS = 10 * 60
MODERATION_REVIEW_PAGE_SIZE = 50
REPORT_CONTEXT_MESSAGES_BEFORE = 20
REPORT_CONTEXT_MESSAGES_AFTER = 10
MAX_MODERATION_QUERY_PAGE_SIZE = 500

REPORT_REASON_CODES: tuple[str, ...] = (
    "spam",
    "harassment",
    "hateful_content",
    "sexual_content",
    "threats",
    "personal_information",
    "other",
)
REPORT_REASON_CODE_SET = frozenset(REPORT_REASON_CODES)

REPORT_STATUSES: tuple[str, ...] = (
    "open",
    "reviewed",
    "dismissed",
    "actioned",
)
REPORT_STATUS_SET = frozenset(REPORT_STATUSES)
CLOSED_REPORT_STATUSES: tuple[str, ...] = REPORT_STATUSES[1:]


def report_reason_localization_key(reason_code: str) -> str:
    """Return the Fluent key for one validated player-report reason."""
    if reason_code not in REPORT_REASON_CODE_SET:
        raise ValueError("Unsupported moderation report reason")
    return f"report-reason-{reason_code.replace('_', '-')}"

ReportSubmissionOutcome = Literal[
    "created",
    "reporter_limit",
    "target_cooldown",
]


@dataclass(frozen=True)
class ModerationReportSubmission:
    """Result of one atomic report submission attempt."""

    outcome: ReportSubmissionOutcome
    report_id: int | None = None
    retry_after_seconds: int = 0
