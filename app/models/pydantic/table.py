from typing import Optional

from pydantic import BaseModel, Field


class TableStyles(BaseModel):
    """Стили таблицы Typst: #set table(...)."""

    stroke: str = Field("0.5pt", max_length=32, description="Толщина линии")
    align: str = Field("auto", max_length=32, description="Выравнивание содержимого")
    inset: str = Field("5pt", max_length=32, description="Внутренний отступ ячеек")
    fill: str = Field("none", max_length=64, description="Заливка ячеек")


class TableStylesUpdate(BaseModel):
    stroke: Optional[str] = Field(None, max_length=32)
    align: Optional[str] = Field(None, max_length=32)
    inset: Optional[str] = Field(None, max_length=32)
    fill: Optional[str] = Field(None, max_length=64)
