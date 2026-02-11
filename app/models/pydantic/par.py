from pydantic import BaseModel, Field


class ParStyles(BaseModel):
    """GOST defaults for Typst paragraph."""

    spacing: float = Field(1.0, ge=0.0, description="Paragraph spacing in em")


class ParStylesUpdate(BaseModel):
    spacing: float | None = Field(None, ge=0.0)
