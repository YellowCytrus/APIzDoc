from pydantic import BaseModel, Field


class TableStyles(BaseModel):
    """GOST defaults for Typst table."""

    stroke: str = Field("0.5pt", max_length=32, description="Stroke width, e.g. '0.5pt'")


class TableStylesUpdate(BaseModel):
    stroke: str | None = Field(None, max_length=32)
