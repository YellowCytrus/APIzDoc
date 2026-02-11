from pydantic import BaseModel, Field


class FigureStyles(BaseModel):
    """GOST defaults for Typst figure."""

    width: float = Field(1.0, ge=0.0, description="Width in em (0 = auto)")
    height: float = Field(0.0, ge=0.0, description="Height in em (0 = auto)")


class FigureStylesUpdate(BaseModel):
    width: float | None = Field(None, ge=0.0)
    height: float | None = Field(None, ge=0.0)
