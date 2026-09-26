"""Persistent moderation-report policy shared by server and database layers."""

import json
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
AUTOMATED_SPAM_REPORT_COOLDOWN_SECONDS = 6 * 60 * 60
AUTOMATED_SPAM_EVIDENCE_VERSION = 1
SYSTEM_REPORTER_UUID = "system:anti-spam"
SYSTEM_REPORTER_USERNAME = "System"
MODERATION_REPORT_NOTIFICATION_SOUND = "moderation_report.ogg"

REPORT_ORIGIN_MANUAL = "manual"
REPORT_ORIGIN_AUTOMATED_SPAM = "automated_spam"
ReportContext = Literal["global", "table"]
REPORT_CONTEXT_GLOBAL: ReportContext = "global"
REPORT_CONTEXT_TABLE: ReportContext = "table"
REPORT_CONTEXT_CODES: tuple[ReportContext, ...] = (
    REPORT_CONTEXT_GLOBAL,
    REPORT_CONTEXT_TABLE,
)
SPAM_DETECTION_KINDS = ("rate_limited", "repeated_message")

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
    "automation_cooldown",
]


@dataclass(frozen=True)
class ModerationReportSubmission:
    """Result of one atomic report submission attempt."""

    outcome: ReportSubmissionOutcome
    report_id: int | None = None
    retry_after_seconds: int = 0


@dataclass(frozen=True)
class AutomatedSpamEvidence:
    """Versioned, non-punitive evidence attached to an automatic report."""

    scope: ReportContext
    detection_kind: Literal["rate_limited", "repeated_message"]
    incident_count: int
    rejected_attempt_count: int
    accepted_message_count: int
    observation_window_seconds: int
    sample_message: str

    def to_json(self) -> str:
        """Serialize validated evidence without locale-dependent prose."""
        if self.scope not in REPORT_CONTEXT_CODES:
            raise ValueError("Unsupported automated-report scope")
        if self.detection_kind not in SPAM_DETECTION_KINDS:
            raise ValueError("Unsupported spam detection kind")
        if min(
            self.incident_count,
            self.rejected_attempt_count,
            self.accepted_message_count,
            self.observation_window_seconds,
        ) < 0:
            raise ValueError("Automated-report counters cannot be negative")
        if not isinstance(self.sample_message, str):
            raise ValueError("Automated-report sample must be text")
        return json.dumps(
            {
                "version": AUTOMATED_SPAM_EVIDENCE_VERSION,
                "scope": self.scope,
                "detection_kind": self.detection_kind,
                "incident_count": self.incident_count,
                "rejected_attempt_count": self.rejected_attempt_count,
                "accepted_message_count": self.accepted_message_count,
                "observation_window_seconds": self.observation_window_seconds,
                "sample_message": self.sample_message[:MAX_REPORT_DETAILS_LENGTH],
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, value: str) -> "AutomatedSpamEvidence | None":
        """Parse evidence defensively so damaged or unsupported rows remain reviewable."""
        try:
            data = json.loads(value)
            if data.get("version") != AUTOMATED_SPAM_EVIDENCE_VERSION:
                return None
            evidence = cls(
                scope=data["scope"],
                detection_kind=data["detection_kind"],
                incident_count=int(data["incident_count"]),
                rejected_attempt_count=int(data["rejected_attempt_count"]),
                accepted_message_count=int(data["accepted_message_count"]),
                observation_window_seconds=int(data["observation_window_seconds"]),
                sample_message=str(data["sample_message"])[
                    :MAX_REPORT_DETAILS_LENGTH
                ],
            )
            evidence.to_json()
            return evidence
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            return None
