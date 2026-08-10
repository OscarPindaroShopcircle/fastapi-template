import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...db import Base
from .enums import UserRole
from ...mixins import IntegerPrimaryKeyMixin, TimestampMixin


class InvitationModel(Base, IntegerPrimaryKeyMixin, TimestampMixin):
    """An email-based invitation to join the platform.

    Matching is by email only — on Google callback, ``openid.email`` is matched
    against pending (``accepted_at IS NULL``, not expired) invitations. No token
    column is needed because the OAuth flow itself is the proof of email
    ownership.
    """

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"), nullable=False, default=UserRole.MEMBER
    )
    invited_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
