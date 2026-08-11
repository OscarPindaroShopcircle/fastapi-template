from datetime import datetime
from typing import Annotated, Optional

from pydantic import ConfigDict, Field

from ..db.models.core.enums import UserRole
from ..schemas import AppBaseModelStripped


class TokenResponse(AppBaseModelStripped):
    """JWT access + refresh token pair returned after login or refresh.

    Overrides the camelCase alias generator so the JSON keys are snake_case
    (``access_token``, ``refresh_token``, ``token_type``) — the frontend JS
    and htmx interceptor read these exact keys from the response body.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        validate_default=True,
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        from_attributes=True,
        alias_generator=None,
    )

    access_token: Annotated[str, Field(description="Short-lived JWT access token")]
    refresh_token: Annotated[str, Field(description="Long-lived JWT refresh token")]
    token_type: Annotated[str, Field(default="bearer", description="Token type")]


class RefreshRequest(AppBaseModelStripped):
    """Request body for ``POST /auth/refresh``."""

    refresh_token: Annotated[str, Field(description="A valid refresh token")]


class InvitationCreate(AppBaseModelStripped):
    """Input for creating an invitation."""

    email: Annotated[str, Field(description="Email address to invite")]
    role: Annotated[
        UserRole,
        Field(default=UserRole.MEMBER, description="Role to assign"),
    ]


class InvitationResponse(AppBaseModelStripped):
    """API response for an invitation."""

    id: Annotated[int, Field(description="Invitation ID")]
    email: Annotated[str, Field(description="Invited email address")]
    role: Annotated[UserRole, Field(description="Role assigned to the invitee")]
    invited_by: Annotated[int, Field(description="User ID of the inviter")]
    created_at: Annotated[
        datetime, Field(description="When the invitation was created")
    ]
    accepted_at: Annotated[
        Optional[datetime],
        Field(description="When the invitation was accepted, if ever"),
    ]
    expires_at: Annotated[datetime, Field(description="When the invitation expires")]


class InvitationCreateResponse(AppBaseModelStripped):
    """Response for ``POST /api/invitations`` — invitation plus the login link."""

    invitation: Annotated[
        InvitationResponse, Field(description="The created invitation")
    ]
    invite_link: Annotated[str, Field(description="Login link for the invitee")]
