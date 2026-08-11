from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from .dependencies import get_catalog_dep

router = APIRouter(tags=["views"])


@router.get("/", response_class=HTMLResponse)
async def index(catalog=Depends(get_catalog_dep)):
    """Home page — renders the Page layout with Sidebar and some content."""
    # Mock user for preview — will be replaced with get_optional_user
    # once DB is running
    mock_user = {
        "name": "Oscar",
        "email": "oscar@circeus.com",
        "role": "admin",
    }
    return catalog.render(
        "layout.Page",
        title="Home",
        current_user=mock_user,
        active="home",
    )


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(catalog=Depends(get_catalog_dep)):
    """Admin dashboard — shows users and pending invitations."""
    mock_user = {
        "name": "Oscar",
        "email": "oscar@circeus.com",
        "role": "admin",
    }
    mock_users = [
        {
            "name": "Oscar",
            "email": "oscar@circeus.com",
            "role": "admin",
            "is_active": True,
        },
        {
            "name": "Alice",
            "email": "alice@circeus.com",
            "role": "member",
            "is_active": True,
        },
        {
            "name": "Bob",
            "email": "bob@circeus.com",
            "role": "member",
            "is_active": False,
        },
    ]
    mock_invitations = [
        {
            "email": "charlie@circeus.com",
            "role": "member",
            "invited_by": "Oscar",
            "invited_by_name": "Oscar",
            "expires_at": "2026-08-18",
            "accepted_at": None,
        },
        {
            "email": "diana@circeus.com",
            "role": "admin",
            "invited_by": "Oscar",
            "invited_by_name": "Oscar",
            "expires_at": "2026-08-20",
            "accepted_at": None,
        },
    ]
    return catalog.render(
        "admin.AdminDashboard",
        users=mock_users,
        invitations=mock_invitations,
        current_user=mock_user,
    )
