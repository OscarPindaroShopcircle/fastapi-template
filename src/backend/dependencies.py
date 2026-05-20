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
