"""Pydantic schemas for title page API."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.pydantic.page_editor import TitlePageContent


class TitlePageCreate(BaseModel):
    """Create a new title page."""

    name: str = Field(..., min_length=1, max_length=255)
    content: TitlePageContent


class TitlePageUpdate(BaseModel):
    """Update title page fields."""

    name: str | None = Field(None, min_length=1, max_length=255)
    content: TitlePageContent | None = None


class TitlePageRead(BaseModel):
    """Title page response."""

    id: int
    name: str
    content: TitlePageContent
    created_at: datetime

    model_config = {"from_attributes": True}
