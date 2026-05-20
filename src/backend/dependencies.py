from functools import lru_cache
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_app_config, AppConfig
from .db.db import DatabaseManager
from fastapi import Depends


def get_db_manager(config: AppConfig = Depends(get_app_config)) -> DatabaseManager:
    db_manager = DatabaseManager(config.database)
    return db_manager


async def get_db_session(
    db_manager: DatabaseManager = Depends(get_db_manager),
) -> AsyncGenerator[AsyncSession, None]:
    async with db_manager.async_session() as session:
        yield session


async def get_config() -> AppConfig:
    return get_app_config()


@lru_cache
async def get_templates_singleton(
    get_config: AppConfig = Depends(get_config),
):
    # local import in case jinja2 is not installed
    from fastapi.templating import Jinja2Templates

    return Jinja2Templates(directory=get_config.frontend.templates_dir)


async def get_templates():
    return get_templates_singleton()
