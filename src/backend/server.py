from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth.routes.auth import router as auth_router
from .config import AppConfig, get_app_config
from .db.db import DatabaseManager
from .users.routes import router as users_router
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = get_app_config()
    db_manager = DatabaseManager(config.database)
    yield
    await db_manager.close()


def create_app(config: AppConfig | None = None) -> FastAPI:
    if config is None:
        config = get_app_config()

    app = FastAPI(
        title="Fantasy Backend",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=config.cors_allow_credentials,
        allow_methods=config.cors_allow_methods,
        allow_headers=config.cors_allow_headers,
    )

    if config.frontend and config.frontend.enabled:
        # JinjaX generates asset URLs like /static/components/common/button.css.
        # Mount the components directory BEFORE the generic /static mount so
        # the more specific prefix takes priority.
        app.mount(
            "/static/components",
            StaticFiles(directory=config.frontend.components_dir),
            name="components-static",
        )
        app.mount(
            "/static", StaticFiles(directory=config.frontend.static_dir), name="static"
        )

    # normal router import
    app.include_router(users_router)
    app.include_router(auth_router)

    # optional frontend routes
    if config.frontend and config.frontend.enabled:
        from .views import router as views_router  # noqa: PLC0415

        app.include_router(views_router)

    # health check endpoint
    @app.get("/ping")
    async def ping():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    config = get_app_config()
    app = create_app(config)
