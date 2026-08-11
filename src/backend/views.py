from fastapi import APIRouter, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .auth.dependencies import get_current_user, get_optional_user
from .auth.schemas import InvitationView, RegisterRequest
from .auth.service import (
    get_all_invitations,
    login_with_password,
    register_with_password,
)
from .auth.exceptions import AuthError, InvalidCredentials, NotInvited
from .auth.sso import build_google_sso
from .auth.tokens import create_access_token, create_refresh_token, set_auth_cookies
from .config import AppConfig, get_app_config
from .db.models import UserModel
from .dependencies import get_catalog_dep, get_db_session
from .users.schemas import User
from .users.service import get_all_users

router = APIRouter(tags=["views"])


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    mode: str = Query("login", pattern="^(login|register)$"),
    error: str | None = Query(None),
    catalog=Depends(get_catalog_dep),
    config: AppConfig = Depends(get_app_config),
):
    """Login / register page — standalone (no sidebar layout)."""
    google_enabled = build_google_sso(config) is not None
    return catalog.render(
        "pages.login.Login",
        mode=mode,
        error=error,
        google_enabled=google_enabled,
    )


@router.post("/auth/login-form")
async def login_form(
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db_session),
    config: AppConfig = Depends(get_app_config),
):
    """Browser form-based login — sets cookies and redirects to /."""
    try:
        user = await login_with_password(db, email, password)
    except InvalidCredentials:
        return RedirectResponse(
            url="/login?error=Invalid email or password", status_code=303
        )
    access_token = create_access_token(user.id, user.email, user.role)
    refresh_token = create_refresh_token(user.id)
    response = RedirectResponse(url="/", status_code=303)
    set_auth_cookies(response, access_token, refresh_token, config)
    return response


@router.post("/auth/register-form")
async def register_form(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db_session),
    config: AppConfig = Depends(get_app_config),
):
    """Browser form-based registration — sets cookies and redirects to /."""
    try:
        user = await register_with_password(
            db,
            RegisterRequest(name=name, email=email, password=password),
            config,
        )
    except NotInvited:
        return RedirectResponse(
            url="/login?mode=register&error=This email is not invited",
            status_code=303,
        )
    except AuthError as e:
        return RedirectResponse(
            url=f"/login?mode=register&error={e.detail}", status_code=303
        )
    access_token = create_access_token(user.id, user.email, user.role)
    refresh_token = create_refresh_token(user.id)
    response = RedirectResponse(url="/", status_code=303)
    set_auth_cookies(response, access_token, refresh_token, config)
    return response


@router.get("/auth/logout-view")
async def logout_view():
    """Redirect-based logout — clears cookies and sends to /login."""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return response


@router.get("/", response_class=HTMLResponse)
async def index(
    catalog=Depends(get_catalog_dep),
    user: User | None = Depends(get_optional_user),
):
    """Home page — redirect to /login if not authenticated."""
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    return catalog.render(
        "layout.Page",
        title="Home",
        current_user=user,
        active="home",
    )


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(
    catalog=Depends(get_catalog_dep),
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    """Admin dashboard — real users and invitations from DB."""
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


@router.get("/components", response_class=HTMLResponse)
async def showcase(
    catalog=Depends(get_catalog_dep),
    db: AsyncSession = Depends(get_db_session),
    user: User | None = Depends(get_optional_user),
):
    """Component showcase — living style guide."""
    users = [User.model_validate(u) for u in await get_all_users(db)]
    return catalog.render(
        "pages.showcase.Showcase",
        users=users,
        current_user=user,
    )
