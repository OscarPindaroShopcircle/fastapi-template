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
