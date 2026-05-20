from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base
from ..mixins import IntegerPrimaryKeyMixin, TimestampMixin


class UserModel(Base, IntegerPrimaryKeyMixin, TimestampMixin):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
