from pydantic import BaseModel, Field


class HeadingStyles(BaseModel):
    """GOST defaults for Typst heading."""

    numbering: str = Field("1.1.1", max_length=64, description="Numbering pattern or 'none'")


class HeadingStylesUpdate(BaseModel):
    numbering: str | None = Field(None, max_length=64)
