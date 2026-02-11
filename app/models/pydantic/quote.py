from pydantic import BaseModel, Field


class QuoteStyles(BaseModel):
    """GOST defaults for Typst quote block."""

    indent: float = Field(1.5, ge=0.0, description="Indent in em")


class QuoteStylesUpdate(BaseModel):
    indent: float | None = Field(None, ge=0.0)
