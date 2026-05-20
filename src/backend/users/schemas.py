from datetime import datetime
from typing import Annotated

from pydantic import Field

from ..schemas import AppBaseModelStripped


class UserCreate(AppBaseModelStripped):
    name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=255,
            examples=["John Doe"],
            description="User's full name",
        ),
    ]


class User(AppBaseModelStripped):
    id: Annotated[int, Field(examples=[1], description="User ID")]
    name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=255,
            examples=["John Doe"],
            description="User's full name",
        ),
    ]
    created_at: Annotated[
        datetime, Field(description="Timestamp when user was created")
    ]
    updated_at: Annotated[
        datetime, Field(description="Timestamp when user was last updated")
    ]


class UserResponse(AppBaseModelStripped):
    id: Annotated[int, Field(examples=[1], description="User ID")]
    name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=255,
            examples=["John Doe"],
            description="User's full name",
        ),
    ]
    created_at: Annotated[
        datetime, Field(description="Timestamp when user was created")
    ]
    updated_at: Annotated[
        datetime, Field(description="Timestamp when user was last updated")
    ]


class UserUpdate(AppBaseModelStripped):
    name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=255,
            examples=["Jane Smith"],
            description="Updated user name",
        ),
    ]


class UserDelete(AppBaseModelStripped):
    pass
