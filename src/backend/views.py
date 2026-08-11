from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from .auth.dependencies import get_optional_user
from .dependencies import get_catalog_dep
from .users.schemas import User

router = APIRouter(tags=["views"])


@router.get("/", response_class=HTMLResponse)
async def index(
    catalog=Depends(get_catalog_dep),
    user: User | None = Depends(get_optional_user),
):
    """Home page — redirect to /login if not authenticated."""
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    return catalog.render(
        "pages.home.Home",
        current_user=user,
    )
