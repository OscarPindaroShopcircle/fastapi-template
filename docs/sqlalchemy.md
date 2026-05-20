# SQLAlchemy Model Conventions

## Base Class

All models must inherit from `Base` located in `src/backend/db/db.py`.

```python
from ..db.db import Base
```

## Naming Convention

- **Class names** should end with `Model` (e.g., `UserModel`, `TeamModel`)
- **Table names** are auto-generated: `UserModel` → `users`, `TeamModel` → `teams`
  - The `Model` suffix is stripped automatically
  - CamelCase is converted to snake_case
  - Names are pluralized

## Available Mixins

Mixins are located in `src/backend/db/mixins.py`. Use them to add common fields:

| Mixin | Fields | Use Case |
|-------|--------|----------|
| `IntegerPrimaryKeyMixin` | `id: int` (auto-increment) | Standard integer PKs |
| `BigIntPrimaryKeyMixin` | `id: int` (BigInteger) | High-volume tables |
| `UUIDv4PrimaryKeyMixin` | `id: UUID` (random) | External-facing, security-sensitive IDs |
| `UUIDv7PrimaryKeyMixin` | `id: UUID` (time-sortable) | High-insert tables, better index locality |
| `TimestampMixin` | `created_at`, `updated_at` | Track record timestamps |
| `SoftDeleteMixin` | `deleted_at` | Soft delete pattern |
| `OptimisticLockMixin` | `version` | Prevent lost updates |
| `AuditMixin` | `created_by`, `updated_by` | Track who modified records |

## Example Model

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base
from ..mixins import IntegerPrimaryKeyMixin, TimestampMixin


class UserModel(Base, IntegerPrimaryKeyMixin, TimestampMixin):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
```

## Model Registration

All models must be imported in `src/backend/db/models/__init__.py` to ensure they are registered with SQLAlchemy before table creation:

```python
from .user import UserModel
from .team import TeamModel

__all__ = ["UserModel", "TeamModel"]
```

This ensures `Base.metadata.create_all()` creates all tables during application startup.
