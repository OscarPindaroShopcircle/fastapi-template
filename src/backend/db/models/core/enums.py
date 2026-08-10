"""Enumerations shared by the database models.

Backed by SQLAlchemy `Enum(...)` columns on the models. We prefer real enums
over free string columns so the set of valid values is enforced at the DB level.
"""

from enum import Enum


class TaskStatus(str, Enum):
    """Lifecycle status of an async Task.

    WAITING     → created but blocked on something else before it can start
    IN_PROGRESS → currently running
    FAILED      → terminated with an error
    SUCCESS     → completed successfully
    """

    WAITING = "WAITING"
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"


class StorageType(str, Enum):
    """Where a File physically lives.

    Only LOCAL is wired up for now; the rest are placeholders for the
    filesystem backends we'll add later (S3, Azure Blob, Railway volumes).
    """

    LOCAL = "LOCAL"
    S3 = "S3"


class FeedbackValue(str, Enum):
    """Thumbs up / thumbs down feedback value.

    Used by ``BinaryFeedbackMixin`` on the ranking and generative output
    tables — the human "OK / NOT OK" judgment on a prediction (F7).
    """

    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"


class DataSplit(str, Enum):
    """Train/test split assignment for a judgement.

    TRAIN — used for model training (example sampling, prompt construction)
    VAL   — reserved for future validation split (not used yet)
    TEST  — held out for evaluation only

    NULL on the column means the judgement has not been assigned to a split yet.
    """

    TRAIN = "train"
    VAL = "val"
    TEST = "test"


class UserRole(str, Enum):
    """User role for authorization.

    ADMIN  — full access, can view admin pages and create invitations
    MEMBER — default role for invited users
    """

    ADMIN = "admin"
    MEMBER = "member"
