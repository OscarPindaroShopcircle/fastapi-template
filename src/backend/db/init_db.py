from .db import DatabaseManager


async def init_db(db_manager: DatabaseManager) -> None:
    """Initialize the database by creating all tables from Base metadata.

    Args:
        db_manager: DatabaseManager instance
    """
    await db_manager.initialize_tables()
