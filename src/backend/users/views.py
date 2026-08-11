from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import get_current_admin_user
from ..auth.schemas import InvitationView
from ..auth.service import get_all_invitations
from ..config import AppConfig, get_app_config
from ..dependencies import get_catalog_dep, get_db_session
from ..db.models import InvitationModel, UserModel
from ..db.models.core.enums import UserRole
from ..users.schemas import User
from ..users.service import get_all_users

router = APIRouter(tags=["users-views"])


async def _build_invitations(db: AsyncSession) -> list[InvitationView]:
    """Fetch all invitations with inviter names — shared by page + htmx routes."""
    invitations_raw = await get_all_invitations(db)
    invitations = []
    for inv in invitations_raw:
        inviter = await db.get(UserModel, inv.invited_by)
        invitations.append(
            InvitationView(
                email=inv.email,
                role=inv.role,
                invited_by_name=inviter.name if inviter else "Unknown",
                expires_at=inv.expires_at,
                accepted_at=inv.accepted_at,
            )
        )
    return invitations


@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users(
    catalog=Depends(get_catalog_dep),
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_admin_user),
):
    """Admin users page — users and invitations from DB.

    Only accessible to admins; ``get_current_admin_user`` raises 403
    for non-admins and 401 for unauthenticated visitors.
    """
    users = [User.model_validate(u) for u in await get_all_users(db)]
    invitations = await _build_invitations(db)

    return catalog.render(
        "pages.admin.AdminDashboard",
        users=users,
        invitations=invitations,
        current_user=user,
    )


@router.get("/admin/users/invite", response_class=HTMLResponse)
async def invite_user_form(
    catalog=Depends(get_catalog_dep),
    user: User = Depends(get_current_admin_user),
):
    """Return the invite-user dialog — loaded by htmx into the page."""
    roles = [{"value": r.value, "label": r.value.capitalize()} for r in UserRole]
    return catalog.render("pages.admin.InviteDialog", current_user=user, roles=roles)


@router.post("/admin/users/invite", response_class=HTMLResponse)
async def invite_user_submit(
    email: str = Form(...),
    role: str = Form("member"),
    catalog=Depends(get_catalog_dep),
    db: AsyncSession = Depends(get_db_session),
    config: AppConfig = Depends(get_app_config),
    user: User = Depends(get_current_admin_user),
):
    """Create an invitation via htmx form submit.

    On success, returns the updated invitations table so htmx can
    swap it in place. On conflict (already invited), returns the
    dialog again with an error alert.
    """
    # Validate role
    try:
        role_enum = UserRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Check for existing pending invitation
    existing = await db.execute(
        select(InvitationModel).where(InvitationModel.email == email)
    )
    if existing.scalar_one_or_none() is not None:
        roles = [{"value": r.value, "label": r.value.capitalize()} for r in UserRole]
        return catalog.render(
            "pages.admin.InviteDialog",
            current_user=user,
            roles=roles,
            error=f"An invitation for {email} already exists",
            email=email,
            role=role,
        )

    expire_days = config.auth.invitation_expire_days if config.auth else 7
    invitation = InvitationModel(
        email=email,
        role=role_enum,
        invited_by=user.id,
        expires_at=datetime.now(UTC) + timedelta(days=expire_days),
    )
    db.add(invitation)
    await db.flush()

    # Return the updated invitations table for htmx to swap in
    invitations = await _build_invitations(db)
    return catalog.render(
        "pages.admin.InvitationsTable",
        invitations=invitations,
    )
