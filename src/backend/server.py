from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_app_config
from .db.db import DatabaseManager
from .users.routes import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = get_app_config()
    db_manager = DatabaseManager(config.database)
    yield
    await db_manager.close()


def create_app() -> FastAPI:
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

    app.include_router(users_router)

    @app.get("/ping")
    async def ping():
        return {"status": "ok"}

    return app


app = create_app()
