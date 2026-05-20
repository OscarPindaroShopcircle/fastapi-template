from datetime import datetime
from typing import Generic, List, TypeVar
from zoneinfo import ZoneInfo

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


def datetime_to_gmt_str(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


_base_config = dict(
    json_encoders={datetime: datetime_to_gmt_str},
    populate_by_name=True,
    alias_generator=to_camel,
    validate_default=True,
    validate_assignment=True,
    use_enum_values=True,
)


class AppBaseModel(BaseModel):
    """Base model — preserves original whitespace in string fields."""

    model_config = ConfigDict(**_base_config, from_attributes=True)

    def serializable_dict(self, **kwargs):
        """Return a dict which contains only serializable fields."""
        return jsonable_encoder(self.model_dump())


class AppBaseModelStripped(AppBaseModel):
    """Base model — strips leading/trailing whitespace from all string fields."""

    model_config = ConfigDict(
        **_base_config, str_strip_whitespace=True, from_attributes=True
    )


T = TypeVar("T")


class ListResponse(AppBaseModel, Generic[T]):
    """Generic wrapper for list responses to allow future metadata extension."""

    data: List[T]
