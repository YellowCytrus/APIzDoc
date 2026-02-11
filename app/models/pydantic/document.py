from pydantic import BaseModel, Field


class DocumentStyles(BaseModel):
    """GOST defaults for Typst document (page, text size)."""

    font_size: float = Field(12.0, ge=6.0, le=72.0, description="Font size in pt")
    line_spacing: float = Field(1.2, ge=0.5, le=3.0, description="Line spacing in em")


class DocumentStylesUpdate(BaseModel):
    font_size: float | None = Field(None, ge=6.0, le=72.0)
    line_spacing: float | None = Field(None, ge=0.5, le=3.0)
