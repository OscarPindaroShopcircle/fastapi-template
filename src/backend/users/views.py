from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import get_current_admin_user
from ..auth.schemas import InvitationView
from ..auth.service import get_all_invitations
from ..dependencies import get_catalog_dep, get_db_session
from ..db.models import UserModel
from ..users.schemas import User
from ..users.service import get_all_users

router = APIRouter(tags=["users-views"])


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

    return catalog.render(
        "pages.admin.AdminDashboard",
        users=users,
        invitations=invitations,
        current_user=user,
    )
