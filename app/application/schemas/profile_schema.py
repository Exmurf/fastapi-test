from uuid import UUID

from pydantic import(
    BaseModel,
    EmailStr,
    Field,
)


class ProfileUserResponse(BaseModel):
    public_id: UUID
    email: EmailStr

class ProfileResponse(BaseModel):
    user: ProfileUserResponse
    first_name: str | None
    last_name: str | None
    bio: str | None

class ProfileUpdateRequest(BaseModel):
    first_name: str | None = Field(
        max_length=100,
    )

    last_name: str | None = Field(
        max_length=100,
    )

    bio: str | None = Field(
        max_length=500,
    )