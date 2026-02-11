from pydantic import BaseModel, Field


class ProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)


class ProfileRead(ProfileBase):
    id: int

    model_config = {"from_attributes": True}
