import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...db import Base
from .enums import UserRole
from ...mixins import IntegerPrimaryKeyMixin, TimestampMixin, UUIDv7PrimaryKeyMixin


class UserModel(Base, UUIDv7PrimaryKeyMixin, TimestampMixin):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"), nullable=False, default=UserRole.MEMBER
    )
    is_active: Mapped[bool] = mapped_column(default=True)


class UserPasswordModel(Base, IntegerPrimaryKeyMixin, TimestampMixin):
    """Password hash for test/admin users who authenticate without an OAuth provider.

    One row per user (enforced by the unique FK column). Storing the hash in a
    separate table keeps ``UserModel`` provider-agnostic — a user with only
    Google SSO has no row here at all.
    """

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)


class UserAuthProviderModel(Base, IntegerPrimaryKeyMixin, TimestampMixin):
    """Links a user to an external auth provider (Google, GitHub, …) or password.

    One row per provider per user — a user who has logged in via both Google
    and GitHub has two rows here. ``provider_sub`` is the provider's own unique
    identifier for the user (the ``sub`` claim in OIDC).
    """

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_sub: Mapped[str] = mapped_column(String(255), nullable=False)

    __table_args__ = (
        UniqueConstraint("provider", "provider_sub", name="uq_provider_sub"),
    )
