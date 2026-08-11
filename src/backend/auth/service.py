from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import AppConfig
from ..db.models.core.enums import UserRole
from ..db.models import InvitationModel, UserAuthProviderModel, UserModel
from .exceptions import NotInvited


async def find_by_provider(
    db: AsyncSession, provider: str, provider_sub: str
) -> UserModel | None:
    """Find a user by their provider link (already linked)."""
    stmt = (
        select(UserModel)
        .join(
            UserAuthProviderModel,
            UserAuthProviderModel.user_id == UserModel.id,
        )
        .where(
            UserAuthProviderModel.provider == provider,
            UserAuthProviderModel.provider_sub == provider_sub,
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def find_by_email(db: AsyncSession, email: str) -> UserModel | None:
    """Find a user by email (may exist from another provider)."""
    result = await db.execute(select(UserModel).where(UserModel.email == email))
    return result.scalar_one_or_none()


async def find_pending_invitation(
    db: AsyncSession, email: str
) -> InvitationModel | None:
    """Find a non-expired, non-accepted invitation for ``email``."""
    now = datetime.now(UTC)
    result = await db.execute(
        select(InvitationModel).where(
            InvitationModel.email == email,
            InvitationModel.accepted_at.is_(None),
            InvitationModel.expires_at > now,
        )
    )
    return result.scalar_one_or_none()


async def login_with_provider(
    db: AsyncSession, provider: str, openid, config: AppConfig
) -> UserModel:
    """Core login logic — link or create a user from a provider OpenID payload.

    1. If the provider link already exists, return that user.
    2. If the email matches an existing user (from another provider), link the
       new provider and return the user.
    3. Otherwise, check for a pending invitation or the bootstrap admin email.
       If neither, raise ``NotInvited``.
    4. Create the user + provider link.
    """
    # 1. Already linked?
    user = await find_by_provider(db, provider, openid.id)
    if user:
        return user

    # 2. Existing user via email from another provider?
    user = await find_by_email(db, openid.email)
    if user:
        db.add(
            UserAuthProviderModel(
                user_id=user.id, provider=provider, provider_sub=openid.id
            )
        )
        await db.flush()
        return user

    # 3. No user — check invitation or bootstrap admin
    invitation = await find_pending_invitation(db, openid.email)
    if invitation is None:
        bootstrap_email = config.auth.bootstrap_admin_email if config.auth else None
        if bootstrap_email and openid.email == bootstrap_email:
            role = UserRole.ADMIN
        else:
            raise NotInvited(openid.email)
    else:
        role = invitation.role
        invitation.accepted_at = datetime.now(UTC)

    # 4. Create user
    user = UserModel(
        name=openid.display_name or openid.email,
        email=openid.email,
        role=role,
    )
    db.add(user)
    await db.flush()

    # 5. Link provider
    db.add(
        UserAuthProviderModel(
            user_id=user.id, provider=provider, provider_sub=openid.id
        )
    )
    await db.flush()
    return user
