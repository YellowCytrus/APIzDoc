from typing import Optional

from pydantic import BaseModel, Field

from app.models.pydantic.text_override import TextOverrideStyles, TextOverrideStylesUpdate


class TableStyles(BaseModel):
    """Стили таблицы Typst: #set table(...)."""

    stroke: float = Field(0.1763888889, ge=0.0, description="Толщина линии в mm")
    align: str = Field("auto", max_length=32, description="Выравнивание содержимого")
    inset: float = Field(1.7638888889, ge=0.0, description="Внутренний отступ ячеек в mm")
    fill: str = Field("none", max_length=64, description="Заливка ячеек")
    text_override: Optional[TextOverrideStyles] = None


class TableStylesUpdate(BaseModel):
    stroke: Optional[float] = Field(None, ge=0.0)
    align: Optional[str] = Field(None, max_length=32)
    inset: Optional[float] = Field(None, ge=0.0)
    fill: Optional[str] = Field(None, max_length=64)
    text_override: Optional[TextOverrideStylesUpdate | dict] = None
