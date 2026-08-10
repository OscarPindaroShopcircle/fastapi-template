from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ...db import Base
from .enums import StorageType
from ...mixins import TimestampMixin, UUIDv7PrimaryKeyMixin


class FileModel(Base, UUIDv7PrimaryKeyMixin, TimestampMixin):
    """A storage-agnostic reference to a file.

    Fully generic — a file can belong to a project, a user profile, or
    anything else later; whoever owns that link manages it (see
    ``ProjectFileModel``) rather than this table growing an FK per owner type.
    Ownership (who uploaded it) will likely be its own join table later too.

    ``location`` is the path/key of the file *within* its storage backend; the
    concrete FileSystem (local, s3, ...) knows how to resolve it. ``storage_type``
    records where it lives so we know which backend to hand it to.
    """

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(Text, nullable=False)
    storage_type: Mapped[StorageType | None] = mapped_column(
        Enum(StorageType),
        nullable=True,
        default=None,
    )
