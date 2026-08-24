from pydantic import BaseModel, EmailStr, Field

from app.modules.users.schemas import UserResponse


class RegisterRequest(BaseModel):
    """Payload for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    avatar_url: str | None = Field(default=None, max_length=500)


class LoginRequest(BaseModel):
    """Payload for user authentication."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class RefreshTokenRequest(BaseModel):
    """Payload for refreshing an access token."""

    refresh_token: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Authentication tokens returned upon login/registration/refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(BaseModel):
    """Combined response with token pair and user profile."""

    tokens: TokenResponse
    user: UserResponse


class MessageResponse(BaseModel):
    """Standard message response."""

    message: str
