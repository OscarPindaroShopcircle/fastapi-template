# FastAPI Conventions

## Project Structure

Each feature lives in its own folder under `src/backend/`:

```
src/backend/
├── feature_name/
│   ├── __init__.py
│   ├── routes.py      # API endpoints
│   ├── schemas.py     # Pydantic models
│   ├── service.py     # Business logic
│   └── exceptions.py  # Feature-specific exceptions
├── db/
│   ├── db.py          # Base class, DatabaseManager
│   ├── mixins.py      # Reusable model mixins
│   └── models/        # SQLAlchemy models
├── schemas.py         # Shared base schemas (AppBaseModel, ListResponse)
├── dependencies.py    # Shared dependencies (get_db_session)
├── config.py          # Application configuration
└── server.py          # FastAPI app creation
```

## Shared Code Locations

| What | Where |
|------|-------|
| Base Pydantic models | `src/backend/schemas.py` |
| Database session dependency | `src/backend/dependencies.py` |
| SQLAlchemy Base & mixins | `src/backend/db/db.py`, `db/mixins.py` |
| App configuration | `src/backend/config.py` |

## Routes (routes.py)

### Router Setup

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db_session
from ..schemas import ListResponse
from .exceptions import EntityNotFound
from .schemas import EntityCreate, EntityResponse, EntityUpdate
from .service import create_entity, get_entity, get_all_entities, update_entity, delete_entity

router = APIRouter(prefix="/entities", tags=["entities"])
```

### Endpoint Documentation

Every endpoint must include:
1. **Docstring** - Explains what the endpoint does
2. **response_model** - Pydantic schema for response
3. **status_code** - Appropriate HTTP status code
4. **responses** - Document all possible status codes

```python
@router.post(
    "/",
    response_model=EntityResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Entity successfully created"},
    },
)
async def create_entity_endpoint(
    entity_data: EntityCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new entity with the provided data."""
    entity = await create_entity(db, entity_data)
    return entity
```

### Standard CRUD Endpoints

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| POST | `/` | 201 | Create new entity |
| GET | `/{id}` | 200, 404 | Get single entity |
| GET | `/` | 200 | Get all entities (wrapped in ListResponse) |
| PATCH | `/{id}` | 200, 404 | Update entity |
| DELETE | `/{id}` | 204, 404 | Delete entity |

## Service Layer (service.py)

Business logic functions that interact with the database:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.entity import EntityModel
from .schemas import EntityCreate, EntityUpdate


async def create_entity(db: AsyncSession, data: EntityCreate) -> EntityModel:
    entity = EntityModel(**data.model_dump())
    db.add(entity)
    await db.flush()
    await db.refresh(entity)
    return entity


async def get_entity(db: AsyncSession, entity_id: int) -> EntityModel | None:
    result = await db.execute(select(EntityModel).where(EntityModel.id == entity_id))
    return result.scalar_one_or_none()


async def get_all_entities(db: AsyncSession) -> list[EntityModel]:
    result = await db.execute(select(EntityModel))
    return list(result.scalars().all())


async def update_entity(db: AsyncSession, entity_id: int, data: EntityUpdate) -> EntityModel | None:
    entity = await get_entity(db, entity_id)
    if entity is None:
        return None

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)

    await db.flush()
    await db.refresh(entity)
    return entity


async def delete_entity(db: AsyncSession, entity_id: int) -> bool:
    entity = await get_entity(db, entity_id)
    if entity is None:
        return False

    await db.delete(entity)
    await db.flush()
    return True
```

## Exceptions (exceptions.py)

Feature-specific HTTP exceptions:

```python
from fastapi import HTTPException, status


class EntityNotFound(HTTPException):
    def __init__(self, entity_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with id {entity_id} not found",
        )
```

## Registering Routes

Add the router to the application in `server.py`:

```python
from .feature_name.routes import router as feature_router

app.include_router(feature_router)
```
