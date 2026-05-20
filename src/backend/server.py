from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_app_config
from .dependencies import get_db_manager
from .users.routes import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_manager = get_db_manager()
    await db_manager.initialize_tables()
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

    return app


app = create_app()
