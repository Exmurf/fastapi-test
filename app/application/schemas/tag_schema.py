from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class TagCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=50,
    )


class TagResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    public_id: UUID
    name: str
