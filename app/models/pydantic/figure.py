from pydantic import BaseModel, Field


class FigureStyles(BaseModel):
    """Значения по умолчанию ГОСТ для изображения Typst."""

    width: float = Field(1.0, ge=0.0, description="Ширина в em (0 = auto)")
    height: float = Field(0.0, ge=0.0, description="Высота в em (0 = auto)")


class FigureStylesUpdate(BaseModel):
    width: float | None = Field(None, ge=0.0)
    height: float | None = Field(None, ge=0.0)
