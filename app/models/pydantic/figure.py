from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.models.pydantic.text_override import TextOverrideStyles, TextOverrideStylesUpdate


class FigureStyles(BaseModel):
    """Стили изображения/фигуры Typst: #set image(...) + #set figure(...)."""

    width: float = Field(1.0, ge=0.0, description="Ширина в em (0 = auto)")
    height: float = Field(0.0, ge=0.0, description="Высота в em (0 = auto)")
    placement: Literal["none", "auto", "top", "bottom"] = Field(
        "none",
        description="Размещение фигуры на странице",
    )
    gap: float = Field(0.65, ge=0.0, description="Зазор между телом и подписью в em")
    outlined: bool = Field(True, description="Включать в список фигур")
    fit: Literal["cover", "contain", "stretch"] = Field(
        "cover",
        description="Способ подгонки изображения",
    )
    text_override: Optional[TextOverrideStyles] = None


class FigureStylesUpdate(BaseModel):
    width: Optional[float] = Field(None, ge=0.0)
    height: Optional[float] = Field(None, ge=0.0)
    placement: Optional[Literal["none", "auto", "top", "bottom"]] = None
    gap: Optional[float] = Field(None, ge=0.0)
    outlined: Optional[bool] = None
    fit: Optional[Literal["cover", "contain", "stretch"]] = None
    text_override: Optional[TextOverrideStylesUpdate | dict] = None
