from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=1,
        max_length=128,
    )

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )

class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    public_id: str
    email: EmailStr
    is_active: bool

