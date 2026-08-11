from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config import AppConfig, get_app_config
from ...dependencies import get_db_session
from ...db.models import InvitationModel
from ...schemas import ListResponse
from ...users.schemas import User
from ..dependencies import get_current_admin_user
from ..schemas import InvitationCreate, InvitationCreateResponse, InvitationResponse

router = APIRouter(
    prefix="/api/invitations",
    tags=["invitations"],
    dependencies=[Depends(get_current_admin_user)],
)


def _to_response(invitation: InvitationModel) -> InvitationResponse:
    return InvitationResponse(
        id=invitation.id,
        email=invitation.email,
        role=invitation.role,
        invited_by=invitation.invited_by,
        created_at=invitation.created_at,
        accepted_at=invitation.accepted_at,
        expires_at=invitation.expires_at,
    )


@router.post(
    "/",
    response_model=InvitationCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Invitation successfully created"},
        409: {"description": "An invitation for this email already exists"},
    },
)
async def create_invitation(
    body: InvitationCreate,
    db: AsyncSession = Depends(get_db_session),
    config: AppConfig = Depends(get_app_config),
    admin: User = Depends(get_current_admin_user),
):
    """Invite a user by email. Returns the invitation and the login link.

    Since matching is email-based, the invite link is just the regular login
    page — no token is needed.
    """
    # Check for an existing pending invitation for the same email.
    existing = await db.execute(
        select(InvitationModel).where(InvitationModel.email == body.email)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An invitation for {body.email} already exists",
        )

    expire_days = config.auth.invitation_expire_days if config.auth else 7
    invitation = InvitationModel(
        email=body.email,
        role=body.role,
        invited_by=admin.id,
        expires_at=datetime.now(UTC) + timedelta(days=expire_days),
    )
    db.add(invitation)
    await db.flush()
    await db.refresh(invitation)

    return InvitationCreateResponse(
        invitation=_to_response(invitation),
        invite_link="/auth/login",
    )


@router.get(
    "/",
    response_model=ListResponse[InvitationResponse],
    responses={
        200: {"description": "List of all invitations returned"},
    },
)
async def list_invitations(
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin_user),
):
    """List all invitations (pending and accepted)."""
    result = await db.execute(select(InvitationModel))
    invitations = result.scalars().all()
    return ListResponse(data=[_to_response(i) for i in invitations])


@router.delete(
    "/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Invitation successfully revoked"},
        404: {"description": "Invitation not found"},
    },
)
async def revoke_invitation(
    invitation_id: int,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(get_current_admin_user),
):
    """Revoke (delete) an invitation by ID."""
    result = await db.execute(
        select(InvitationModel).where(InvitationModel.id == invitation_id)
    )
    invitation = result.scalar_one_or_none()
    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invitation with id {invitation_id} not found",
        )
    await db.delete(invitation)
    await db.flush()
