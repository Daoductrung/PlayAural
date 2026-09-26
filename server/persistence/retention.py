"""Shared lifecycle constants for persistent transient server data."""

# A matching hidden backup fragment is not assumed to be abandoned while it
# could still belong to another operator-owned backup or recovery process.
ABANDONED_BACKUP_FRAGMENT_MINIMUM_AGE_SECONDS = 24 * 60 * 60

TRANSIENT_TABLE_CHECKPOINT_RETENTION_DAYS = 1
EXPIRED_BAN_RETENTION_DAYS = 30
PENDING_FRIEND_REQUEST_RETENTION_DAYS = 180
USER_NOTIFICATION_RETENTION_DAYS = 180
